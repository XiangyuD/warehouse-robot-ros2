import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from warehouse_robot_interfaces.action import MoveRobot


class MoveRobotClient(Node):

    def __init__(self):
        super().__init__("move_robot_client")

        self.client = ActionClient(
            self,
            MoveRobot,
            "move_robot"
        )

        self.goal_handle = None

    def send_goal(self, target_x):
        self.client.wait_for_server()

        goal_msg = MoveRobot.Goal()
        goal_msg.target_x = target_x

        self.get_logger().info(
            f"Sending goal: target_x={target_x}"
        )

        send_goal_future = self.client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        send_goal_future.add_done_callback(
            self.goal_response_callback
        )

    def goal_response_callback(self, future):
        self.goal_handle = future.result()

        if not self.goal_handle.accepted:
            self.get_logger().info("Goal rejected")
            return

        self.get_logger().info("Goal accepted")

        # 5 秒后取消
        self.cancel_timer = self.create_timer(
            5.0,
            self.cancel_goal
        )

        result_future = self.goal_handle.get_result_async()

        result_future.add_done_callback(
            self.result_callback
        )

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback

        self.get_logger().info(
            f"Current x: {feedback.current_x}"
        )

    def cancel_goal(self):
        if self.goal_handle is None:
            return

        self.get_logger().info(
            "Sending cancel request..."
        )

        cancel_future = self.goal_handle.cancel_goal_async()

        cancel_future.add_done_callback(
            self.cancel_done_callback
        )

        # 防止 timer 每 5 秒继续取消
        self.cancel_timer.cancel()

    def cancel_done_callback(self, future):
        response = future.result()

        if len(response.goals_canceling) > 0:
            self.get_logger().info(
                "Cancel request accepted"
            )
        else:
            self.get_logger().info(
                "Cancel request rejected"
            )

    def result_callback(self, future):
        result = future.result().result

        self.get_logger().info(
            f"Result: {result.message}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = MoveRobotClient()

    node.send_goal(100)

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()