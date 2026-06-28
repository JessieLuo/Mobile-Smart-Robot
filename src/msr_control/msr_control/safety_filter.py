import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


def clamp(value: float, limit: float) -> float:
    if value > limit:
        return limit
    if value < -limit:
        return -limit
    return value


class SafetyFilter(Node):
    def __init__(self):
        super().__init__('safety_filter')

        self.declare_parameter('input_topic', '/cmd_vel')
        self.declare_parameter('output_topic', '/cmd_vel_safe')
        self.declare_parameter('max_vx', 0.15)
        self.declare_parameter('max_vy', 0.12)
        self.declare_parameter('max_wz', 0.5)
        self.declare_parameter('timeout_sec', 0.5)

        self.input_topic = self.get_parameter('input_topic').value
        self.output_topic = self.get_parameter('output_topic').value
        self.max_vx = float(self.get_parameter('max_vx').value)
        self.max_vy = float(self.get_parameter('max_vy').value)
        self.max_wz = float(self.get_parameter('max_wz').value)
        self.timeout_sec = float(self.get_parameter('timeout_sec').value)

        self.last_cmd_time = self.get_clock().now()
        self.last_safe_cmd = Twist()

        self.pub = self.create_publisher(Twist, self.output_topic, 10)
        self.sub = self.create_subscription(Twist, self.input_topic, self.on_cmd, 10)
        self.timer = self.create_timer(0.05, self.on_timer)

        self.get_logger().info(f'safety_filter: {self.input_topic} -> {self.output_topic}')

    def on_cmd(self, msg: Twist):
        safe = Twist()
        safe.linear.x = clamp(msg.linear.x, self.max_vx)
        safe.linear.y = clamp(msg.linear.y, self.max_vy)
        safe.angular.z = clamp(msg.angular.z, self.max_wz)

        self.last_safe_cmd = safe
        self.last_cmd_time = self.get_clock().now()
        self.pub.publish(safe)

    def on_timer(self):
        dt = (self.get_clock().now() - self.last_cmd_time).nanoseconds / 1e9
        if dt > self.timeout_sec:
            stop = Twist()
            self.pub.publish(stop)


def main():
    rclpy.init()
    node = SafetyFilter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
