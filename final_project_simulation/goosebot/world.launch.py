"""Start server, spawn in the named world, then open the GUI on create success."""
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable, DeclareLaunchArgument, EmitEvent, ExecuteProcess,
    LogInfo, OpaqueFunction, RegisterEventHandler, TimerAction,
)
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def existing_servers(proc=Path('/proc')):
    """Find Gazebo servers, not their shell wrappers or unrelated processes."""
    found = []
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            args = (entry / 'cmdline').read_bytes().decode(errors='replace').split('\0')
        except (OSError, ProcessLookupError):
            continue
        if args and (args[0].strip() == 'gz sim server'
                     or (Path(args[0]).name == 'gz' and args[1:3] == ['sim', 'server'])):
            found.append(entry.name)
    return found


def start(context):
    servers = existing_servers()
    if servers:
        raise RuntimeError('Gazebo server(s) already running: PID ' + ', '.join(servers)
                           + '. Stop the previous course simulation before retrying. '
                           'No processes were killed and no new robot was spawned.')
    world = Path(LaunchConfiguration('world').perform(context)).expanduser().resolve()
    if not world.is_file():
        raise RuntimeError(f'World file not found: {world}')
    world_element = ET.parse(world).getroot().find('world')
    if world_element is None or not world_element.get('name'):
        raise RuntimeError('Expected one named SDF world')
    world_name = world_element.get('name')
    home = json.loads((world.parent / 'mission.json').read_text())['stops'][0]
    here = Path(__file__).resolve().parent
    package = Path(get_package_share_directory('goosebot_0'))
    description = xacro.process_file(str(package / 'urdf/robot.urdf.xacro')).toxml()
    description_parameter = ParameterValue(description, value_type=str)
    server = ExecuteProcess(cmd=['gz', 'sim', '-s', '-r', str(world)], output='screen',
                            sigterm_timeout='10', sigkill_timeout='10')
    gui = ExecuteProcess(cmd=['gz', 'sim', '-g'], output='screen',
                         sigterm_timeout='10', sigkill_timeout='10')
    spawn = Node(package='ros_gz_sim', executable='create', output='screen',
                 arguments=['-world', world_name, '-param', 'robot_description',
                            '-name', 'goosebot', '-allow_renaming=false',
                            '-x', str(home['xy'][0]), '-y', str(home['xy'][1]),
                            '-z', '0.05', '-Y', str(home.get('yaw', 0))],
                 parameters=[{'robot_description': description_parameter,
                              'use_sim_time': True}])
    state = {'ready': False}

    def shutdown(reason):
        return [LogInfo(msg=reason), EmitEvent(event=Shutdown(reason=reason))]

    def after_spawn(event, _context):
        if event.returncode != 0:
            return shutdown('Goosebot spawn failed; GUI was not started. See create log above.')
        state['ready'] = True
        return [LogInfo(msg='GOOSEBOT SPAWNED: creation accepted; opening Gazebo GUI now.'), gui]

    def startup_timeout(_context):
        if not state['ready']:
            return shutdown('Startup timed out. Check world loading/create logs; all owned processes are stopping.')
        return []

    wheel_odom = ExecuteProcess(cmd=[sys.executable, '-u', str(here / 'wheel_joint_odometry.py')],
                                output='screen', sigterm_timeout='10', sigkill_timeout='5')
    return [
        RegisterEventHandler(OnProcessExit(target_action=wheel_odom,
            on_exit=lambda _event, _context: shutdown('Wheel odometry stopped; stopping the course launch.'))),
        LogInfo(msg=f'Course spawn: entity=goosebot world={world_name} file={world} '
                    f'x={home["xy"][0]} y={home["xy"][1]} z=0.05 yaw={home.get("yaw", 0)}'),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', str(world.parent)),
        RegisterEventHandler(OnProcessExit(target_action=spawn, on_exit=after_spawn)),
        RegisterEventHandler(OnProcessExit(target_action=server,
            on_exit=lambda _event, _context: shutdown('Gazebo server exited; stopping the course launch.'))),
        RegisterEventHandler(OnProcessExit(target_action=gui,
            on_exit=lambda _event, _context: shutdown('Gazebo GUI exited; stopping the course launch.'))),
        server,
        Node(package='robot_state_publisher', executable='robot_state_publisher', output='screen',
             parameters=[{'robot_description': description_parameter, 'use_sim_time': True}]),
        Node(package='ros_gz_bridge', executable='parameter_bridge', name='ros_gz_bridge',
             output='screen', parameters=[{'config_file': str(package / 'config/ros_gz_bridge.yaml'),
                                           'use_sim_time': True}]),
        wheel_odom,
        Node(package='robot_localization', executable='ekf_node', name='ekf_filter_node',
             output='screen', parameters=[str(here / 'ekf_wheel.yaml'), {'use_sim_time': True}]),
        spawn,
        TimerAction(period=120.0, actions=[OpaqueFunction(function=startup_timeout)]),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('world', description='Absolute SDF path with adjacent mission.json'),
        OpaqueFunction(function=start),
    ])
