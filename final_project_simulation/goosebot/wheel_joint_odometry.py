#!/usr/bin/env python3
"""Publish /wheel/odometry from /joint_states, never from commanded motion."""
import math
import time

from wheel_odometry_core import model_geometry, track_width, wheel_twist, WheelOdometry


def main():
    import rclpy
    from rclpy.node import Node
    from rclpy.parameter import Parameter
    from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
    from rclpy.clock import Clock
    from rclpy.clock_type import ClockType
    from rclpy.signals import SignalHandlerOptions
    from sensor_msgs.msg import JointState
    from std_msgs.msg import String
    from nav_msgs.msg import Odometry

    rclpy.init(args=[], signal_handler_options=SignalHandlerOptions.NO)

    class WheelNode(Node):
        def __init__(self):
            super().__init__('wheel_joint_odometry',
                             parameter_overrides=[Parameter('use_sim_time', value=True)])
            self.model = None
            self.model_text = None
            self.odometry = WheelOdometry()
            self.failure = None
            self.started_wall = time.monotonic()
            self.last_t = None
            self.ready_logged = False
            self.last_publish_t = -math.inf
            self.publisher = self.create_publisher(Odometry, '/wheel/odometry', 10)
            retained = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
            samples = QoSProfile(depth=100, reliability=ReliabilityPolicy.BEST_EFFORT)
            self.create_subscription(String, '/robot_description', self.description, retained)
            self.create_subscription(JointState, '/joint_states', self.joints, samples)
            self.steady = Clock(clock_type=ClockType.STEADY_TIME)
            self.create_timer(.2, self.check, clock=self.steady)

        def description(self, msg):
            try:
                if self.model_text is not None and msg.data != self.model_text:
                    raise ValueError('Robot geometry changed; restart the complete simulation')
                radii, _ = model_geometry(msg.data)
                self.model = radii, track_width(msg.data)
                self.model_text = msg.data
            except (ValueError, TypeError) as exc:
                self.failure = str(exc)

        def joints(self, msg):
            if self.model is None or self.failure:
                return
            try:
                velocity, omega = wheel_twist(list(msg.name), msg.velocity, *self.model)
                t = msg.header.stamp.sec + msg.header.stamp.nanosec*1e-9
                if not self.odometry.update(t, velocity, omega):
                    return
                self.last_t = t
                if t-self.last_publish_t < .02:
                    return
                self.last_publish_t = t
                output = Odometry()
                output.header = msg.header
                output.header.frame_id = 'odom'
                output.child_frame_id = 'base_footprint'
                x, y, yaw = self.odometry.pose
                output.pose.pose.position.x = x
                output.pose.pose.position.y = y
                output.pose.pose.orientation.z = math.sin(yaw/2)
                output.pose.pose.orientation.w = math.cos(yaw/2)
                for i, variance in zip((0, 7, 35), self.odometry.variance):
                    output.pose.covariance[i] = variance
                for i in (14, 21, 28):
                    output.pose.covariance[i] = 1e6
                output.twist.twist.linear.x = velocity
                output.twist.twist.angular.z = omega
                output.twist.covariance[0] = .05**2
                output.twist.covariance[35] = .2**2
                for i in (7, 14, 21, 28):
                    output.twist.covariance[i] = 1e6
                self.publisher.publish(output)
                if not self.ready_logged:
                    print('WHEEL_ODOMETRY_READY: measured /joint_states -> /wheel/odometry; no TF.', flush=True)
                    self.ready_logged = True
            except (ValueError, TypeError) as exc:
                self.failure = str(exc)

        def check(self):
            now = self.get_clock().now().nanoseconds*1e-9
            if self.last_t is None:
                if time.monotonic()-self.started_wall > 120:
                    self.failure = 'No measured wheel states; check /joint_states bridge and robot description'
            elif now-self.last_t > .5:
                self.failure = 'Wheel states stale or simulation clock reset; stopping course world'

    node = WheelNode()
    try:
        while rclpy.ok() and not node.failure:
            rclpy.spin_once(node, timeout_sec=.1)
        if node.failure:
            raise ValueError(node.failure)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
