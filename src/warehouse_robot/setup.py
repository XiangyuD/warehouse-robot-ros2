from setuptools import find_packages, setup

package_name = 'warehouse_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='XiangyuD',
    maintainer_email='xiangyudeng@yahoo.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "robot_node = warehouse_robot.robot_node:main",
            'monitor_node = warehouse_robot.monitor_node:main',
            "status_client = warehouse_robot.status_client:main",
            "action_server = warehouse_robot.action_server:main",
            "move_client = warehouse_robot.move_client:main",
        ],
    },
)
