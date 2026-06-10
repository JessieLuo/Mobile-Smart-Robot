from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

from pathlib import Path


def generate_launch_description():
    pkg_share = Path(get_package_share_directory("msr_gazebo"))
    bridge_config = pkg_share / "config" / "ros_gz_bridge.yaml"

    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="msr_ros_gz_bridge",
        output="screen",
        parameters=[
            {
                "config_file": str(bridge_config),
            }
        ],
    )

    return LaunchDescription([
        ros_gz_bridge,
    ])