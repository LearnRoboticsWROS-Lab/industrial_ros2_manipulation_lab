from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess, RegisterEventHandler
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, Command
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.event_handlers import OnProcessStart
from launch.event_handlers import OnProcessExit
from launch.events import TimerEvent
from launch.actions import TimerAction
from ament_index_python.packages import get_package_share_directory
import os
import xacro
from launch.event_handlers import OnProcessStart
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    ld = LaunchDescription()

    joint_controllers_file = os.path.join(
        get_package_share_directory('lrwros_ur5_workcell'), 'config', 'ur5_gripper_controllers.yaml'
    )
    gazebo_launch_file = os.path.join(
        get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'
    )

    world_file = os.path.join(
        get_package_share_directory('lrwros_ur5_workcell'), 'worlds', 'pick_place_workplace.world'
    )

    moveit_config = (
        MoveItConfigsBuilder("custom_robot", package_name="lrwros_ur5_moveit_config")
        .robot_description(file_path="config/ur.urdf.xacro")
        .robot_description_semantic(file_path="config/ur.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .planning_scene_monitor(
            publish_robot_description= True, publish_robot_description_semantic=True, publish_planning_scene=True
        )
        .planning_pipelines(
            pipelines=["ompl", "chomp", "pilz_industrial_motion_planner"]
        )
        .to_moveit_configs()
    )


    x_arg = DeclareLaunchArgument('x', default_value='0', description='X position of the robot')
    y_arg = DeclareLaunchArgument('y', default_value='0', description='Y position of the robot')
    z_arg = DeclareLaunchArgument('z', default_value='0', description='Z position of the robot')

    # Include Gazebo launch file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch_file),
        launch_arguments={
            'use_sim_time': 'true',
            'debug': 'false',
            'gui': 'true',
            'paused': 'true',
            'world' : world_file
        }.items()
    )

    rviz_config_path = os.path.join(
        get_package_share_directory("lrwros_ur5_moveit_config"),
        "config",
        "moveit.rviz",
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_path],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.planning_pipelines,
            moveit_config.robot_description_kinematics,
        ],
    )

    # spawn the robot
    spawn_the_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'cobot',
            '-topic', 'robot_description',
            '-x', LaunchConfiguration('x'),
            '-y', LaunchConfiguration('y'),
            '-z', LaunchConfiguration('z')
        ],
        output='screen',
    )

    # Controller startup — the reliability-critical part on Gazebo Classic.
    #
    # This standalone controller_manager node is REQUIRED even though it exits: on
    # Gazebo Classic the real controller_manager is the one embedded in the
    # gazebo_ros2_control plugin (inside gzserver), but bringing this node up (same
    # robot_description + controllers YAML) is what lets the plugin's controllers
    # reach a configurable state. Removing it makes every configure fail
    # persistently ("Failed to configure controller" forever). It only sequences
    # the spawners via OnProcessStart, then exits (it cannot load GazeboSystem).
    controller_manager_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[moveit_config.robot_description, joint_controllers_file],
        output='screen',
        remappings=[
            ("~/robot_description", "/robot_description"),
        ],
    )

    # Even with the node above, the plugin's GazeboSystem hardware is exported a
    # variable moment later, so a one-shot spawner that fires too early dies with
    # "Failed to configure controller" — the flaky failure that left the arm with
    # no active controller. Instead of guessing a delay we RETRY: re-attempt each
    # controller until configure sticks (the spawner re-configures an already-loaded
    # controller on each pass). Timing-independent, so reliable headless and in GUI.
    spawn_controllers = ExecuteProcess(
        cmd=['bash', '-c', '''
CM=/controller_manager
spawn() {
  name=$1
  for i in $(seq 1 30); do
    if ros2 run controller_manager spawner "$name" -c "$CM" --controller-manager-timeout 60; then
      echo "[spawn_controllers] $name active"
      return 0
    fi
    echo "[spawn_controllers] $name attempt $i not ready; retrying in 2s"
    sleep 2
  done
  echo "[spawn_controllers] ERROR: $name never came up"
  return 1
}
spawn joint_state_broadcaster
spawn joint_trajectory_controller
spawn gripper_position_controller
echo "[spawn_controllers] all controllers up"

# --- Homing -------------------------------------------------------------------------
# A real cell homes its robot when it powers up, and so does this one.
#
# It is not cosmetic. Between the moment Gazebo spawns the arm and the moment the
# controllers actually take command of it (the ten-odd seconds above, while the plugin
# exports its hardware), NOTHING is holding the arm: it sags forward under gravity and
# comes to rest lying over the bench. The controller then activates and dutifully holds
# it THERE.
#
# That resting pose is inside the table's collision volume, so the first thing any
# application does — plan a motion — fails before it starts:
#
#   Start state appears to be in collision with respect to group ur5_manipulator
#   contact between 'table1' (Object) and 'upper_arm_link' (Robot link)
#
# We command 'home' straight through the controller's trajectory topic: no MoveIt, no
# planning, no collision checking. That is the whole point — a planner cannot rescue a
# robot that starts in collision.
sleep 2
ros2 topic pub --once /joint_trajectory_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory \
  "{joint_names: [shoulder_pan_joint, shoulder_lift_joint, elbow_joint, wrist_1_joint, wrist_2_joint, wrist_3_joint], points: [{positions: [0.0, -2.2564, 1.4059, -1.57, -1.57, 0.0], time_from_start: {sec: 5, nanosec: 0}}]}" \
  >/dev/null 2>&1
sleep 6
echo "[homing] the arm is at 'home' — the cell is ready for an application"
'''],
        output='screen',
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[moveit_config.robot_description],
        output='screen'
    )

    use_sim_time={"use_sim_time": True}
    config_dict = moveit_config.to_dict()
    config_dict.update(use_sim_time)

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[config_dict],
        arguments=["--ros-args", "--log-level", "info"],
    )


    # Start the retry-spawner as soon as the controller_manager node starts (as in
    # the original launch); the retry loop absorbs the plugin hardware-init race.
    start_controllers = RegisterEventHandler(
        OnProcessStart(
            target_action=controller_manager_node,
            on_start=[spawn_controllers],
        )
    )

    delay_rviz_node = RegisterEventHandler(
        OnProcessStart(
            target_action=robot_state_publisher,
            on_start=[rviz_node],
        )
    )


    # Launch Description
    ld.add_action(x_arg)
    ld.add_action(y_arg)
    ld.add_action(z_arg)
    ld.add_action(gazebo)
    ld.add_action(controller_manager_node)  # sequences the retry-spawner (OnProcessStart)
    ld.add_action(spawn_the_robot)
    ld.add_action(robot_state_publisher)
    ld.add_action(move_group_node)
    # Bring the controllers up, with retry to absorb the Gazebo hardware-init race.
    ld.add_action(start_controllers)
    ld.add_action(delay_rviz_node)



    return ld


