import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger


class StatusClient(Node):

    def __init__(self):
        super().__init__("status_client")

        self.client = self.create_client(
            Trigger,
            "get_robot_status"
        )

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(
                "Waiting for get_robot_status service..."
            )

        self.request = Trigger.Request()

    def send_request(self):
        future = self.client.call_async(self.request)

        rclpy.spin_until_future_complete(self, future)

        return future.result()


def main(args=None):
    rclpy.init(args=args)

    node = StatusClient()

    response = node.send_request()

    if response is not None:
        node.get_logger().info(
            f"Robot status: {response.message}"
        )

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()