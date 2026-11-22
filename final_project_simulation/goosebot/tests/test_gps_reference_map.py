"""Prior-map/road-mask geometry and GPS Nav2 launch regression checks."""
import ast
from collections import deque
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

import numpy as np
from PIL import Image, ImageFilter
import yaml

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from gps_reference_map import validate_reference_map, prepare_reference_map, road_mask
from gps_navigation_core import prepare_parameters


class ReferenceMapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.campus = HERE.parent / 'campus'
        self.world = self.campus / 'campus.sdf'
        self.map = self.campus / 'reference.yaml'

    def test_supplied_map_pixels_match_layout_and_datum(self):
        data = validate_reference_map(self.map, self.world)
        self.assertEqual(data['origin'], [-500., -733.5, 0.])
        self.assertEqual(data['resolution'], .25)

    def test_rejects_unaligned_map_mismatched_datum_origin_and_image(self):
        with self.assertRaisesRegex(ValueError, 'unaligned SLAM'):
            validate_reference_map(self.root / 'student_map.yaml', self.world)
        for name in ('campus.sdf', 'mission.json', 'reference.yaml', 'reference.png',
                     'layout.json', 'generate_campus.py', 'assets_manifest.json'):
            shutil.copyfile(self.campus / name, self.root / name)
        shutil.copytree(self.campus/'meshes',self.root/'meshes')
        world = self.root / 'campus.sdf'
        path = self.root / 'reference.yaml'
        world.write_text(world.read_text()+'\n<!-- stale or locally changed world -->\n')
        with self.assertRaisesRegex(ValueError, 'bundle mismatch: campus.sdf'):
            validate_reference_map(path, world)
        shutil.copyfile(self.world, world)
        layout = json.loads((self.root / 'layout.json').read_text())
        layout['origin_lon_lat'][0] += 1
        (self.root / 'layout.json').write_text(json.dumps(layout))
        with self.assertRaisesRegex(ValueError, 'datum differ'):
            validate_reference_map(path, world)
        shutil.copyfile(self.campus / 'layout.json', self.root / 'layout.json')
        data = yaml.safe_load(path.read_text())
        data['origin'][2] = .2
        path.write_text(yaml.safe_dump(data))
        with self.assertRaisesRegex(ValueError, 'origin/resolution'):
            validate_reference_map(path, world)
        shutil.copyfile(self.map, path)
        image = Image.open(self.root / 'reference.png').copy()
        image.putpixel((20, 20), 0 if image.getpixel((20, 20)) else 254)
        image.save(self.root / 'reference.png')
        with self.assertRaisesRegex(ValueError, 'image differs'):
            validate_reference_map(path, world)

    def test_road_mask_never_opens_grass_or_water_and_does_not_bridge_gaps(self):
        obstacles = np.full((100, 100), 254, dtype='uint8')
        obstacles[45:55, 45:55] = 0  # physical obstacle/water wins over a path
        layout = {'paths': [{'kind': 'road', 'width': 1., 'points': [[1, 5], [9, 5]]},
                            {'kind': 'walk', 'width': 1., 'points': [[2, 1], [2, 3]]}]}
        mask = road_mask(layout, obstacles, .1, [0, 0, 0])
        self.assertEqual(mask[50, 20], 254)
        self.assertEqual(mask[50, 50], 0)
        self.assertEqual(mask[10, 80], 0)  # grass
        self.assertEqual(mask[60, 20], 0)  # gap between walkway and road
        self.assertFalse(np.any((obstacles == 0) & (mask == 254)))

    def test_road_map_has_footprint_clearance_for_required_route(self):
        from scipy.ndimage import label, distance_transform_edt
        output = prepare_reference_map(self.map, self.world, self.root / 'roads.yaml')
        data = yaml.safe_load(output.read_text())
        self.assertEqual(data['resolution'], .25)
        raster = np.asarray(Image.open(data['image']))
        # At least 0.5 m from forbidden grid cells exceeds the 0.142 m
        # footprint circumradius plus half the 0.25 m cell diagonal.
        safe = distance_transform_edt(raster == 254, sampling=.25) >= .5
        components, _ = label(safe)
        mission=json.loads((self.campus/'mission.json').read_text())
        def cell(xy):
            x,y=np.floor((np.asarray(xy)-data['origin'][:2])/.25).astype(int)
            return raster.shape[0]-1-y,x
        start=cell(mission['stops'][0]['xy']);component=components[start]
        self.assertNotEqual(component,0)
        self.assertEqual([g['id'] for g in mission['navigation_goals']],['A','B'])
        for goal in mission['navigation_goals']:
            self.assertEqual(components[cell(goal['xy'])],component)
        self.assertGreater(np.linalg.norm(np.array(mission['navigation_goals'][0]['xy'])-mission['stops'][0]['xy']),15)
        self.assertLess(raster.size,30_000_000)  # no full-campus 5 cm upsampling

    def test_generated_world_mission_layout_and_marker_coordinates_agree(self):
        layout=json.loads((self.campus/'layout.json').read_text())
        mission=json.loads((self.campus/'mission.json').read_text())
        self.assertEqual(layout['scale'],1.)
        self.assertEqual(layout['stops'],mission['stops'])
        self.assertEqual(layout['navigation_goals'],mission['navigation_goals'])
        for name in ('campus.sdf','campus_blocked.sdf'):
            tree=ET.parse(self.campus/name)
            for i,stop in enumerate(mission['stops']):
                pose=tree.find(f".//model[@name='delivery_pad_{i}']/pose").text.split()
                np.testing.assert_allclose(list(map(float,pose[:2])),stop['xy'])
            camera=list(map(float,tree.find(".//plugin[@filename='MinimalScene']/camera_pose").text.split()))
            self.assertLess(np.linalg.norm(np.array(camera[:2])-mission['stops'][0]['xy']),10)
        rows=(self.campus/'reference_goals.csv').read_text().splitlines()
        for row,stop in zip(rows[1:],mission['stops'][1:]):
            np.testing.assert_allclose(list(map(float,row.split(',')[:2])),stop['xy'])

    def test_prior_mode_grass_is_lethal_in_both_costmaps_and_gate_remains(self):
        data = prepare_parameters(HERE / 'nav2_goosebot.yaml', self.root / 'params.yaml',
                                  'rtk', reference_map=self.map, world=self.world)
        self.assertNotIn('amcl', data)
        map_file = Path(data['map_server']['ros__parameters']['yaml_filename'])
        self.assertEqual(map_file, self.root / 'campus_roads.yaml')
        for name, rolling in [('global_costmap', False), ('local_costmap', True)]:
            cost = data[name][name]['ros__parameters']
            self.assertEqual(cost['rolling_window'], rolling)
            self.assertEqual(cost['plugins'], ['static_layer', 'obstacle_layer', 'inflation_layer'])
            self.assertTrue(cost['static_layer']['map_subscribe_transient_local'])
        self.assertIn('ObstacleFootprint', data['controller_server']['ros__parameters']['FollowPath']['critics'])
        self.assertEqual(data['collision_monitor']['ros__parameters']['cmd_vel_out_topic'], '/gps_nav/cmd_vel_request')
        planner = data['planner_server']['ros__parameters']['GridBased']
        self.assertFalse(planner['allow_unknown'])
        self.assertEqual(planner['tolerance'], 0)
        with self.assertRaisesRegex(ValueError, 'requires RTK'):
            prepare_parameters(HERE / 'nav2_goosebot.yaml', self.root / 'bad.yaml',
                               'ordinary', reference_map=self.map, world=self.world)

    def test_launch_waits_for_ready_then_starts_map_server_without_amcl(self):
        # Exercise launch construction with light ROS-launch stand-ins. This
        # checks control flow and booleans; it is not a ROS/Gazebo execution test.
        class Action:
            def __init__(self, *args, **kwargs):
                self.args, self.kwargs = args, kwargs
        class Configuration:
            def __init__(self, name):
                self.name = name
            def perform(self, context):
                return context[self.name]
        modules = {}
        exports = {
            'ament_index_python.packages': {'get_package_share_directory': lambda _: '/nav2'},
            'launch': {'LaunchDescription': Action},
            'launch.actions': {name: Action for name in ('DeclareLaunchArgument', 'ExecuteProcess',
                'OpaqueFunction', 'RegisterEventHandler', 'IncludeLaunchDescription', 'EmitEvent', 'LogInfo')},
            'launch.event_handlers': {name: Action for name in ('OnProcessIO', 'OnProcessExit')},
            'launch.events': {'Shutdown': Action},
            'launch.launch_description_sources': {'PythonLaunchDescriptionSource': Action},
            'launch.substitutions': {'LaunchConfiguration': Configuration},
            'launch_ros.actions': {'Node': Action},
        }
        for name, attrs in exports.items():
            module = types.ModuleType(name)
            module.__dict__.update(attrs)
            modules[name] = module
        spec = importlib.util.spec_from_file_location('road_launch_test', HERE / 'gps_navigation.launch.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.dict(sys.modules, modules):
            description = module.generate_launch_description()
            declared = next(a for a in description.args[0] if a.args and a.args[0]=='reference_map')
            self.assertEqual(declared.kwargs['default_value'],str(self.map))
            start = next(a.kwargs['function'] for a in description.args[0] if 'function' in a.kwargs)
            context = {'profile': 'rtk', 'world': str(self.world), 'reference_map': str(self.map)}
            waiting = start(context)
            callback = waiting[0].args[0].kwargs['on_stdout']
            self.assertEqual(callback(types.SimpleNamespace(text=b'GPS_LOCALIZ')), [])
            started = callback(types.SimpleNamespace(text=b'ATION_READY: ready\n'))
            self.assertEqual(len(started), 4)  # log, map server, map lifecycle, Nav2
            self.assertEqual(started[1].kwargs['executable'], 'map_server')
            self.assertEqual(started[2].kwargs['parameters'][0]['node_names'], ['map_server'])
            arguments = dict(started[3].kwargs['launch_arguments'])
            self.assertTrue(eval('not ' + arguments['use_composition'], {'__builtins__': {}}))
            self.assertEqual(callback(types.SimpleNamespace(text=b'GPS_LOCALIZATION_READY: duplicate\n')), [])
            with self.assertRaisesRegex(ValueError,'short-range mode is retired'):
                start(dict(context,reference_map=''))
        for directory in module._TEMP_DIRS:
            directory.cleanup()


if __name__ == '__main__':
    unittest.main()
