"""Offline checks for GNSS profiles, live fusion math, gating and Nav2 wiring."""
import ast
import importlib.util
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import numpy as np
import yaml

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from gps_fusion_core import read_settings, read_world, fallback_gps_covariance
from gps_profiles import apply_profile, validate_profile, PROFILES
from gps_navigation_core import PlanarFusion, odometry_increment, map_to_odom, healthy, prepare_parameters
from gps_goal import goal_xy
from gps_compare import inspect_baseline

spec = importlib.util.spec_from_file_location('gps_navigation_launch', HERE / 'gps_navigation.launch.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)

SENSOR = '''<robot><gazebo reference="gps_link"><sensor type="navsat" name="gps_sensor">
<update_rate>5</update_rate><topic>gps/fix</topic><gz_frame_id>gps_link</gz_frame_id>
<navsat><position_sensing><horizontal><noise type="gaussian"><mean>0</mean><stddev>1.5</stddev>
</noise></horizontal><vertical><noise type="gaussian"><mean>0</mean><stddev>3</stddev>
</noise></vertical></position_sensing></navsat></sensor></gazebo></robot>'''


class GPSNavigationTests(unittest.TestCase):
    def setUp(self):
        self.settings = read_settings(HERE / 'gps_fusion_settings.json')
        self.world = read_world(HERE.parent / 'campus/campus.sdf')

    def test_profile_runtime_comparison_has_two_independent_sensors(self):
        described = apply_profile(SENSOR, 'comparison')
        root = ET.fromstring(described)
        self.assertEqual(len(root.findall('.//sensor')), 2)
        validate_profile(described, 'ordinary')
        validate_profile(described, 'rtk', 'rtk_sensor')
        sensors = root.findall('.//sensor')
        self.assertEqual({s.findtext('topic') for s in sensors}, {'gps/fix', 'gps/rtk_fix'})
        self.assertEqual({s.findtext('gz_frame_id') for s in sensors}, {'gps_link'})
        self.assertEqual(apply_profile(SENSOR, 'model'), SENSOR)
        self.assertIn('<stddev>1.5</stddev>', SENSOR)  # source string never edited

    def test_profiles_and_covariances_are_consistent(self):
        for profile in PROFILES:
            doc = apply_profile(SENSOR, profile)
            validate_profile(doc, profile)
            other = 'rtk' if profile == 'ordinary' else 'ordinary'
            with self.assertRaises(ValueError):
                validate_profile(doc, other)
        rtk = fallback_gps_covariance(28.1485, PROFILES['rtk']['horizontal_std_deg'])
        self.assertAlmostEqual(math.sqrt(rtk[0, 0]), .01964, delta=.0001)
        self.assertAlmostEqual(math.sqrt(rtk[1, 1]), .02216, delta=.0001)
        with self.assertRaises(ValueError):
            apply_profile(apply_profile(SENSOR, 'comparison'), 'comparison')

    def test_map_odom_composition_equals_global_pose_without_touching_local_odom(self):
        for a in np.linspace(-3, 3, 10):
            local = np.array([4.2, -3.1, a])
            global_pose = np.array([-8.5, 9.5, a / 2])
            before = local.copy()
            x, y, yaw = map_to_odom(global_pose, local)
            c, s = math.cos(yaw), math.sin(yaw)
            reconstructed = [x + c * local[0] - s * local[1],
                             y + s * local[0] + c * local[1]]
            np.testing.assert_allclose(reconstructed, global_pose[:2])
            self.assertAlmostEqual(math.atan2(math.sin(yaw + local[2] - global_pose[2]),
                                              math.cos(yaw + local[2] - global_pose[2])), 0)
            np.testing.assert_array_equal(local, before)

    def test_pose_ekf_corrects_position_and_retains_positive_covariance(self):
        rng = np.random.default_rng(12)
        initial = [*self.world['home_xy'], self.world['home_yaw']]
        filt = PlanarFusion(initial, self.settings)
        covariance = fallback_gps_covariance(28.1485, PROFILES['rtk']['horizontal_std_deg'])
        errors = []
        heading = initial[2]
        for i in range(1, 1001):
            # 10% overestimated displacement; same gyro increment, no truth input.
            filt.predict([.011, 0], 0, .05)
            truth = np.array(initial[:2]) + .01 * i * np.array([math.cos(heading), math.sin(heading)])
            if i % 4 == 0:
                fix = truth + rng.multivariate_normal([0, 0], covariance)
                self.assertTrue(filt.correct(fix, covariance))
            errors.append(np.linalg.norm(filt.state[:2] - truth))
        self.assertLess(np.sqrt(np.mean(np.square(errors))), .08)
        self.assertGreater(np.linalg.eigvalsh(filt.covariance).min(), 0)
        with self.assertRaises(ValueError):
            filt.predict([0, 0], 0, -1)
        with self.assertRaises(ValueError):
            filt.predict([float('nan'), 0], 0, .1)

    def test_local_motion_rotation_and_yaw_wrap(self):
        delta, yaw = odometry_increment([0, 0, math.pi / 2], [0, 1, math.pi / 2 + .1])
        np.testing.assert_allclose(delta, [1, 0], atol=1e-12)
        self.assertAlmostEqual(yaw, .1)

    def test_health_gate_rejects_each_missing_or_stale_source(self):
        values = dict(ready=True, now_sim=10, gps_sim=9.9, now_wall=100,
                      odom_wall=99.9, gps_wall=99.9, scan_wall=99.9, command_wall=99.9,
                      command_sim=9.9)
        self.assertTrue(healthy(**values))
        for key, bad in [('ready', False), ('gps_sim', None), ('gps_sim', 7),
                         ('gps_sim', 12), ('odom_wall', 90), ('gps_wall', 70),
                         ('scan_wall', 90), ('command_wall', 90), ('command_sim', 8),
                         ('command_sim', None)]:
            self.assertFalse(healthy(**dict(values, **{key: bad})), key)

    def test_nav2_uses_no_amcl_or_static_map_and_routes_commands_through_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            for profile, tolerance in [('ordinary', 1.5), ('rtk', .2)]:
                destination = Path(temp) / 'gps.yaml'
                data = prepare_parameters(HERE / 'nav2_goosebot.yaml', destination, profile)
                self.assertNotIn('amcl', data)
                self.assertNotIn('map_server', data)
                for name in ('global_costmap', 'local_costmap'):
                    params = data[name][name]['ros__parameters']
                    self.assertTrue(params['rolling_window'])
                    self.assertNotIn('static_layer', params['plugins'])
                    self.assertIn('obstacle_layer', params['plugins'])
                self.assertFalse(data['planner_server']['ros__parameters']['GridBased']['allow_unknown'])
                self.assertEqual(data['collision_monitor']['ros__parameters']['cmd_vel_out_topic'],
                                 '/gps_nav/cmd_vel_request')
                self.assertEqual(data['controller_server']['ros__parameters']['goal_checker']['xy_goal_tolerance'], tolerance)
                self.assertEqual(yaml.safe_load(destination.read_text()), data)

    def test_launch_waits_for_complete_ready_sentinel(self):
        text, ready = launcher.ready_actions('', b'Initializing...\nGPS_LOCALIZ')
        self.assertFalse(ready)
        text, ready = launcher.ready_actions(text, b'ATION_READY: OK\n')
        self.assertTrue(ready)

    def test_global_node_has_no_truth_subscription_and_shutdown_closes_gate(self):
        source = (HERE / 'gps_localizer.py').read_text()
        tree = ast.parse(source)
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == 'create_subscription']
        topics = [n.args[1].value for n in calls if isinstance(n.args[1], ast.Constant)]
        self.assertNotIn('/ground_truth/pose', topics)
        self.assertIn('/odometry/filtered', topics)
        self.assertIn('/gps/fix', topics)
        self.assertIn('/gps_nav/cmd_vel_request', topics)
        self.assertIn('node.ready = False', source[source.index('    finally:'):])

    def test_home_goal_is_known_configuration_not_truth(self):
        from types import SimpleNamespace
        args = SimpleNamespace(world=HERE.parent / 'campus/campus.sdf', home=True)
        np.testing.assert_allclose(goal_xy(args), [*self.world['home_xy'], self.world['home_yaw']])

    def test_running_baseline_validation_rejects_hidden_gps_input(self):
        from types import SimpleNamespace
        p = {'world_frame': 'odom', 'odom0': 'odom_cmdvel', 'imu0': 'imu/data',
             'odom0_config': [False] * 6 + [True, True] + [False] * 7,
             'imu0_config': [False] * 11 + [True] + [False] * 3}
        def dumped():
            return SimpleNamespace(stdout=yaml.safe_dump({'ekf_filter_node': {'ros__parameters': p}}))
        with patch('gps_compare.subprocess.run', side_effect=lambda *a, **k: dumped()):
            self.assertEqual(inspect_baseline(), p)
            p['odom1'] = '/gps/already_fused'
            with self.assertRaisesRegex(ValueError, 'Additional baseline input'):
                inspect_baseline()


if __name__ == '__main__':
    unittest.main()
