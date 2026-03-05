from glob import glob

from setuptools import find_packages, setup


package_name = 'bnl_autonomy'


setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', ['config/nav2_params.yaml', 'config/autonomy_params.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='Minimal autonomy executive: SLAM+Nav2 frontier exploration with banana approach integration.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'frontier_explorer_node = bnl_autonomy.frontier_explorer_node:main',
            'task_executive_node = bnl_autonomy.task_executive_node:main',
            'banana_approach_node = bnl_autonomy.banana_approach_node:main',
            'cmd_vel_mux_node = bnl_autonomy.cmd_vel_mux_node:main',
        ],
    },
)
