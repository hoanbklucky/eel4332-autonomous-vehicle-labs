"""Launch the EEL 4332 counter publisher and subscriber."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    rate_hz = LaunchConfiguration("rate_hz")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "rate_hz",
                default_value="2.0",
                description="Counter publication rate in hertz.",
            ),
            Node(
                package="eel4332_ros_practice",
                executable="counter_publisher",
                parameters=[{"rate_hz": ParameterValue(rate_hz, value_type=float)}],
                output="screen",
            ),
            Node(
                package="eel4332_ros_practice",
                executable="counter_subscriber",
                output="screen",
            ),
        ]
    )
