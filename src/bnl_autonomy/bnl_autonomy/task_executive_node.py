#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped, Twist
import rclpy
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.duration import Duration
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String

from nav2_msgs.action import NavigateToPose

from bnl_msgs.srv import DetectBanana


@dataclass
class _BananaObs:
    stamp: rclpy.time.Time
    found: bool
    confidence: float


class TaskExecutiveNode(Node):
    """Simple mode switcher: EXPLORE (Nav2 frontier goals) ↔ APPROACH_BANANA (visual servo)."""

    def __init__(self) -> None:
        super().__init__('task_executive_node')

        self._cb_group = ReentrantCallbackGroup()

        self.declare_parameter('mode_topic', '/autonomy/mode')
        self.declare_parameter('explore_goal_topic', '/autonomy/explore_goal')
        self.declare_parameter('banana_state_topic', '/autonomy/banana_state')
        self.declare_parameter('detect_banana_service', '/detect_banana')
        self.declare_parameter('banana_confidence_threshold', 0.70)
        self.declare_parameter('banana_persistence_sec', 0.6)
        self.declare_parameter('banana_lost_recover_sec', 2.0)
        self.declare_parameter('nav_goal_timeout_sec', 60.0)
        self.declare_parameter('nav_cooldown_sec', 1.0)
        self.declare_parameter('recover_spin_wz', 0.6)
        self.declare_parameter('recover_spin_sec', 3.0)
        self.declare_parameter('autonomy_cmd_vel_topic', '/autonomy/cmd_vel')
        self.declare_parameter('nav_action', 'navigate_to_pose')

        self._mode_pub = self.create_publisher(String, str(self.get_parameter('mode_topic').value), 10)
        self._cmd_pub = self.create_publisher(Twist, str(self.get_parameter('autonomy_cmd_vel_topic').value), 10)

        self._mode: str = 'EXPLORE'
        self._publish_mode(self._mode)

        self._latest_explore_goal: Optional[PoseStamped] = None
        self.create_subscription(PoseStamped, str(self.get_parameter('explore_goal_topic').value), self._on_explore_goal, 10)
        self.create_subscription(String, str(self.get_parameter('banana_state_topic').value), self._on_banana_state, 10)

        self._banana_state: str = 'IDLE'

        srv = str(self.get_parameter('detect_banana_service').value)
        self._banana_client = self.create_client(DetectBanana, srv, callback_group=self._cb_group)
        self._banana_pending = None
        self._banana_last_good: Optional[_BananaObs] = None

        self._nav_client = ActionClient(self, NavigateToPose, str(self.get_parameter('nav_action').value))
        self._nav_goal_handle = None
        self._nav_goal_stamp: Optional[rclpy.time.Time] = None
        self._nav_last_done: Optional[rclpy.time.Time] = None

        self._recover_end: Optional[rclpy.time.Time] = None

        self.create_timer(0.2, self._tick)
        self.create_timer(0.3, self._poll_banana)

        self.get_logger().info('Task executive active. Initial mode=EXPLORE')

    def _publish_mode(self, mode: str) -> None:
        msg = String()
        msg.data = mode
        self._mode_pub.publish(msg)

    def _set_mode(self, mode: str) -> None:
        if mode == self._mode:
            return
        self._mode = mode
        self.get_logger().info(f'Mode -> {mode}')
        self._publish_mode(mode)

    def _on_explore_goal(self, msg: PoseStamped) -> None:
        self._latest_explore_goal = msg

    def _on_banana_state(self, msg: String) -> None:
        self._banana_state = str(msg.data)

    def _poll_banana(self) -> None:
        if not self._banana_client.service_is_ready():
            return
        if self._banana_pending is None:
            self._banana_pending = self._banana_client.call_async(DetectBanana.Request())
            return
        if not self._banana_pending.done():
            return
        try:
            resp = self._banana_pending.result()
        except Exception:
            self._banana_pending = None
            return
        self._banana_pending = None

        if not resp.found:
            return
        conf = float(resp.confidence)
        if conf < float(self.get_parameter('banana_confidence_threshold').value):
            return
        self._banana_last_good = _BananaObs(stamp=self.get_clock().now(), found=True, confidence=conf)

    def _banana_persistent(self) -> bool:
        obs = self._banana_last_good
        if obs is None:
            return False
        persist = Duration(seconds=float(self.get_parameter('banana_persistence_sec').value))
        return (self.get_clock().now() - obs.stamp) <= persist

    def _banana_recently_lost(self) -> bool:
        obs = self._banana_last_good
        if obs is None:
            return True
        window = Duration(seconds=float(self.get_parameter('banana_lost_recover_sec').value))
        return (self.get_clock().now() - obs.stamp) > window

    def _nav_send_goal(self, goal: PoseStamped) -> None:
        if not self._nav_client.wait_for_server(timeout_sec=0.2):
            return

        g = NavigateToPose.Goal()
        g.pose = goal
        send_future = self._nav_client.send_goal_async(g)
        send_future.add_done_callback(self._on_nav_goal_sent)
        self._nav_goal_stamp = self.get_clock().now()

    def _on_nav_goal_sent(self, future) -> None:
        try:
            handle = future.result()
        except Exception as exc:
            self.get_logger().warn(f'NavigateToPose goal send failed: {exc}')
            return
        if not handle.accepted:
            self.get_logger().warn('NavigateToPose goal rejected')
            return
        self._nav_goal_handle = handle
        result_future = handle.get_result_async()
        result_future.add_done_callback(self._on_nav_result)

    def _on_nav_result(self, future) -> None:
        self._nav_goal_handle = None
        self._nav_goal_stamp = None
        self._nav_last_done = self.get_clock().now()
        try:
            res = future.result()
        except Exception as exc:
            self.get_logger().warn(f'NavigateToPose result error: {exc}')
            return
        status = int(res.status)
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('NavigateToPose succeeded')
        else:
            self.get_logger().warn(f'NavigateToPose failed status={status}')

    def _nav_cancel(self) -> None:
        handle = self._nav_goal_handle
        if handle is None:
            return
        try:
            handle.cancel_goal_async()
        except Exception:
            pass
        self._nav_goal_handle = None
        self._nav_goal_stamp = None

    def _nav_timed_out(self) -> bool:
        stamp = self._nav_goal_stamp
        if stamp is None:
            return False
        timeout = Duration(seconds=float(self.get_parameter('nav_goal_timeout_sec').value))
        return (self.get_clock().now() - stamp) > timeout

    def _nav_cooldown_ok(self) -> bool:
        last = self._nav_last_done
        if last is None:
            return True
        cd = Duration(seconds=float(self.get_parameter('nav_cooldown_sec').value))
        return (self.get_clock().now() - last) > cd

    def _recover_begin(self) -> None:
        dur = float(self.get_parameter('recover_spin_sec').value)
        self._recover_end = self.get_clock().now() + Duration(seconds=dur)

    def _recover_tick(self) -> None:
        if self._recover_end is None:
            return
        if self.get_clock().now() >= self._recover_end:
            self._cmd_pub.publish(Twist())
            self._recover_end = None
            return
        cmd = Twist()
        cmd.angular.z = float(self.get_parameter('recover_spin_wz').value)
        self._cmd_pub.publish(cmd)

    def _tick(self) -> None:
        if self._mode == 'RECOVER':
            self._recover_tick()
            if self._recover_end is not None:
                return

            # Recovery finished; either keep approaching (if banana reacquired) or resume exploration.
            if self._banana_persistent():
                self._set_mode('APPROACH_BANANA')
            else:
                self._set_mode('EXPLORE')
            return

        # Switch from explore to approach when banana becomes persistent.
        if self._mode == 'EXPLORE' and self._banana_persistent():
            self._nav_cancel()
            self._set_mode('APPROACH_BANANA')
            return

        if self._mode == 'APPROACH_BANANA':
            # If approach node reports reached, hold.
            if self._banana_state == 'REACHED':
                self._set_mode('IDLE')
                return
            # If we've lost banana recently, attempt short recovery.
            if self._banana_recently_lost() or self._banana_state == 'LOST':
                self._set_mode('RECOVER')
                self._recover_begin()
                return
            return

        if self._mode == 'IDLE':
            # If banana persists again, approach; else explore.
            if self._banana_persistent():
                self._set_mode('APPROACH_BANANA')
            else:
                self._set_mode('EXPLORE')
            return

        # EXPLORE mode navigation
        if self._nav_timed_out():
            self.get_logger().warn('Nav goal timed out; cancelling')
            self._nav_cancel()
            self._nav_last_done = self.get_clock().now()

        if self._nav_goal_handle is not None:
            return

        if not self._nav_cooldown_ok():
            return

        goal = self._latest_explore_goal
        if goal is None:
            return

        self._nav_send_goal(goal)


def main() -> None:
    rclpy.init()
    node = TaskExecutiveNode()
    try:
        executor = MultiThreadedExecutor(num_threads=3)
        executor.add_node(node)
        executor.spin()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
