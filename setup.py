import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'autonomous_sphere_collector_pkg'

setup(
    name=package_name,
    version='0.0.1',  # Good practice to start tracking versions
    packages=find_packages(exclude=['test']),
    data_files=[
        # 1. Register package in the ament index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        
        # 2. Include the package.xml file
        ('share/' + package_name, ['package.xml']),
        
        # 3. Include Launch files
        # It is convention to name launch files .launch.py
        (os.path.join('share', package_name, 'launch'), glob('launch/*_launch.py')),
        
        # 4. Include URDF/Xacro files
        # Note: If you have subfolders (like urdf/wheels/), glob won't pick them up recursively
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.xacro')),

        # 5. Include RViz configuration files
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),

        # 6. Include Config/Params files (if you use YAML files later)
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),

        # 7. Include World files (if you use Gazebo worlds)
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
        
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='arman',
    maintainer_email='armaanshakeelshaikh@gmail.com',
    description='A package for an autonomous robot that collects spheres',
    license='Apache-2.0', # Updated to a standard open source license
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            # Add your nodes here later, format:
            # 'node_name = package_name.python_file_name:main',
        ],
    },
)