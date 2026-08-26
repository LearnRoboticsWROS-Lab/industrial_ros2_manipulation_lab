cmake_minimum_required(VERSION 3.8)
project(yt_vision_pick_place)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(moveit_msgs REQUIRED)
find_package(shape_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(linkattacher_msgs REQUIRED)

# --- C++ motion node: plan, grasp, attach, place -----------------------------
add_executable(pick_place_node src/pick_place_node.cpp)
ament_target_dependencies(pick_place_node
  rclcpp
  moveit_ros_planning_interface
  moveit_msgs
  shape_msgs
  geometry_msgs
  std_msgs
  std_srvs
  tf2
  tf2_ros
  tf2_geometry_msgs
  linkattacher_msgs
)

install(TARGETS pick_place_node
  DESTINATION lib/${PROJECT_NAME}
)

# --- Python perception + spawn helpers ---------------------------------------
install(PROGRAMS
  scripts/perception_node.py
  scripts/spawn_target.py
  DESTINATION lib/${PROJECT_NAME}
)

# --- launch / config / models -------------------------------------------------
install(DIRECTORY launch config models
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
