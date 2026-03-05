from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true')

    # Banana vision
    semantic_node = Node(
        package='bnl_perception',
        executable='semantic_observation_node',
        name='semantic_observation_node',
        output='screen',
        parameters=[
            {
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'base_frame': 'chassis',
                'fallback_frame': 'odom',
            }
        ],
        # CUDA path is currently unstable in this integrated bringup; force CPU for robustness.
        additional_env={'CUDA_VISIBLE_DEVICES': ''},
    )

    frontier_node = Node(
        package='bnl_autonomy',
        executable='frontier_explorer_node',
        name='frontier_explorer_node',
        output='screen',
        parameters=[
            PathJoinSubstitution([FindPackageShare('bnl_autonomy'), 'config', 'autonomy_params.yaml']),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    banana_approach_node = Node(
        package='bnl_autonomy',
        executable='banana_approach_node',
        name='banana_approach_node',
        output='screen',
        parameters=[
            PathJoinSubstitution([FindPackageShare('bnl_autonomy'), 'config', 'autonomy_params.yaml']),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    executive_node = Node(
        package='bnl_autonomy',
        executable='task_executive_node',
        name='task_executive_node',
        output='screen',
        parameters=[
            PathJoinSubstitution([FindPackageShare('bnl_autonomy'), 'config', 'autonomy_params.yaml']),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    cmd_vel_mux_node = Node(
        package='bnl_autonomy',
        executable='cmd_vel_mux_node',
        name='cmd_vel_mux_node',
        output='screen',
        parameters=[
            PathJoinSubstitution([FindPackageShare('bnl_autonomy'), 'config', 'autonomy_params.yaml']),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    return LaunchDescription([
        use_sim_time_arg,
        semantic_node,
        frontier_node,
        executive_node,
        banana_approach_node,
        cmd_vel_mux_node,
    ])
