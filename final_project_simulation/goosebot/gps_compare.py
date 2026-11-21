#!/usr/bin/env python3
"""Record one stationary-start campus drive, then compare GPS fusion offline.

No TF, velocity or localization messages are published. Ground truth is saved
in a separate CSV and is not loaded until both estimate variants are complete.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import numpy as np

from gps_fusion_core import (
    align_odometry, fuse_positions, gps_covariance, gps_to_enu,
    read_settings, read_world, score, timeseries,
)
from gps_profiles import PROFILES, validate_profile

HERE = Path(__file__).resolve().parent
SENSOR_FIELDS = ['kind', 't', 'x', 'y', 'yaw', 'latitude', 'longitude',
                 'altitude', 'status', 'covariance_type', 'r00', 'r01', 'r11']
TRUTH_FIELDS = ['t', 'x', 'y']


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y),
                      1 - 2 * (q.y * q.y + q.z * q.z))


def read_baseline_parameters():
    """Retry incomplete dumps, then query parameters individually if needed."""
    import yaml

    required = {'odom0', 'odom0_config', 'imu0', 'imu0_config', 'world_frame'}
    last_error = 'empty parameter response'
    for attempt in range(3):
        try:
            dumped = subprocess.run(
                ['ros2', 'param', 'dump', '/ekf_filter_node'],
                capture_output=True, text=True, timeout=15, check=True)
            runtime = yaml.safe_load(dumped.stdout)
            entry = runtime.get('/ekf_filter_node', runtime.get('ekf_filter_node', {})) if isinstance(runtime, dict) else {}
            params = entry.get('ros__parameters', {}) if isinstance(entry, dict) else {}
            if isinstance(params, dict) and required <= params.keys():
                return params
            last_error = 'empty or incomplete parameter dump'
        except (subprocess.SubprocessError, yaml.YAMLError) as exc:
            last_error = str(exc)
        if attempt < 2:
            time.sleep(0.3)

    # Some ROS CLI/service responses yield an empty dump while individual gets
    # work. List all inputs as well, so this fallback cannot hide extra sensors.
    print('EKF parameter dump unavailable; checking individual parameters.', flush=True)
    try:
        listed = subprocess.run(
            ['ros2', 'param', 'list', '/ekf_filter_node'],
            capture_output=True, text=True, timeout=15, check=True)
        names = set(required)
        listed_names = {line.strip() for line in listed.stdout.splitlines()}
        if not required <= listed_names:
            raise ValueError('Parameter list is empty or incomplete')
        for line in listed.stdout.splitlines():
            name = line.strip()
            for family in ('odom', 'pose', 'twist', 'imu'):
                if name.startswith(family) and name[len(family):].isdigit():
                    names.add(name)
        params = {}
        for name in sorted(names):
            result = subprocess.run(
                ['ros2', 'param', 'get', '/ekf_filter_node', name],
                capture_output=True, text=True, timeout=15, check=True)
            prefix, separator, value = result.stdout.strip().partition(':')
            if not separator or prefix not in (
                    'String value is', 'Boolean values are'):
                raise ValueError(f'Could not read {name}: {result.stdout.strip()}')
            params[name] = value.strip() if prefix == 'String value is' else yaml.safe_load(value)
        return params
    except (subprocess.SubprocessError, yaml.YAMLError, ValueError) as exc:
        raise ValueError(
            'Could not read running EKF parameters; this is not a confirmed '
            f'configuration mismatch ({last_error}; individual query: {exc}). '
            'Keep the world running and check ros2 param list /ekf_filter_node.') from exc


def inspect_baseline():
    # Inspect running baseline inputs, rather than assuming messages imply fusion.
    params = read_baseline_parameters()
    expected_odom = [False] * 15
    expected_odom[6:8] = [True, True]
    expected_imu = [False] * 15
    expected_imu[11] = True
    expected = {
        'odom0_config': expected_odom, 'imu0_config': expected_imu,
        'odom0': 'odom_cmdvel', 'imu0': 'imu/data', 'world_frame': 'odom',
    }
    differences = []
    for name, wanted in expected.items():
        actual = params.get(name)
        comparable = actual.strip('/') if name in ('odom0', 'imu0') and isinstance(actual, str) else actual
        if comparable != wanted:
            differences.append(f'{name}: got {actual!r}, expected {wanted!r}')
    if differences:
        raise ValueError('Running EKF differs from the supplied baseline: '
                         + '; '.join(differences))
    for family in ('odom', 'pose', 'twist', 'imu'):
        allowed = {'odom0', 'imu0'}
        for name, value in params.items():
            if name.startswith(family) and name[len(family):].isdigit():
                if name not in allowed and value:
                    raise ValueError(f'Additional baseline input {name}={value}; comparison stopped.')

    return params


def record(args):
    # Lazy imports let plotting and mathematical tests run without ROS.
    import rclpy
    from rclpy.node import Node
    from rclpy.parameter import Parameter
    from rclpy.qos import QoSProfile, ReliabilityPolicy
    from rclpy.executors import ExternalShutdownException
    from nav_msgs.msg import Odometry
    from sensor_msgs.msg import NavSatFix
    from std_msgs.msg import String
    from rclpy.qos import DurabilityPolicy
    from tf2_ros import Buffer, TransformListener

    world = read_world(args.world)
    output = Path(args.output).expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError(f'Recording directory is not empty: {output}. Use a new directory.')
    output.mkdir(parents=True, exist_ok=True)
    params = inspect_baseline()

    metadata = {
        'schema': 2, 'complete': False, 'world': world,
        'profiles': PROFILES,
        'baseline': '/odometry/filtered: command-derived vx/vy + IMU yaw rate',
        'topics': {'odometry': '/odometry/filtered', 'gps': '/gps/fix',
                   'rtk': '/gps/rtk_fix',
                   'evaluation_only': '/ground_truth/pose'},
        'runtime_ekf_parameters': params,
        'settings': read_settings(args.settings),
        'settings_sha256': hashlib.sha256(Path(args.settings).read_bytes()).hexdigest(),
        'initialization': 'Known commanded Home spawn pose from mission.json; no truth alignment',
    }
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2))
    sensor_file = (output / 'sensors.csv').open('x', newline='')
    truth_file = (output / 'truth.csv').open('x', newline='')
    sensor_writer = csv.DictWriter(sensor_file, fieldnames=SENSOR_FIELDS)
    truth_writer = csv.DictWriter(truth_file, fieldnames=TRUTH_FIELDS)
    sensor_writer.writeheader()
    truth_writer.writeheader()
    rclpy.init(args=[])

    class Recorder(Node):
        def __init__(self):
            super().__init__('course_gps_comparison_recorder',
                             parameter_overrides=[Parameter('use_sim_time', value=True)])
            self.counts = {'odom': 0, 'gps': 0, 'rtk': 0, 'truth': 0}
            self.last_stamp = {}
            self.stationary_since = None
            self.ready = False
            self.error = None
            self.mount = None
            self.profile_checked = False
            self.first_stamp = None
            self.last_received = time.monotonic()
            self.buffer = Buffer()
            self.listener = TransformListener(self.buffer, self)
            qos = QoSProfile(depth=200, reliability=ReliabilityPolicy.BEST_EFFORT)
            self.create_subscription(Odometry, '/odometry/filtered', self.odom, qos)
            self.create_subscription(NavSatFix, '/gps/fix', self.gps, qos)
            self.create_subscription(NavSatFix, '/gps/rtk_fix',
                                     lambda msg: self.gps(msg, 'rtk'), qos)
            self.create_subscription(Odometry, '/ground_truth/pose', self.truth, qos)
            self.create_subscription(String, '/robot_description', self.description,
                QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))

        def description(self, msg):
            try:
                validate_profile(msg.data, 'ordinary')
                validate_profile(msg.data, 'rtk', 'rtk_sensor')
                self.profile_checked = True
            except (ValueError, TypeError) as exc:
                self.error = str(exc) + '; launch campus with gps_profile:=comparison.'

        def stamp(self, msg, kind):
            t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            previous = self.last_stamp.get(kind, -math.inf)
            if t < previous:
                self.error = 'Simulation clock reset; record a fresh run in a new directory.'
                return None
            if t == previous:
                return None
            self.last_stamp[kind] = t
            self.first_stamp = t if self.first_stamp is None else min(self.first_stamp, t)
            self.last_received = time.monotonic()
            return t

        def odom(self, msg):
            if msg.header.frame_id != 'odom' or msg.child_frame_id != 'base_footprint':
                self.error = 'Expected odom -> base_footprint on /odometry/filtered.'
                return
            t = self.stamp(msg, 'odom')
            if t is None:
                return
            p, v = msg.pose.pose, msg.twist.twist
            sensor_writer.writerow(dict(kind='odom', t=t, x=p.position.x,
                                        y=p.position.y, yaw=yaw_of(p.orientation)))
            self.counts['odom'] += 1
            stopped = math.hypot(v.linear.x, v.linear.y) < 0.02 and abs(v.angular.z) < 0.03
            if not self.ready:
                if not stopped:
                    self.error = 'Robot moved before READY. Restart at Home, then record again.'
                    return
                if self.stationary_since is None:
                    self.stationary_since = t
                if (t - self.stationary_since >= 3 and self.counts['gps'] >= 10
                        and self.counts['rtk'] >= 10 and self.profile_checked
                        and self.counts['truth'] >= 10 and self.mount is not None):
                    self.ready = True
                    self.get_logger().info('READY: drive a safe 10–20 m loop, stop at Home, '
                                           'wait 3 simulated seconds, then Ctrl+C HERE to save.')

        def gps(self, msg, kind='gps'):
            if msg.header.frame_id != 'gps_link':
                self.error = 'Expected GPS frame gps_link; custom frames require review.'
                return
            t = self.stamp(msg, kind)
            if t is None or msg.status.status < 0:
                return
            values = [msg.latitude, msg.longitude, msg.altitude]
            if not all(map(math.isfinite, values)):
                self.error = 'Non-finite GPS fix; inspect sensor configuration.'
                return
            xy = gps_to_enu(*values, world['datum'])[:2]
            if np.linalg.norm(xy) > metadata['settings']['max_world_radius_m']:
                self.error = 'GPS far outside campus; rebuild the corrected horizontal noise '
                self.error += '(0.000015 degrees), source and restart before recording.'
                return
            cov = msg.position_covariance
            sensor_writer.writerow(dict(kind=kind, t=t, latitude=msg.latitude,
                longitude=msg.longitude, altitude=msg.altitude, status=msg.status.status,
                covariance_type=msg.position_covariance_type,
                r00=cov[0], r01=(cov[1] + cov[3]) / 2, r11=cov[4]))
            self.counts[kind] += 1

        def truth(self, msg):
            # Raw Gazebo model world pose; never call estimator code here.
            if msg.header.frame_id != 'map':
                self.error = 'Expected raw course Gazebo truth frame label map.'
                return
            t = self.stamp(msg, 'truth')
            if t is None:
                return
            p = msg.pose.pose.position
            truth_writer.writerow(dict(t=t, x=p.x, y=p.y))
            self.counts['truth'] += 1

        def inspect_mount(self):
            if self.mount is not None:
                return
            try:
                tf = self.buffer.lookup_transform('base_footprint', 'gps_link', rclpy.time.Time())
            except Exception:
                return  # TF discovery; main loop's startup timeout reports missing inputs.
            p = tf.transform.translation
            if math.hypot(p.x, p.y) > 0.001:
                self.error = 'Comparison assumes centered GPS antenna (mount x=y=0).'
                return
            self.mount = [p.x, p.y, p.z]

    node = Recorder()
    start, last_log = time.monotonic(), 0.0
    interrupted = False
    try:
        print(f'Recording to {output}. Keep robot stationary at Home until READY.', flush=True)
        while rclpy.ok() and not node.error:
            rclpy.spin_once(node, timeout_sec=0.2)
            node.inspect_mount()
            now = time.monotonic()
            if not node.ready and now - last_log > 10:
                print(f'Waiting for stationary start / sensor discovery: {node.counts}', flush=True)
                last_log = now
            if not node.ready and now - start > 180:
                node.error = f'Startup timed out: {node.counts}; check clock, bridge and TF.'
            if node.ready and now - node.last_received > 30:
                node.error = 'No messages for 30 wall seconds; is Gazebo paused/stopped?'
    except (KeyboardInterrupt, ExternalShutdownException):
        interrupted = True
    finally:
        metadata.update(complete=bool(node.ready and not node.error and interrupted),
                        counts=node.counts, gps_mount_xyz=node.mount, error=node.error)
        sensor_file.close()
        truth_file.close()
        (output / 'metadata.json').write_text(json.dumps(metadata, indent=2))
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    if not metadata['complete']:
        raise ValueError(node.error or 'Stopped before READY; no valid comparison recorded.')
    print('Saved sensors.csv, evaluation-only truth.csv, metadata.json. Run the report command.')


def read_csv(path):
    with Path(path).open(newline='') as handle:
        return list(csv.DictReader(handle))


def estimate_recording(directory):
    """Read ONLY metadata and sensor CSV; truth cannot influence estimates."""
    directory = Path(directory)
    meta = json.loads((directory / 'metadata.json').read_text())
    if meta.get('schema') not in (1, 2) or not meta.get('complete'):
        raise ValueError('Recording incomplete; restart at Home and wait for READY.')
    rows = read_csv(directory / 'sensors.csv')
    odom = sorted((r for r in rows if r['kind'] == 'odom'), key=lambda r: float(r['t']))
    gps = sorted((r for r in rows if r['kind'] == 'gps'), key=lambda r: float(r['t']))
    t = np.array([float(r['t']) for r in odom])
    xy = np.array([[float(r['x']), float(r['y'])] for r in odom])
    timeseries(t, xy, 'recorded odometry')
    if t[-1] - t[0] < 10:
        raise ValueError('Recording shorter than 10 simulation seconds.')
    base = align_odometry(xy, float(odom[0]['yaw']), meta['world'])
    if np.sum(np.linalg.norm(np.diff(base, axis=0), axis=1)) < 5:
        raise ValueError('Recorded route shorter than 5 m; drive a longer safe loop.')
    g_t, g_xy, g_cov = [], [], []
    for row in gps:
        if int(row['status']) < 0:
            continue
        point = gps_to_enu(float(row['latitude']), float(row['longitude']),
                           float(row['altitude']), meta['world']['datum'])[:2]
        if np.linalg.norm(point) > meta['settings']['max_world_radius_m']:
            raise ValueError('GPS outside campus bounds; fix noise units/datum before comparison.')
        g_t.append(float(row['t']))
        g_xy.append(point)
        g_cov.append(gps_covariance(row, meta['world']['datum'][0],
                         meta['settings']['fallback_horizontal_std_deg']))
    cases = {}
    for label, scale in [('unmodified', 1.0),
                         ('controlled_scale_error', meta['settings']['controlled_prediction_scale'])]:
        cases[label] = fuse_positions(t, base, g_t, g_xy, g_cov, meta['settings'], scale)
    # A second independent simulated sensor measures the SAME drive, not
    # truth-derived "improved" fixes. Legacy schema-1 records still plot A/B.
    if meta.get('schema') == 2:
        rtk = sorted((r for r in rows if r['kind'] == 'rtk'), key=lambda r: float(r['t']))
        rt, rx, rc = [], [], []
        for row in rtk:
            if int(row['status']) < 0:
                continue
            point = gps_to_enu(float(row['latitude']), float(row['longitude']),
                              float(row['altitude']), meta['world']['datum'])[:2]
            if np.linalg.norm(point) > meta['settings']['max_world_radius_m']:
                raise ValueError('RTK-like fix outside campus; check world datum')
            rt.append(float(row['t']))
            rx.append(point)
            rc.append(gps_covariance(row, meta['world']['datum'][0],
                                    meta['profiles']['rtk']['horizontal_std_deg']))
        for label, scale in [('unmodified', 1.0),
                ('controlled_scale_error', meta['settings']['controlled_prediction_scale'])]:
            precise = fuse_positions(t, base, rt, rx, rc, meta['settings'], scale)
            cases[label].update(rtk=precise['fused'], rtk_accepted=precise['accepted'],
                                rtk_rejected=precise['rejected'])
    return meta, t, cases, np.asarray(g_t), np.asarray(g_xy)


def report(args):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    directory = Path(args.input).expanduser().resolve()
    meta, t, cases, gps_t, gps_xy = estimate_recording(directory)
    # Only now load evaluation data, after both estimates have been computed.
    truth_rows = sorted(read_csv(directory / 'truth.csv'), key=lambda r: float(r['t']))
    truth_t = np.array([float(r['t']) for r in truth_rows])
    truth_xy = np.array([[float(r['x']), float(r['y'])] for r in truth_rows])
    metrics, truth, valid = score(t, cases, truth_t, truth_xy,
                                  meta['settings']['max_interpolation_gap_s'])
    if valid.mean() < 0.9:
        raise ValueError('Ground truth overlaps less than 90% of samples; inspect recording gaps.')
    if np.linalg.norm(truth[valid][0] - meta['world']['home_xy']) > 1.0:
        raise ValueError('Recorded start was not near commanded Home. No truth alignment applied; '
                         'restart simulator, stay at Home and record again.')
    summary = {
        'comparison': 'Identical recording; known spawn pose, no ground-truth estimator input',
        'scope': 'Offline planar position fusion; baseline IMU/odometry EKF and Nav2 unchanged',
        'controlled_prediction_scale': meta['settings']['controlled_prediction_scale'],
        'controlled_case_is_artificial': True, 'settings': meta['settings'], 'metrics': metrics,
    }
    (directory / 'metrics.json').write_text(json.dumps(summary, indent=2))
    with (directory / 'estimates.csv').open('w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['t', 'case', 'baseline_x', 'baseline_y', 'fused_x', 'fused_y',
                         'rtk_x', 'rtk_y'])
        for label, case in cases.items():
            precise = case.get('rtk', np.full_like(case['fused'], np.nan))
            for stamp, a, b, c in zip(t, case['baseline'], case['fused'], precise):
                writer.writerow([stamp, label, *a, *b, *c])
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    for col, (label, case) in enumerate(cases.items()):
        ax, error_ax = axes[0, col], axes[1, col]
        ax.plot(truth[valid, 0], truth[valid, 1], 'k-', label='Gazebo truth (scoring only)')
        shown = (gps_t >= t[0]) & (gps_t <= t[-1])
        ax.scatter(gps_xy[shown, 0], gps_xy[shown, 1], s=4, color='gray', alpha=0.3, label='GPS fixes')
        variants = [('baseline', 'tab:orange', 'A: odometry + IMU'),
                    ('fused', 'tab:blue', 'B: A + ordinary GPS')]
        if 'rtk' in case:
            variants.append(('rtk', 'tab:green', 'C: A + RTK-like GPS'))
        for variant, color, title in variants:
            est = case[variant]
            ax.plot(est[:, 0], est[:, 1], color=color, label=title)
            error = np.linalg.norm(est[valid] - truth[valid], axis=1)
            rmse = metrics[label][variant]['rmse_m']
            error_ax.plot(t[valid] - t[0], error, color=color, label=f'{variant}: RMSE {rmse:.2f} m')
        ax.set_aspect('equal', adjustable='datalim')
        ax.set_xlabel('World East (m)')
        ax.set_ylabel('World North (m)')
        ax.legend(fontsize=7)
        scale = meta['settings']['controlled_prediction_scale']
        ax.set_title('Unmodified recorded prediction' if col == 0 else
                     f'CONTROLLED test: prediction increments × {scale:g} in BOTH A/B')
        error_ax.set_xlabel('Simulation time since recording start (s)')
        error_ax.set_ylabel('Horizontal position error (m)')
        error_ax.legend(fontsize=8)
        for axis in (ax, error_ax):
            axis.grid(alpha=0.25)
    fig.suptitle('Ordinary GPS / RTK-like localization — same drive, offline replay')
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(directory / 'comparison.png', dpi=160)
    plt.close(fig)
    print('Horizontal RMSE / final error (meters):')
    for label, result in metrics.items():
        print(label)
        for variant in ('baseline', 'fused', 'rtk') if 'rtk' in cases[label] else ('baseline', 'fused'):
            m = result[variant]
            print(f"  {variant}: {m['rmse_m']:.3f} / {m['final_error_m']:.3f}")
    print(f'Open {directory / "comparison.png"}; metrics.json has numeric results.')
    print('GPS may improve or worsen error. The controlled panel adds a declared scale error; '
          'it is not the unmodified simulator result or improved navigation.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    rec = sub.add_parser('record', help='Record, stationary at fresh campus Home, until Ctrl+C')
    rec.add_argument('--output', required=True)
    rec.add_argument('--world', default=str(HERE.parent / 'campus/campus.sdf'))
    rec.add_argument('--settings', default=str(HERE / 'gps_fusion_settings.json'))
    plot = sub.add_parser('report', help='Replay A/B variants and plot errors')
    plot.add_argument('--input', required=True)
    args = parser.parse_args(argv)
    try:
        (record if args.command == 'record' else report)(args)
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f'GPS comparison stopped: {error}\n')


if __name__ == '__main__':
    main()

