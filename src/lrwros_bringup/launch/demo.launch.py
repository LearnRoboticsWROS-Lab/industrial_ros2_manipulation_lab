"""The Module 0 demo: launch the UR5 + Robotiq + depth camera workcell.

The fast win — Gazebo with the full cell and RViz with the MoveIt planning
scene, one command. This is the same cell Module 3 opens up layer by layer.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    workcell_launch = os.path.join(
        get_package_share_directory('lrwros_ur5_workcell'),
        'launch', 'spawn_ur5_camera_gripper_world_moveit.launch.py')
    return LaunchDescription([
        IncludeLaunchDescription(PythonLaunchDescriptionSource(workcell_launch)),
    ])
