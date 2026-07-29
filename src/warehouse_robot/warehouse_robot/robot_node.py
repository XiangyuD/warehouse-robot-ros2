import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class RobotNode(Node):

    def __init__(self):
        super().__init__('robot_node')

        self.publisher_ = self.create_publisher(
            String,
            'robot_position',
            10
        )

        self.x = 0

        self.timer = self.create_timer(
            1.0,
            self.publish_position
        )

        self.get_logger().info('Warehouse robot started')

    def publish_position(self):
        message = String()

        message.data = f'Robot position: x={self.x}, y=0'

        self.publisher_.publish(message)

        self.get_logger().info(
            f'Publishing: "{message.data}"'
        )

        self.x += 1


def main(args=None):
    rclpy.init(args=args)

    node = RobotNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()