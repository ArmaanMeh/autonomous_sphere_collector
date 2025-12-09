from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'autonomous_sphere_collector_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
         # Install launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),

        # Install URDF/Xacro files
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),

        # Install config files
        (os.path.join('share', package_name, 'config'), glob('config/*')),

        # Install RViz configs
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*')),

        # Install resource files (worlds, etc.)
        (os.path.join('share', package_name, 'resource'), glob('resource/*')),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='arman',
    maintainer_email='armaanshakeelshaikh@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
