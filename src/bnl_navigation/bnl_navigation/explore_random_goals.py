import math
import random
import time

import rclpy
from rclpy.duration import Duration
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import ComputePathToPose, NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener


def _quat_from_yaw(yaw: float):
    # z-yaw only
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))


class RandomGoalExplorer(Node):
    def __init__(self):
        super().__init__('bnl_explore_random_goals')

        self.declare_parameter('frame_id', 'map')
        self.declare_parameter('base_frame', 'chassis')
        self.declare_parameter('min_radius', 0.8)
        self.declare_parameter('max_radius', 3.0)
        self.declare_parameter('plan_timeout_sec', 2.0)
        self.declare_parameter('nav_timeout_sec', 45.0)
        self.declare_parameter('period_sec', 1.0)
        self.declare_parameter('max_attempts', 15)

        self.frame_id = self.get_parameter('frame_id').get_parameter_value().string_value
        self.base_frame = self.get_parameter('base_frame').get_parameter_value().string_value
        self.min_radius = float(self.get_parameter('min_radius').value)
        self.max_radius = float(self.get_parameter('max_radius').value)
        self.plan_timeout_sec = float(self.get_parameter('plan_timeout_sec').value)
        self.nav_timeout_sec = float(self.get_parameter('nav_timeout_sec').value)
        self.period_sec = float(self.get_parameter('period_sec').value)
        self.max_attempts = int(self.get_parameter('max_attempts').value)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.compute_path_client = ActionClient(self, ComputePathToPose, 'compute_path_to_pose')
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.get_logger().info('Waiting for Nav2 action servers...')
        self.compute_path_client.wait_for_server()
        self.nav_client.wait_for_server()
        self.get_logger().info('Nav2 action servers available.')

    def _spin_for(self, seconds: float) -> None:
        deadline = self.get_clock().now() + Duration(seconds=float(seconds))
        while rclpy.ok() and self.get_clock().now() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)

    def _get_robot_pose_xy_yaw(self):
        tf = self.tf_buffer.lookup_transform(self.frame_id, self.base_frame, rclpy.time.Time())
        x = tf.transform.translation.x
        y = tf.transform.translation.y
        q = tf.transform.rotation
        # yaw from quaternion (assuming planar)
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        return x, y, yaw

    def _make_goal(self, x: float, y: float, yaw: float) -> PoseStamped:
        goal = PoseStamped()
        goal.header.frame_id = self.frame_id
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.pose.position.x = float(x)
        goal.pose.position.y = float(y)
        goal.pose.position.z = 0.0
        qx, qy, qz, qw = _quat_from_yaw(yaw)
        goal.pose.orientation.x = qx
        goal.pose.orientation.y = qy
        goal.pose.orientation.z = qz
        goal.pose.orientation.w = qw
        return goal

    def _goal_has_plan(self, goal: PoseStamped) -> bool:
        req = ComputePathToPose.Goal()
        req.goal = goal
        req.start = PoseStamped()  # let planner use robot pose
        req.use_start = False

        future = self.compute_path_client.send_goal_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=self.plan_timeout_sec)
        goal_handle = future.result()
        if goal_handle is None or not goal_handle.accepted:
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=self.plan_timeout_sec)
        result = result_future.result()
        if result is None:
            return False

        path = result.result.path
        return len(path.poses) > 0

    def _navigate(self, goal: PoseStamped) -> bool:
        req = NavigateToPose.Goal()
        req.pose = goal

        future = self.nav_client.send_goal_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        goal_handle = future.result()
        if goal_handle is None or not goal_handle.accepted:
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=self.nav_timeout_sec)
        result = result_future.result()
        if result is None:
            return False

        return result.status == 4  # STATUS_SUCCEEDED

    def run(self):
        self.get_logger().info('Explorer running: selecting random nearby goals.')
        while rclpy.ok():
            # Ensure TF subscriptions and action client state are serviced.
            rclpy.spin_once(self, timeout_sec=0.1)
            try:
                rx, ry, ryaw = self._get_robot_pose_xy_yaw()
            except Exception:
                self._spin_for(self.period_sec)
                continue

            picked = None
            for _ in range(self.max_attempts):
                r = random.uniform(self.min_radius, self.max_radius)
                a = random.uniform(-math.pi, math.pi)
                gx = rx + r * math.cos(a)
                gy = ry + r * math.sin(a)
                gyaw = a
                goal = self._make_goal(gx, gy, gyaw)

                if self._goal_has_plan(goal):
                    picked = goal
                    break

            if picked is None:
                self.get_logger().warn('No valid goal found; retrying.')
                self._spin_for(self.period_sec)
                continue

            self.get_logger().info(
                f"Navigating to goal x={picked.pose.position.x:.2f} y={picked.pose.position.y:.2f}"
            )
            self._navigate(picked)
            self._spin_for(self.period_sec)


def main():
    rclpy.init()
    node = RandomGoalExplorer()
    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()
