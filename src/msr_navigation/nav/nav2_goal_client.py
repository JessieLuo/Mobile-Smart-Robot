import math
from typing import Tuple

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose


def yaw_to_quaternion(yaw: float):
    qz = math.sin(yaw * 0.5)
    qw = math.cos(yaw * 0.5)
    return qz, qw


class Nav2GoalClient(Node):
    def __init__(self):
        super().__init__("nav2_goal_client")
        self._client = ActionClient(self, NavigateToPose, "navigate_to_pose")

    def send_goal(self, frame_id: str, x: float, y: float, yaw: float) -> bool:
        if not self._client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Nav2 action server /navigate_to_pose not available")
            return False

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self._make_pose(frame_id, x, y, yaw)

        self.get_logger().info(
            f"Sending Nav2 goal: frame={frame_id}, x={x:.2f}, y={y:.2f}, yaw={yaw:.2f}"
        )

        send_future = self._client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_future)

        goal_handle = send_future.result()
        if goal_handle is None:
            self.get_logger().error("Failed to send goal")
            return False

        if not goal_handle.accepted:
            self.get_logger().warn("Goal rejected by Nav2")
            return False

        self.get_logger().info("Goal accepted")

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result()
        if result is None:
            self.get_logger().error("No result from Nav2")
            return False

        status = result.status
        self.get_logger().info(f"Nav2 finished with status={status}")

        return status == 4

    def _make_pose(self, frame_id: str, x: float, y: float, yaw: float) -> PoseStamped:
        pose = PoseStamped()
        pose.header.frame_id = frame_id
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.position.z = 0.0

        qz, qw = yaw_to_quaternion(float(yaw))
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        return pose


def main():
    rclpy.init()
    node = Nav2GoalClient()

    node.declare_parameter("frame_id", "odom")
    node.declare_parameter("x", 1.0)
    node.declare_parameter("y", 0.0)
    node.declare_parameter("yaw", 0.0)

    frame_id = node.get_parameter("frame_id").value
    x = node.get_parameter("x").value
    y = node.get_parameter("y").value
    yaw = node.get_parameter("yaw").value

    ok = node.send_goal(frame_id, x, y, yaw)

    node.get_logger().info(f"Goal result: {ok}")
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()