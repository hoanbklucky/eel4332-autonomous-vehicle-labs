#!/usr/bin/env python3
"""Optional ordinary-GPS + simulated encoder + gyro + 2D LiDAR experiment.

Record actual joint velocities, IMU yaw rate, GPS and scans. Replay supplied
filters offline. Truth is saved separately and used only for final scoring.
This tool publishes no motion, odometry, localization, or TF.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np

from budget_fusion_core import wheel_geometry, wheel_speed, LikelihoodField, estimate, FILTER_SETTINGS
from gps_fusion_core import read_world
from gps_profiles import validate_profile

HERE = Path(__file__).resolve().parent
LABELS = {'A': 'wheel encoder + gyro', 'B': 'A + ordinary GPS',
          'C': 'A + ordinary GPS + LiDAR map matching', 'D': 'A + LiDAR (no GPS control)'}


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def record(args):
    import rclpy
    from rclpy.node import Node
    from rclpy.parameter import Parameter
    from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
    from rclpy.signals import SignalHandlerOptions
    from sensor_msgs.msg import JointState, Imu, NavSatFix, LaserScan
    from std_msgs.msg import String
    from nav_msgs.msg import Odometry
    from tf2_ros import Buffer, TransformListener, TransformException

    output = Path(args.output).expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output is not empty; use a new directory')
    world = read_world(args.world)
    output.mkdir(parents=True, exist_ok=True)
    metadata = {'schema': 1, 'complete': False, 'world': world,
        'filter_settings': FILTER_SETTINGS,
        'encoder_model': 'Gazebo joint angular velocities, not cmd_vel; no hardware encoder quantization',
        'initialization': 'Known commanded Home position/heading; no truth alignment',
        'ready_t': None, 'wheel_radii_m': None, 'lidar_mount_xyyaw': None}
    sensors = (output / 'sensors.jsonl').open('x')
    truth = (output / 'truth.csv').open('x', newline='')
    writer = csv.writer(truth)
    writer.writerow(['t', 'x', 'y'])
    rclpy.init(args=[], signal_handler_options=SignalHandlerOptions.NO)

    class Recorder(Node):
        def __init__(self):
            super().__init__('budget_localization_recorder',
                             parameter_overrides=[Parameter('use_sim_time', value=True)])
            self.buffer = Buffer()
            self.listener = TransformListener(self.buffer, self)
            self.counts = dict(wheel=0, imu=0, gps=0, scan=0, truth=0)
            self.last = {}
            self.speed = self.rate = 0.
            self.stationary = None
            self.error = None
            self.description_ok = False
            self.travel = 0.
            self.last_wheel_t = None
            self.pre_ready_travel = 0.
            sensor_qos = QoSProfile(depth=500, reliability=ReliabilityPolicy.BEST_EFFORT)
            retained = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
            self.create_subscription(String, '/robot_description', self.description, retained)
            self.create_subscription(JointState, '/joint_states', self.wheels, sensor_qos)
            self.create_subscription(Imu, '/imu/data', self.imu, sensor_qos)
            self.create_subscription(NavSatFix, '/gps/fix', self.gps, sensor_qos)
            self.create_subscription(LaserScan, '/scan', self.scan, sensor_qos)
            self.create_subscription(Odometry, '/ground_truth/pose', self.score_truth, sensor_qos)

        def stamp(self, msg, kind, interval):
            t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            previous = self.last.get(kind, -math.inf)
            if t < previous:
                self.error = 'Simulation clock reset; restart fresh at Home'
                return None
            if t - previous < interval:
                return None
            self.last[kind] = t
            self.counts[kind] += 1
            return t

        def save(self, kind, t, **values):
            sensors.write(json.dumps(dict(kind=kind, t=t, **values), allow_nan=False) + '\n')

        def description(self, msg):
            try:
                validate_profile(msg.data, 'ordinary')
                metadata['wheel_radii_m'] = wheel_geometry(msg.data)
                metadata['robot_description_sha256'] = hashlib.sha256(msg.data.encode()).hexdigest()
                self.description_ok = True
            except (ValueError, TypeError, KeyError) as exc:
                self.error = str(exc)

        def wheels(self, msg):
            if not self.description_ok:
                return
            try:
                t = self.stamp(msg, 'wheel', .02)
                if t is None:
                    return
                self.speed = wheel_speed(list(msg.name), msg.velocity, metadata['wheel_radii_m'])
                if metadata['ready_t'] is None and self.last_wheel_t is not None:
                    self.pre_ready_travel += abs(self.speed) * max(0., t-self.last_wheel_t)
                    if self.pre_ready_travel > .1:
                        self.error = 'Wheel motion before READY exceeded 0.1 m; restart at fresh Home'
                        return
                if metadata['ready_t'] is not None and self.last_wheel_t is not None:
                    dt = t-self.last_wheel_t
                    if not 0 < dt <= .25:
                        self.error = 'Wheel timestamps have a gap; restart a continuous recording'
                        return
                    self.travel += abs(self.speed) * dt
                self.last_wheel_t = t
                self.save('wheel', t, speed=self.speed,
                          names=list(msg.name), velocities=[float(v) for v in msg.velocity])
                if metadata['ready_t'] is None:
                    if abs(self.speed) > .02 or abs(self.rate) > .03:
                        self.stationary = None
                        return
                    if self.stationary is None:
                        self.stationary = t
                    if (t-self.stationary >= 3 and self.counts['gps'] >= 10
                            and self.counts['imu'] >= 30 and self.counts['scan'] >= 2
                            and self.counts['truth'] >= 1 and metadata['lidar_mount_xyyaw'] is not None):
                        metadata['ready_t'] = t
                        print('READY: drive a 10–20 m loop near building walls. Stop, wait 3 simulated seconds, then Ctrl+C HERE.', flush=True)
            except (ValueError, TypeError) as exc:
                self.error = str(exc)

        def imu(self, msg):
            if msg.header.frame_id != 'imu_link':
                self.error = 'Expected the supplied aligned imu_link frame'
                return
            try:
                tf = self.buffer.lookup_transform('base_footprint', 'imu_link', rclpy.time.Time())
                q = tf.transform.rotation
                if max(abs(q.x), abs(q.y), abs(q.z)) > 1e-6:
                    self.error = 'This experiment expects the supplied aligned IMU mount'
                    return
            except TransformException:
                return
            t = self.stamp(msg, 'imu', .02)
            if t is not None:
                self.rate = float(msg.angular_velocity.z)
                if not math.isfinite(self.rate):
                    self.error = 'Invalid gyro yaw rate'
                    return
                self.save('imu', t, yaw_rate=self.rate)

        def gps(self, msg):
            if msg.header.frame_id != 'gps_link':
                self.error = 'Expected gps_link'
                return
            try:
                tf = self.buffer.lookup_transform('base_footprint', 'gps_link', rclpy.time.Time())
                if math.hypot(tf.transform.translation.x, tf.transform.translation.y) > .001:
                    self.error = 'Use the supplied horizontally centered GPS antenna'
                    return
            except TransformException:
                return
            if msg.status.status < 0:
                return
            t = self.stamp(msg, 'gps', .01)
            if t is not None:
                values = [msg.latitude, msg.longitude, msg.altitude]
                if not np.isfinite(values).all():
                    return
                self.save('gps', t, latitude=msg.latitude, longitude=msg.longitude,
                    altitude=msg.altitude, status=msg.status.status,
                    covariance_type=msg.position_covariance_type,
                    r00=msg.position_covariance[0], r01=msg.position_covariance[1],
                    r11=msg.position_covariance[4])

        def scan(self, msg):
            if msg.header.frame_id != 'lidar_link':
                self.error = 'Expected lidar_link on /scan'
                return
            try:
                tf = self.buffer.lookup_transform('base_footprint', 'lidar_link', rclpy.time.Time())
                q = tf.transform.rotation
                if abs(q.x) > 1e-6 or abs(q.y) > 1e-6:
                    self.error = 'Use a level 2D LiDAR mount'
                    return
                yaw = math.atan2(2*q.w*q.z, 1-2*q.z*q.z)
                metadata['lidar_mount_xyyaw'] = [tf.transform.translation.x, tf.transform.translation.y, yaw]
            except TransformException:
                return
            t = self.stamp(msg, 'scan', .95)
            if t is not None:
                self.save('scan', t, angle_min=msg.angle_min, angle_increment=msg.angle_increment,
                    range_min=msg.range_min, range_max=msg.range_max,
                    ranges=[float(v) if math.isfinite(v) else None for v in msg.ranges])

        def score_truth(self, msg):
            if msg.header.frame_id != 'map':
                self.error = 'Evaluation truth must use the supplied raw world/map frame'
                return
            t = self.stamp(msg, 'truth', .03)
            if t is not None:
                writer.writerow([t, msg.pose.pose.position.x, msg.pose.pose.position.y])

    node = Recorder()
    start = time.monotonic()
    last_log = start
    interrupted = False
    try:
        print(f'Recording to {output}; keep stationary at fresh Home until READY.', flush=True)
        while rclpy.ok() and node.error is None:
            rclpy.spin_once(node, timeout_sec=.1)
            if metadata['ready_t'] is None and time.monotonic()-start > 180:
                node.error = f'Sensor discovery timeout: {node.counts}'
            names = node.get_node_names()
            if 'gps_global_localizer' in names or 'amcl' in names or any('slam_toolbox' in n for n in names):
                node.error = 'Stop GPS navigation, AMCL and SLAM; record a manual drive only'
            if time.monotonic()-last_log > 5:
                if metadata['ready_t'] is None:
                    print(f'Waiting for stationary sensors: {node.counts}', flush=True)
                else:
                    print(f'Recorded wheel travel: {node.travel:.1f} m; minimum 5 m, aim for 10–20 m.', flush=True)
                sensors.flush()
                truth.flush()
                last_log = time.monotonic()
    except KeyboardInterrupt:
        interrupted = True
    finally:
        sensors.close()
        truth.close()
        metadata['complete'] = interrupted and node.error is None and metadata['ready_t'] is not None
        metadata['counts'] = node.counts
        metadata['live_wheel_travel_m'] = node.travel
        metadata['error'] = node.error
        (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    if not metadata['complete']:
        raise ValueError(metadata['error'] or 'Recording ended before READY')
    print('Saved sensors.jsonl, evaluation-only truth.csv and metadata.json. Run report next.', flush=True)


def report(args):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    directory = Path(args.input).expanduser().resolve()
    meta = json.loads((directory / 'metadata.json').read_text())
    if not meta.get('complete'):
        raise ValueError('Recording is incomplete; wait for READY and stop with Ctrl+C')
    rows = [json.loads(line) for line in (directory / 'sensors.jsonl').read_text().splitlines()]
    map_path = Path(args.map).expanduser().resolve()
    from gps_reference_map import validate_reference_map
    validate_reference_map(map_path, args.world)
    current_world = read_world(args.world)
    for key in ('datum', 'home_xy', 'home_yaw'):
        if current_world[key] != meta['world'][key]:
            raise ValueError('Recording and reference world use different GPS/Home coordinates')
    field = LikelihoodField(map_path)
    dropout = tuple(args.gps_dropout) if args.gps_dropout else None
    if dropout and not 0 <= dropout[0] < dropout[1]:
        raise ValueError('GPS dropout must be START END seconds after READY, START < END')
    if dropout and dropout[1] > max(r['t'] for r in rows)-meta['ready_t']:
        raise ValueError('GPS dropout extends beyond this recording; choose an interval within the drive')
    estimates, diagnostics = estimate(rows, meta, field, seed=args.seed, dropout=dropout)
    # The estimates above are complete before evaluation-only truth is read.
    truth = np.genfromtxt(directory / 'truth.csv', delimiter=',', skip_header=1)
    if truth.ndim != 2 or truth.shape[1] != 3 or len(truth) < 2:
        raise ValueError('Insufficient evaluation truth')
    if not np.isfinite(truth).all() or np.any(np.diff(truth[:, 0]) <= 0):
        raise ValueError('Evaluation truth contains non-finite data or repeated/reset timestamps')
    t = estimates[:, 0]
    indices = np.searchsorted(truth[:, 0], t)
    inside = (indices > 0) & (indices < len(truth))
    good = np.flatnonzero(inside)
    good = good[(truth[indices[good], 0]-truth[indices[good]-1, 0]) <= .25]
    if len(good) < 20 or len(good) < .9*len(t):
        raise ValueError('Truth coverage/gaps prevent a fair score; record again')
    estimates, t = estimates[good], t[good]
    reference = np.column_stack([np.interp(t, truth[:, 0], truth[:, k]) for k in (1, 2)])
    metrics = {}
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(reference[:, 0], reference[:, 1], 'k-', label='Gazebo truth (scoring only)')
    for i, (key, label) in enumerate(LABELS.items()):
        xy = estimates[:, 1+2*i:3+2*i]
        error = np.linalg.norm(xy-reference, axis=1)
        metrics[key] = {'label': label, 'rmse_m': float(np.sqrt(np.mean(error**2))),
                        'final_error_m': float(error[-1]), 'max_error_m': float(error.max())}
        axes[0].plot(xy[:, 0], xy[:, 1], label=key+': '+label)
        axes[1].plot(t-meta['ready_t'], error, label=f'{key}: RMSE {metrics[key]["rmse_m"]:.3f} m')
    if dropout:
        axes[1].axvspan(*dropout, color='gray', alpha=.2, label='Artificial GPS withholding')
    axes[0].set(xlabel='East (m)', ylabel='North (m)', title='Same drive; no RTK input')
    axes[0].axis('equal')
    axes[1].set(xlabel='Simulation seconds after READY', ylabel='Horizontal error (m)')
    for ax in axes:
        ax.grid(True, alpha=.3)
        ax.legend(fontsize=7)
    fig.tight_layout()
    prefix = 'budget_dropout' if dropout else 'budget_comparison'
    artifacts = [directory / (prefix+suffix) for suffix in ('.png', '_metrics.json', '_estimates.csv')]
    if any(p.exists() for p in artifacts):
        raise ValueError('Report outputs exist; preserve them or use a new recording directory')
    fig.savefig(artifacts[0], dpi=150)
    plt.close(fig)
    artifacts[1].write_text(json.dumps({'scope': 'Offline localization, not live navigation or hardware validation',
        'method': 'B/C/D use the same 600-particle likelihood filter; A integrates measured wheel/gyro motion',
        'encoder_model': meta.get('encoder_model'),
        'map': str(map_path), 'map_yaml_sha256': file_digest(map_path),
        'map_image_sha256': file_digest(map_path.parent / 'reference.png'),
        'seed': args.seed, 'artificial_gps_withholding_s': dropout,
        'filter_settings': FILTER_SETTINGS,
        'diagnostics': diagnostics, 'metrics': metrics}, indent=2) + '\n')
    np.savetxt(artifacts[2], estimates, delimiter=',',
               header='t,A_x,A_y,B_x,B_y,C_x,C_y,D_x,D_y', comments='')
    for key, value in metrics.items():
        print(f'{key}: RMSE {value["rmse_m"]:.3f} m / final {value["final_error_m"]:.3f} m')
    print(f'Open {artifacts[0]} and {artifacts[1]}. Improvement is not guaranteed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    rec = commands.add_parser('record')
    rec.add_argument('--output', required=True)
    rec.add_argument('--world', default=str(HERE.parent / 'campus/campus.sdf'))
    rep = commands.add_parser('report')
    rep.add_argument('--input', required=True)
    rep.add_argument('--map', default=str(HERE.parent / 'campus/reference.yaml'))
    rep.add_argument('--world', default=str(HERE.parent / 'campus/campus.sdf'))
    rep.add_argument('--seed', type=int, default=7)
    rep.add_argument('--gps-dropout', nargs=2, type=float, metavar=('START', 'END'))
    args = parser.parse_args()
    try:
        record(args) if args.command == 'record' else report(args)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f'Budget localization experiment stopped: {exc}\n')


if __name__ == '__main__':
    main()
