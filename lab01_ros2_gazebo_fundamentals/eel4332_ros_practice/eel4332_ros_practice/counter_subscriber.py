"""Subscribe to the counter used in the Lab 1 ROS 2 practice."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class CounterSubscriber(Node):
    """Log each integer received from the practice publisher."""

    def __init__(self) -> None:
        """Initialize the ROS node and its `/practice/count` subscription."""
        super().__init__("counter_subscriber")
        self.subscription = self.create_subscription(
            Int32,
            "practice/count",
            self.receive_count,
            10,
        )

    def receive_count(self, message: Int32) -> None:
        """Log one counter message received by the subscription callback.

        Parameters:
          message: std_msgs/Int32 message received from `/practice/count`

        Returns:
          None.
        """
        self.get_logger().info(f"Received count={message.data}")


def main(args=None) -> None:
    """Run the counter subscriber until shutdown or a keyboard interrupt.

    Parameters:
      args: optional ROS 2 command-line arguments passed to rclpy.init

    Returns:
      None.
    """
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
