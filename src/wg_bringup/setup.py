from setuptools import find_packages, setup
import glob

package_name = 'wg_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/wg.launch.py']),
        ('lib/' + package_name, ['bnl_startup.sh']),
    ],
    install_requires=['setuptools', 'RPi.GPIO', 'numpy'],
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
            'servo_oscillator = wg_bringup.servo_oscillator:main',
            'scan_projection = wg_bringup.scan_projection:main',
        ],
    },
)
