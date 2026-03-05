import subprocess

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def _preflight_no_duplicate_nodes(context, *args, **kwargs):
    expected = {
        # Layer-1
        '/ros_gz_bridge',
        '/tf_chassis_to_scan_frame',
        # Layer-2
        '/slam_toolbox',
        # Layer-3
        '/controller_server',
        '/planner_server',
        '/bt_navigator',
        '/behavior_server',
        '/waypoint_follower',
        '/lifecycle_manager_navigation',
        # UX
        '/rviz',
        '/bnl_explore_random_goals',
    }

    result = subprocess.run(
        ['ros2', 'node', 'list'],
        check=False,
        capture_output=True,
        text=True,
        timeout=8.0,
    )
    if result.returncode != 0:
        stderr = (result.stderr or '').strip()
        raise RuntimeError(f"Preflight failed to query ROS graph (ros2 node list): {stderr}")

    existing = {line.strip() for line in (result.stdout or '').splitlines() if line.strip()}
    collisions = sorted(existing.intersection(expected))
    if collisions:
        msg = (
            "BNL full autonomy refused to start because nodes already exist (likely a previous session is still running):\n"
            + "\n".join(f"  - {n}" for n in collisions)
            + "\nStop the other launch cleanly (Ctrl-C in its terminal), then retry."
        )
        raise RuntimeError(msg)

    explore = LaunchConfiguration('explore').perform(context).lower() in ('1', 'true', 'yes')
    nav2 = LaunchConfiguration('nav2').perform(context).lower() in ('1', 'true', 'yes')
    if explore and not nav2:
        raise RuntimeError('explore:=true requires nav2:=true')

    return []


def generate_launch_description():
    default_world = PathJoinSubstitution(
        [FindPackageShare('simulation_package'), 'gazebo_includes', 'worlds', 'example.sdf']
    )
    default_models = PathJoinSubstitution(
        [FindPackageShare('simulation_package'), 'gazebo_includes', 'models']
    )
    default_slam_params = PathJoinSubstitution(
        [FindPackageShare('bnl_slam_bringup_pkg'), 'config', 'slam_toolbox_async.yaml']
    )
    default_nav2_params = PathJoinSubstitution(
        [FindPackageShare('bnl_nav2_bringup_pkg'), 'config', 'nav2_params_mapping.yaml']
    )
    default_rviz_config = PathJoinSubstitution(
        [FindPackageShare('bnl_nav2_bringup_pkg'), 'config', 'rviz_nav2_slam.rviz']
    )

    world_arg = DeclareLaunchArgument('world', default_value=default_world)
    models_arg = DeclareLaunchArgument('models_path', default_value=default_models)
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true')

    gz_ip_arg = DeclareLaunchArgument(
        'gz_ip',
        default_value=EnvironmentVariable('GZ_IP', default_value=''),
        description='Optional: set GZ_IP for Gazebo Transport discovery (restart bridge if host IP changes).',
    )

    base_frame_arg = DeclareLaunchArgument('base_frame', default_value='chassis')
    scan_frame_arg = DeclareLaunchArgument('scan_frame', default_value='two_wheel_robot/lidar_link/lidar')
    laser_z_arg = DeclareLaunchArgument('laser_z', default_value='0.13')

    slam_arg = DeclareLaunchArgument('slam', default_value='true')
    nav2_arg = DeclareLaunchArgument('nav2', default_value='true')
    explore_arg = DeclareLaunchArgument('explore', default_value='false')

    slam_params_arg = DeclareLaunchArgument('slam_params', default_value=default_slam_params)
    slam_delay_arg = DeclareLaunchArgument('slam_delay', default_value='3.0')

    nav2_params_arg = DeclareLaunchArgument('nav2_params', default_value=default_nav2_params)
    nav2_delay_arg = DeclareLaunchArgument('nav2_delay', default_value='6.0')

    rviz_arg = DeclareLaunchArgument('rviz', default_value='true')
    rviz_config_arg = DeclareLaunchArgument('rviz_config', default_value=default_rviz_config)

    layer1 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('bnl_bringup_pkg'), 'launch', 'bnl_layer1_sim.launch.py'])
        ),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'models_path': LaunchConfiguration('models_path'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'gz_ip': LaunchConfiguration('gz_ip'),
            'base_frame': LaunchConfiguration('base_frame'),
            'scan_frame': LaunchConfiguration('scan_frame'),
            'laser_z': LaunchConfiguration('laser_z'),
            'rviz': 'false',
        }.items(),
    )

    layer2_slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('bnl_slam_bringup_pkg'), 'launch', 'bnl_layer2_slam.launch.py'])
        ),
        condition=IfCondition(LaunchConfiguration('slam')),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'base_frame': LaunchConfiguration('base_frame'),
            'slam_params': LaunchConfiguration('slam_params'),
            'slam_delay': LaunchConfiguration('slam_delay'),
            'rviz': 'false',
        }.items(),
    )

    layer3_nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('bnl_nav2_bringup_pkg'), 'launch', 'bnl_layer3_nav2.launch.py'])
        ),
        condition=IfCondition(LaunchConfiguration('nav2')),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'nav2_params': LaunchConfiguration('nav2_params'),
            'nav2_delay': LaunchConfiguration('nav2_delay'),
            'autostart': 'true',
            'base_frame': LaunchConfiguration('base_frame'),
            'explore': LaunchConfiguration('explore'),
        }.items(),
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(LaunchConfiguration('rviz')),
    )
    rviz_delayed = TimerAction(period=8.0, actions=[rviz], condition=IfCondition(LaunchConfiguration('rviz')))


    return LaunchDescription(
        [
            world_arg,
            models_arg,
            use_sim_time_arg,
            gz_ip_arg,
            base_frame_arg,
            scan_frame_arg,
            laser_z_arg,
            slam_arg,
            nav2_arg,
            explore_arg,
            slam_params_arg,
            slam_delay_arg,
            nav2_params_arg,
            nav2_delay_arg,
            rviz_arg,
            rviz_config_arg,
            OpaqueFunction(function=_preflight_no_duplicate_nodes),
            layer1,
            layer2_slam,
            layer3_nav2,
            rviz_delayed,
        ]
    )
