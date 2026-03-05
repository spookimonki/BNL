import os
import subprocess

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def _preflight_no_duplicate_nodes(context, *args, **kwargs):
    """Fail fast if a previous bringup is still running.

    Hard rule: do not kill processes from scripts. We only detect + warn + exit.
    """
    expected = {
        '/ros_gz_bridge',
        '/rviz',
        '/tf_chassis_to_scan_frame',
        # Layer2 stacks (slam/nav2) sometimes get launched separately; if they're
        # still around it's almost always from a previous bringup.
        '/slam_toolbox',
    }

    try:
        result = subprocess.run(
            ['ros2', 'node', 'list'],
            check=False,
            capture_output=True,
            text=True,
            timeout=8.0,
        )
    except Exception as exc:  # best-effort guard
        raise RuntimeError(f"Preflight failed to query ROS graph: {exc}") from exc

    if result.returncode != 0:
        stderr = (result.stderr or '').strip()
        raise RuntimeError(f"Preflight failed to query ROS graph (ros2 node list): {stderr}")

    existing = {line.strip() for line in (result.stdout or '').splitlines() if line.strip()}
    collisions = sorted(existing.intersection(expected))
    if collisions:
        msg = (
            "BNL bringup refused to start because nodes already exist (likely a previous session is still running):\n"
            + "\n".join(f"  - {n}" for n in collisions)
            + "\nStop the other launch cleanly (Ctrl-C in its terminal), then retry."
        )
        raise RuntimeError(msg)

    return []


def _set_gz_sim_resource_path(context, *args, **kwargs):
    from launch.actions import SetEnvironmentVariable

    models_path = LaunchConfiguration('models_path').perform(context)

    current = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    parts = [p for p in current.split(':') if p]
    if models_path not in parts:
        parts.append(models_path)

    return [SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', ':'.join(parts))]


def generate_launch_description():
    default_world = PathJoinSubstitution(
        [FindPackageShare('bnl_sim'), 'worlds', 'example.sdf']
    )
    default_models = PathJoinSubstitution(
        [FindPackageShare('bnl_sim'), 'models']
    )

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
        description='Use simulation time (applies to nodes launched here).',
    )

    gz_ip_arg = DeclareLaunchArgument(
        'gz_ip',
        default_value=EnvironmentVariable('GZ_IP', default_value=''),
        description='Optional: set GZ_IP for Gazebo Transport discovery (restart bridge if host IP changes).',
    )

    base_frame_arg = DeclareLaunchArgument(
        'base_frame',
        default_value='chassis',
        description='Robot base frame (must match the SDF link name).',
    )

    scan_frame_arg = DeclareLaunchArgument(
        'scan_frame',
        default_value='two_wheel_robot/lidar_link/lidar',
        description='Actual LaserScan frame_id coming from the simulation.',
    )
    laser_z_arg = DeclareLaunchArgument(
        'laser_z',
        default_value='0.13',
        description='Z offset from base_frame to laser_frame (meters).',
    )

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='false',
        description='Launch RViz2 for sensor visualization.',
    )
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=PathJoinSubstitution([FindPackageShare('bnl_bringup'), 'config', 'rviz_sensors.rviz']),
        description='RViz config file path (used if rviz:=true).',
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
        ),
        launch_arguments={'gz_args': [TextSubstitution(text='-r '), LaunchConfiguration('world')]}.items(),
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        arguments=[
            # ros_gz_bridge direction hint:
            #   - "[" means Gazebo -> ROS2 (bridge subscribes to GZ, publishes ROS)
            #   - "]" means ROS2 -> Gazebo (bridge subscribes to ROS, publishes GZ)
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan_gpu@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            # Banana MVP: bridge the Gazebo camera stream into ROS2.
            # Verified gz topic (runtime): /camera_image (gz.msgs.Image)
            '/camera_image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        ],
        remappings=[
            ('/scan_gpu', '/scan'),
            # Banana MVP: stable topic name expected by the perception node.
            ('/camera_image', '/camera/image_raw'),
            ('/cmd_vel', '/cmd_vel_mux'),
        ],
        additional_env={
            'GZ_IP': LaunchConfiguration('gz_ip'),
        },
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )

    # TF contract (Option A): no fake frames.
    #   Gazebo publishes: odom -> chassis (via bridged /tf)
    #   We must provide:  chassis -> scan_frame (so SLAM/Nav2 can transform LaserScan)
    tf_chassis_to_scan_frame = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='tf_chassis_to_scan_frame',
        output='screen',
        arguments=[
            '0',
            '0',
            LaunchConfiguration('laser_z'),
            '0',
            '0',
            '0',
            LaunchConfiguration('base_frame'),
            LaunchConfiguration('scan_frame'),
        ],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
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

    return LaunchDescription(
        [
            world_arg,
            models_arg,
            use_sim_time_arg,
            gz_ip_arg,
            base_frame_arg,
            scan_frame_arg,
            laser_z_arg,
            rviz_arg,
            rviz_config_arg,
            OpaqueFunction(function=_preflight_no_duplicate_nodes),
            OpaqueFunction(function=_set_gz_sim_resource_path),
            gz_sim,
            bridge,
            tf_chassis_to_scan_frame,
            rviz,
        ]
    )
