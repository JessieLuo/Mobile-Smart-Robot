import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")

    msr_navigation_dir = get_package_share_directory("msr_navigation")

    slam_launch = os.path.join(
        msr_navigation_dir,
        "launch",
        "slam.launch.py",
    )

    nav2_launch = os.path.join(
        msr_navigation_dir,
        "launch",
        "nav2.launch.py",
    )

    waypoints_file = os.path.join(
        msr_navigation_dir,
        "config",
        "semantic_waypoints.yaml",
    )

    semantic_nav_server = Node(
        package="msr_navigation",
        executable="semantic_nav_server",
        name="semantic_nav_server",
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time},
            {"waypoints_file": waypoints_file},
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(slam_launch),
            launch_arguments={
                "use_sim_time": use_sim_time,
            }.items(),
        ),

        TimerAction(
            period=2.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(nav2_launch),
                    launch_arguments={
                        "use_sim_time": use_sim_time,
                    }.items(),
                ),
            ],
        ),

        TimerAction(
            period=5.0,
            actions=[semantic_nav_server],
        ),
    ])