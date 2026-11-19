"""Tests for the supplied comparison utility, not student-required algorithms."""
import csv
import inspect
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import gps_compare as demo
import gps_fusion_core as core


class FusionTests(unittest.TestCase):
    def setUp(self):
        self.settings = core.read_settings(HERE / 'gps_fusion_settings.json')
        self.world = core.read_world(HERE.parent / 'campus/campus.sdf')

    def test_geographic_units_and_known_spawn_alignment(self):
        datum = self.world['datum']
        np.testing.assert_allclose(core.gps_to_enu(*datum, datum), [0, 0, 0], atol=1e-8)
        east = core.gps_to_enu(datum[0], datum[1] + 0.00001, datum[2], datum)
        north = core.gps_to_enu(datum[0] + 0.00001, datum[1], datum[2], datum)
        self.assertAlmostEqual(east[0], 0.982, delta=0.005)
        self.assertAlmostEqual(north[1], 1.108, delta=0.005)
        initial_yaw = 0.3
        xy = core.align_odometry([[4, 6], [5, 6]], initial_yaw, self.world)
        np.testing.assert_allclose(xy[0], self.world['home_xy'])
        angle = self.world['home_yaw'] - initial_yaw
        np.testing.assert_allclose(xy[1] - xy[0], [math.cos(angle), math.sin(angle)])

    def test_unknown_or_zero_covariance_has_realistic_fallback(self):
        for kind in (0, 2):
            cov = core.gps_covariance(dict(covariance_type=kind, r00=0, r01=0, r11=0),
                                      self.world['datum'][0], 0.000015)
            self.assertGreater(cov[0, 0], 2)
            self.assertGreater(cov[1, 1], 2)
            self.assertTrue(np.all(np.linalg.eigvalsh(cov) > 0))

    def synthetic_case(self):
        rng = np.random.default_rng(724)
        t = np.linspace(0, 120, 1201)
        truth = np.column_stack([0.3 * t, 2 * np.sin(t / 20)])
        # A gradually accumulating dead-reckoning error, independent of GPS.
        baseline = truth + np.column_stack([0.04 * t, -0.015 * t])
        g = np.arange(0, 120.001, 0.2)
        gps_truth = np.column_stack([np.interp(g, t, truth[:, i]) for i in (0, 1)])
        gps = gps_truth + rng.normal(0, 1.5, gps_truth.shape)
        cov = np.tile(np.eye(2) * 2.25, (len(g), 1, 1))
        return t, truth, baseline, g, gps, cov

    def test_gps_corrects_accumulated_error_and_uses_same_predictions(self):
        t, truth, baseline, g, gps, cov = self.synthetic_case()
        result = core.fuse_positions(t, baseline, g, gps, cov, self.settings)
        np.testing.assert_array_equal(result['baseline'], baseline)
        a = np.sqrt(np.mean(np.sum((result['baseline'] - truth) ** 2, axis=1)))
        b = np.sqrt(np.mean(np.sum((result['fused'] - truth) ** 2, axis=1)))
        self.assertLess(b, a * 0.5)
        scaled = core.fuse_positions(t, baseline, g, gps, cov, self.settings, 1.15)
        np.testing.assert_allclose(scaled['baseline'], baseline[0] + 1.15 * (baseline - baseline[0]))

    def test_future_gps_does_not_change_past_estimates(self):
        t, _, baseline, g, gps, cov = self.synthetic_case()
        a = core.fuse_positions(t, baseline, g, gps, cov, self.settings)
        changed = gps.copy()
        changed[g > 60] += [10, -10]
        b = core.fuse_positions(t, baseline, g, changed, cov, self.settings)
        np.testing.assert_array_equal(a['fused'][t <= 60], b['fused'][t <= 60])

    def test_gps_gaps_and_bad_updates_do_not_reset_state(self):
        t, _, baseline, g, gps, cov = self.synthetic_case()
        keep = (g < 40) | (g > 70)
        gps = gps[keep]
        gps[10] += [1000, -1000]
        result = core.fuse_positions(t, baseline, g[keep], gps, cov[keep], self.settings)
        self.assertGreaterEqual(result['rejected'], 1)
        self.assertTrue(np.isfinite(result['fused']).all())
        # During dropout, only odometry prediction increments advance the state.
        i, j = np.searchsorted(t, [45, 65])
        np.testing.assert_allclose(result['fused'][j] - result['fused'][i],
                                   baseline[j] - baseline[i], atol=1e-9)

    def test_covariance_stays_positive_after_many_updates(self):
        filt = core.PositionFilter([0, 0], self.settings)
        for _ in range(1000):
            filt.predict([0.01, 0], 0.1)
            filt.correct(filt.position + [0.1, -0.1], np.eye(2) * 2)
        np.testing.assert_allclose(filt.covariance, filt.covariance.T, atol=1e-12)
        self.assertGreater(np.linalg.eigvalsh(filt.covariance).min(), 0)

    def test_evaluation_interpolates_but_never_extrapolates_or_bridges_gaps(self):
        t = [1, 2, 10]
        xy = [[1, 0], [2, 0], [10, 0]]
        result, valid = core.interpolate(t, xy, [0, 1, 1.5, 2, 5, 10, 11], 1)
        np.testing.assert_array_equal(valid, [False, True, True, True, False, True, False])
        self.assertAlmostEqual(result[2, 0], 1.5)

    def test_no_automatic_success_if_gps_makes_estimate_worse(self):
        t = np.arange(0, 20.1, 0.1)
        truth = np.column_stack([t, np.zeros_like(t)])
        g = t[::2]
        gps = truth[::2] + [1.0, 0.5]
        cov = np.tile(np.eye(2) * 2, (len(g), 1, 1))
        case = core.fuse_positions(t, truth, g, gps, cov, self.settings)
        result, _, _ = core.score(t, {'raw': case}, t, truth, 0.5)
        self.assertAlmostEqual(result['raw']['baseline']['rmse_m'], 0)
        self.assertGreater(result['raw']['fused']['rmse_m'], 0)

    def test_reject_resets_and_large_odometry_gaps(self):
        t, _, baseline, g, gps, cov = self.synthetic_case()
        bad = t.copy()
        bad[10] = bad[9]
        with self.assertRaisesRegex(ValueError, 'strictly increasing'):
            core.fuse_positions(bad, baseline, g, gps, cov, self.settings)
        with self.assertRaisesRegex(ValueError, 'Odometry gap'):
            core.fuse_positions(t[::10], baseline[::10], g, gps, cov, self.settings)

    def test_truth_is_not_an_estimator_input(self):
        self.assertNotIn('truth', inspect.signature(core.fuse_positions).parameters)
        self.assertNotIn('truth.csv', inspect.getsource(demo.estimate_recording))
        source = inspect.getsource(demo.report)
        self.assertLess(source.index('estimate_recording(directory)'), source.index("'truth.csv'"))

    def test_recorded_input_estimates_do_not_change_when_truth_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            (directory / 'metadata.json').write_text(json.dumps({
                'schema': 1, 'complete': True, 'world': self.world, 'settings': self.settings}))
            datum = self.world['datum']
            rows = []
            for stamp in np.arange(0, 20.001, 0.1):
                rows.append(dict(kind='odom', t=stamp, x=stamp * 0.5, y=0, yaw=0))
            angle = self.world['home_yaw']
            for stamp in np.arange(0, 20.001, 0.2):
                x = self.world['home_xy'][0] + stamp * 0.5 * math.cos(angle)
                y = self.world['home_xy'][1] + stamp * 0.5 * math.sin(angle)
                rows.append(dict(kind='gps', t=stamp, latitude=datum[0] + y / 110815,
                    longitude=datum[1] + x / 98200, altitude=0, status=0,
                    covariance_type=0, r00=0, r01=0, r11=0))
            with (directory / 'sensors.csv').open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=demo.SENSOR_FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            before = demo.estimate_recording(directory)[2]  # no truth file exists
            (directory / 'truth.csv').write_text('t,x,y\n0,999,999\n20,-999,-999\n')
            after = demo.estimate_recording(directory)[2]
            for label in before:
                np.testing.assert_array_equal(before[label]['fused'], after[label]['fused'])


if __name__ == '__main__':
    unittest.main()
