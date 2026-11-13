import os  # Build file paths.

from ament_index_python.packages import get_package_share_directory  # Find the installed package.
from launch import LaunchDescription  # Store the nodes to start.
from launch.substitutions import Command  # Run xacro and read its output.
from launch_ros.actions import Node  # Describe a ROS 2 node.
from launch_ros.parameter_descriptions import ParameterValue  # Treat XML as a string.


def generate_launch_description():  # ROS 2 calls this function.
    package_path = get_package_share_directory('my_best_model')
    model_path = os.path.join(package_path, 'urdf', 'robot_model.xacro')
    rviz_path = os.path.join(package_path, 'config', 'rviz.rviz')

    # Convert Xacro to URDF XML for the robot_description parameter.
    robot_description = ParameterValue(
        Command(['xacro ', model_path]), value_type=str
    )

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen',
        ),  # Calculate link transforms using the model and joint positions.
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen',
        ),  # Publish joint positions chosen with sliders.
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_path],
            output='screen',
        ),  # Display the model and TF using our saved configuration.
    ])
