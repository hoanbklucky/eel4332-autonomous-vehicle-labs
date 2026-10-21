"""Record stamped odometry for analysis; this is a provided utility."""

import argparse
import csv
from pathlib import Path

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data


class OdometryRecorder(Node):
    def __init__(self, stream):
        super().__init__("lab05_odometry_recorder")
        self.writer = csv.writer(stream)
        self.writer.writerow(["stamp_s", "frame_id", "x_m", "y_m", "vx_m_s", "wz_rad_s"])
        self.stream = stream
        self.previous_stamp = None
        self.frame = None
        self.subscription = self.create_subscription(
            Odometry, "/odom", self.record, qos_profile_sensor_data
        )

    def record(self, message):
        stamp_ns = message.header.stamp.sec * 1_000_000_000 + message.header.stamp.nanosec
        if self.previous_stamp is not None and stamp_ns <= self.previous_stamp:
            raise RuntimeError("Non-increasing odometry time: restart with a new run log")
        if self.frame is not None and message.header.frame_id != self.frame:
            raise RuntimeError("Odometry frame changed within this trial")
        self.previous_stamp = stamp_ns
        self.frame = message.header.frame_id
        position = message.pose.pose.position
        twist = message.twist.twist
        self.writer.writerow([
            f"{stamp_ns / 1e9:.9f}", self.frame, position.x, position.y,
            twist.linear.x, twist.angular.z,
        ])
        self.stream.flush()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(rclpy.utilities.remove_ros_args()[1:])
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    rclpy.init()
    try:
        with path.open("x", newline="", encoding="utf-8") as stream:
            recorder = OdometryRecorder(stream)
            try:
                rclpy.spin(recorder)
            except KeyboardInterrupt:
                pass
            finally:
                recorder.destroy_node()
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
