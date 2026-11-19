"""Start only the recording tool; launch the campus world separately first."""
import sys
from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration


def start(context):
    here = Path(__file__).resolve().parent
    return [ExecuteProcess(
        cmd=[sys.executable, '-u', str(here / 'gps_compare.py'), 'record',
             '--output', LaunchConfiguration('output').perform(context),
             '--world', LaunchConfiguration('world').perform(context),
             '--settings', str(here / 'gps_fusion_settings.json')],
        output='screen', sigterm_timeout='15', sigkill_timeout='10')]


def generate_launch_description():
    here = Path(__file__).resolve().parent
    return LaunchDescription([
        DeclareLaunchArgument('output', description='New/empty recording directory'),
        DeclareLaunchArgument('world', default_value=str(here.parent / 'campus/campus.sdf')),
        OpaqueFunction(function=start),
    ])
