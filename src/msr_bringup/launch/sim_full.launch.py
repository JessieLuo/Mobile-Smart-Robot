from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_gazebo = get_package_share_directory("msr_gazebo")
    pkg_description = get_package_share_directory("msr_description")

    sim_launch = os.path.join(pkg_gazebo, "launch", "sim.launch.py")
    bridge_launch = os.path.join(pkg_gazebo, "launch", "bridge.launch.py")

    xacro_file = os.path.join(
        pkg_description,
        "urdf",
        "msr_robot.urdf.xacro",
    )

    rviz_config = os.path.join(
        pkg_description,
        "rviz",
        "robot_view.rviz",
    )

    from launch_ros.parameter_descriptions import ParameterValue
    robot_description = ParameterValue(
        Command([
            "xacro ",
            xacro_file,
            " use_sim:=true"
        ]),
        value_type=str,
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": True,
            }
        ]
    )

    # Gazebo LaserScan frame_id is:
    #   mobile_sorting_robot/lidar_link/gpu_lidar
    # robot_state_publisher publishes:
    #   base_link -> lidar_link
    # This static TF connects the Gazebo sensor frame to the ROS TF tree.
    lidar_sensor_static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="lidar_sensor_static_tf",
        output="screen",
        arguments=[
            "--x", "0",
            "--y", "0",
            "--z", "0",
            "--roll", "0",
            "--pitch", "0",
            "--yaw", "0",
            "--frame-id", "lidar_link",
            "--child-frame-id", "mobile_sorting_robot/lidar_link/gpu_lidar",
        ],
        parameters=[{"use_sim_time": True}],
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config],
        parameters=[{"use_sim_time": True}],
    )

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sim_launch),
        ),

        TimerAction(
            period=1.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(bridge_launch),
                ),
            ],
        ),

        TimerAction(
            period=1.5,
            actions=[
                robot_state_publisher,
                lidar_sensor_static_tf,
            ],
        ),

        TimerAction(
            period=2.0,
            actions=[rviz],
        ),
    ])
