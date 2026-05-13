import os
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import (DeclareLaunchArgument,IncludeLaunchDescription,LogInfo)


def generate_launch_description():
    # ───── Set up paths and environment ────────────────────────────────────────
    go2_nav_dir = get_package_share_directory('navigation2')
    rviz_template_path = os.path.join(go2_nav_dir, 'rviz', 'go2_nav2.rviz')
    default_map_path = os.path.join(go2_nav_dir, 'maps', 'warehouse_map.yaml')

    param_file_name = f"go2_nav2.yaml"
    param_file_path = os.path.join(go2_nav_dir, 'param', param_file_name)

    # ───── Launch arguments ────────────────────────────────────────────────────
    declare_map_arg = DeclareLaunchArgument(
        'map',
        default_value=default_map_path,
        description='Full path to the map file to load.'
    )

    declare_params_arg = DeclareLaunchArgument(
        'params_file',
        default_value=param_file_path,
        description='Full path to the navigation parameter file.'
    )

    declare_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true.'
    )

    # Create main launch description
    ld = LaunchDescription()
    ld.add_action(declare_map_arg)
    ld.add_action(declare_params_arg)
    ld.add_action(declare_sim_time_arg)

    map_path = LaunchConfiguration('map')
    params_path = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch',
                'bringup_launch.py'
            )
        ),
        launch_arguments={
            'map': map_path,
            'use_sim_time': use_sim_time,
            'params_file': params_path,
        }.items()
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_template_path],
        parameters=[{'use_sim_time': use_sim_time, 'log_level': 'warn'}],
        remappings=[
            ('/tf', f'tf'),
            ('/tf_static', f'tf_static')
        ],
        output='screen'
    )

    ld.add_action(nav2_launch)
    ld.add_action(rviz_node)

    return ld