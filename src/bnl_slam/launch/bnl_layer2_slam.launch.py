"""
BNL SLAM Layer (Layer 2)

Purpose:
Live mapping using slam_toolbox in async mode.

Inputs:
- /scan
- /tf
- /odom

Outputs:
- /map
- /map_metadata
- /tf (map->odom when publish_tf is enabled)

Architecture:
Layer 1 (Simulation) → Layer 2 (SLAM) → Optional Layer 3 (Nav2)

NOTE:
This layer does NOT start Nav2.
Navigation is handled in Layer 3.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, RegisterEventHandler, TimerAction
from launch.conditions import IfCondition
from launch.events import matches_action
from launch.substitutions import AndSubstitution, LaunchConfiguration, NotSubstitution, PathJoinSubstitution
from launch_ros.actions import LifecycleNode, Node
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from launch_ros.substitutions import FindPackageShare
from lifecycle_msgs.msg import Transition


def generate_launch_description():
    # ===============================
    # BNL SLAM LAYER (Layer 2)
    # ===============================
    # Local responsibilities:
    #   - Start slam_toolbox (async mapping)
    #   - Optionally start RViz for SLAM visualization
    # External dependencies (provided by Layer 1):
    #   - /scan (LaserScan) from sim bridge
    #   - odom->base_frame TF chain via sim + TF shims

    # --- 1. Parameters (paths) ---
    default_rviz_config = PathJoinSubstitution(
        [FindPackageShare('bnl_slam'), 'config', 'rviz_slam_map.rviz']
    )
    default_slam_params = PathJoinSubstitution(
        [FindPackageShare('bnl_slam'), 'config', 'slam_toolbox_async.yaml']
    )

    # --- 2. Launch arguments (public interface for this layer) ---
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time (slam_toolbox + optional RViz).',
    )

    base_frame_arg = DeclareLaunchArgument(
        'base_frame',
        default_value='chassis',
        description='Base frame for slam_toolbox. Must be connected to scan_frame via TF.',
    )

    autostart_arg = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically configure + activate slam_toolbox lifecycle node.',
    )
    use_lifecycle_manager_arg = DeclareLaunchArgument(
        'use_lifecycle_manager',
        default_value='false',
        description='Enable bond connection during node activation (passed through to slam_toolbox).',
    )

    slam_params_arg = DeclareLaunchArgument(
        'slam_params',
        default_value=default_slam_params,
        description='slam_toolbox params YAML file.',
    )

    slam_delay_arg = DeclareLaunchArgument(
        'slam_delay',
        default_value='3.0',
        description='Seconds to delay slam_toolbox start (lets TF + /scan settle).',
    )

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='false',
        description='Launch RViz2 with map + scan + TF (Layer-2 debug view).',
    )
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config,
        description='RViz config file path (used if rviz:=true).',
    )

    # --- 3. SLAM Toolbox Node ---
    # SLAM Toolbox (Online Async Mapping)
    # Consumes:
    #   - /scan (LaserScan)
    #   - TF: odom -> base_frame (and base_frame -> scan frame)
    # Publishes:
    #   - /map, /map_metadata
    #   - TF: map -> odom (when publish_tf is true in the YAML)
    slam_toolbox = LifecycleNode(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        namespace='',
        parameters=[
            # NOTE: launch_ros merges parameters in-order; later entries win.
            # We load the YAML first, then explicitly override the small set
            # of values that must match our bringup contract.
            LaunchConfiguration('slam_params'),
            {
                'use_lifecycle_manager': LaunchConfiguration('use_lifecycle_manager'),
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'scan_topic': '/scan',
                'map_frame': 'map',
                'odom_frame': 'odom',
                'base_frame': LaunchConfiguration('base_frame'),
            },
        ],
    )

    # --- 4. Lifecycle autostart (configure -> activate) ---
    # We drive the lifecycle transitions ourselves when autostart:=true.
    # When use_lifecycle_manager:=true, slam_toolbox expects a bond-based manager
    # (e.g. nav2_lifecycle_manager). In that case we do NOT emit transitions here.
    configure_event = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(slam_toolbox),
            transition_id=Transition.TRANSITION_CONFIGURE,
        ),
        condition=IfCondition(
            AndSubstitution(LaunchConfiguration('autostart'), NotSubstitution(LaunchConfiguration('use_lifecycle_manager')))
        ),
    )

    activate_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=slam_toolbox,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(slam_toolbox),
                        transition_id=Transition.TRANSITION_ACTIVATE,
                    )
                )
            ],
        ),
        condition=IfCondition(
            AndSubstitution(LaunchConfiguration('autostart'), NotSubstitution(LaunchConfiguration('use_lifecycle_manager')))
        ),
    )

    # --- 5. RViz Visualization (optional) ---
    # RViz is intentionally delayed to avoid racing TF + map initialization.
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    # --- 6. Startup sequencing (delays) ---
    slam_delayed = TimerAction(period=LaunchConfiguration('slam_delay'), actions=[slam_toolbox])
    slam_configure_delayed = TimerAction(period=LaunchConfiguration('slam_delay'), actions=[configure_event])
    rviz_delayed = TimerAction(period=6.0, actions=[rviz], condition=IfCondition(LaunchConfiguration('rviz')))

    return LaunchDescription(
        [
            use_sim_time_arg,
            base_frame_arg,
            autostart_arg,
            use_lifecycle_manager_arg,
            slam_params_arg,
            slam_delay_arg,
            rviz_arg,
            rviz_config_arg,
            activate_event,
            slam_delayed,
            slam_configure_delayed,
            rviz_delayed,
        ]
    )
