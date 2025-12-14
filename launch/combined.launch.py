from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import Command
import os

def generate_launch_description():
    pkg_share = get_package_share_directory('autonomous_sphere_collector_pkg')

    # Path to your URDF/Xacro and controller config
    urdf_file = os.path.join(get_package_share_directory(pkg_share), 'urdf', 'Robot.xacro')
    controllers_yaml = os.path.join(pkg_share, 'config', 'ros_controllers.yaml')

    # Gazebo launch (your existing assessment world launch)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'gazebo_assessment.launch.py')
        )
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro, urdf_file']),
            'use_sim_time': True
        }]
    )

    # ros2_control_node
    control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[controllers_yaml, {'robot_description': Command(['xacro ', urdf_file])}],
        output='screen'
    )

    # Spawners for controllers
    spawner_diff_drive = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller'],
    )
    spawner_jsb = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )
    spawner_scoop = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['scoop_controller'],
    )

    # ROS–Gazebo bridges
    bridge_scan = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/lidar_sensor/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan'],
        output='screen'
    )
    bridge_camera = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/camera_sensor/image@sensor_msgs/msg/Image@gz.msgs.Image'],
        output='screen'
    )
    bridge_clock = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock'],
        output='screen'
    )

    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher,
        control_node,
        spawner_diff_drive,
        spawner_jsb,
        spawner_scoop,
        bridge_scan,
        bridge_camera,
        bridge_clock,
    ])
