"""Launch provided Goosebot in either course world; no ground-truth localizer."""
import json
from pathlib import Path
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory

def start(context):
    world=Path(LaunchConfiguration('world').perform(context)).expanduser().resolve()
    if not world.is_file():raise RuntimeError(f'World file not found: {world}')
    mission=json.loads((world.parent/'mission.json').read_text())
    home=mission['stops'][0]
    package=get_package_share_directory('goosebot_0')
    return [AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH',str(world.parent)),
            IncludeLaunchDescription(PythonLaunchDescriptionSource(str(Path(package)/'launch/spawn_robot.launch.py')),
              launch_arguments={'world':str(world),'x':str(home['xy'][0]),'y':str(home['xy'][1]),
                                'yaw':str(home.get('yaw',0)),'use_sim_time':'true','entity_name':'goosebot'}.items())]

def generate_launch_description():
    return LaunchDescription([DeclareLaunchArgument('world',description='Absolute SDF path; mission.json must be beside it'),OpaqueFunction(function=start)])
