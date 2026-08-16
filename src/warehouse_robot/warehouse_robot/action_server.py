import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from example_interfaces.action import Fibonacci


class RobotActionServer(Node):

    def __init__(self):
        super().__init__("robot_action_server")

        self.action_server = ActionServer(
            self,
            Fibonacci,
            "move_robot",
            self.execute_callback
        )

        self.get_logger().info(
            "Robot action server started"
        )

    def execute_callback(self, goal_handle):

        self.get_logger().info(
            "Received new robot goal"
        )

        feedback_msg = Fibonacci.Feedback()

        sequence = [0, 1]

        for i in range(
            1,
            goal_handle.request.order
        ):
            sequence.append(
                sequence[i] + sequence[i - 1]
            )

            feedback_msg.sequence = sequence.copy()

            goal_handle.publish_feedback(
                feedback_msg
            )

        goal_handle.succeed()

        result = Fibonacci.Result()
        result.sequence = sequence

        return result


def main(args=None):

    rclpy.init(args=args)

    node = RobotActionServer()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()