#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import RPi.GPIO as GPIO  # type: ignore[import-not-found]
import time


class WheelOdom(Node):
    def __init__(self):
        super().__init__('wheel_odom_node')

        self.declare_parameter('odom_topic', '/odom/raw')
        self.declare_parameter('odom_frame_id', 'odom')
        self.declare_parameter('base_frame_id', 'base_link')
        self.odom_topic = str(self.get_parameter('odom_topic').value or '/odom/raw')
        self.odom_frame_id = str(self.get_parameter('odom_frame_id').value or 'odom')
        self.base_frame_id = str(self.get_parameter('base_frame_id').value or 'base_link')

        # 1. Robot parameters
        self.wheel_radius = 0.05
        self.wheel_base = 0.3
        self.encoder_resolution_left = 2048
        self.encoder_resolution_right = 2048

        # 2. Odometry state
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        # encoder counts
        self.left_count = 0
        self.right_count = 0
        self.prev_left_count = 0
        self.prev_right_count = 0

        self.last_time = time.time()

        # 3. ROS publisher and timer
        self.odom_pub = self.create_publisher(Odometry, self.odom_topic, 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.timer = self.create_timer(0.1, self.publish_odom)

        # 4. GPIO setup
        GPIO.setmode(GPIO.BCM)
        self.left_pin_a = 5
        self.left_pin_b = 6
        self.right_pin_a = 4
        self.right_pin_b = 17

        GPIO.setup(self.left_pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.left_pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.right_pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.right_pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # previous A states for quadrature decoding (after pins are configured)
        self.left_a_last = GPIO.input(self.left_pin_a)
        self.right_a_last = GPIO.input(self.right_pin_a)

        GPIO.add_event_detect(self.left_pin_a, GPIO.BOTH, callback=self.left_callback)
        GPIO.add_event_detect(self.left_pin_b, GPIO.BOTH, callback=self.left_callback)
        GPIO.add_event_detect(self.right_pin_a, GPIO.BOTH, callback=self.right_callback)
        GPIO.add_event_detect(self.right_pin_b, GPIO.BOTH, callback=self.right_callback)

    # 5. Encoder callbacks
    def left_callback(self, channel):
        a_state = GPIO.input(self.left_pin_a)

        if a_state != self.left_a_last:
            b_state = GPIO.input(self.left_pin_b)

            if b_state != a_state:
                self.left_count += 1
            else:
                self.left_count -= 1

            self.left_a_last = a_state


    def right_callback(self, channel):
        a_state = GPIO.input(self.right_pin_a)

        if a_state != self.right_a_last:
            b_state = GPIO.input(self.right_pin_b)

            if b_state != a_state:
                self.right_count += 1
            else:
                self.right_count -= 1

            self.right_a_last = a_state

    # 6. Conversion helpers
    def left_ticks_to_distance(self, ticks):
        return (2 * math.pi * self.wheel_radius) * (ticks / self.encoder_resolution_left)

    def right_ticks_to_distance(self, ticks):
        return (2 * math.pi * self.wheel_radius) * (ticks / self.encoder_resolution_right)

    def delta_theta(self, distance_left, distance_right):
        return (distance_right - distance_left) / self.wheel_base

    # 7. Odometry integration
    def integrate_odometry(self, distance_left, distance_right):
        d = (distance_left + distance_right) / 2.0
        dtheta = self.delta_theta(distance_left, distance_right)

        if abs(dtheta) < 1e-9:
            self.x += d * math.cos(self.yaw)
            self.y += d * math.sin(self.yaw)
        else:
            radius = d / dtheta
            self.x += radius * (math.sin(self.yaw + dtheta) - math.sin(self.yaw))
            self.y -= radius * (math.cos(self.yaw + dtheta) - math.cos(self.yaw))

        self.yaw += dtheta
        self.yaw = math.atan2(math.sin(self.yaw), math.cos(self.yaw))

    # 8. Publish odometry
    def publish_odom(self):
        now = time.time()
        delta_time = now - self.last_time
        if delta_time <= 0.0:
            return

        left_ticks = self.left_count - self.prev_left_count
        right_ticks = self.right_count - self.prev_right_count

        distance_left = self.left_ticks_to_distance(left_ticks)
        distance_right = self.right_ticks_to_distance(right_ticks)

        self.integrate_odometry(distance_left, distance_right)

        linear_velocity = ((distance_left + distance_right) / 2.0) / delta_time
        angular_velocity = self.delta_theta(distance_left, distance_right) / delta_time

        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.odom_frame_id
        msg.child_frame_id = self.base_frame_id
        msg.pose.pose.position.x = self.x
        msg.pose.pose.position.y = self.y
        msg.pose.pose.orientation.z = math.sin(self.yaw / 2.0)
        msg.pose.pose.orientation.w = math.cos(self.yaw / 2.0)
        msg.twist.twist.linear.x = linear_velocity
        msg.twist.twist.angular.z = angular_velocity

        msg.pose.covariance = [
            0.02, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.02, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 1e6, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 1e6, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 1e6, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.04,
        ]
        msg.twist.covariance = [
            0.05, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.05, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 1e6, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 1e6, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 1e6, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.08,
        ]

        self.odom_pub.publish(msg)

        tf_msg = TransformStamped()
        tf_msg.header.stamp = msg.header.stamp
        tf_msg.header.frame_id = self.odom_frame_id
        tf_msg.child_frame_id = self.base_frame_id
        tf_msg.transform.translation.x = self.x
        tf_msg.transform.translation.y = self.y
        tf_msg.transform.translation.z = 0.0
        tf_msg.transform.rotation = msg.pose.pose.orientation
        self.tf_broadcaster.sendTransform(tf_msg)

        self.prev_left_count = self.left_count
        self.prev_right_count = self.right_count
        self.last_time = now


def main(args=None):
    rclpy.init(args=args)
    node = WheelOdom()
    try:
        rclpy.spin(node)
    finally:
        GPIO.cleanup()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

