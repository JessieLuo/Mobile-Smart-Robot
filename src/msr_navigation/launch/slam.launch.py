import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    use_sim_time = LaunchConfiguration("use_sim_time")
    slam_params_file = LaunchConfiguration("slam_params_file")

    msr_navigation_dir = get_package_share_directory("msr_navigation")

    default_sim_params = os.path.join(
        msr_navigation_dir,
        "config",
        "mapper_params_online_async.yaml",
    )

    slam_toolbox_dir = get_package_share_directory("slam_toolbox")

    return LaunchDescription([

        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
        ),

        DeclareLaunchArgument(
            "slam_params_file",
            default_value=default_sim_params,
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    slam_toolbox_dir,
                    "launch",
                    "online_async_launch.py",
                )
            ),
            launch_arguments={
                "slam_params_file": slam_params_file,
                "use_sim_time": use_sim_time,
            }.items(),
        ),

    ])