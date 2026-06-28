import os

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_dir = get_package_share_directory('nav_base')

    map_file = os.path.join(pkg_dir, 'config', 'map.yaml')
    amcl_file = os.path.join(pkg_dir, 'config', 'amcl.yaml')

    return LaunchDescription([

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'yaml_filename': map_file,
            }],
        ),

        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[amcl_file],
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_laser_tf',
            output='screen',
            arguments=[
                '0.0', '0.0', '0.12',
                '0.0', '0.0', '0.0',
                'base_link',
                'laser_frame'
            ],
        ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'autostart': True,
                'node_names': [
                    'map_server',
                    'amcl',
                ],
            }],
        ),
    ])
