from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_gazebo = get_package_share_directory("msr_gazebo")
    world = os.path.join(pkg_gazebo, "worlds", "sorting_room.sdf")
    models_dir = os.path.join(pkg_gazebo, "models")

    return LaunchDescription([
        SetEnvironmentVariable(
            name="GZ_SIM_RESOURCE_PATH",
            value=models_dir
        ),

        ExecuteProcess(
            cmd=["gz", "sim", "-r", world],
            output="screen"
        )
    ])