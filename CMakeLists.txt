cmake_minimum_required(VERSION 3.8)
project(autonomous_sphere_collector_pkg)

# --- 1. Find Dependencies ---
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

# --- 2. Install Directories ---

# Explicitly install all assets and configuration folders into the share destination
# --- 2. Install Directories (Corrected Folder Structural Mapping) ---

# --- 2. Install Directories (Corrected Syntax) ---

install(
  DIRECTORY 
    config 
    launch 
    rviz 
    map 
    urdf 
    worlds
  DESTINATION share/${PROJECT_NAME}
)
# --- 3. Export Dependencies ---
# Only exporting active simulation and layout processing dependencies
ament_export_dependencies(
  ros_gz_sim
  ros_gz_bridge
  robot_state_publisher
  xacro
)

# --- 4. Finalize ---
ament_package()