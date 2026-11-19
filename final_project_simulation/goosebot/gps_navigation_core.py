"""Live planar GPS/odometry fusion and Nav2 configuration, without ROS imports."""
import math
from pathlib import Path

import numpy as np
import yaml


def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


class PlanarFusion:
    """State x,y,yaw; initial heading is the known commanded Home heading.

    Prediction uses local EKF motion (command-derived translation + IMU yaw
    rate). GPS corrects position; x/y-yaw cross covariance can correct heading
    after motion. This is a supplied simulation teaching EKF, not RTK firmware.
    """
    def __init__(self, home, settings):
        self.state = np.asarray(home, dtype=float).copy()
        self.settings = settings
        self.covariance = np.diag([settings['initial_std_m'] ** 2] * 2 + [0.03 ** 2])

    def predict(self, body_delta, yaw_delta, dt):
        if not math.isfinite(dt) or dt <= 0 or dt > 0.5:
            raise ValueError('Odometry clock reset/gap; restart GPS navigation at Home')
        if not np.isfinite([*body_delta, yaw_delta]).all():
            raise ValueError('Non-finite odometry motion')
        dx, dy = body_delta
        yaw = self.state[2]
        c, s = math.cos(yaw), math.sin(yaw)
        world_delta = np.array([c * dx - s * dy, s * dx + c * dy])
        jacobian = np.eye(3)
        jacobian[0, 2] = -s * dx - c * dy
        jacobian[1, 2] = c * dx - s * dy
        self.state[:2] += world_delta
        self.state[2] = wrap(yaw + yaw_delta)
        q = (self.settings['process_variance_m2_per_s'] * dt
             + self.settings['process_variance_m2_per_m'] * np.linalg.norm(body_delta))
        noise = np.diag([q, q, 0.0001 * dt + 0.0001 * abs(yaw_delta)])
        self.covariance = jacobian @ self.covariance @ jacobian.T + noise

    def correct(self, xy, covariance):
        covariance = np.asarray(covariance, dtype=float)
        if (not np.isfinite(xy).all() or covariance.shape != (2, 2)
                or not np.isfinite(covariance).all()
                or not np.allclose(covariance, covariance.T)
                or np.linalg.eigvalsh(covariance).min() <= 0):
            raise ValueError('Invalid GPS position/covariance')
        h = np.array([[1., 0, 0], [0, 1., 0]])
        innovation = np.asarray(xy) - h @ self.state
        total = h @ self.covariance @ h.T + covariance
        distance = float(innovation @ np.linalg.solve(total, innovation))
        if distance > self.settings['gps_gate_mahalanobis_squared']:
            return False
        gain = np.linalg.solve(total.T, (self.covariance @ h.T).T).T
        self.state += gain @ innovation
        self.state[2] = wrap(self.state[2])
        residual = np.eye(3) - gain @ h
        self.covariance = (residual @ self.covariance @ residual.T
                           + gain @ covariance @ gain.T)
        return True


def odometry_increment(previous, current):
    if not np.isfinite([*previous, *current]).all():
        raise ValueError('Non-finite local odometry pose')
    dx, dy = np.asarray(current[:2]) - previous[:2]
    c, s = math.cos(previous[2]), math.sin(previous[2])
    return np.array([c * dx + s * dy, -s * dx + c * dy]), wrap(current[2] - previous[2])


def map_to_odom(global_pose, odom_pose):
    yaw = wrap(global_pose[2] - odom_pose[2])
    c, s = math.cos(yaw), math.sin(yaw)
    translation = np.asarray(global_pose[:2]) - np.array([
        c * odom_pose[0] - s * odom_pose[1], s * odom_pose[0] + c * odom_pose[1]])
    return float(translation[0]), float(translation[1]), yaw


def healthy(ready, now_sim, gps_sim, now_wall, odom_wall, gps_wall, scan_wall,
            command_wall, command_sim):
    """Motion gate: stale/outlier-only GPS cannot keep navigation moving."""
    return (ready and gps_sim is not None and 0 <= now_sim - gps_sim <= 2.0
            and now_wall - gps_wall <= 20 and now_wall - odom_wall <= 2
            and now_wall - scan_wall <= 5 and now_wall - command_wall <= 5
            and command_sim is not None and 0 <= now_sim - command_sim <= 0.5)


def prepare_parameters(source, destination, profile):
    if profile not in ('ordinary', 'rtk'):
        raise ValueError('GPS navigation profile must be ordinary or rtk')
    params = yaml.safe_load(Path(source).read_text())
    params.pop('amcl', None)
    params.pop('map_server', None)
    for name in ('local_costmap', 'global_costmap'):
        cost = params[name][name]['ros__parameters']
        cost['plugins'] = ['obstacle_layer', 'inflation_layer']
        cost.pop('static_layer', None)
        cost['track_unknown_space'] = True
        cost['rolling_window'] = True
        cost['initial_transform_timeout'] = 60.0
    glob = params['global_costmap']['global_costmap']['ros__parameters']
    glob.update(global_frame='map', width=30, height=30, resolution=0.1)
    controller = params['controller_server']['ros__parameters']
    tolerance = 0.2 if profile == 'rtk' else 1.5
    controller['goal_checker']['xy_goal_tolerance'] = tolerance
    controller['FollowPath'].update(max_vel_x=0.12, max_speed_xy=0.12,
                                    max_vel_theta=0.8, xy_goal_tolerance=tolerance)
    params['velocity_smoother']['ros__parameters']['max_velocity'] = [0.12, 0., 0.8]
    params['velocity_smoother']['ros__parameters']['min_velocity'] = [-0.12, 0., -0.8]
    # Official navigation_launch.py uses collision_monitor as the last stage.
    # Its output is gated by the GPS localizer before reaching the robot bridge.
    params['collision_monitor']['ros__parameters']['cmd_vel_out_topic'] = '/gps_nav/cmd_vel_request'
    params['planner_server']['ros__parameters']['GridBased']['allow_unknown'] = False
    Path(destination).write_text(yaml.safe_dump(params, sort_keys=False))
    return params
