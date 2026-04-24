from setuptools import find_packages, setup

package_name = 'ur5_pick_place'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='abin',
    maintainer_email='abin@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'pick_and_place        = ur5_pick_place.pick_and_place:main',
            'spawn_box             = ur5_pick_place.spawn_box:main',
            'add_scene_objects     = ur5_pick_place.add_scene_objects:main',
            'blue_box              = ur5_pick_place.blue_box:main',
            'green_box             = ur5_pick_place.green_box:main',
            'red_box               = ur5_pick_place.red_box:main',
            'vacuum_gripper        = ur5_pick_place.vacuum_gripper:main',
            'wrist_camera_detector = ur5_pick_place.wrist_camera_detector:main',
            'wrist_pick_place      = ur5_pick_place.wrist_pick_place:main',
            'spawn_camera          = ur5_pick_place.spawn_camera:main',
        ],
    },
)
