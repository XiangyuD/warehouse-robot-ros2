import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String


class MonitorNode(Node):

    def __init__(self):
        super().__init__("monitor_node")

        self.position = "unknown"
        self.state = "unknown"
        self.battery = 0

        self.position_subscription = self.create_subscription(
            String,
            "robot_position",
            self.position_callback,
            10
        )

        self.state_subscription = self.create_subscription(
            String,
            "robot_state",
            self.state_callback,
            10
        )

        self.battery_subscription = self.create_subscription(
            Int32,
            "robot_battery",
            self.battery_callback,
            10
        )

        self.get_logger().info("Robot monitor started")

    def position_callback(self, message):
        self.position = message.data
        self.show_status()

    def state_callback(self, message):
        self.state = message.data

    def battery_callback(self, message):
        self.battery = message.data

    def show_status(self):
        self.get_logger().info(
            f"Position: {self.position} | "
            f"State: {self.state} | "
            f"Battery: {self.battery}%"
        )


def main(args=None):
    rclpy.init(args=args)

    node = MonitorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()