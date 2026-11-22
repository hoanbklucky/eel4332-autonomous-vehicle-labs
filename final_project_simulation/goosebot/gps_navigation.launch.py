"""Start GPS localization first; start Nav2 only after GPS_LOCALIZATION_READY."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gps_navigation_core import prepare_parameters

_TEMP_DIRS = []  # retain files until the launch process exits


def ready_actions(buffer, data, sentinel='GPS_LOCALIZATION_READY:'):
    """Pure stream parser: tolerate a readiness line split across output chunks."""
    text = (buffer + data.decode(errors='replace'))[-8192:]
    return text, sentinel in text


def generate_launch_description():
    from ament_index_python.packages import get_package_share_directory
    from launch import LaunchDescription
    from launch.actions import (DeclareLaunchArgument, ExecuteProcess, OpaqueFunction,
        RegisterEventHandler, IncludeLaunchDescription, EmitEvent, LogInfo)
    from launch.event_handlers import OnProcessIO, OnProcessExit
    from launch.events import Shutdown
    from launch.launch_description_sources import PythonLaunchDescriptionSource
    from launch.substitutions import LaunchConfiguration
    from launch_ros.actions import Node

    here = Path(__file__).resolve().parent

    def start(context):
        profile = LaunchConfiguration('profile').perform(context)
        world = Path(LaunchConfiguration('world').perform(context)).expanduser().resolve()
        if profile not in ('ordinary', 'rtk') or not world.is_file():
            raise ValueError('Choose ordinary/rtk and the supplied campus world path')
        temp = tempfile.TemporaryDirectory(prefix='course-gps-nav-')
        _TEMP_DIRS.append(temp)
        params = Path(temp.name) / 'nav2_gps.yaml'
        reference_map = LaunchConfiguration('reference_map').perform(context).strip()
        if not reference_map:
            raise ValueError('Campus navigation requires its supplied reference_map; short-range mode is retired')
        prepared = prepare_parameters(here / 'nav2_goosebot.yaml', params, profile,
                           reference_map=reference_map, world=world)
        map_server = Node(package='nav2_map_server', executable='map_server', name='map_server',
            output='screen', parameters=[str(params), {
                'autostart_node': False, 'bond_heartbeat_period': 0.0}])
        map_startup = ExecuteProcess(cmd=[sys.executable, '-u', str(here / 'map_startup.py'),
            '--map-yaml', prepared['map_server']['ros__parameters']['yaml_filename']],
            output='screen', sigterm_timeout='10', sigkill_timeout='5')
        localizer = ExecuteProcess(cmd=[sys.executable, '-u', str(here / 'gps_localizer.py'),
                '--world', str(world), '--profile', profile], output='screen',
                sigterm_timeout='10', sigkill_timeout='5')
        nav2 = IncludeLaunchDescription(PythonLaunchDescriptionSource(str(
                Path(get_package_share_directory('nav2_bringup')) / 'launch/navigation_launch.py')),
            launch_arguments={'use_sim_time': 'true', 'autostart': 'true',
                'use_composition': 'False', 'params_file': str(params)}.items())
        state = {'text': '', 'started': False, 'map_text': '', 'nav_started': False}

        def output(event):
            state['text'], ready = ready_actions(state['text'], event.text)
            if ready and not state['started']:
                state['started'] = True
                return [LogInfo(msg='GPS pose ready; activating and verifying campus map before Nav2.'),
                        map_server, map_startup]
            return []

        def map_output(event):
            state['map_text'], ready = ready_actions(state['map_text'], event.text, 'CAMPUS_MAP_READY:')
            if ready and not state['nav_started']:
                state['nav_started'] = True
                return [LogInfo(msg='Campus map active and received; starting Nav2 (no AMCL).'), nav2]
            return []

        actions = [
            RegisterEventHandler(OnProcessIO(target_action=localizer, on_stdout=output)),
            RegisterEventHandler(OnProcessIO(target_action=map_startup, on_stdout=map_output)),
        ]
        for process in (localizer, map_server, map_startup):
            actions.append(RegisterEventHandler(OnProcessExit(target_action=process,
                on_exit=lambda _event, _context: [EmitEvent(event=Shutdown(
                    reason='GPS localization or campus map stopped; stopping navigation.'))])))
        return [*actions, localizer]

    return LaunchDescription([
        DeclareLaunchArgument('profile', default_value='rtk', choices=['ordinary', 'rtk']),
        DeclareLaunchArgument('world', default_value=str(here.parent / 'campus/campus.sdf')),
        DeclareLaunchArgument('reference_map', default_value=str(here.parent / 'campus/reference.yaml'),
                             description='Required full-scale campus/reference.yaml for pedestrian-only planning'),
        OpaqueFunction(function=start),
    ])

