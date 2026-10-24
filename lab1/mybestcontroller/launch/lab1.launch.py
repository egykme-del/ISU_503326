"""Launch-file backbone for laboratory work 1."""

from launch import LaunchDescription
from launch_ros.actions import Node

ISUID = '503326'


def generate_launch_description():
    """Return the launch description completed by the student."""
    actions = []
    for index in (1, 2):
        namespace = 'ns' + str(index) + '_' + ISUID
        actions.append(Node(
            package='turtlesim',
            executable='turtlesim_node',
            namespace=namespace,
            name='turtlesim',
            output='screen',
        ))
        actions.append(Node(
            package='mybestcontroller',
            executable='lab1_controller',
            namespace=namespace,
            name='lab1_controller',
            output='screen',
        ))
    return LaunchDescription(actions)
