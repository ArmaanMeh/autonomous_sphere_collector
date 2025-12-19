import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'autonomous_sphere_collector_pkg'
    
    # 1. Get the path to the installed package share directory
    pkg_share_dir = get_package_share_directory(pkg_name)
    
    
    return LaunchDescription([
        Node(
            package=pkg_name,
            # The executable is the full path to the Python script
            executable=os.path.join(
                pkg_share_dir,
                '..', # go up to 'install/'
                '..', # go up to 'ros2_ws/'
                'src',
                pkg_name,
                pkg_name, # Python module folder
                'teleop',
                'bot_teleop.py'
            ),
            name='teleop_keyboard',
            output='screen',
            # Forcing python3 execution with proper TTY settings
            prefix=['/usr/bin/python3'],
            emulate_tty=True
        )
    ])