"""Supplied planar position fusion, independent of ROS and ground truth.

Prediction uses increments of the existing odometry/IMU EKF position. GPS
provides independent ENU position updates. This is a two-state Kalman filter,
not a replacement full-state EKF or navsat_transform_node/Nav2 integration.
All coordinates are simulation meters in the campus world's ENU frame.
"""
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np


def finite_array(value, name):
    result = np.asarray(value, dtype=float)
    if not np.isfinite(result).all():
        raise ValueError(f'{name} contains non-finite values')
    return result


def read_settings(path):
    settings = json.loads(Path(path).read_text())
    positive = ('initial_std_m', 'fallback_horizontal_std_deg',
                'gps_gate_mahalanobis_squared', 'max_world_radius_m',
                'max_interpolation_gap_s', 'controlled_prediction_scale')
    nonnegative = ('process_variance_m2_per_s', 'process_variance_m2_per_m')
    for key in positive + nonnegative:
        value = float(settings[key])
        if not math.isfinite(value) or value < 0 or (key in positive and value == 0):
            raise ValueError(f'Invalid setting: {key}')
        settings[key] = value
    return settings


def read_world(world_path):
    """Read a known datum and commanded spawn pose, never measured truth."""
    path = Path(world_path).expanduser().resolve()
    world = ET.parse(path).getroot().find('world')
    if world is None:
        raise ValueError('SDF has no world')
    datum = world.find('spherical_coordinates')
    if datum is None or datum.findtext('surface_model') != 'EARTH_WGS84':
        raise ValueError('Expected the supplied WGS84 campus world')
    if (datum.findtext('world_frame_orientation') != 'ENU'
            or abs(float(datum.findtext('heading_deg', '0'))) > 1e-9):
        raise ValueError('Comparison supports ENU with heading_deg=0 only')
    home = json.loads(path.with_name('mission.json').read_text())['stops'][0]
    config = {
        'world': str(path), 'world_name': world.get('name'),
        'datum': [float(datum.findtext('latitude_deg')),
                  float(datum.findtext('longitude_deg')),
                  float(datum.findtext('elevation', '0'))],
        'home_xy': list(map(float, home['xy'])),
        'home_yaw': float(home.get('yaw', 0)),
    }
    finite_array(config['datum'] + config['home_xy'] + [config['home_yaw']], 'world')
    return config


def ecef(latitude, longitude, altitude):
    lat, lon = math.radians(latitude), math.radians(longitude)
    a, e2 = 6378137.0, 6.6943799901413165e-3  # WGS84
    radius = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    return np.array([(radius + altitude) * math.cos(lat) * math.cos(lon),
                     (radius + altitude) * math.cos(lat) * math.sin(lon),
                     (radius * (1 - e2) + altitude) * math.sin(lat)])


def gps_to_enu(latitude, longitude, altitude, datum):
    finite_array([latitude, longitude, altitude, *datum], 'GPS')
    if abs(latitude) > 90 or abs(longitude) > 180:
        raise ValueError('Invalid latitude/longitude')
    lat, lon = map(math.radians, datum[:2])
    transform = np.array([
        [-math.sin(lon), math.cos(lon), 0],
        [-math.sin(lat) * math.cos(lon), -math.sin(lat) * math.sin(lon), math.cos(lat)],
        [math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat)]])
    return transform @ (ecef(latitude, longitude, altitude) - ecef(*datum))


def fallback_gps_covariance(latitude, std_degrees):
    """Convert Gazebo Sensors 8's angular stddev to per-axis meter variance."""
    lat = math.radians(latitude)
    a, e2 = 6378137.0, 6.6943799901413165e-3
    denom = 1 - e2 * math.sin(lat) ** 2
    north_radius = a * (1 - e2) / denom ** 1.5
    east_radius = a / math.sqrt(denom) * math.cos(lat)
    sigma = np.radians(std_degrees) * np.array([east_radius, north_radius])
    return np.diag(sigma ** 2)


def gps_covariance(row, datum_latitude, std_degrees):
    fallback = fallback_gps_covariance(datum_latitude, std_degrees)
    if int(row.get('covariance_type', 0)) not in (1, 2, 3):
        return fallback
    cov = np.array([[float(row['r00']), float(row['r01'])],
                    [float(row['r01']), float(row['r11'])]])
    if not np.isfinite(cov).all() or np.linalg.eigvalsh(cov).min() <= 0:
        return fallback
    # Do not treat zero/near-zero published uncertainty as certainty.
    return cov + np.eye(2) * 1e-6


def align_odometry(positions, yaw0, world):
    positions = finite_array(positions, 'odometry')
    angle = world['home_yaw'] - float(yaw0)
    rotation = np.array([[math.cos(angle), -math.sin(angle)],
                         [math.sin(angle), math.cos(angle)]])
    return (positions - positions[0]) @ rotation.T + world['home_xy']


def timeseries(times, values, name):
    t, v = finite_array(times, name + ' times'), finite_array(values, name)
    if t.ndim != 1 or len(t) < 2 or len(t) != len(v) or np.any(np.diff(t) <= 0):
        raise ValueError(f'{name} needs at least two strictly increasing timestamps')
    return t, v


def interpolate(times, values, targets, max_gap):
    """No extrapolation and no interpolation across missing-data gaps."""
    t, v = timeseries(times, values, 'interpolation input')
    targets = np.asarray(targets, dtype=float)
    right = np.searchsorted(t, targets, side='left').clip(0, len(t) - 1)
    left = (right - 1).clip(0)
    exact = np.isclose(t[right], targets, rtol=0, atol=1e-9)
    valid = ((targets >= t[0]) & (targets <= t[-1])
             & (exact | ((t[right] - t[left]) <= max_gap)))
    columns = [np.interp(targets, t, v[:, i]) for i in range(v.shape[1])]
    return np.column_stack(columns), valid


class PositionFilter:
    def __init__(self, initial_position, settings):
        self.position = np.asarray(initial_position, dtype=float).copy()
        self.covariance = np.eye(2) * settings['initial_std_m'] ** 2
        self.settings = settings

    def predict(self, displacement, dt):
        displacement = finite_array(displacement, 'prediction')
        self.position += displacement
        variance = (self.settings['process_variance_m2_per_s'] * dt
                    + self.settings['process_variance_m2_per_m']
                    * np.linalg.norm(displacement))
        self.covariance += np.eye(2) * variance

    def correct(self, measurement, covariance):
        innovation = finite_array(measurement, 'measurement') - self.position
        total = self.covariance + covariance
        distance = float(innovation @ np.linalg.solve(total, innovation))
        if distance > self.settings['gps_gate_mahalanobis_squared']:
            return False
        gain = np.linalg.solve(total.T, self.covariance.T).T
        self.position += gain @ innovation
        residual = np.eye(2) - gain
        # Joseph form preserves covariance symmetry/positive definiteness.
        self.covariance = (residual @ self.covariance @ residual.T
                           + gain @ covariance @ gain.T)
        return True


def fuse_positions(odom_t, baseline_xy, gps_t, gps_xy, gps_cov, settings, scale=1.0):
    """Causal replay of identical predictions with/without GPS; no truth input.

    The optional controlled scale error affects BOTH variants identically.
    Interpolation uses bracketing odometry samples; this is offline evaluation,
    not an online low-latency localization system.
    """
    t, base = timeseries(odom_t, baseline_xy, 'odometry')
    if np.max(np.diff(t)) > settings['max_interpolation_gap_s']:
        raise ValueError('Odometry gap exceeds allowed interpolation interval')
    g, xy = timeseries(gps_t, gps_xy, 'GPS')
    covariance = finite_array(gps_cov, 'GPS covariance')
    if covariance.shape != (len(g), 2, 2) or scale <= 0 or not math.isfinite(scale):
        raise ValueError('Invalid covariance shape or prediction scale')
    if (not np.allclose(covariance, covariance.transpose(0, 2, 1))
            or np.min(np.linalg.eigvalsh(covariance)) <= 0):
        raise ValueError('GPS covariance must be symmetric positive definite')
    inside = (g >= t[0]) & (g <= t[-1])
    g, xy, covariance = g[inside], xy[inside], covariance[inside]
    if len(g) < 5:
        raise ValueError('Need at least five GPS fixes overlapping odometry')
    predicted = base[0] + scale * (base - base[0])
    filt = PositionFilter(predicted[0], settings)
    output = np.empty_like(predicted)
    grid = np.unique(np.concatenate([t, g]))
    all_base = np.column_stack([np.interp(grid, t, predicted[:, i]) for i in (0, 1)])
    i = j = accepted = rejected = 0
    last_xy, last_t = all_base[0], grid[0]
    for stamp, point in zip(grid, all_base):
        filt.predict(point - last_xy, stamp - last_t)
        last_xy, last_t = point, stamp
        while j < len(g) and g[j] == stamp:
            if filt.correct(xy[j], covariance[j]):
                accepted += 1
            else:
                rejected += 1
            j += 1
        while i < len(t) and t[i] == stamp:
            output[i] = filt.position
            i += 1
    if accepted < 5:
        raise ValueError('Too few accepted GPS fixes; check datum, noise and start pose')
    return {'baseline': predicted, 'fused': output,
            'accepted': accepted, 'rejected': rejected}


def score(estimate_t, cases, truth_t, truth_xy, max_gap):
    """Ground truth enters ONLY this evaluator, after estimates are complete."""
    truth, valid = interpolate(truth_t, truth_xy, estimate_t, max_gap)
    if valid.sum() < 10:
        raise ValueError('Not enough synchronized ground truth for scoring')
    result = {}
    for name, case in cases.items():
        result[name] = {}
        for variant in ('baseline', 'fused'):
            error = np.linalg.norm(case[variant][valid] - truth[valid], axis=1)
            result[name][variant] = {
                'rmse_m': float(np.sqrt(np.mean(error ** 2))),
                'final_error_m': float(error[-1]), 'max_error_m': float(error.max())}
        result[name]['gps_updates_accepted'] = case['accepted']
        result[name]['gps_updates_rejected'] = case['rejected']
        result[name]['scored_samples'] = int(valid.sum())
        result[name]['scored_fraction'] = float(valid.mean())
    return result, truth, valid
