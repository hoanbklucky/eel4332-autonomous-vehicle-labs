"""Offline wheel/gyro/GPS and likelihood-field LiDAR localization experiment.

Known Home initializes every estimate. A supplied obstacle map is prior knowledge;
neither map-frame truth nor absolute simulated IMU orientation is an input.
"""
import math
from pathlib import Path

import numpy as np
import yaml

from gps_navigation_core import wrap
from gps_fusion_core import gps_to_enu, gps_covariance
from gps_profiles import PROFILES

from wheel_odometry_core import WHEELS, wheel_geometry, wheel_speed

FILTER_SETTINGS = {'particles': 600, 'initial_xy_std_m': .25,
    'initial_yaw_std_rad': .03, 'distance_variance_per_s': .0001,
    'distance_variance_per_m': .0025, 'yaw_variance_per_s': .00001,
    'yaw_variance_per_rad': .0004, 'lidar_hit_sigma_m': .18,
    'effective_lidar_beams': 12}


class LikelihoodField:
    def __init__(self, map_path):
        from PIL import Image
        from scipy.ndimage import distance_transform_edt
        path = Path(map_path).resolve()
        data = yaml.safe_load(path.read_text())
        self.resolution = float(data['resolution'])
        self.origin = np.asarray(data['origin'], dtype=float)
        if self.origin.shape != (3,) or abs(self.origin[2]) > 1e-9:
            raise ValueError('Use the axis-aligned supplied obstacle reference map')
        with Image.open(path.parent / data['image']) as image:
            pixels = np.asarray(image.convert('L'))
        probability = pixels / 255. if data.get('negate', 0) else (255. - pixels) / 255.
        occupied = probability > float(data['occupied_thresh'])
        if not occupied.any():
            raise ValueError('LiDAR matching map contains no obstacles')
        self.distance = distance_transform_edt(~occupied) * self.resolution
        self.height, self.width = pixels.shape

    def distances(self, points):
        from scipy.ndimage import map_coordinates
        x = (points[..., 0] - self.origin[0]) / self.resolution - .5
        y = self.height - (points[..., 1] - self.origin[1]) / self.resolution - .5
        return map_coordinates(self.distance, [y, x], order=1, mode='constant', cval=3.)


class Particles:
    """Small supplied localization filter, not AMCL or a production safety stack."""
    def __init__(self, home, seed, count=FILTER_SETTINGS['particles']):
        self.rng = np.random.default_rng(seed)
        self.states = np.asarray(home) + self.rng.normal(size=(count, 3)) * [
            FILTER_SETTINGS['initial_xy_std_m'], FILTER_SETTINGS['initial_xy_std_m'],
            FILTER_SETTINGS['initial_yaw_std_rad']]
        self.weights = np.full(count, 1. / count)
        self.lidar_updates = 0
        self.lidar_skipped = 0

    def predict(self, distance, yaw_delta, dt):
        if not math.isfinite(dt) or not 0 < dt <= .25:
            raise ValueError('Wheel/IMU data gap; record a fresh continuous run')
        # Same nominal measured increment for every variant; particles model
        # uncertainty instead of pretending joint velocity equals ground travel.
        ds = distance + self.rng.normal(0, math.sqrt(FILTER_SETTINGS['distance_variance_per_s'] * dt
            + FILTER_SETTINGS['distance_variance_per_m'] * abs(distance)), len(self.weights))
        da = yaw_delta + self.rng.normal(0, math.sqrt(FILTER_SETTINGS['yaw_variance_per_s'] * dt
            + FILTER_SETTINGS['yaw_variance_per_rad'] * abs(yaw_delta)), len(self.weights))
        heading = self.states[:, 2] + da / 2
        self.states[:, 0] += ds * np.cos(heading)
        self.states[:, 1] += ds * np.sin(heading)
        self.states[:, 2] = np.arctan2(np.sin(self.states[:, 2] + da), np.cos(self.states[:, 2] + da))

    def likelihood(self, log_weight):
        values = np.log(np.maximum(self.weights, 1e-300)) + log_weight
        values -= np.max(values)
        self.weights = np.exp(values)
        self.weights /= self.weights.sum()
        if 1 / np.sum(self.weights ** 2) < len(self.weights) / 2:
            positions = (self.rng.random() + np.arange(len(self.weights))) / len(self.weights)
            indices = np.searchsorted(np.cumsum(self.weights), positions)
            self.states = self.states[np.minimum(indices, len(self.weights)-1)].copy()
            self.weights.fill(1 / len(self.weights))

    def gps(self, xy, covariance):
        delta = self.states[:, :2] - xy
        error = np.einsum('ni,ij,nj->n', delta, np.linalg.inv(covariance), delta)
        # Heavy-tailed contamination term limits single-fix domination, but
        # does not simulate real multipath or guarantee outlier robustness.
        self.likelihood(np.log(.95 * np.exp(-.5 * np.minimum(error, 1000)) + .05 * .01))

    def scan(self, points, field):
        if len(points) < 20:
            self.lidar_skipped += 1
            return
        c, s = np.cos(self.states[:, 2]), np.sin(self.states[:, 2])
        transformed = np.empty((len(self.weights), len(points), 2))
        transformed[:, :, 0] = self.states[:, 0, None] + c[:, None] * points[:, 0] - s[:, None] * points[:, 1]
        transformed[:, :, 1] = self.states[:, 1, None] + s[:, None] * points[:, 0] + c[:, None] * points[:, 1]
        distances = field.distances(transformed)
        if np.max(np.mean(distances < .5, axis=1)) < .1:
            self.lidar_skipped += 1
            return
        # Correlated beams are not independent measurements. Use a capped
        # effective beam count and a random-return mixture, not 120 certainties.
        likelihood = .9 * np.exp(-.5 * (distances / FILTER_SETTINGS['lidar_hit_sigma_m']) ** 2) + .1 / 12
        self.likelihood(FILTER_SETTINGS['effective_lidar_beams'] * np.mean(np.log(likelihood), axis=1))
        self.lidar_updates += 1

    def pose(self):
        return np.array([self.weights @ self.states[:, 0], self.weights @ self.states[:, 1],
                         math.atan2(self.weights @ np.sin(self.states[:, 2]),
                                    self.weights @ np.cos(self.states[:, 2]))])


def scan_points(row, mount):
    ranges = np.asarray([np.nan if v is None else v for v in row['ranges']], dtype=float)
    angles = row['angle_min'] + np.arange(len(ranges)) * row['angle_increment']
    good = np.isfinite(ranges) & (ranges >= row['range_min']) & (ranges < row['range_max'] * .98)
    points = np.column_stack((ranges[good] * np.cos(angles[good]), ranges[good] * np.sin(angles[good])))
    if len(points) > 120:
        points = points[np.linspace(0, len(points)-1, 120).astype(int)]
    x, y, yaw = mount
    c, s = math.cos(yaw), math.sin(yaw)
    return points @ np.array([[c, s], [-s, c]]) + [x, y]


def estimate(rows, metadata, field, seed=7, dropout=None):
    """No truth argument: produce A/B/C/D estimates before evaluation is read."""
    ready = float(metadata['ready_t'])
    rows = sorted(rows, key=lambda r: (r['t'], {'wheel': 0, 'imu': 1, 'gps': 2, 'scan': 3}[r['kind']]))
    stationary_gyro = [r['yaw_rate'] for r in rows if r['kind'] == 'imu' and ready-3 <= r['t'] <= ready]
    if len(stationary_gyro) < 20:
        raise ValueError('Missing stationary IMU samples before READY')
    bias = float(np.mean(stationary_gyro))
    home = [*metadata['world']['home_xy'], metadata['world']['home_yaw']]
    a = np.asarray(home, dtype=float)
    b, c, d = (Particles(home, seed) for _ in range(3))
    output = []
    v = gyro = 0.
    wheel_t = imu_t = None
    previous = ready
    travel = 0.
    accepted_gps = rejected_gps = 0
    for row in rows:
        t = float(row['t'])
        if t <= ready:
            if row['kind'] == 'wheel':
                v, wheel_t = float(row['speed']), t
            elif row['kind'] == 'imu':
                gyro, imu_t = float(row['yaw_rate']) - bias, t
            continue
        dt = t - previous
        if dt:
            if wheel_t is None or imu_t is None or t - wheel_t > .25 or t - imu_t > .25:
                raise ValueError('Wheel/IMU samples missing or stale; cannot score continuous fusion')
            ds, da = v * dt, gyro * dt
            travel += abs(ds)
            a[:2] += ds * np.array([math.cos(a[2]+da/2), math.sin(a[2]+da/2)])
            a[2] = wrap(a[2]+da)
            b.predict(ds, da, dt)
            c.predict(ds, da, dt)
            d.predict(ds, da, dt)
            previous = t
        kind = row['kind']
        if kind == 'wheel':
            v, wheel_t = float(row['speed']), t
            output.append([t, *a[:2], *b.pose()[:2], *c.pose()[:2], *d.pose()[:2]])
        elif kind == 'imu':
            gyro, imu_t = float(row['yaw_rate']) - bias, t
        elif kind == 'gps':
            if dropout and dropout[0] <= t-ready <= dropout[1]:
                continue
            if row['status'] < 0:
                rejected_gps += 1
                continue
            xy = gps_to_enu(row['latitude'], row['longitude'], row['altitude'], metadata['world']['datum'])[:2]
            covariance = gps_covariance(row, metadata['world']['datum'][0], PROFILES['ordinary']['horizontal_std_deg'])
            if np.linalg.norm(xy) > 200:
                rejected_gps += 1
                continue
            b.gps(xy, covariance)
            c.gps(xy, covariance)
            accepted_gps += 1
        elif kind == 'scan':
            points = scan_points(row, metadata['lidar_mount_xyyaw'])
            c.scan(points, field)
            d.scan(points, field)
    if travel < 5:
        raise ValueError(f'Recorded wheel travel {travel:.2f} m is below 5 m; drive a 10–20 m loop')
    if c.lidar_updates < 3:
        raise ValueError('Too few usable LiDAR matches; drive near mapped building boundaries')
    return np.asarray(output), {'wheel_travel_m': travel, 'gyro_bias_rad_s': bias,
        'seed': seed, 'gps_accepted': accepted_gps, 'gps_rejected': rejected_gps,
        'lidar_updates_C': c.lidar_updates, 'lidar_skipped_C': c.lidar_skipped,
        'lidar_updates_D': d.lidar_updates, 'lidar_skipped_D': d.lidar_skipped}

