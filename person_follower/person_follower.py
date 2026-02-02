import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import math


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


class PersonFollower(Node):
    def __init__(self):
        super().__init__('person_follower')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.debug_scan_pub = self.create_publisher(LaserScan, '/scan_front', 10)
        self.sub = self.create_subscription(LaserScan, '/scan', self.listener_callback, 10)
        self.dist_obj = 0.9 
        self.stop_dist = 0.35
        self.k_ang = 2.5
        self.k_lin = 0.6 

        self.max_v = 0.22
        self.max_w = 1.0

    def listener_callback(self, input_msg: LaserScan):
        ranges = list(input_msg.ranges)
        n = len(ranges)

        i0 = 165
        i1 = 195

        # Debug scan 
        debug_msg = LaserScan()
        debug_msg.header = input_msg.header
        debug_msg.angle_min = input_msg.angle_min
        debug_msg.angle_max = input_msg.angle_max
        debug_msg.angle_increment = input_msg.angle_increment
        debug_msg.time_increment = input_msg.time_increment
        debug_msg.scan_time = input_msg.scan_time
        debug_msg.range_min = input_msg.range_min
        debug_msg.range_max = input_msg.range_max

        debug_ranges = [float('inf')] * n
        for i in range(i0, i1):
            debug_ranges[i] = ranges[i]
        debug_msg.ranges = debug_ranges
        self.debug_scan_pub.publish(debug_msg)

        best_r = None
        best_i = None
        for i in range(i0, i1):
            r = ranges[i]
            if r is None or (not math.isfinite(r)):
                continue
            if r < input_msg.range_min or r > input_msg.range_max:
                continue
            if best_r is None or r < best_r:
                best_r = r
                best_i = i
        vx = 0.0
        wz = 0.0

        if best_r is not None:
            angle = input_msg.angle_min + best_i * input_msg.angle_increment
            if best_r < self.stop_dist:
                vx = 0.0
            else:
                vx = self.k_lin * (best_r - self.dist_obj)

            wz = self.k_ang * angle

            vx = clamp(vx, -self.max_v, self.max_v)
            wz = clamp(wz, -self.max_w, self.max_w)
        else:
            vx = 0.0
            wz = 0.0

        cmd = Twist()
        cmd.linear.x = float(vx)
        cmd.angular.z = float(wz)
        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = PersonFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
