#!/usr/bin/env python3
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from geometry_msgs.msg import Twist
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.duration import Duration
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.time import Time
from sensor_msgs.msg import Image, LaserScan
from std_msgs.msg import String

from bnl_msgs.srv import DetectBanana

from bnl_autonomy.util import clamp


@dataclass
class _Detection:
    stamp: Time
    found: bool
    confidence: float
    u: int
    v: int


class BananaApproachNode(Node):
    """Vision-guided approach using pixel error + lidar standoff.

    Note: We do NOT attempt 3D triangulation. This is a robust staged approach:
    - rotate to center banana in image
    - drive forward while keeping it centered
    - stop when lidar reports standoff distance in front sector
    """

    def __init__(self) -> None:
        super().__init__('banana_approach_node')

        self._cb_group = ReentrantCallbackGroup()

        self.declare_parameter('mode_topic', '/autonomy/mode')
        self.declare_parameter('cmd_vel_topic', '/autonomy/cmd_vel')
        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('scan_topic', '/scan')
        self.declare_parameter('detect_banana_service', '/detect_banana')
        self.declare_parameter('detect_poll_hz', 5.0)
        self.declare_parameter('control_hz', 12.0)
        self.declare_parameter('confidence_threshold', 0.65)
        self.declare_parameter('lost_timeout_sec', 1.0)
        self.declare_parameter('center_tolerance_px', 35)
        self.declare_parameter('k_yaw', 1.2)
        self.declare_parameter('max_wz', 1.0)
        self.declare_parameter('forward_speed', 0.12)
        self.declare_parameter('standoff_m', 0.65)
        self.declare_parameter('front_sector_deg', 20.0)
        self.declare_parameter('min_valid_range_m', 0.05)

        self._mode: str = 'IDLE'
        self._image_width: Optional[int] = None
        self._scan: Optional[LaserScan] = None
        self._last_detection: Optional[_Detection] = None
        self._last_state: str = 'IDLE'

        mode_topic = str(self.get_parameter('mode_topic').value)
        self.create_subscription(String, mode_topic, self._on_mode, 10)

        self._cmd_pub = self.create_publisher(Twist, str(self.get_parameter('cmd_vel_topic').value), 10)
        self._state_pub = self.create_publisher(String, '/autonomy/banana_state', 10)

        self.create_subscription(Image, str(self.get_parameter('image_topic').value), self._on_image, 10)
        self.create_subscription(LaserScan, str(self.get_parameter('scan_topic').value), self._on_scan, 10)

        srv_name = str(self.get_parameter('detect_banana_service').value)
        self._client = self.create_client(DetectBanana, srv_name, callback_group=self._cb_group)
        self._pending = None

        self.create_timer(1.0 / max(1e-3, float(self.get_parameter('detect_poll_hz').value)), self._poll)
        self.create_timer(1.0 / max(1e-3, float(self.get_parameter('control_hz').value)), self._control)

        self.get_logger().info(f'Banana approach active. service={srv_name} mode_topic={mode_topic}')

    def _on_mode(self, msg: String) -> None:
        self._mode = str(msg.data)

    def _on_image(self, msg: Image) -> None:
        self._image_width = int(msg.width)

    def _on_scan(self, msg: LaserScan) -> None:
        self._scan = msg

    def _publish_state(self, state: str) -> None:
        if state == self._last_state:
            return
        self._last_state = state
        m = String()
        m.data = state
        self._state_pub.publish(m)

    def _poll(self) -> None:
        if self._mode != 'APPROACH_BANANA':
            self._pending = None
            self._last_detection = None
            self._publish_state('IDLE')
            return

        if not self._client.service_is_ready():
            self._publish_state('WAIT_SERVICE')
            return

        if self._pending is None:
            self._pending = self._client.call_async(DetectBanana.Request())
            return

        if not self._pending.done():
            return

        try:
            resp = self._pending.result()
        except Exception:
            self._pending = None
            return

        self._pending = None
        self._last_detection = _Detection(
            stamp=self.get_clock().now(),
            found=bool(resp.found),
            confidence=float(resp.confidence),
            u=int(resp.pixel_u),
            v=int(resp.pixel_v),
        )

    def _front_range(self) -> Optional[float]:
        scan = self._scan
        if scan is None or not scan.ranges:
            return None

        sector_deg = float(self.get_parameter('front_sector_deg').value)
        sector = math.radians(sector_deg)
        a_min = float(scan.angle_min)
        a_inc = float(scan.angle_increment)
        if a_inc <= 0.0:
            return None

        i0 = int(((-sector) - a_min) / a_inc)
        i1 = int(((+sector) - a_min) / a_inc)
        i0 = max(0, min(i0, len(scan.ranges) - 1))
        i1 = max(0, min(i1, len(scan.ranges) - 1))
        if i1 < i0:
            i0, i1 = i1, i0

        min_valid = float(self.get_parameter('min_valid_range_m').value)
        best: Optional[float] = None
        for r in scan.ranges[i0 : i1 + 1]:
            if math.isfinite(r) and r > min_valid:
                if best is None or r < best:
                    best = float(r)
        return best

    def _control(self) -> None:
        if self._mode != 'APPROACH_BANANA':
            return

        det = self._last_detection
        width = self._image_width
        if det is None or width is None:
            self._publish_state('SEARCHING')
            self._cmd_pub.publish(Twist())
            return

        age = self.get_clock().now() - det.stamp
        lost_timeout = Duration(seconds=float(self.get_parameter('lost_timeout_sec').value))
        if age > lost_timeout:
            self._publish_state('LOST')
            self._cmd_pub.publish(Twist())
            return

        conf_th = float(self.get_parameter('confidence_threshold').value)
        if (not det.found) or det.confidence < conf_th:
            self._publish_state('SEARCHING')
            self._cmd_pub.publish(Twist())
            return

        standoff = float(self.get_parameter('standoff_m').value)
        front = self._front_range()
        if front is not None and front <= standoff:
            self._publish_state('REACHED')
            self._cmd_pub.publish(Twist())
            return

        center_px = width / 2.0
        err_px = float(det.u) - center_px
        tol_px = float(self.get_parameter('center_tolerance_px').value)

        k_yaw = float(self.get_parameter('k_yaw').value)
        max_wz = float(self.get_parameter('max_wz').value)
        wz = clamp(-k_yaw * (err_px / max(1.0, center_px)), -max_wz, +max_wz)

        cmd = Twist()
        cmd.angular.z = float(wz)

        # Only drive forward if sufficiently centered.
        if abs(err_px) < tol_px:
            cmd.linear.x = float(self.get_parameter('forward_speed').value)
            self._publish_state('APPROACHING')
        else:
            cmd.linear.x = 0.0
            self._publish_state('CENTERING')

        self._cmd_pub.publish(cmd)


def main() -> None:
    rclpy.init()
    node = BananaApproachNode()
    try:
        executor = MultiThreadedExecutor(num_threads=2)
        executor.add_node(node)
        executor.spin()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
