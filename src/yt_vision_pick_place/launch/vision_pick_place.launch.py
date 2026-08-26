"""yt_vision_pick_place — one-command launch.

Brings up the existing Manipulation Lab cell (Gazebo world + UR5 + Robotiq +
depth camera + MoveIt2), then adds the three demo nodes on top of it:

    spawn_target      -> drops the red object at a random valid spot
    perception_node   -> finds it and publishes a 3D target pose
    pick_place_node   -> plans, grasps, attaches, lifts, places

The cell itself is NOT reimplemented here — it is included from
lrwros_ur5_workcell. This launch only adds the vertical slice.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory("yt_vision_pick_place")
    workcell = get_package_share_directory("lrwros_ur5_workcell")
    params = os.path.join(pkg, "config", "params.yaml")

    run_on_start = LaunchConfiguration("run_on_start")
    use_collision_scene = LaunchConfiguration("use_collision_scene")
    motion_planning = LaunchConfiguration("motion_planning")

    # The cell: world + UR5(cobot) + Robotiq + camera + MoveIt2 (the module_03 launch).
    cell = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(workcell, "launch", "spawn_ur5_camera_gripper_world_moveit.launch.py")
        )
    )

    spawn = Node(
        package="yt_vision_pick_place", executable="spawn_target.py",
        name="yt_spawn_target", output="screen", parameters=[params],
    )
    perception = Node(
        package="yt_vision_pick_place", executable="perception_node.py",
        name="yt_perception_node", output="screen", parameters=[params],
    )
    pick_place = Node(
        package="yt_vision_pick_place", executable="pick_place_node",
        name="yt_pick_place_node", output="screen",
        parameters=[params,
                    {"run_on_start": run_on_start,
                     "use_collision_scene": use_collision_scene,
                     "motion_planning": motion_planning}],
    )

    return LaunchDescription([
        DeclareLaunchArgument("run_on_start", default_value="true",
                              description="Run one pick-and-place automatically once the cell is up."),
        DeclareLaunchArgument("use_collision_scene", default_value="true",
                              description="Add the tables as obstacles. Set false to show unplanned chaos."),
        DeclareLaunchArgument("motion_planning", default_value="ompl",
                              description="Planner pipeline: 'ompl' (avoids obstacles) or 'pilz' (industrial PTP)."),
        cell,
        # Give Gazebo, controllers and move_group time to come up before we act.
        TimerAction(period=8.0, actions=[spawn, perception]),
        TimerAction(period=22.0, actions=[pick_place]),
    ])
