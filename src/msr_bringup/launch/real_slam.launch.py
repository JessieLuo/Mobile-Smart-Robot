import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    nav_base_dir = get_package_share_directory('nav_base')

    real_base_config = os.path.join(
        nav_base_dir,
        'config',
        'real_base.yaml'
    )

    slam_config = os.path.join(
        nav_base_dir,
        'config',
        'slam_toolbox.yaml'
    )

    slam_toolbox_dir = get_package_share_directory('slam_toolbox')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    slam_toolbox_dir,
                    'launch',
                    'online_async_launch.py'
                )
            ),
            launch_arguments={
                'slam_params_file': slam_config,
                'use_sim_time': 'false',
            }.items()
        ),
    ])
