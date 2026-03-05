import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    enable_nav2_arg = DeclareLaunchArgument(
        'enable_nav2',
        default_value='false',
        description='If true, include nav2_bringup navigation_launch.py.',
    )

    # Gazebo simulation: use the existing workspace bringup (gz-sim + bridge + TF shims).
    bnl_bringup_share = get_package_share_directory('bnl_bringup')
    gazebo_launch_path = os.path.join(bnl_bringup_share, 'launch', 'bnl_layer1_sim.launch.py')
    gazebo = IncludeLaunchDescription(PythonLaunchDescriptionSource(gazebo_launch_path))

    nav2_bringup_share = get_package_share_directory('nav2_bringup')
    nav2_launch_path = os.path.join(nav2_bringup_share, 'launch', 'navigation_launch.py')

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_launch_path),
        condition=IfCondition(LaunchConfiguration('enable_nav2')),
    )

    return LaunchDescription(
        [
            enable_nav2_arg,
            gazebo,
            nav2,
        ]
    )
