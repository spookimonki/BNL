from glob import glob

from setuptools import find_packages, setup


package_name = 'bnl_autonomy_bringup_pkg'


setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='BNL',
    maintainer_email='user@example.com',
    description='BNL top-level bringup: Layer1 + SLAM + Nav2 + optional exploration.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
