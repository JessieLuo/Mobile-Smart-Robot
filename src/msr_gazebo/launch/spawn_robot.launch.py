from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description():
    return LaunchDescription([
        LogInfo(
            msg="Day 1: robot is embedded directly in sorting_room.sdf. No extra spawn is required."
        )
    ])