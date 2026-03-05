#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from geometry_msgs.msg import Twist
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from std_msgs.msg import String


@dataclass
class _TwistCache:
    stamp: Time
    msg: Twist


class CmdVelMuxNode(Node):
    """Select between Nav2 /cmd_vel and autonomy /autonomy/cmd_vel and publish /cmd_vel_mux."""

    def __init__(self) -> None:
        super().__init__('cmd_vel_mux_node')

        self.declare_parameter('mode_topic', '/autonomy/mode')
        self.declare_parameter('nav2_cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('autonomy_cmd_vel_topic', '/autonomy/cmd_vel')
        self.declare_parameter('output_cmd_vel_topic', '/cmd_vel_mux')
        self.declare_parameter('publish_rate_hz', 20.0)
        self.declare_parameter('timeout_sec', 0.5)

        self._mode: str = 'IDLE'
        self._nav2: Optional[_TwistCache] = None
        self._autonomy: Optional[_TwistCache] = None

        mode_topic = str(self.get_parameter('mode_topic').value)
        self.create_subscription(String, mode_topic, self._on_mode, 10)

        nav2_topic = str(self.get_parameter('nav2_cmd_vel_topic').value)
        self.create_subscription(Twist, nav2_topic, self._on_nav2, 10)

        autonomy_topic = str(self.get_parameter('autonomy_cmd_vel_topic').value)
        self.create_subscription(Twist, autonomy_topic, self._on_autonomy, 10)

        out_topic = str(self.get_parameter('output_cmd_vel_topic').value)
        self._pub = self.create_publisher(Twist, out_topic, 10)

        rate = float(self.get_parameter('publish_rate_hz').value)
        self.create_timer(1.0 / max(1e-3, rate), self._tick)

        self.get_logger().info(
            f'CmdVelMux active. nav2={nav2_topic} autonomy={autonomy_topic} out={out_topic} mode_topic={mode_topic}'
        )

    def _on_mode(self, msg: String) -> None:
        self._mode = str(msg.data)

    def _on_nav2(self, msg: Twist) -> None:
        self._nav2 = _TwistCache(stamp=self.get_clock().now(), msg=msg)

    def _on_autonomy(self, msg: Twist) -> None:
        self._autonomy = _TwistCache(stamp=self.get_clock().now(), msg=msg)

    def _select_cache(self) -> Optional[_TwistCache]:
        # In APPROACH/RECOVER, autonomy owns cmd_vel.
        if self._mode in ('APPROACH_BANANA', 'RECOVER'):
            return self._autonomy
        return self._nav2

    def _tick(self) -> None:
        cache = self._select_cache()
        now = self.get_clock().now()
        timeout = Duration(seconds=float(self.get_parameter('timeout_sec').value))
        if cache is None or (now - cache.stamp) > timeout:
            self._pub.publish(Twist())
            return
        self._pub.publish(cache.msg)


def main() -> None:
    rclpy.init()
    node = CmdVelMuxNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
