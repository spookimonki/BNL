from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import SetEnvironmentVariable, IncludeLaunchDescription, TimerAction, RegisterEventHandler, DeclareLaunchArgument
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
import os

def generate_launch_description():
    ros_gz_sim_pkg_path = get_package_share_directory('ros_gz_sim')
    sim_pkg_path = FindPackageShare('simulation_package')
    wg_state_est_pkg_path = get_package_share_directory('wg_state_est')
    robot_localization_pkg_path = get_package_share_directory('robot_localization')
    
    gz_launch_path = PathJoinSubstitution([ros_gz_sim_pkg_path, 'launch', 'gz_sim.launch.py'])
    nav2_launch_path = os.path.join(wg_state_est_pkg_path, 'launch', 'nav2_launch.py')
    full_localization_launch_path = os.path.join(wg_state_est_pkg_path, 'launch', 'full_localization.launch.py')
    
    # Create default nav2 params path (update this to match your setup)
    nav2_params_file = os.path.join(wg_state_est_pkg_path, 'config', 'nav2_params.yaml')
    
    mode = LaunchConfiguration('mode')

    mode_arg = DeclareLaunchArgument('mode', 
                          default_value='sim',
                          description="Launch argument som bestemme om vi kjøre simulasjon eller ikke."
                          )


    startup_node = Node(
        package='wg_bringup',
        executable='bnl_startup.sh',
        name='BNL_startup',
        output='screen',
        emulate_tty=True
    )

    # Bridging and remapping Gazebo topics to ROS 2 (replace with your own topics)
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/scan_gpu@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                    '/camera_image@sensor_msgs/msg/Image[gz.msgs.Image'],
        condition=IfCondition(PythonExpression(["'", mode, "' == 'sim'"])),
        output='screen'
    )
    
    # Include full localization (wheel odom, IMU, lidar, UKF filter)
    full_localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(full_localization_launch_path),
        launch_arguments={
            'autostart': 'true',
        }.items(),
    )
    
    # Include Nav2 with slam_toolbox (slam:='True' tells Nav2 to start slam_toolbox internally)
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_launch_path),
        launch_arguments={
            'namespace': '',
            'use_sim_time': 'true',
            'autostart': 'true',
            'params_file': nav2_params_file,
        }.items(),
    )
    
    

    wrapper_node = Node(
        package='wg_yolo_package',
        executable='yolo_wrapper.sh',
        name='ros_yolo_node',
        output='screen'
    )

    hack_node_gz_topic_list = Node(
        package='wg_yolo_package',
        executable='HACK_run_topic_list.sh',
        name='hacky_node_gz',
        output='screen'
    )

    gz_start_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_launch_path),
        launch_arguments={
            'gz_args': PathJoinSubstitution([sim_pkg_path, 'gazebo_includes', 'worlds/example.sdf']), 
            'on_exit_shutdown': 'True'
        }.items(),
        condition=IfCondition(PythonExpression(["'", mode, "' == 'sim'"])),
    )

    picamera_node = Node(
        package='wg_picamera',
        executable='camera_wrapper.sh',
        name='picamera_node',
        output='screen',
        condition=IfCondition(PythonExpression(["'", mode, "' == 'real'"])),
    )

    wait_sec_node = TimerAction(period=2.0,
                                actions=[gz_start_node,
                                         bridge_node,
                                         full_localization,
                                         nav2_launch,
                                         wrapper_node,
                                         picamera_node])

    return LaunchDescription([
        SetEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            PathJoinSubstitution([sim_pkg_path, 'gazebo_includes', 'models'])
        ),
        SetEnvironmentVariable(
            'BNL_VENV_PATH',os.path.expandvars('/home/${USER}/.BNL_venv/.venv') 
        ),

        mode_arg,
        startup_node,

        RegisterEventHandler(
            OnProcessExit(
                target_action=startup_node,
                on_exit=[wait_sec_node]
            )
        )
    ])