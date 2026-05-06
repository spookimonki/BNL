from setuptools import find_packages, setup

package_name = 'wg_sensor_pullup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'adafruit-circuitpython-bno08x', 'pyserial'],
    zip_safe=True,
    maintainer='lillehavard',
    maintainer_email='haavaali@stud.ntnu.no',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'imuodom = IMU.imuodom:main',
            'wheelodom = elias_relay.wheelodom:main',
            'lidar_relay = elias_relay.lidar_relay:main',
            'vel_to_pmw = elias_relay.vel_to_pmw:main',
        ],
    },
)
