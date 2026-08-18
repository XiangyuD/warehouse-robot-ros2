import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from warehouse_robot_interfaces.action import MoveRobot


class MoveRobotActionServer(Node):

    def __init__(self):
        super().__init__("move_robot_action_server")

        self.current_x = 0

        self.action_server = ActionServer(
            self,
            MoveRobot,
            "move_robot",
            self.execute_callback
        )

        self.get_logger().info(
            "MoveRobot action server started"
        )

    def execute_callback(self, goal_handle):
        target_x = goal_handle.request.target_x

        self.get_logger().info(
            f"Received goal: target_x={target_x}"
        )

        feedback = MoveRobot.Feedback()

        while self.current_x != target_x:

            if self.current_x < target_x:
                self.current_x += 1
            else:
                self.current_x -= 1

            feedback.current_x = self.current_x

            goal_handle.publish_feedback(feedback)

            self.get_logger().info(
                f"Moving... current_x={self.current_x}"
            )

            time.sleep(1)

        goal_handle.succeed()

        result = MoveRobot.Result()
        result.success = True
        result.message = (
            f"Robot reached target x={target_x}"
        )

        self.get_logger().info(
            result.message
        )

        return result


def main(args=None):
    rclpy.init(args=args)

    node = MoveRobotActionServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()