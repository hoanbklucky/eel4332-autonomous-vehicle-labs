"""Publish a counter for the Lab 00 ROS 2 fundamentals practice."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class CounterPublisher(Node):
    """Publish increasing integers at a configurable startup rate."""

    def __init__(self) -> None:
        super().__init__("counter_publisher")
        self.declare_parameter("rate_hz", 2.0)
        rate_hz = self.get_parameter("rate_hz").value
        if rate_hz <= 0.0:
            raise ValueError("rate_hz must be positive")

        self.publisher = self.create_publisher(Int32, "practice/count", 10)
        self.count = 0
        self.timer = self.create_timer(1.0 / rate_hz, self.publish_count)
        self.get_logger().info(f"Publishing /practice/count at {rate_hz:.1f} Hz")

    def publish_count(self) -> None:
        message = Int32()
        message.data = self.count
        self.publisher.publish(message)
        self.get_logger().info(f"Published count={self.count}")
        self.count += 1


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CounterPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
