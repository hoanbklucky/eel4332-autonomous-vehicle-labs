"""Local-file launch: reuse ROBOTIS Waffle spawning, bridges, and robot TF."""
import os
import json
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


def generate_launch_description():
    if os.environ.get('TURTLEBOT3_MODEL') != 'waffle':
        raise RuntimeError('Run: export TURTLEBOT3_MODEL=waffle')
    root = str(Path(__file__).resolve().parent)
    mission = json.loads((Path(root) / 'mission.json').read_text())
    home_x, home_y = mission['stops'][0]['xy']
    tb = get_package_share_directory('turtlebot3_gazebo')
    gz = get_package_share_directory('ros_gz_sim')
    def include(path, args):
        return IncludeLaunchDescription(PythonLaunchDescriptionSource(path), launch_arguments=args.items())
    return LaunchDescription([
        DeclareLaunchArgument('world_file', default_value='campus.sdf',
                              description='campus.sdf or campus_blocked.sdf'),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.join(tb, 'models')),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', root),
        include(os.path.join(gz, 'launch', 'gz_sim.launch.py'),
                {'gz_args': ['-r -v2 ', PathJoinSubstitution([root, LaunchConfiguration('world_file')])],
                 'on_exit_shutdown': 'true'}),
        include(os.path.join(tb, 'launch', 'robot_state_publisher.launch.py'),
                {'use_sim_time': 'true'}),
        include(os.path.join(tb, 'launch', 'spawn_turtlebot3.launch.py'),
                {'x_pose': str(home_x), 'y_pose': str(home_y)}),
    ])

