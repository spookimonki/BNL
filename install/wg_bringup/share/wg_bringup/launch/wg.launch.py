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
    #wg_state_est_pkg_path = get_package_share_directory('robot_localization')
    wg_utilities_pkg_path = get_package_share_directory('wg_utilities')
    static_tf_path = '/home/bnluser/Desktop/Elias_BNL/src/wg_utilities/nav2/static_tf.urdf'
    
    gz_launch_path = PathJoinSubstitution([ros_gz_sim_pkg_path, 'launch', 'gz_sim.launch.py'])
    nav2_launch_path = os.path.join(get_package_share_directory('nav2_bringup'), 'launch', 'bringup_launch.py')
    nav2_navigation_launch_path = os.path.join(get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py')
    slam_launch_path = os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
    #full_localization_launch_path = os.path.join(wg_state_est_pkg_path, 'launch', 'full_localization.launch.py')
    
    # Create default nav2 params path (update this to match your setup)
    nav2_params_file = '/home/bnluser/Desktop/Elias_BNL/src/wg_utilities/nav2/nav2_param.yaml'
    
    mode = LaunchConfiguration('mode')
    use_sim_time = PythonExpression(["'", mode, "' == 'sim' and 'true' or 'false'"])

    sim_condition = IfCondition(PythonExpression(["'", mode, "' == 'sim'"]))
    real_condition = IfCondition(PythonExpression(["'", mode, "' == 'real'"]))

    mode_arg = DeclareLaunchArgument('mode',
                          default_value='sim',
                          description='Launch mode: "sim" for Gazebo simulation, "real" for physical robot'
                          )


    startup_node = Node(
        package='wg_bringup',
        executable='bnl_startup.sh',
        name='BNL_startup',
        output='screen',
        emulate_tty=True
    )

    # Bridging and remapping Gazebo topics to ROS 2 (simulation only)
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/scan_gpu@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                    '/camera_image@sensor_msgs/msg/Image[gz.msgs.Image'],
        condition=sim_condition,
        output='screen'
    )
    
    '''
    # Include full localization (wheel odom, IMU, lidar, UKF filter)
    full_localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(full_localization_launch_path),
        launch_arguments={
            'autostart': 'true',
            'mode': mode,
        }.items(),
    )
    '''
    # Include Nav2 with slam_toolbox (slam:='True' tells Nav2 to start slam_toolbox internally)
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_launch_path),
        launch_arguments={
            'namespace': '',
            'use_sim_time': use_sim_time,
            'autostart': 'true',
            'slam': 'True',
            'params_file': nav2_params_file,
        }.items(),
        condition=sim_condition,
    )

    nav2_navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_navigation_launch_path),
        launch_arguments={
            'namespace': '',
            'use_sim_time': 'false',
            'autostart': 'true',
            'params_file': nav2_params_file,
        }.items(),
        condition=real_condition,
    )

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_launch_path),
        launch_arguments={
            'use_sim_time': 'false',
            'slam_params_file': '/home/bnluser/Desktop/Elias_BNL/src/wg_utilities/nav2/slam_params.yaml',
            'autostart': 'true',
        }.items(),
        condition=real_condition,
    )
    
    

    wrapper_node = Node(
        package='wg_yolo_package',
        executable='yolo_wrapper.sh',
        name='ros_yolo_node',
        output='screen',
        condition=sim_condition,
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
        condition=sim_condition,
    )

    picamera_node = Node(
        package='wg_picamera',
        executable='wg_picamera_exec',
        name='picamera_node',
        output='screen',
        condition=sim_condition,
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        condition=real_condition,
        parameters=[{
            'robot_description': ParameterValue(
                Command(['cat ', static_tf_path]),
                value_type=str,
            ),
        }],
    )

    lidar_node = Node(
        package='ldlidar_stl_ros2',
        executable='ldlidar_stl_ros2_node',
        name='lidar_node',
        output='screen',
        condition=real_condition,
        parameters=[{
            'product_name': 'LDLiDAR_LD06',
            'topic_name': 'scan',
            'frame_id': 'lidar_link',
            'port_name': '/dev/ttyAMA0',
            'port_baudrate': 230400,
            'laser_scan_dir': True,
            'enable_angle_crop_func': False,
            'angle_crop_min': 135.0,
            'angle_crop_max': 225.0,
        }],
    )

    wheel_odom_node = Node(
        package='wg_sensor_pullup',
        executable='wheelodom',
        name='wheel_odom_node',
        output='screen',
        condition=real_condition,
        parameters=[{
            'odom_topic': '/odom',
            'odom_frame_id': 'odom',
            'base_frame_id': 'base_link',
            'publish_rate_hz': 10.0,
            'wheel_radius': 0.0275,
            'wheel_base': 0.2,
            'encoder_resolution_left': 2048,
            'encoder_resolution_right': 2048,
            'left_pin_a': 5,
            'left_pin_b': 6,
            'right_pin_a': 4,
            'right_pin_b': 17,
        }],
    )

    vel_to_pwm_node = Node(
        package='wg_sensor_pullup',
        executable='vel_to_pmw',
        name='vel_to_pwm_node',
        output='screen',
        condition=real_condition,
    )

    imu_node = Node(
        package='wg_sensor_pullup',
        executable='imuodom',
        name='imu_odom_node',
        output='screen',
        condition=real_condition,
        parameters=[{
            'topic_name': '/imu/data',
            'frame_id': 'imu_link',
            'publish_hz': 100.0,
            'i2c_address': 0x4A,
        }],
    )

    wait_sec_node = TimerAction(period=2.0,
                                actions=[gz_start_node,
                                         bridge_node,
                                         nav2_launch,
                                         nav2_navigation_launch,
                                         slam_launch,
                                         robot_state_publisher,
                                         lidar_node,
                                         imu_node,
                                         wheel_odom_node,
                                         vel_to_pwm_node,
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