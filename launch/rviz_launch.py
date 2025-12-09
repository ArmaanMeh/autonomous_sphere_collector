from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
import os

def generate_launch_description():
    # Path to your robot description (Xacro file)
    urdf_file = os.path.join(
        os.getenv('HOME'),
        'ros2/ros2_ws/src/autonomous_sphere_collector_pkg/urdf',
        'Robot.xacro'
    )

     # Path to your RViz config file
    rviz_config_file = os.path.join(
        os.getenv('HOME'),
        'ros2/ros2_ws/src/autonomous_sphere_collector_pkg/rviz',
        'Robot_view.rviz'
    )    
    return LaunchDescription([
        # Robot State Publisher (publishes TF tree from URDF/Xacro)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': Command(['xacro ', urdf_file])
            }]
        ),

        # Joint State Publisher GUI (optional, lets you move joints manually)
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        ),

        # RViz2 (no .rviz config needed unless you want custom views)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen'
            arguments=['-d',rviz_config_file]
        )
    ])
