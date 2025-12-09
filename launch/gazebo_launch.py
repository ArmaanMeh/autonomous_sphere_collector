## autonomous_sphere_collector_pkg/launch/gazebo.launch.py

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # --- 1. Package and File Paths ---
    pkg_share = FindPackageShare('autonomous_sphere_collector_pkg')

    urdf_file = PathJoinSubstitution([
        pkg_share,
        'urdf',
        'Robot.xacro'
    ])

    world_file = PathJoinSubstitution([
        pkg_share,
        'resource',
        'assessment.sdf'
    ])

    controllers_file = PathJoinSubstitution([
        pkg_share,
        'config',
        'ros_controllers.yaml'
    ])

    # --- 2. ROS Nodes and Actions ---

    # 🤖 Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': ParameterValue(
                Command(['xacro',urdf_file]),
                value_type=str
            )
        }]
    )

    # 🌍 Gazebo Simulator
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={'world': world_file}.items()
    )

    # 🤖 Spawn Entity
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'autonomous_sphere_collector'
        ],
        output='screen'
    )

    # 🎮 Controller Manager
    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[controllers_file],
        output='screen'
    )

    # 🚀 Spawners
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    scoop_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['scoop_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    # --- 3. Launch Description Return ---
    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        controller_manager,
        joint_state_broadcaster_spawner,
        diff_drive_spawner,
        scoop_controller_spawner
    ])
