import math
import os
from typing import Dict, Any, Optional

import yaml
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from ament_index_python.packages import get_package_share_directory

from msr_interfaces.srv import NavigateToSemantic


def yaw_to_quaternion(yaw: float):
    qz = math.sin(yaw * 0.5)
    qw = math.cos(yaw * 0.5)
    return qz, qw


class SemanticNavServer(Node):
    def __init__(self):
        super().__init__("semantic_nav_server")

        default_config = os.path.join(
            get_package_share_directory("msr_navigation"),
            "config",
            "semantic_waypoints.yaml",
        )

        self.declare_parameter("waypoints_file", default_config)
        self.declare_parameter("nav2_action_name", "navigate_to_pose")
        self.declare_parameter("goal_timeout_sec", 120.0)

        self.waypoints_file = self.get_parameter("waypoints_file").value
        self.nav2_action_name = self.get_parameter("nav2_action_name").value
        self.goal_timeout_sec = float(self.get_parameter("goal_timeout_sec").value)

        self.frame_id = "odom"
        self.points: Dict[str, Dict[str, float]] = {}

        self._load_waypoints()

        self.nav_client = ActionClient(self, NavigateToPose, self.nav2_action_name)

        self.server = self.create_service(
            NavigateToSemantic,
            "navigate_to_semantic",
            self.handle_navigate_to_semantic,
        )

        self.get_logger().info("semantic_nav_server ready")
        self.get_logger().info(f"Loaded waypoints: {list(self.points.keys())}")

    def _load_waypoints(self):
        if not os.path.exists(self.waypoints_file):
            raise FileNotFoundError(f"Waypoint file not found: {self.waypoints_file}")

        with open(self.waypoints_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        root = data.get("semantic_waypoints", {})
        self.frame_id = root.get("frame_id", "odom")
        self.points = root.get("points", {})

        if not self.points:
            raise RuntimeError("No semantic waypoints found")

    def handle_navigate_to_semantic(self, request, response):
        target_name = request.target_name.strip()

        if target_name not in self.points:
            response.success = False
            response.message = f"Unknown semantic target: {target_name}"
            self.get_logger().warn(response.message)
            return response

        point = self.points[target_name]
        x = float(point["x"])
        y = float(point["y"])
        yaw = float(point.get("yaw", 0.0))

        self.get_logger().info(
            f"Navigate request: target={target_name}, x={x:.2f}, y={y:.2f}, yaw={yaw:.2f}"
        )

        ok = self._send_nav2_goal(self.frame_id, x, y, yaw)

        response.success = ok
        response.message = "Navigation succeeded" if ok else "Navigation failed"
        return response

    def _send_nav2_goal(self, frame_id: str, x: float, y: float, yaw: float) -> bool:
        if not self.nav_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error("Nav2 action server not available")
            return False

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self._make_pose(frame_id, x, y, yaw)

        send_future = self.nav_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_future)

        goal_handle = send_future.result()
        if goal_handle is None:
            self.get_logger().error("Failed to send Nav2 goal")
            return False

        if not goal_handle.accepted:
            self.get_logger().warn("Nav2 goal rejected")
            return False

        self.get_logger().info("Nav2 goal accepted")

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=self.goal_timeout_sec)

        if not result_future.done():
            self.get_logger().error("Nav2 goal timeout")
            try:
                cancel_future = goal_handle.cancel_goal_async()
                rclpy.spin_until_future_complete(self, cancel_future, timeout_sec=3.0)
            except Exception as exc:
                self.get_logger().warn(f"Cancel failed: {exc}")
            return False

        result = result_future.result()
        if result is None:
            self.get_logger().error("No result from Nav2")
            return False

        status = result.status
        self.get_logger().info(f"Nav2 result status={status}")

        return status == 4

    def _make_pose(self, frame_id: str, x: float, y: float, yaw: float) -> PoseStamped:
        pose = PoseStamped()
        pose.header.frame_id = frame_id
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0

        qz, qw = yaw_to_quaternion(yaw)
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        return pose


def main():
    rclpy.init()
    node = SemanticNavServer()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()