cmake_minimum_required(VERSION 3.8)
project(yt_ur5_robotiq_app)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config bt_trees groot2
  DESTINATION share/${PROJECT_NAME})
# mock gripper action server (no-op, used in mock mode)
install(PROGRAMS scripts/mock_gripper_action_server.py
  DESTINATION lib/${PROJECT_NAME})

ament_package()
