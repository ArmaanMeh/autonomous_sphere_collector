import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'autonomous_sphere_collector_pkg'

def package_files(directory):
    paths = []
    for (path, directory, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths

# --- Define the data files using the helper ---
data_files = [
    # 1. Register package in the ament index
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    
    # 2. Include the package.xml file
    ('share/' + package_name, ['package.xml']),
    
    (os.path.join(package_name, 'launch'), [
        'launch/gazebo_assessment.launch.py',
        'launch/gazebo_launch.py',
        'launch/combined.launch.py',
        'launch/controller_launch.py',
    ]),
    
    # 4. Include URDF/Xacro files
    (os.path.join('share', package_name, 'urdf'), glob('urdf/*')), # Using glob('*') for all files in urdf/

    # 5. Include **Config/Params files (YAML files)**
    (os.path.join('share/' + package_name + '/config', glob('config/*.yaml'))),
    # 6. Include RViz configuration files
    (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
]

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=data_files, # Use the list generated above
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='arman',
    maintainer_email='armaanshakeelshaikh@gmail.com',
    description='A package for an autonomous robot that collects spheres',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [],
    },
)