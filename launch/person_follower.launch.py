from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    scan_follower = Node(
        package='person_follower',
        executable='person_follower',
        name='person_follower',
        output='screen'
    )

    yolo_follower = Node(
        package='person_follower',
        executable='person_follower_yolo',
        name='person_follower_yolo',
        output='screen'
    )

    supervisor = Node(
        package='person_follower',
        executable='cmd_vel_supervisor',
        name='cmd_vel_supervisor',
        output='screen'
    )

    return LaunchDescription([
        scan_follower,
        yolo_follower,
        supervisor,
    ])