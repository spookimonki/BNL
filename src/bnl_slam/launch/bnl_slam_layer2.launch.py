"""
BNL SLAM Layer (Layer 2)

Purpose:
Single-command SLAM session wrapper: brings up simulation (Layer 1) and SLAM (Layer 2).

Inputs:
- /scan
- /tf
- /odom
- /clock

Outputs:
- /map
- /map_metadata
- /tf

Architecture:
Layer 1 (Simulation) → Layer 2 (SLAM) → Optional Layer 3 (Nav2)

NOTE:
This file does NOT start Nav2.
Navigation is handled in Layer 3.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # ===============================
    # BNL SLAM LAYER (Layer 2) - Session Wrapper
    # ===============================
    # What is inherited:
    #   - Layer 1 provides simulation, ROS<->GZ bridge, and TF shims
    # What is local:
    #   - Layer 2 provides slam_toolbox + optional RViz SLAM view
    # What is external:
    #   - slam_toolbox package (LifecycleNode)
    #
    # NOTE:
    # This wrapper intentionally does NOT start Nav2.

    # --- 1. Parameters (paths) ---
    default_world = PathJoinSubstitution(
        [FindPackageShare('bnl_sim'), 'worlds', 'example.sdf']
    )
    default_models = PathJoinSubstitution(
        [FindPackageShare('bnl_sim'), 'models']
    )
    default_slam_params = PathJoinSubstitution(
        [FindPackageShare('bnl_slam'), 'config', 'slam_toolbox_async.yaml']
    )
    default_rviz_config = PathJoinSubstitution(
        [FindPackageShare('bnl_slam'), 'config', 'rviz_slam_map.rviz']
    )

    # --- 2. Launch arguments (public interface for the SLAM session) ---
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Path to Gazebo world SDF file.',
    )
    models_arg = DeclareLaunchArgument(
        'models_path',
        default_value=default_models,
        description='Directory to append to GZ_SIM_RESOURCE_PATH (models).',
    )
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time (applies to slam_toolbox + RViz).',
    )

    gz_ip_arg = DeclareLaunchArgument(
        'gz_ip',
        default_value='',
        description='Optional: set GZ_IP for Gazebo Transport discovery (passed to the bridge).',
    )

    autostart_arg = DeclareLaunchArgument('autostart', default_value='true')
    use_lifecycle_manager_arg = DeclareLaunchArgument('use_lifecycle_manager', default_value='false')

    base_frame_arg = DeclareLaunchArgument(
        'base_frame',
        default_value='chassis',
        description='Robot base frame (must match the SDF link name).',
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
        default_value='true',
        description='Launch RViz2 (Layer-2 debug view).',
    )
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config,
        description='RViz config file path (used if rviz:=true).',
    )

    # --- 3. Include Layer 1 (Simulation + Bridge + TF shim: chassis->scan_frame) ---
    layer1 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('bnl_bringup'), 'launch', 'bnl_layer1_sim.launch.py'])
        ),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'models_path': LaunchConfiguration('models_path'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'gz_ip': LaunchConfiguration('gz_ip'),
            'base_frame': LaunchConfiguration('base_frame'),
            'rviz': 'false',
        }.items(),
    )

    # --- 4. Include Layer 2 (SLAM Toolbox + optional RViz SLAM view) ---
    layer2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('bnl_slam'), 'launch', 'bnl_layer2_slam.launch.py'])
        ),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'base_frame': LaunchConfiguration('base_frame'),
            'autostart': LaunchConfiguration('autostart'),
            'use_lifecycle_manager': LaunchConfiguration('use_lifecycle_manager'),
            'slam_params': LaunchConfiguration('slam_params'),
            'slam_delay': LaunchConfiguration('slam_delay'),
            'rviz': LaunchConfiguration('rviz'),
            'rviz_config': LaunchConfiguration('rviz_config'),
        }.items(),
    )

    return LaunchDescription(
        [
            world_arg,
            models_arg,
            use_sim_time_arg,
            gz_ip_arg,
            autostart_arg,
            use_lifecycle_manager_arg,
            base_frame_arg,
            slam_params_arg,
            slam_delay_arg,
            rviz_arg,
            rviz_config_arg,
            layer1,
            layer2,
        ]
    )


# ===============================
# Validation checklist (non-functional)
# ===============================
#   ros2 lifecycle get /slam_toolbox        # expect: active [3]
#   ros2 topic info /map --verbose          # expect: 1 publisher (slam_toolbox)
#   ros2 topic info /clock --verbose        # expect: 1 publisher (ros_gz_bridge)
#   ros2 run tf2_ros tf2_echo map odom
#   ros2 run tf2_ros tf2_echo odom chassis
