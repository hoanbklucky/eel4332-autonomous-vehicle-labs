"""Subscribe to the counter used in the Lab 00 ROS 2 practice."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class CounterSubscriber(Node):
    """Log each integer received from the practice publisher."""

    def __init__(self) -> None:
        super().__init__("counter_subscriber")
        self.subscription = self.create_subscription(
            Int32,
            "practice/count",
            self.receive_count,
            10,
        )

    def receive_count(self, message: Int32) -> None:
        self.get_logger().info(f"Received count={message.data}")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CounterSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
