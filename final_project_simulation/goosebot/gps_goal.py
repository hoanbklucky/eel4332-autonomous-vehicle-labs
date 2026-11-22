#!/usr/bin/env python3
"""Send an ENU-aligned Nav2 goal from GPS degrees, or return to known Home."""
import argparse
import math
import json
from pathlib import Path
import time

from gps_fusion_core import gps_to_enu, read_world


def goal_xy(args):
    world = read_world(args.world)
    if getattr(args, 'waypoint', None):
        mission = json.loads(Path(args.world).with_name('mission.json').read_text())
        matches = [g for g in mission.get('navigation_goals', []) if g['id'] == args.waypoint]
        if len(matches) != 1:
            raise ValueError('Unknown campus waypoint; use A or B from the current mission.json')
        return [*matches[0]['xy'], matches[0]['yaw']]
    if args.home:
        return [*world['home_xy'], world['home_yaw']]
    if args.latitude is None or args.longitude is None:
        raise ValueError('Use --home, --waypoint A/B, or both --latitude and --longitude')
    xy = gps_to_enu(args.latitude, args.longitude, world['datum'][2], world['datum'])[:2]
    if math.hypot(*xy) > 2000 or not math.isfinite(args.yaw_deg):
        raise ValueError('Invalid goal outside the full-scale campus')
    return [*xy, math.radians(args.yaw_deg)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--world', default=str(Path(__file__).resolve().parents[1] / 'campus/campus.sdf'))
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--home', action='store_true')
    modes.add_argument('--waypoint', choices=['A', 'B'])
    parser.add_argument('--latitude', type=float)
    parser.add_argument('--longitude', type=float)
    parser.add_argument('--yaw-deg', type=float, default=0)
    args = parser.parse_args()
    try:
        x, y, yaw = goal_xy(args)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    import rclpy
    from rclpy.node import Node
    from rclpy.parameter import Parameter
    from rclpy.action import ActionClient
    from rclpy.qos import QoSProfile, DurabilityPolicy
    from rclpy.signals import SignalHandlerOptions
    from nav2_msgs.action import NavigateToPose
    from action_msgs.msg import GoalStatus
    from std_msgs.msg import Bool
    rclpy.init(args=[], signal_handler_options=SignalHandlerOptions.NO)
    node = Node('course_gps_goal', parameter_overrides=[Parameter('use_sim_time', value=True)])
    ready = {'value': False}
    subscription = node.create_subscription(Bool, '/gps_nav/ready',
        lambda msg: ready.update(value=msg.data),
        QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))
    client = ActionClient(node, NavigateToPose, '/navigate_to_pose')
    handle = None
    try:
        deadline = time.monotonic() + 10
        while not ready['value'] and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
        if not ready['value'] or not client.wait_for_server(timeout_sec=10):
            raise RuntimeError('Start GPS navigation and wait for GPS_LOCALIZATION_READY/Nav2 active first')
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = node.get_clock().now().to_msg()
        goal.pose.pose.position.x, goal.pose.pose.position.y = float(x), float(y)
        goal.pose.pose.orientation.z, goal.pose.pose.orientation.w = math.sin(yaw / 2), math.cos(yaw / 2)
        sent = client.send_goal_async(goal)
        rclpy.spin_until_future_complete(node, sent, timeout_sec=15)
        if not sent.done() or sent.result() is None:
            raise RuntimeError('Goal request timed out')
        handle = sent.result()
        if not handle.accepted:
            raise RuntimeError('Nav2 rejected the goal')
        print(f'Accepted GPS-aligned ENU goal ({x:.2f}, {y:.2f}) m. Ctrl+C cancels.')
        result = handle.get_result_async()
        rclpy.spin_until_future_complete(node, result)
        status = result.result().status
        if status != GoalStatus.STATUS_SUCCEEDED:
            raise RuntimeError(f'Navigation did not succeed (action status {status})')
        print('SUCCEEDED: Nav2 reports the goal reached. Verify the robot in Gazebo.')
    except KeyboardInterrupt:
        if handle is not None:
            cancelled = handle.cancel_goal_async()
            rclpy.spin_until_future_complete(node, cancelled, timeout_sec=2)
        print('Cancellation requested.')
    finally:
        client.destroy()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
