import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Define the package name for dynamic path retrieval
    pkg_name = 'autonomous_sphere_collector_pkg'
    
    # 2. Get the path to the installed package 'share' directory
    pkg_share = get_package_share_directory(pkg_name)

    # 3. Define paths to xacro and rviz files based on the share directory
    # Note: Ensure these files are installed via setup.py or CMakeLists.txt
    urdf_file = os.path.join(pkg_share, 'urdf', 'autonomous_sphere_collector.urdf.xacro')
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'Robot_view.rviz')

    # 4. Create the Robot State Publisher Node
    # We use xacro to process the file before passing it to the parameter
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', urdf_file])
        }]
    )

    # 5. Create the Joint State Publisher GUI Node
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # 6. Create the RViz2 Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
    )

    # 7. Return the LaunchDescription
    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])