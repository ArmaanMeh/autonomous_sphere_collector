from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
import os

def generate_launch_description():
    # Package paths
    pkg_share = FindPackageShare('autonomous_sphere_collector_pkg').find('autonomous_sphere_collector_pkg')
    urdf_file = os.path.join(pkg_share, 'urdf', 'Robot.xacro')
    world_file = os.path.join(pkg_share, 'resource', 'assessment.sdf')
    controllers_file = os.path.join(pkg_share, 'config', 'ros_controllers.yaml')

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro', urdf_file])
        }]
    )

    # Gazebo with professor's world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
        ]),
        launch_arguments={'world': world_file}.items()
    )

    # Spawn robot into Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'autonomous_sphere_collector'],
        output='screen'
    )

    # Controller Manager
    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[controllers_file],
        output='screen'
    )

    # Spawners
    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller'],
        output='screen'
    )
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )
    scoop_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['scoop_controller'],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        controller_manager,
        diff_drive_spawner,
        joint_state_broadcaster_spawner,
        scoop_controller_spawner
    ])
