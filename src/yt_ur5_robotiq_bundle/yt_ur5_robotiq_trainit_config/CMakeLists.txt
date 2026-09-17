cmake_minimum_required(VERSION 3.8)
project(yt_ur5_robotiq_trainit_config)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME})

# Gazebo LinkAttacher grasp adapter bridge (ADR-0010), run in the gazebo bring-up.
install(PROGRAMS scripts/link_attacher_bridge.py
  DESTINATION lib/${PROJECT_NAME})

ament_package()
