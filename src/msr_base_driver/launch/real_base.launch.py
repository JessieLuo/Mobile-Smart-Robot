from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_dir = get_package_share_directory('nav_base')
    config = os.path.join(pkg_dir, 'config', 'real_base.yaml')

    return LaunchDescription([
        Node(
            package='msr_control',
            executable='safety_filter',
            name='safety_filter',
            output='screen',
            parameters=[config],
        ),
        Node(
            package='nav_base',
            executable='c30d_base_driver',
            name='c30d_base_driver',
            output='screen',
            parameters=[config],
        ),
    ])
