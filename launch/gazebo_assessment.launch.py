import os
import xacro
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_name = 'autonomous_sphere_collector_pkg'
    pkg_share_dir = get_package_share_directory(pkg_name)
    
    # --- Paths to your configuration files ---
    xacro_file = os.path.join(pkg_share_dir, 'urdf', 'autonomous_sphere_collector.urdf.xacro')
    bridge_params = os.path.join(pkg_share_dir, 'config', 'gz_bridge.yaml')
    controller_params_file = os.path.join(pkg_share_dir, 'config', 'ros_controllers.yaml') 
    
    # --- RVIZ Config and Map Paths ---
    rviz_config_path = os.path.join(pkg_share_dir, 'rviz', 'Robot1.rviz') 
    map_file = os.path.join(pkg_share_dir, 'map', 'assessment_arena.yaml') 
    
    # --- 1. Process XACRO to URDF ---
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = {'robot_description': robot_description_config.toxml()}

    # --- 2. Launch the assessment world (Loads Gazebo Environment) ---
    # Note: Using the assessment_complete.launch.py path as provided in your last update
    assessment_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('assessment_world'),
                'launch',
                'assessment_complete.launch.py'
            ])
        ])
    )
    
    # --- 3. Sphere Spawning (Using the TimerAction for delay, as requested) ---
    spawn_spheres_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('assessment_world'),
                'launch',
                'spawn_spheres.launch.py' # Assumes this file contains sphere spawning logic
            ])
        ])
    )
    
    # Delay spawning spheres by 5.0 seconds to ensure the world is ready
    delayed_spawn_spheres = TimerAction(
        period=5.0,
        actions=[spawn_spheres_launch]
    )

    # --- 4. Map Server Node (Loads Static Map) ---
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            {'yaml_filename': map_file},
            {'use_sim_time': True}
        ]
    )

    # --- 5. Robot State Publisher (Publishes the URDF and TF transforms) ---
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    # --- 6. ROS-Gazebo Bridge (Connects ROS commands to Gazebo physics) ---
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_params}],
        output='screen'
    )

    # --- 7. Spawn robot into Gazebo Sim (Puts the model into the world) ---
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'autonomous_sphere_collector',
            # CRITICAL FIX: Spawn 5mm above ground 
            '-z', '0' 
        ],
        output='screen'
    )
    
    # --- 8. Controller Spawners ---
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster', 
            '-c', '/controller_manager', 
            '-p', controller_params_file
        ],
    )

    diff_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diff_drive_controller', 
            '-c', '/controller_manager', 
            '-p', controller_params_file
        ],
    )

    scoop_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'scoop_controller', 
            '-c', '/controller_manager', 
            '-p', controller_params_file
        ],
    )
    
    # --- 9. RViz Node ---
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
    )
    
    # --- 10. Event Handler (Waits for robot to spawn before starting control) ---
    delayed_controller_spawning = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[
                joint_state_broadcaster_spawner,
                diff_drive_controller_spawner,
                scoop_controller_spawner
            ],
        )
    )

    return LaunchDescription([
        # World, Map, and Robot Description
        assessment_world,
        map_server_node,
        robot_state_publisher,
        gz_bridge,
        
        # Spawning Entities (Robot and Spheres)
        spawn_entity,
        delayed_spawn_spheres, # Replaces the individual sphere nodes
        
        # Controllers and Visualization
        delayed_controller_spawning,
        rviz_node,
    ])