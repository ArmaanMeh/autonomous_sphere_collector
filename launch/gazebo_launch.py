import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # --- 1. Package Shared Tracking Definitions ---
    pkg_share = FindPackageShare('autonomous_sphere_collector_pkg')
    world_pkg_share = FindPackageShare('assessment_world')

    # Path to your main modular configuration layout description
    xacro_file = os.path.join(
        get_package_share_directory('autonomous_sphere_collector_pkg'),
        'urdf',
        'autonomous_sphere_collector.urdf.xacro'
    )

    # Path to your custom active ROS-GZ topic communication map
    bridge_config_file = os.path.join(
        get_package_share_directory('autonomous_sphere_collector_pkg'),
        'config',
        'gz_bridge.yaml'
    )

    # Path to your pre-saved system display configurations

    rviz_config_file = os.path.join(
        get_package_share_directory('autonomous_sphere_collector_pkg'),
        'rviz',
        'auto.rviz' 
    )

    # --- 2. External World Dependencies Actions ---
    
    # 🌍 Include environment world layout structure from assessment_world package
    assessment_world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([world_pkg_share, 'launch', 'assessment_world.launch.py'])
        ])
    )
    
    # 🔴 Include the targeted collection sphere engine script execution block
    spawn_spheres_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([world_pkg_share, 'launch', 'spawn_spheres.launch.py'])
        ])
    )
    
    # Delay sphere production execution layers to ensure physics server engine initialization completes
    delayed_sphere_spawn = TimerAction(
        period=5.0,
        actions=[spawn_spheres_launch]
    )

    # --- 3. Core Package System Node Executions ---
    
    # 🤖 Robot State Publisher Node execution block (Transforms xacro tree nodes dynamically)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', xacro_file])
        }]
    )

    # 🤖 Spawn Entity Creation Node (Drops the robot into the Gazebo Sim interface)
    spawn_robot_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'autonomous_sphere_collector',
            '-z', '0.2' # Minor elevation clearing buffer drops nicely over target surface planes
        ],
        output='screen'
    )
    
    # Delay entity spawning by 2 seconds to safeguard tracking structures against empty environment drops
    delayed_robot_spawn = TimerAction(
        period=2.0,
        actions=[spawn_robot_entity]
    )

    # 🎛️ ROS-GZ Communication Parameter Bridge Node mapping tracking layer
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{
            'config_file': bridge_config_file
        }]
    )

  # 📊 RViz2 Display Node (Launches a clean, default instance without loading a file)
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
    )

    # ⌨️ Interactive Teleop Keyboard Controller Node
    teleop_node = Node(
        package='autonomous_sphere_collector_pkg',
        executable='teleop_node.py',
        name='sphere_collector_teleop',
        prefix='xterm -e', # Forces a separate popup window to accept keyboard presses cleanly
        output='screen'
    )

    # --- 4. Launch Pipeline Deployment Execution Return Array ---
    return LaunchDescription([
        assessment_world_launch,
        delayed_sphere_spawn,
        robot_state_publisher,
        delayed_robot_spawn,
        ros_gz_bridge,
        rviz2_node,
        teleop_node
    ])