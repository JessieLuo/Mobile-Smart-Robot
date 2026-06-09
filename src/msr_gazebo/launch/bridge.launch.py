from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_gazebo = get_package_share_directory("msr_gazebo")
    bridge_config = os.path.join(pkg_gazebo, "config", "ros_gz_bridge.yaml")

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="ros_gz_bridge",
        output="screen",
        parameters=[{
            "config_file": bridge_config,
            "qos_overrides./scan.publisher.reliability": "best_effort",
            "qos_overrides./camera/image.publisher.reliability": "best_effort",
            "qos_overrides./imu.publisher.reliability": "best_effort",
        }]
    )

    return LaunchDescription([bridge])