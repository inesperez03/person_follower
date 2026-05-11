#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from yolo_msgs.msg import DetectionArray


class FollowID1(Node):
    def __init__(self):
        super().__init__("follow_id_1")

        self.pub = self.create_publisher(Twist, "/cmd_vel_yolo", 10)

        self.sub = self.create_subscription(
            DetectionArray,
            "/yolo/detections_3d",
            self.cb,
            10
        )

        self.target_distance = 0.85
        self.k_v = 0.3
        self.k_w = 0.5

    def cb(self, msg):
        cmd = Twist()

        for det in msg.detections:
            if det.id == '541':
                print("a")
                x = det.bbox3d.center.position.x
                y = det.bbox3d.center.position.y
                print(x,y)

                cmd.linear.x = self.k_v * (x - self.target_distance)
                cmd.angular.z = self.k_w * y
                print("cmd.linear.x", cmd.linear.x)
                print("cmd_angular.z", cmd.angular.z)
                self.pub.publish(cmd)
                print("publicado")
                return

        # Si no ve el ID 1, se para
        self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = FollowID1()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()