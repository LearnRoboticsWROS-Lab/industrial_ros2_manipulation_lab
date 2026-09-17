cmake_minimum_required(VERSION 3.8)
project(yt_ur5_robotiq_scene_loader_moveit_config)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME})

ament_package()
