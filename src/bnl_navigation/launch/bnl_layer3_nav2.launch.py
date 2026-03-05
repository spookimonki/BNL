import subprocess

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def _preflight_no_duplicate_nav2_nodes(context, *args, **kwargs):
    expected = {
        '/controller_server',
        '/planner_server',
        '/bt_navigator',
        '/behavior_server',
        '/waypoint_follower',
        '/lifecycle_manager_navigation',
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
            "Nav2 bringup refused to start because Nav2 nodes already exist (likely a previous session is still running):\n"
            + "\n".join(f"  - {n}" for n in collisions)
            + "\nStop the other launch cleanly (Ctrl-C in its terminal), then retry."
        )
        raise RuntimeError(msg)

    return []


def generate_launch_description():
    default_params = PathJoinSubstitution(
        [FindPackageShare('bnl_navigation'), 'config', 'nav2_params_mapping.yaml']
    )

    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true')
    base_frame_arg = DeclareLaunchArgument('base_frame', default_value='chassis')
    params_file_arg = DeclareLaunchArgument('nav2_params', default_value=default_params)
    autostart_arg = DeclareLaunchArgument('autostart', default_value='true')
    explore_arg = DeclareLaunchArgument('explore', default_value='false')
    nav2_delay_arg = DeclareLaunchArgument(
        'nav2_delay',
        default_value='6.0',
        description='Seconds to delay Nav2 start (lets SLAM and TF stabilize).',
    )

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[
            LaunchConfiguration('nav2_params'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[
            LaunchConfiguration('nav2_params'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[
            LaunchConfiguration('nav2_params'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[
            LaunchConfiguration('nav2_params'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    waypoint_follower = Node(
        package='nav2_waypoint_follower',
        executable='waypoint_follower',
        name='waypoint_follower',
        output='screen',
        parameters=[
            LaunchConfiguration('nav2_params'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    explorer = Node(
        package='bnl_navigation',
        executable='bnl_explore_random_goals',
        name='bnl_explore_random_goals',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
            {'frame_id': 'map'},
            {'base_frame': LaunchConfiguration('base_frame')},
        ],
        condition=IfCondition(LaunchConfiguration('explore')),
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[
            {
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'autostart': LaunchConfiguration('autostart'),
                'bond_timeout': 20.0,
                'node_names': [
                    'controller_server',
                    'planner_server',
                    'behavior_server',
                    'bt_navigator',
                    'waypoint_follower',
                ],
            }
        ],
    )

    twist_mux = Node(
        package="twist_mux",
        executable="twist_mux",
        name="twist_mux",
        parameters=[
            PathJoinSubstitution([
                FindPackageShare("bnl_navigation"),
                "config",
                "twist_mux.yaml"
            ]),
            {"use_stamped": False},
            {"use_sim_time": LaunchConfiguration('use_sim_time')},
        ],
        remappings=[
            ("/cmd_vel_out", "/cmd_vel_mux")
        ],
        output="screen",
    )

    nav2_group = [
        controller_server,
        planner_server,
        behavior_server,
        bt_navigator,
        waypoint_follower,
        lifecycle_manager,
        twist_mux,
    ]

    nav2_delayed = TimerAction(period=LaunchConfiguration('nav2_delay'), actions=nav2_group)
    explorer_delayed = TimerAction(
        period=LaunchConfiguration('nav2_delay'),
        actions=[explorer],
        condition=IfCondition(LaunchConfiguration('explore')),
    )

    return LaunchDescription(
        [
            use_sim_time_arg,
            base_frame_arg,
            params_file_arg,
            autostart_arg,
            explore_arg,
            nav2_delay_arg,
            OpaqueFunction(function=_preflight_no_duplicate_nav2_nodes),
            nav2_delayed,
            explorer_delayed,
        ]
    )
