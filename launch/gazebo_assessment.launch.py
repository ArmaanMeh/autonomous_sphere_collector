from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, Command
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # --- Launch the assessment world (no spheres for SLAM) ---
    assessment_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('assessment_world'),
                'launch',
                'assessment_world.launch.py'
            ])
        ])
    )

    # --- Robot URDF/Xacro ---
    urdf_file = os.path.join(
        get_package_share_directory('autonomous_sphere_collector_pkg'),
        'urdf',
        'Robot.urdf'
    )

    robot_state_publisher = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    output='screen',
    parameters=[{
        'robot_description': open(urdf_file).read()
            
        }]
    )

    # --- Spawn robot into Gazebo ---
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'autonomous_sphere_collector'
        ],
        output='screen'
    )

    return LaunchDescription([
        assessment_world,
        robot_state_publisher,
        spawn_entity,
    ])
