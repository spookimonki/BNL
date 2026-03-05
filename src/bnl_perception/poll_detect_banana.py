#!/usr/bin/env python3
from __future__ import annotations

import rclpy
from rclpy.node import Node

from bnl_msgs.srv import DetectBanana


class PollDetectBanana(Node):
    def __init__(self) -> None:
        super().__init__('poll_detect_banana')

        self.declare_parameter('service_name', '/detect_banana')
        self.declare_parameter('poll_hz', 2.0)

        service_name = str(self.get_parameter('service_name').value)
        self._client = self.create_client(DetectBanana, service_name)

        poll_hz = float(self.get_parameter('poll_hz').value)
        poll_hz = poll_hz if poll_hz > 0 else 1.0
        self._timer = self.create_timer(1.0 / poll_hz, self._tick)

        self._last_line: str | None = None

        self.get_logger().info(f'Polling {service_name} @ {poll_hz:.2f} Hz')

    def _tick(self) -> None:
        if not self._client.service_is_ready():
            self._client.wait_for_service(timeout_sec=0.0)
            return

        req = DetectBanana.Request()
        future = self._client.call_async(req)
        future.add_done_callback(self._on_response)

    def _on_response(self, future) -> None:
        try:
            resp: DetectBanana.Response = future.result()
        except Exception as exc:
            self.get_logger().warn(f'service call failed: {exc}')
            return

        if not resp.found:
            self._last_line = None
            return

        pose = resp.pose_map
        x = pose.pose.position.x
        y = pose.pose.position.y
        frame = pose.header.frame_id or 'unknown'

        line = (
            f"BANANA FOUND @ ({x:.2f}, {y:.2f}) frame={frame} "
            f"conf={resp.confidence:.2f} pixel=({resp.pixel_u},{resp.pixel_v})"
        )
        if line != self._last_line:
            print(line)
            self._last_line = line


def main() -> None:
    rclpy.init()
    node = PollDetectBanana()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
