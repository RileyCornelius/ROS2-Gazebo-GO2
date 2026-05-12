import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    ExecuteProcess,
    GroupAction
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.descriptions import ComposableNode
from launch.conditions import IfCondition
from launch_ros.actions import Node, SetRemap
import xacro


def generate_launch_description():
    ld = LaunchDescription()

    # ---------- 基础配置 ----------
    package_name = 'gazebo_sim'
    pkg_path = get_package_share_directory(package_name)
    
    # ---------- 声明启动参数 ----------
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    declare_use_sim_time = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='true',
        description='仿真时间是否使用'
    )

    enable_rviz = LaunchConfiguration('enable_rviz', default='true')
    declare_enable_rviz = DeclareLaunchArgument(
        name='enable_rviz', default_value=enable_rviz, description='Enable rviz launch'
    )

    ld.add_action(declare_enable_rviz)
    ld.add_action(declare_use_sim_time)

    # ---------- 多机器人全局话题重映射 ----------
    remappings=[
            ("/tf", "tf"),
            ("/tf_static", "tf_static"),
            ("/scan", "scan"),
            ("/odom", "odometry/filtered")
        ]
    
    # ---------- Gazebo-ROS时间同步配置 ----------
    bridge_params = os.path.join(pkg_path,'config','gz_bridge.yaml')
    ros_gz_bridge_clock = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}',
        ]
    )
    ld.add_action(ros_gz_bridge_clock)   

    # ---------- 多机器人循环启动 ----------
    last_action = None

    xacro_file = os.path.join(os.path.join(get_package_share_directory('go2_description')), 'xacro', 'robot.xacro') ## CHANGE ME!!!!
    robot_desc = xacro.process_file(xacro_file, mappings={'robot_name': 'go2'}).toxml()
    params_robot_state_publisher = {'robot_description': robot_desc, 'use_sim_time': use_sim_time}

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params_robot_state_publisher],
        remappings=remappings
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', '/robot_description',
            '-name', 'go2',
            '-allow_renaming', 'true',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.8',
            # '-Y', robot['Y_pose']
        ],
        output='screen'
    )

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        arguments=[
            '/imu_plugin/out@sensor_msgs/msg/Imu@gz.msgs.IMU',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/scan/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
            '/color/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/color/image_raw@sensor_msgs/msg/Image@gz.msgs.Image',
            # '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock'
        ]
    )
    start_gazebo_ros_image_bridge_cmd = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['color/image_raw', 
                    ],
        output='screen',
    )

    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        name='joint_state_broadcaster',
        arguments=['joint_state_broadcaster'],
        output='screen',
        remappings=remappings
    )

    joint_group_controller = Node(
        package='controller_manager',
        executable='spawner',
        name='joint_group_controller',
        arguments=['joint_group_controller'],
        output='screen',
        remappings=remappings
    )

    controller = Node(
        package='quadropted_controller',
        executable='robot_controller_gazebo.py',
        name='quadruped_controller',
        output='screen',
        remappings=remappings
    )

    odom = Node(
        package='quadropted_controller',
        executable='QuadrupedOdometryNode.py',
        name='odom',
        output='screen',
        parameters=[{
            "verbose": False,
            'publish_rate': 50,
            'open_loop': False,
            'has_imu_heading': True,
            'is_gazebo': True,
            'imu_topic': '/imu',
            'base_frame_id': "base_link",
            'odom_frame_id': "odom",
            'clock_topic': f'/clock',
            'enable_odom_tf': True,
        }],
        remappings=remappings
    )

    rviz_launch_file = os.path.join(pkg_path, 'launch', 'rviz_launch.py')
    rviz_config_file = os.path.join(pkg_path, 'rviz', 'go2_self.rviz')

    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(rviz_launch_file),
        launch_arguments={
            "rviz_config": rviz_config_file,
        }.items(),
        condition=IfCondition(enable_rviz)
    )

    cmd_vel_pub = Node(
        package='quadropted_controller',
        executable='cmd_vel_pub.py',
        name='cmd_vel_pub',
        output='screen',
        remappings=remappings
    )

    fake_bms = ExecuteProcess(
        cmd=[
            'ros2', 'topic', 'pub', '/battery_state', 'sensor_msgs/msg/BatteryState',
            "{header: {stamp: {sec: 0, nanosec: 0}, frame_id: ''}, voltage: 24.0, percentage: 0.8, capacity: 10.0}",
            '-r', '1'
        ],
        output='log'
    )
    robot_localization_file_path = os.path.join(pkg_path, 'config', 'ekf.yaml')
    # Start robot localization using an Extended Kalman filter
    start_robot_localization_cmd = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[robot_localization_file_path, 
        {'use_sim_time': use_sim_time}],
        remappings=remappings)

    robot_control = GroupAction([
        SetRemap(src="/tf", dst="tf"),
        SetRemap(src="/tf_static", dst="tf_static"),
        joint_state_broadcaster,
        joint_group_controller,
        controller,
        cmd_vel_pub,
        odom,
        start_robot_localization_cmd,
        fake_bms,
    ])

    # 当前机器人动作组
    robot_group = GroupAction([
        node_robot_state_publisher,
        spawn_entity,
        ros_gz_bridge,
        start_gazebo_ros_image_bridge_cmd,
        robot_control,
        rviz,
    ])

    ld.add_action(robot_group)

    return ld
