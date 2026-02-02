# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node
import statistics
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class PersonFollower(Node):

    def __init__(self):
        super().__init__('person_follower')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, input_msg):
        vx = 0.0
        wz = 0.0
        angle_min = input_msg.angle_min
        angle_max = input_msg.angle_max
        angle_increment = input_msg.angle_increment
        it_angle = 6.27//0.0241
        ranges = input_msg.ranges
        persona_detectada = []
        distancia_detectada = []
        rango_frente = (int(it_angle*3//8), int(it_angle*6//8))
        for i in range (int(it_angle*2//8), int(it_angle*7//8)):
            if ranges[i] != float('inf'):
                persona_detectada.append(i*angle_increment)
                distancia_detectada.append(ranges[i])
        if len(persona_detectada) > 0:
            angulo = statistics.mean(persona_detectada) + 3.14
            lineal = statistics.mean(distancia_detectada)
            vx = lineal * 0.1
            wz = angulo * 1
            print("Lineal:", lineal, vx)
            print("Angular:", angulo, wz)

        output_msg = Twist()
        output_msg.linear.x = vx
        output_msg.angular.z = wz
        self.publisher_.publish(output_msg)

def main(args=None):
    rclpy.init(args=args)
    person_follower = PersonFollower()
    rclpy.spin(person_follower)
    person_follower.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
