"""Launch saved-map AMCL/Nav2 with a validated, explicit map-server parameter."""
from pathlib import Path
import tempfile

import yaml


def prepare_parameters(map_file, params_file, output_file):
    """Validate the selected saved map, preserving all unrelated Nav2 settings."""
    map_file = Path(map_file).expanduser().resolve()
    params_file = Path(params_file).expanduser().resolve()
    if not map_file.is_file():
        raise ValueError(f'Saved map YAML not found: {map_file}. Save/select your SLAM map first.')
    map_data = yaml.safe_load(map_file.read_text())
    if not isinstance(map_data, dict) or not isinstance(map_data.get('image'), str):
        raise ValueError(f'Map YAML must specify an image: {map_file}')
    image = Path(map_data['image']).expanduser()
    if not image.is_absolute():
        image = map_file.parent / image
    image = image.resolve()
    if not image.is_file():
        raise ValueError(f'Map image not found: {image}. Keep the saved YAML/image pair together.')
    if not params_file.is_file():
        raise ValueError(f'Nav2 parameters not found: {params_file}')
    params = yaml.safe_load(params_file.read_text())
    if not isinstance(params, dict):
        raise ValueError(f'Expected a Nav2 YAML mapping: {params_file}')
    server = params.setdefault('map_server', {})
    if not isinstance(server, dict):
        raise ValueError('Expected map_server to be a mapping in the Nav2 YAML')
    server_params = server.setdefault('ros__parameters', {})
    if not isinstance(server_params, dict):
        raise ValueError('Expected map_server.ros__parameters to be a mapping')
    server_params['yaml_filename'] = str(map_file)
    Path(output_file).write_text(yaml.safe_dump(params, sort_keys=False))
    return map_file, image


def start(context):
    from ament_index_python.packages import get_package_share_directory
    from launch.actions import IncludeLaunchDescription, LogInfo, RegisterEventHandler
    from launch.event_handlers import OnShutdown
    from launch.launch_description_sources import PythonLaunchDescriptionSource
    from launch.substitutions import LaunchConfiguration

    temporary = tempfile.TemporaryDirectory(prefix='eel4332-nav2-')
    prepared = Path(temporary.name) / 'nav2.yaml'
    try:
        map_file, image = prepare_parameters(
            LaunchConfiguration('map').perform(context),
            LaunchConfiguration('params_file').perform(context), prepared)
        bringup = Path(get_package_share_directory('nav2_bringup')) / 'launch/bringup_launch.py'
    except Exception:
        temporary.cleanup()
        raise

    def cleanup(_event, _context):
        temporary.cleanup()
        return []

    return [
        LogInfo(msg=f'Course navigation map: {map_file}; image: {image}'),
        RegisterEventHandler(OnShutdown(on_shutdown=cleanup)),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(bringup)),
            launch_arguments={
                'map': str(map_file), 'params_file': str(prepared),
                'slam': 'False', 'use_localization': 'True',
                'use_sim_time': 'True', 'use_composition': 'False',
                'autostart': 'True',
            }.items()),
    ]


def generate_launch_description():
    from launch import LaunchDescription
    from launch.actions import DeclareLaunchArgument, OpaqueFunction

    return LaunchDescription([
        DeclareLaunchArgument('map', description='Saved SLAM map YAML; image must exist'),
        DeclareLaunchArgument('params_file',
            default_value=str(Path(__file__).with_name('nav2_goosebot.yaml')),
            description='Course Nav2 settings; map_server path is supplied by this launcher'),
        OpaqueFunction(function=start),
    ])
