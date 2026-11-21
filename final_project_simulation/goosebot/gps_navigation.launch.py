"""Start GPS localization first; start Nav2 only after GPS_LOCALIZATION_READY."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gps_navigation_core import prepare_parameters

_TEMP_DIRS = []  # retain files until the launch process exits


def ready_actions(buffer, data):
    """Pure stream parser: tolerate a readiness line split across output chunks."""
    text = (buffer + data.decode(errors='replace'))[-8192:]
    return text, 'GPS_LOCALIZATION_READY:' in text


def generate_launch_description():
    from ament_index_python.packages import get_package_share_directory
    from launch import LaunchDescription
    from launch.actions import (DeclareLaunchArgument, ExecuteProcess, OpaqueFunction,
        RegisterEventHandler, IncludeLaunchDescription, EmitEvent, LogInfo)
    from launch.event_handlers import OnProcessIO, OnProcessExit
    from launch.events import Shutdown
    from launch.launch_description_sources import PythonLaunchDescriptionSource
    from launch.substitutions import LaunchConfiguration

    here = Path(__file__).resolve().parent

    def start(context):
        profile = LaunchConfiguration('profile').perform(context)
        world = Path(LaunchConfiguration('world').perform(context)).expanduser().resolve()
        if profile not in ('ordinary', 'rtk') or not world.is_file():
            raise ValueError('Choose ordinary/rtk and the supplied campus world path')
        temp = tempfile.TemporaryDirectory(prefix='course-gps-nav-')
        _TEMP_DIRS.append(temp)
        params = Path(temp.name) / 'nav2_gps.yaml'
        prepare_parameters(here / 'nav2_goosebot.yaml', params, profile)
        localizer = ExecuteProcess(cmd=[sys.executable, '-u', str(here / 'gps_localizer.py'),
                '--world', str(world), '--profile', profile], output='screen',
                sigterm_timeout='10', sigkill_timeout='5')
        nav2 = IncludeLaunchDescription(PythonLaunchDescriptionSource(str(
                Path(get_package_share_directory('nav2_bringup')) / 'launch/navigation_launch.py')),
            launch_arguments={'use_sim_time': 'true', 'autostart': 'true',
                'use_composition': 'False', 'params_file': str(params)}.items())
        state = {'text': '', 'started': False}

        def output(event):
            state['text'], ready = ready_actions(state['text'], event.text)
            if ready and not state['started']:
                state['started'] = True
                return [LogInfo(msg='GPS pose ready; starting navigation-only Nav2 (no AMCL/map server).'), nav2]
            return []

        return [
            RegisterEventHandler(OnProcessIO(target_action=localizer, on_stdout=output)),
            RegisterEventHandler(OnProcessExit(target_action=localizer,
                on_exit=lambda _event, _context: [EmitEvent(event=Shutdown(
                    reason='GPS localizer stopped; stopping its navigation stack.'))])),
            localizer,
        ]

    return LaunchDescription([
        DeclareLaunchArgument('profile', default_value='rtk', choices=['ordinary', 'rtk']),
        DeclareLaunchArgument('world', default_value=str(here.parent / 'campus/campus.sdf')),
        OpaqueFunction(function=start),
    ])
