import os
import xacro
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, DeclareLaunchArgument
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_name = 'autonomous_sphere_collector_pkg'
    
    # --- Paths to your configuration files ---
    xacro_file = os.path.join(get_package_share_directory(pkg_name), 'urdf', 'autonomous_sphere_collector.urdf.xacro')
    bridge_params = os.path.join(get_package_share_directory(pkg_name), 'config', 'gz_bridge.yaml')
    controller_params_file = os.path.join(get_package_share_directory(pkg_name), 'config', 'ros_controllers.yaml') 

    # --- 1. Process XACRO to URDF ---
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = {'robot_description': robot_description_config.toxml()}

    # --- 2. Launch the assessment world (Loads Gazebo Environment) ---
    assessment_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('assessment_world'),
                'launch',
                'assessment_world.launch.py'
            ])
        ])
    )

    # --- 3. Robot State Publisher (Publishes the URDF and TF transforms) ---
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    # --- 4. ROS-Gazebo Bridge (Connects ROS commands to Gazebo physics) ---
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_params}],
        output='screen'
    )

    # --- 5. Spawn robot into Gazebo Sim (Puts the model into the world) ---
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'autonomous_sphere_collector',
            '-z', '0.1' 
        ],
        output='screen'
    )

    # --- 6. Controller Spawners (FIXED: Passing the YAML config) ---
    
    # Standard arguments required for the spawner to find the controller config
    spawner_args = ['--controller-manager', '/controller_manager', '--param-file', controller_params_file]

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'] + spawner_args,
    )

    diff_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller'] + spawner_args,
    )

    scoop_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['scoop_controller'] + spawner_args,
    )

    # --- 7. Event Handler (Waits for robot to spawn before starting control) ---
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
        assessment_world,
        robot_state_publisher,
        gz_bridge,
        spawn_entity,
        delayed_controller_spawning,
    ])