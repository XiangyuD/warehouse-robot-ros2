import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String
from std_srvs.srv import Trigger

import time

from rclpy.action import ActionServer, CancelResponse
from warehouse_robot_interfaces.action import MoveRobot


class RobotNode(Node):

    def __init__(self):
        super().__init__("robot_node")


        self.status_service = self.create_service(
            Trigger,
            "get_robot_status",
            self.get_status_callback
        )
        
        # 发布当前位置
        self.position_publisher = self.create_publisher(
            String,
            "robot_position",
            10
        )

        # 发布机器人状态
        self.state_publisher = self.create_publisher(
            String,
            "robot_state",
            10
        )

        # 发布电量
        self.battery_publisher = self.create_publisher(
            Int32,
            "robot_battery",
            10
        )

        # 接收目标位置
        self.goal_subscription = self.create_subscription(
            Int32,
            "robot_goal",
            self.goal_callback,
            10
        )

        self.move_action_server = ActionServer(
            self,
            MoveRobot,
            "move_robot",
            self.execute_move_callback,
            cancel_callback=self.cancel_callback
        )

        # 每秒运行一次
        self.timer = self.create_timer(
            1.0,
            self.update_robot
        )

        self.x = 0
        self.goal_x = None
        self.battery = 100
        self.state = "IDLE"

        self.get_logger().info("Warehouse robot started")
        self.get_logger().info("Waiting for a goal...")

    def goal_callback(self, message):
        if self.state == "CHARGING":
            self.get_logger().warning(
                "Robot is charging and cannot accept a goal."
            )
            return

        self.goal_x = message.data

        if self.goal_x == self.x:
            self.state = "IDLE"
            self.goal_x = None

            self.get_logger().info(
                f"Robot is already at x={self.x}"
            )
            return

        self.state = "MOVING"

        self.get_logger().info(
            f"New goal received: x={message.data}"
        )

    def update_robot(self):
        if self.state == "MOVING":
            self.move_robot()

        elif self.state == "CHARGING":
            self.charge_robot()

        self.publish_status()

    def move_robot(self):
        if self.goal_x is None:
            self.state = "IDLE"
            return

        if self.x < self.goal_x:
            self.x += 1

        elif self.x > self.goal_x:
            self.x -= 1

        self.battery = max(self.battery - 5, 0)

        self.get_logger().info(
            f"Moving: x={self.x}, battery={self.battery}%"
        )

        if self.x == self.goal_x:
            self.get_logger().info(
                f"Goal reached: x={self.goal_x}"
            )

            self.goal_x = None
            self.state = "IDLE"

        if self.battery < 20:
            self.goal_x = None
            self.state = "CHARGING"

            self.get_logger().warning(
                "Battery is low. Robot entered CHARGING state."
            )

    def charge_robot(self):
        self.battery = min(self.battery + 10, 100)

        self.get_logger().info(
            f"Charging: battery={self.battery}%"
        )

        if self.battery >= 80:
            self.state = "IDLE"

            self.get_logger().info(
                "Charging complete. Robot is IDLE."
            )

    def publish_status(self):
        position_message = String()
        position_message.data = f"x={self.x}, y=0"
        self.position_publisher.publish(position_message)

        state_message = String()
        state_message.data = self.state
        self.state_publisher.publish(state_message)

        battery_message = Int32()
        battery_message.data = self.battery
        self.battery_publisher.publish(battery_message)


    def get_status_callback(self, request, response):
        response.success = True

        response.message = (
            f"Position: x={self.x}, y=0 | "
            f"State: {self.state} | "
            f"Battery: {self.battery}%"
        )

        self.get_logger().info(
            "Robot status requested"
        )

        return response


    def execute_move_callback(self, goal_handle):
        target_x = goal_handle.request.target_x

        self.get_logger().info(
            f"Action goal received: target_x={target_x}"
        )

        if self.state == "CHARGING":
            goal_handle.abort()

            result = MoveRobot.Result()
            result.success = False
            result.message = "Robot is charging"

            return result

        self.goal_x = target_x
        self.state = "MOVING"

        feedback = MoveRobot.Feedback()

        while self.x != target_x:

            if goal_handle.is_cancel_requested:
                self.state = "IDLE"
                self.goal_x = None

                goal_handle.canceled()

                result = MoveRobot.Result()
                result.success = False
                result.message = f"Movement canceled at x={self.x}"

                self.get_logger().info(result.message)

                return result

            if self.battery < 20:
                self.state = "CHARGING"
                self.goal_x = None

                goal_handle.abort()

                result = MoveRobot.Result()
                result.success = False
                result.message = "Battery too low"

                return result

            if self.x < target_x:
                self.x += 1
            else:
                self.x -= 1

            self.battery = max(
                self.battery - 5,
                0
            )

            feedback.current_x = self.x

            goal_handle.publish_feedback(
                feedback
            )

            self.publish_status()

            self.get_logger().info(
                f"Moving: x={self.x}, "
                f"battery={self.battery}%"
            )

            time.sleep(1)

        self.goal_x = None
        self.state = "IDLE"

        self.publish_status()

        goal_handle.succeed()

        result = MoveRobot.Result()
        result.success = True
        result.message = (
            f"Robot reached x={target_x}"
        )

        return result
    def cancel_callback(self, goal_handle):
        self.get_logger().info("Cancel request received")
        return CancelResponse.ACCEPT


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


if __name__ == "__main__":
    main()