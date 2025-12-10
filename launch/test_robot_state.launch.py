from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Path to your Robot.xacro
    urdf_file = os.path.join(
        get_package_share_directory('autonomous_sphere_collector_pkg'),
        'urdf',
        'Robot.urdf'
    )

    # Robot State Publisher node
    robot_state_publisher = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    output='screen',
    parameters=[{
        'robot_description': open(urdf_file).read()
            
        }]
    )

    return LaunchDescription([
        robot_state_publisher
    ])
