cmake_minimum_required(VERSION 3.8)
project(autonomous_sphere_collector_pkg)

# --- 1. Find Dependencies (Added Missing Controllers/Bridge Packages) ---
find_package(ament_cmake REQUIRED)

# Core ROS 2 packages
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# Simulation and Description Packages
find_package(ros_gz_sim REQUIRED)
find_package(ros_gz_bridge REQUIRED)     # <-- ADDED for the gz_bridge.yaml
find_package(robot_state_publisher REQUIRED)
find_package(xacro REQUIRED)

# ROS 2 Control Packages
find_package(ros2_control REQUIRED)
find_package(controller_manager REQUIRED) # <-- ADDED for launching controllers
find_package(control_msgs REQUIRED)
find_package(joint_state_broadcaster REQUIRED) # <-- ADDED based on YAML
find_package(diff_drive_controller REQUIRED)    # <-- ADDED based on YAML
find_package(joint_trajectory_controller REQUIRED) # <-- ADDED for scoop_controller

# --- 2. Install Directories (Specific File/Directory Installation) ---


# Install Config/YAML files
install(
  DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
)

install(
  DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

install(
  DIRECTORY rviz/
  DESTINATION share/${PROJECT_NAME}/rviz
)
install(
  DIRECTORY map/
  DESTINATION share/${PROJECT_NAME}/map
)
# Install URDF/Xacro files and Meshes/Models
# Use GLOB_RECURSE to ensure all files (including subfolders for meshes) are included
file(GLOB_RECURSE URDF_FILES "urdf/*")
install(
  FILES ${URDF_FILES}
  DESTINATION share/${PROJECT_NAME}/urdf
)

# --- 3. Export Dependencies (Includes new found packages) ---
ament_export_dependencies(
  ros_gz_sim
  ros_gz_bridge
  robot_state_publisher
  xacro
  ros2_control
  controller_manager
  joint_state_broadcaster
  diff_drive_controller
  joint_trajectory_controller
)

# --- 4. Finalize ---
ament_package()