cmake_minimum_required(VERSION 3.8)
project(autonomous_sphere_collector)

# =================================================================
# 1. Find Dependencies
# =================================================================
find_package(ament_cmake REQUIRED)

# Core ROS 2 packages
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# Simulation and Description Packages
find_package(ros_gz_sim REQUIRED)
find_package(ros_gz_bridge REQUIRED)     
find_package(robot_state_publisher REQUIRED)
find_package(xacro REQUIRED)

# =================================================================
# 2. Install Configurations and Executables
# =================================================================

# Installs static directories to the share path
install(
  DIRECTORY 
    config 
    launch 
    rviz 
    map 
    urdf 
  DESTINATION share/${PROJECT_NAME}
)

# Installs Python teleop script to the libexec folder
# Using CMAKE_CURRENT_SOURCE_DIR guarantees CMake finds the absolute path!
install(PROGRAMS
  ${CMAKE_CURRENT_SOURCE_DIR}/autonomous_sphere_collector/teleop/bot_teleop.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME bot_teleop
)

# =================================================================
# 3. Export Dependencies
# =================================================================
ament_export_dependencies(
  ros_gz_sim
  ros_gz_bridge
  robot_state_publisher
  xacro
)

# =================================================================
# 4. Finalize Package Indexing
# =================================================================
ament_package()