import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from std_msgs.msg import String


class RobotNode(Node):

    def __init__(self):
        super().__init__('robot_node')

        # 发布机器人的当前位置
        self.position_publisher = self.create_publisher(
            String,
            'robot_position',
            10
        )

        # 接收目标位置
        self.goal_subscription = self.create_subscription(
            Int32,
            'robot_goal',
            self.goal_callback,
            10
        )

        # 每秒执行一次移动逻辑
        self.timer = self.create_timer(
            1.0,
            self.move_robot
        )

        self.x = 0
        self.goal_x = None

        self.get_logger().info('Warehouse robot started')
        self.get_logger().info('Waiting for a goal...')

    def goal_callback(self, message):
        self.goal_x = message.data

        self.get_logger().info(
            f'New goal received: x={self.goal_x}'
        )

    def move_robot(self):
        if self.goal_x is None:
            return

        if self.x < self.goal_x:
            self.x += 1

        elif self.x > self.goal_x:
            self.x -= 1

        message = String()
        message.data = f'Robot position: x={self.x}, y=0'

        self.position_publisher.publish(message)
        self.get_logger().info(message.data)

        if self.x == self.goal_x:
            self.get_logger().info(
                f'Goal reached: x={self.goal_x}'
            )

            self.goal_x = None


def main(args=None):
    rclpy.init(args=args)

    node = RobotNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()