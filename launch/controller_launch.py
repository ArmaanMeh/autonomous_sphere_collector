from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
import os

def generate_launch_description():
    # Absolute paths to your files
    urdf_file = os.path.join(
        os.getenv('HOME'),
        'ros2/ros2_ws/src/autonomous_sphere_collector_pkg/urdf',
        'Robot.xacro'
    )
    controllers_file = os.path.join(
        os.getenv('HOME'),
        'ros2/ros2_ws/src/autonomous_sphere_collector_pkg/config',
        'ros_controllers.yaml'
    )

    return LaunchDescription([
        # Robot State Publisher (publishes TF tree from URDF/Xacro)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': Command(['xacro ', urdf_file])
            }]
        ),

        # Controller Manager (loads ros_controllers.yaml)
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[controllers_file],
            output='screen'
        ),

        # Spawners for controllers
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_state_broadcaster'],
            output='screen'
        ),
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['diff_drive_controller'],
            output='screen'
        ),
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['scoop_controller'],
            output='screen'
        )
    ])
