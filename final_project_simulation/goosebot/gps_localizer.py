#!/usr/bin/env python3
"""GPS-aligned map->odom localization and health-gated Nav2 motion for simulation.

Uses no ground truth or absolute simulated IMU orientation. Initial global
heading/position are the known Home spawn command, then local EKF increments
and actual GPS measurements update the supplied 3-state planar EKF.
"""
import argparse
from collections import deque
import math
from pathlib import Path
import time

import numpy as np

from gps_compare import yaw_of, inspect_baseline
from gps_fusion_core import read_settings, read_world, gps_to_enu, gps_covariance
from gps_profiles import PROFILES, validate_profile
from gps_navigation_core import PlanarFusion, odometry_increment, map_to_odom, healthy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--world', required=True)
    parser.add_argument('--profile', choices=['ordinary', 'rtk'], default='rtk')
    args = parser.parse_args()
    inspect_baseline()
    world = read_world(args.world)
    settings = read_settings(Path(__file__).with_name('gps_fusion_settings.json'))

    import rclpy
    from rclpy.node import Node
    from rclpy.parameter import Parameter
    from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
    from rclpy.signals import SignalHandlerOptions
    from rclpy.clock import Clock
    from rclpy.clock_type import ClockType
    from geometry_msgs.msg import TransformStamped, Twist
    from nav_msgs.msg import Odometry
    from sensor_msgs.msg import NavSatFix, LaserScan
    from std_msgs.msg import Bool, String
    from tf2_ros import TransformBroadcaster, Buffer, TransformListener

    rclpy.init(args=[], signal_handler_options=SignalHandlerOptions.NO)

    class Localizer(Node):
        def __init__(self):
            super().__init__('gps_global_localizer',
                             parameter_overrides=[Parameter('use_sim_time', value=True)])
            self.filter = PlanarFusion([*world['home_xy'], world['home_yaw']], settings)
            self.previous = self.previous_t = None
            self.start_t = None
            self.pending = deque(maxlen=100)
            self.last_gps = None
            self.last_gps_wall = self.last_odom_wall = self.last_scan_wall = -math.inf
            self.last_command_wall = -math.inf
            self.last_command_sim = None
            self.command = Twist()
            self.ready = False
            self.profile_checked = self.mount_checked = False
            self.accepted = 0
            self.fatal = None
            self.start_wall = time.monotonic()
            self.last_fix_t = -math.inf
            self.stop_sent = False
            reliable = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
            sensors = QoSProfile(depth=100, reliability=ReliabilityPolicy.BEST_EFFORT)
            self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
            self.pose_pub = self.create_publisher(Odometry, '/gps_nav/odometry', 10)
            self.ready_pub = self.create_publisher(Bool, '/gps_nav/ready', reliable)
            self.tf = TransformBroadcaster(self)
            self.buffer = Buffer()
            self.listener = TransformListener(self.buffer, self)
            self.create_subscription(Odometry, '/odometry/filtered', self.odom, sensors)
            self.create_subscription(NavSatFix, '/gps/fix', self.gps, sensors)
            self.create_subscription(LaserScan, '/scan', self.scan, sensors)
            self.create_subscription(String, '/robot_description', self.description, reliable)
            self.create_subscription(Twist, '/gps_nav/cmd_vel_request', self.request, 10)
            self.wall_clock = Clock(clock_type=ClockType.STEADY_TIME)
            self.create_timer(0.1, self.watchdog, clock=self.wall_clock)
            self.ready_pub.publish(Bool(data=False))

        def description(self, msg):
            try:
                validate_profile(msg.data, args.profile)
                self.profile_checked = True
            except (ValueError, TypeError) as exc:
                self.fatal = str(exc)

        def scan(self, msg):
            if msg.ranges:
                self.last_scan_wall = time.monotonic()

        def request(self, msg):
            self.command = msg
            self.last_command_wall = time.monotonic()
            self.last_command_sim = self.get_clock().now().nanoseconds * 1e-9
            self.gate()

        def gate(self):
            now = time.monotonic()
            sim = self.get_clock().now().nanoseconds * 1e-9
            permitted = healthy(self.ready and not self.fatal, sim, self.last_gps,
                now, self.last_odom_wall, self.last_gps_wall, self.last_scan_wall,
                self.last_command_wall, self.last_command_sim)
            self.cmd_pub.publish(self.command if permitted else Twist())

        def watchdog(self):
            self.gate()
            names = self.get_node_names()
            forbidden = [n for n in names if n == 'amcl' or 'slam_toolbox' in n
                         or 'ground_truth_map_odom' in n]
            if forbidden or names.count('gps_global_localizer') > 1:
                self.fatal = f'Conflicting global localizer(s): {forbidden}; stop other launches.'
            if not self.mount_checked:
                try:
                    tf = self.buffer.lookup_transform('base_footprint', 'gps_link', rclpy.time.Time())
                    p = tf.transform.translation
                    if math.hypot(p.x, p.y) > 0.001:
                        self.fatal = 'Centered GPS mount x=y=0 required for this supplied mode.'
                    else:
                        self.mount_checked = True
                except Exception:
                    pass  # wait for static TF discovery; startup timeout is explicit below
            now = time.monotonic()
            if not self.ready and now - self.start_wall > 180:
                self.fatal = 'GPS startup timed out; check matching world profile, GPS, odometry and scan.'
            if self.ready:
                sim = self.get_clock().now().nanoseconds * 1e-9
                if (self.last_gps is None or sim - self.last_gps > 2
                        or now - self.last_gps_wall > 20 or now - self.last_odom_wall > 2
                        or now - self.last_scan_wall > 5):
                    self.fatal = 'Localization/scan stale: motion stopped; restart GPS navigation at Home.'
            if self.fatal:
                self.cmd_pub.publish(Twist())

        def gps(self, msg):
            if msg.header.frame_id != 'gps_link':
                self.fatal = 'GPS frame must be gps_link'
                return
            t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            if t < self.last_fix_t:
                self.fatal = 'GPS clock reset; restart at Home'
                return
            if t == self.last_fix_t or msg.status.status < 0:
                return
            self.last_fix_t = t
            if not all(map(math.isfinite, [msg.latitude, msg.longitude, msg.altitude])):
                return
            xy = gps_to_enu(msg.latitude, msg.longitude, msg.altitude, world['datum'])[:2]
            if np.linalg.norm(xy) > settings['max_world_radius_m']:
                self.fatal = 'GPS outside campus; inspect profile noise/datum and restart.'
                return
            row = dict(covariance_type=msg.position_covariance_type,
                       r00=msg.position_covariance[0],
                       r01=(msg.position_covariance[1] + msg.position_covariance[3]) / 2,
                       r11=msg.position_covariance[4])
            cov = gps_covariance(row, world['datum'][0],
                                  PROFILES[args.profile]['horizontal_std_deg'])
            self.pending.append((t, xy, cov, time.monotonic()))

        def odom(self, msg):
            if msg.header.frame_id != 'odom' or msg.child_frame_id != 'base_footprint':
                self.fatal = 'Expected local odom -> base_footprint; inspect active workspace'
                return
            t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            p, velocity = msg.pose.pose, msg.twist.twist
            pose = np.array([p.position.x, p.position.y, yaw_of(p.orientation)])
            self.last_odom_wall = time.monotonic()
            if not self.ready and (math.hypot(velocity.linear.x, velocity.linear.y) > 0.02
                                   or abs(velocity.angular.z) > 0.05):
                self.fatal = 'Moved before GPS initialization. Start a fresh world at Home.'
                return
            if self.previous is None:
                self.previous, self.previous_t, self.start_t = pose, t, t
                return
            if t == self.previous_t:
                return
            dt = t - self.previous_t
            try:
                body, turn = odometry_increment(self.previous, pose)
                self.filter.predict(body, turn, dt)
            except ValueError as exc:
                self.fatal = str(exc)
                return
            self.previous, self.previous_t = pose, t
            c, s = math.cos(self.filter.state[2]), math.sin(self.filter.state[2])
            world_velocity = np.array([c * body[0] - s * body[1],
                                       s * body[0] + c * body[1]]) / dt
            while self.pending and self.pending[0][0] <= t:
                gt, xy, covariance, received = self.pending.popleft()
                age = t - gt
                if age > 0.25:
                    continue
                # Small sensor latency compensation using estimated motion, never truth.
                if self.filter.correct(xy + world_velocity * age,
                                       covariance + np.eye(2) * 0.0025 * age):
                    self.accepted += 1
                    self.last_gps, self.last_gps_wall = gt, received
            if (not self.ready and t - self.start_t >= 3 and self.accepted >= 10
                    and self.profile_checked and self.mount_checked
                    and time.monotonic() - self.last_scan_wall < 5):
                self.ready = True
                self.ready_pub.publish(Bool(data=True))
                print('GPS_LOCALIZATION_READY: known Home initialization + '
                      f'{args.profile} GPS + local odometry/IMU; starting Nav2.', flush=True)
            if not self.ready or self.fatal:
                return
            x, y, yaw = map_to_odom(self.filter.state, pose)
            tf = TransformStamped()
            tf.header.stamp = msg.header.stamp
            tf.header.frame_id, tf.child_frame_id = 'map', 'odom'
            tf.transform.translation.x, tf.transform.translation.y = x, y
            tf.transform.rotation.z, tf.transform.rotation.w = math.sin(yaw / 2), math.cos(yaw / 2)
            self.tf.sendTransform(tf)
            out = Odometry()
            out.header.stamp = msg.header.stamp
            out.header.frame_id, out.child_frame_id = 'map', 'base_footprint'
            out.twist = msg.twist  # body-frame velocity remains the local EKF estimate
            out.pose.pose.position.x, out.pose.pose.position.y = map(float, self.filter.state[:2])
            theta = float(self.filter.state[2])
            out.pose.pose.orientation.z, out.pose.pose.orientation.w = math.sin(theta / 2), math.cos(theta / 2)
            for i, row in enumerate((0, 1, 5)):
                for j, col in enumerate((0, 1, 5)):
                    out.pose.covariance[row * 6 + col] = float(self.filter.covariance[i, j])
            self.pose_pub.publish(out)

    node = Localizer()
    error = None
    try:
        print(f'Initializing {args.profile} GPS navigation. Keep stationary at fresh campus Home.', flush=True)
        while rclpy.ok() and not node.fatal:
            rclpy.spin_once(node, timeout_sec=0.05)
        error = node.fatal
    except KeyboardInterrupt:
        pass
    finally:
        node.ready = False
        node.command = Twist()
        # We own signal handling so the context is still valid for the stop message.
        if rclpy.ok():
            for _ in range(3):
                node.cmd_pub.publish(Twist())
                rclpy.spin_once(node, timeout_sec=0.02)
            node.ready_pub.publish(Bool(data=False))
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    if error:
        raise SystemExit(error)


if __name__ == '__main__':
    main()
