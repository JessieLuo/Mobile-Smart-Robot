import math
import time
import threading
from typing import List, Optional

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32MultiArray
from tf2_ros import TransformBroadcaster

try:
    import serial
except ImportError:
    serial = None


class C30DBaseDriver(Node):
    def __init__(self):
        super().__init__('c30d_base_driver')

        # Declaration
        self.declare_parameter('cmd_topic', '/cmd_vel_safe')
        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('dry_run', True)

        self.declare_parameter('wheel_radius_m', 0.04)
        self.declare_parameter('half_length_m', 0.125)
        self.declare_parameter('half_width_m', 0.075)
        self.declare_parameter('max_rpm', 80.0)

        self.declare_parameter('command_prefix', 'M')
        self.declare_parameter('timeout_sec', 0.5)

        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('publish_tf', True)
        self.declare_parameter('odom_publish_hz', 20.0)

        self.declare_parameter('rpm_compensation', [1.0, 1.0, 1.0, 1.0])

        # Loader
        self.cmd_topic = self.get_parameter('cmd_topic').value
        self.serial_port = self.get_parameter('serial_port').value
        self.baudrate = int(self.get_parameter('baudrate').value)
        self.dry_run = bool(self.get_parameter('dry_run').value)

        self.wheel_radius_m = float(self.get_parameter('wheel_radius_m').value)
        self.half_length_m = float(self.get_parameter('half_length_m').value)
        self.half_width_m = float(self.get_parameter('half_width_m').value)
        self.max_rpm = float(self.get_parameter('max_rpm').value)

        self.command_prefix = str(self.get_parameter('command_prefix').value)
        self.timeout_sec = float(self.get_parameter('timeout_sec').value)

        self.odom_frame = str(self.get_parameter('odom_frame').value)
        self.base_frame = str(self.get_parameter('base_frame').value)
        self.publish_tf = bool(self.get_parameter('publish_tf').value)
        self.odom_publish_hz = float(self.get_parameter('odom_publish_hz').value)

        self.ser: Optional[object] = None
        self.last_cmd_time = self.get_clock().now()
        self.last_odom_time = self.get_clock().now()

        self.target_rpm = [0.0, 0.0, 0.0, 0.0]
        self.wheel_rpm = [0.0, 0.0, 0.0, 0.0]

        self.filtered_wheel_rpm = [0.0, 0.0, 0.0, 0.0]
        self.rpm_filter_alpha = 0.3

        self.rpm_compensation = list(self.get_parameter('rpm_compensation').value)

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.vx = 0.0
        self.vy = 0.0
        self.wz = 0.0

        self.target_rpm_pub = self.create_publisher(Float32MultiArray, '/target_rpm', 10)
        self.wheel_rpm_pub = self.create_publisher(Float32MultiArray, '/wheel_rpm', 10)
        self.imu_pub = self.create_publisher(Imu, '/imu/data', 10)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        if not self.dry_run:
            if serial is None:
                raise RuntimeError('pyserial is not installed')

            self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=0.05)
            time.sleep(0.5)

            self.serial_thread = threading.Thread(
                target=self.serial_read_loop,
                daemon=True
            )
            self.serial_thread.start()

        self.sub = self.create_subscription(Twist, self.cmd_topic, self.on_cmd, 10)
        self.cmd_timer = self.create_timer(0.05, self.on_cmd_timer)
        self.odom_timer = self.create_timer(1.0 / self.odom_publish_hz, self.on_odom_timer)

        mode = 'DRY_RUN' if self.dry_run else f'SERIAL {self.serial_port}'
        self.get_logger().info(f'c30d_base_driver started: {mode}, topic={self.cmd_topic}')
        self.send_stop()


    def clamp(self, value: float, limit: float) -> float:
        if value > limit:
            return limit
        if value < -limit:
            return -limit
        return value

    def twist_to_rpm(self, msg: Twist) -> List[int]:
        vx = msg.linear.x
        vy = -msg.linear.y
        wz = msg.angular.z

        r = self.wheel_radius_m
        k = self.half_length_m + self.half_width_m

        forward = vx / r
        strafe = vy / r
        rotate = k * wz / r

        wheel_rad_s = [
            forward + strafe - rotate,   # A = left_front
            forward - strafe + rotate,   # B = right_front
            -forward - strafe - rotate,  # C = right_rear
            -forward + strafe + rotate,  # D = left_rear
        ]

        rpm = [w * 60.0 / (2.0 * math.pi) for w in wheel_rad_s]
        return [int(round(self.clamp(v, self.max_rpm))) for v in rpm]

    def rpm_to_body_twist(self):
        a = self.wheel_rpm[0] * 2.0 * math.pi / 60.0
        b = self.wheel_rpm[1] * 2.0 * math.pi / 60.0
        c = self.wheel_rpm[2] * 2.0 * math.pi / 60.0
        d = self.wheel_rpm[3] * 2.0 * math.pi / 60.0

        r = self.wheel_radius_m
        k = self.half_length_m + self.half_width_m

        vx = r * (a + b - c - d) / 4.0
        vy = -r * (a - b - c + d) / 4.0
        wz = r * (-a + b - c + d) / (4.0 * k)

        return vx, vy, wz

    def build_command(self, rpm: List[int]) -> str:
        return f'{self.command_prefix},{rpm[0]},{rpm[1]},{rpm[2]},{rpm[3]}\n'

    def write_command(self, command: str):
        if self.dry_run:
            return

        if self.ser is not None:
            self.ser.write(command.encode('utf-8'))
            self.ser.flush()

    def send_stop(self):
        self.target_rpm = [0.0, 0.0, 0.0, 0.0]
        self.write_command(self.build_command([0, 0, 0, 0]))

    def on_cmd(self, msg: Twist):
        rpm = self.twist_to_rpm(msg)

        rpm = [
            int(round(rpm[i] * self.rpm_compensation[i]))
            for i in range(4)
        ]
        self.target_rpm = [float(rpm[0]), float(rpm[1]), float(rpm[2]), float(rpm[3])]

        target_msg = Float32MultiArray()
        target_msg.data = self.target_rpm
        self.target_rpm_pub.publish(target_msg)

        self.write_command(self.build_command(rpm))
        self.last_cmd_time = self.get_clock().now()

    def on_cmd_timer(self):
        dt = (self.get_clock().now() - self.last_cmd_time).nanoseconds / 1e9
        if dt > self.timeout_sec:
            self.send_stop()

    def handle_encoder(self, line):
        parts = line.split(',')

        if len(parts) != 5:
            return

        raw_rpm = [
            float(parts[1]),
            float(parts[2]),
            float(parts[3]),
            float(parts[4]),
        ]

        for i in range(4):
            self.filtered_wheel_rpm[i] = (
                self.rpm_filter_alpha * raw_rpm[i]
                + (1.0 - self.rpm_filter_alpha)
                * self.filtered_wheel_rpm[i]
            )

        self.wheel_rpm = self.filtered_wheel_rpm[:]

        msg = Float32MultiArray()
        msg.data = self.wheel_rpm

        self.wheel_rpm_pub.publish(msg)
    
    def handle_imu(self, line):
        parts = line.split(',')

        if len(parts) != 7:
            return

        ax = float(parts[1]) / 1000.0
        ay = float(parts[2]) / 1000.0
        az = float(parts[3]) / 1000.0

        gx = float(parts[4]) / 1000.0
        gy = float(parts[5]) / 1000.0
        gz = float(parts[6]) / 1000.0

        msg = Imu()

        msg.header.stamp = (
            self.get_clock()
            .now()
            .to_msg()
        )

        msg.header.frame_id = 'base_link'

        msg.linear_acceleration.x = ax
        msg.linear_acceleration.y = ay
        msg.linear_acceleration.z = az

        msg.angular_velocity.x = gx
        msg.angular_velocity.y = gy
        msg.angular_velocity.z = gz

        self.imu_pub.publish(msg)
    
    def serial_read_loop(self):
        while rclpy.ok():
            try:
                if self.ser is None:
                    continue

                line = self.ser.readline().decode(errors='ignore').strip()

                if line.startswith('E,'):
                    self.handle_encoder(line)

                elif line.startswith('I,'):
                    self.handle_imu(line)

                parts = line.split(',')
                if len(parts) != 5:
                    continue

                raw_rpm = [
                    float(parts[1]),
                    float(parts[2]),
                    float(parts[3]),
                    float(parts[4]),
                ]

                for i in range(4):
                    self.filtered_wheel_rpm[i] = (
                        self.rpm_filter_alpha * raw_rpm[i]
                        + (1.0 - self.rpm_filter_alpha) * self.filtered_wheel_rpm[i]
                    )

                self.wheel_rpm = self.filtered_wheel_rpm[:]

                msg = Float32MultiArray()
                msg.data = self.wheel_rpm
                self.wheel_rpm_pub.publish(msg)

            except Exception:
                pass

    def on_odom_timer(self):
        now = self.get_clock().now()
        dt = (now - self.last_odom_time).nanoseconds / 1e9
        self.last_odom_time = now

        self.vx, self.vy, self.wz = self.rpm_to_body_twist()

        cos_yaw = math.cos(self.yaw)
        sin_yaw = math.sin(self.yaw)

        self.x += (self.vx * cos_yaw - self.vy * sin_yaw) * dt
        self.y += (self.vx * sin_yaw + self.vy * cos_yaw) * dt
        self.yaw += self.wz * dt
        self.yaw = math.atan2(math.sin(self.yaw), math.cos(self.yaw))

        self.publish_odom(now)

    def publish_odom(self, stamp):
        qz = math.sin(self.yaw * 0.5)
        qw = math.cos(self.yaw * 0.5)

        odom = Odometry()
        odom.header.stamp = stamp.to_msg()
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame

        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw

        odom.twist.twist.linear.x = self.vx
        odom.twist.twist.linear.y = self.vy
        odom.twist.twist.angular.z = self.wz

        self.odom_pub.publish(odom)

        if self.publish_tf:
            tf = TransformStamped()
            tf.header.stamp = stamp.to_msg()
            tf.header.frame_id = self.odom_frame
            tf.child_frame_id = self.base_frame
            tf.transform.translation.x = self.x
            tf.transform.translation.y = self.y
            tf.transform.translation.z = 0.0
            tf.transform.rotation.z = qz
            tf.transform.rotation.w = qw
            self.tf_broadcaster.sendTransform(tf)

    def destroy_node(self):
        self.send_stop()
        if self.ser is not None:
            self.ser.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = C30DBaseDriver()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()