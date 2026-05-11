#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist


class CmdVelSupervisor(Node):
    def __init__(self):
        super().__init__("cmd_vel_supervisor")

        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)

        self.sub_yolo = self.create_subscription(
            Twist,
            "/cmd_vel_yolo",
            self.cb_yolo,
            10
        )

        self.sub_scan = self.create_subscription(
            Twist,
            "/cmd_vel_scan",
            self.cb_scan,
            10
        )

        self.cmd_yolo = Twist()
        self.cmd_scan = Twist()

        self.last_yolo_time = None
        self.last_scan_time = None

        # tiempos en segundos
        self.yolo_timeout = 0.4
        self.scan_backup_time = 1.5

        self.timer = self.create_timer(0.05, self.control_loop)

    def cb_yolo(self, msg):
        self.cmd_yolo = msg
        self.last_yolo_time = self.get_clock().now()

    def cb_scan(self, msg):
        self.cmd_scan = msg
        self.last_scan_time = self.get_clock().now()

    def control_loop(self):
        now = self.get_clock().now()
        cmd = Twist()

        yolo_age = 999.0
        scan_age = 999.0

        if self.last_yolo_time is not None:
            yolo_age = (now - self.last_yolo_time).nanoseconds / 1e9

        if self.last_scan_time is not None:
            scan_age = (now - self.last_scan_time).nanoseconds / 1e9

        yolo_active = yolo_age < self.yolo_timeout
        yolo_recent = yolo_age < self.scan_backup_time
        scan_active = scan_age < self.yolo_timeout

        if yolo_active:
            # Prioridad principal: YOLO
            cmd = self.cmd_yolo

        elif yolo_recent and scan_active:
            # YOLO se acaba de perder: dejamos que scan ayude un momento
            cmd = self.cmd_scan

        else:
            # Persona perdida demasiado tiempo: parar
            cmd = Twist()

        self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelSupervisor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()