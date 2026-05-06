#!/usr/bin/env python3
import rclpy
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from math import cos, sin, pi
import time
import random

def main():
    rclpy.init()
    node = rclpy.create_node('frontier_explorer')

    client = ActionClient(node, NavigateToPose, 'navigate_to_pose')

    node.get_logger().info('Waiting for navigate_to_pose action...')
    if not client.wait_for_server(timeout_sec=10.0):
        node.get_logger().error('Action server not available')
        return

    node.get_logger().info('✓ Connected to navigate_to_pose')

    # Start exploration with random goals in expanding search pattern
    radius = 1.0
    angle_offset = 0.0
    max_radius = 5.0

    while rclpy.ok():
        try:
            # Generate exploration goal in spiral pattern
            angle = angle_offset
            x = radius * cos(angle)
            y = radius * sin(angle)

            goal = NavigateToPose.Goal()
            goal.pose.header.frame_id = 'map'
            goal.pose.header.stamp = node.get_clock().now().to_msg()
            goal.pose.pose.position.x = x
            goal.pose.pose.position.y = y
            goal.pose.pose.position.z = 0.0
            goal.pose.pose.orientation.w = 1.0

            node.get_logger().info(f'🎯 Sending goal: ({x:.2f}, {y:.2f})')

            future = client.send_goal_async(goal)
            rclpy.spin_until_future_complete(node, future, timeout_sec=2.0)

            if future.result() is not None:
                get_result_future = future.result().get_result_async()
                rclpy.spin_until_future_complete(node, get_result_future, timeout_sec=30.0)
                node.get_logger().info('✓ Goal reached')

            # Update exploration parameters
            angle_offset += pi / 4  # Rotate around circle
            if angle_offset > 2 * pi:
                angle_offset = 0.0
                radius = min(radius + 0.5, max_radius)  # Expand search radius

            time.sleep(0.5)

        except Exception as e:
            node.get_logger().error(f'Error: {e}')
            time.sleep(1.0)

    rclpy.shutdown()

if __name__ == '__main__':
    main()
