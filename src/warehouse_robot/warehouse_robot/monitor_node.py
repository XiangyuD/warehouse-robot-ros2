import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MonitorNode(Node):

    def __init__(self):
        super().__init__('monitor_node')

        self.subscription = self.create_subscription(
            String,
            'robot_position',
            self.position_callback,
            10
        )

        self.get_logger().info('Robot monitor started')

    def position_callback(self, message):
        self.get_logger().info(
            f'Received: "{message.data}"'
        )


def main(args=None):
    rclpy.init(args=args)

    node = MonitorNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()