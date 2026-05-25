import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription, LaunchContext
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    ExecuteProcess,
    RegisterEventHandler,
    OpaqueFunction  
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.event_handlers import OnProcessExit
from launch_ros.actions import SetParameter

def create_gazebo_action(context: LaunchContext, package_name: str):
    world_name = LaunchConfiguration('world').perform(context)
    render_engine = LaunchConfiguration('render_engine').perform(context)
    pkg_path = get_package_share_directory(package_name)
    world_file = os.path.join(pkg_path, 'world', world_name)
    
    gazebo_action = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args': (
                f'-r -v4 '
                f'--render-engine {render_engine} '
                f'{world_file}'
            ),
            'on_exit_shutdown': 'true'
        }.items()
    )
    return [gazebo_action]

def choose_launch_file(context, *args, **kwargs):
    use_sensors = LaunchConfiguration('sensors').perform(context)
    package_name = 'gazebo_sim'
    pkg_path = get_package_share_directory(package_name)
    
    if use_sensors.lower() == 'true':
        launch_file = 'gazebo_go2_sensors.launch.py'
    else:
        launch_file = 'gazebo_go2_self.launch.py'
    
    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_path, 'launch', launch_file)
            )
        )
    ]

def generate_launch_description():
    ld = LaunchDescription()
    package_name = 'gazebo_sim'

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    ld.add_action(DeclareLaunchArgument(
        'use_sim_time', 
        default_value='true',
        description='Whether to use simulation time'
    ))
    ld.add_action(SetParameter(name='use_sim_time', value=use_sim_time))

    ld.add_action(DeclareLaunchArgument(
        'sensors',
        default_value='false',
        description='Whether to launch the sensor-enabled launch file (defaults to the version without external sensors)'
    ))

    ld.add_action(DeclareLaunchArgument(
        'world',
        default_value='rmuc_2025_world.sdf',
        description='Gazebo world file to load (must be placed under gazebo_sim/world)'
    ))

    ld.add_action(DeclareLaunchArgument(
        'render_engine',
        default_value='ogre',
        description='Gazebo render engine to use (for example: ogre or ogre2)'
    ))

    gazebo_action = OpaqueFunction(
        function=create_gazebo_action,
        args=[package_name]  
    )
    ld.add_action(gazebo_action)


    pause = ExecuteProcess(
        cmd=['sleep', '6'],
        output='screen'
    )
    ld.add_action(pause)

    go2_sensors_launch = OpaqueFunction(function=choose_launch_file)

    launch_after_pause = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=pause,
            on_exit=[go2_sensors_launch]
        )
    )
    ld.add_action(launch_after_pause)

    return ld
