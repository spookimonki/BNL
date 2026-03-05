#!/usr/bin/env python3
from __future__ import annotations

"""Project timestamped semantic pixel observations into world-frame XY.

Pipeline:
1) Convert semantic pixel (u, v) to a normalized camera ray from CameraInfo.
2) Rotate that ray into base_link and match its horizontal angle to a LaserScan beam.
3) Convert matched beam range to local base_link XY.
4) Transform local XY to target world frame (`map`) with fallback (`odom`).
"""

import math
from typing import Optional, Tuple

import rclpy
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from rclpy.time import Time
from sensor_msgs.msg import CameraInfo, LaserScan
from bnl_msgs.msg import SemanticObservation, SemanticXY
from tf2_ros import Buffer, TransformException, TransformListener


class SemanticProjectionNode(Node):
    def __init__(self) -> None:
        super().__init__('semantic_projection_node')

        self.declare_parameter(
            'target_frame',
            'map',
            ParameterDescriptor(type=ParameterType.PARAMETER_STRING, description='Primary projection world frame'),
        )
        self.declare_parameter(
            'fallback_frame',
            'odom',
            ParameterDescriptor(type=ParameterType.PARAMETER_STRING, description='Fallback projection frame'),
        )
        self.declare_parameter(
            'use_lidar_alignment',
            True,
            ParameterDescriptor(type=ParameterType.PARAMETER_BOOL, description='Enable lidar-aligned projection'),
        )
        self.declare_parameter(
            'max_scan_age_sec',
            0.2,
            ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE, description='Maximum semantic-to-scan timestamp delta'),
        )

        self._target_frame = self.get_parameter('target_frame').get_parameter_value().string_value
        self._fallback_frame = self.get_parameter('fallback_frame').get_parameter_value().string_value
        self._use_lidar_alignment = self.get_parameter('use_lidar_alignment').get_parameter_value().bool_value
        self._max_scan_age_sec = self.get_parameter('max_scan_age_sec').get_parameter_value().double_value

        self._latest_scan: Optional[LaserScan] = None
        self._latest_camera_info: Optional[CameraInfo] = None

        self._tf_buffer = Buffer(cache_time=Duration(seconds=10.0))
        self._tf_listener = TransformListener(self._tf_buffer, self)

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self._scan_sub = self.create_subscription(LaserScan, '/scan', self._on_scan, qos)
        self._camera_info_sub = self.create_subscription(CameraInfo, '/camera/camera_info', self._on_camera_info, qos)
        self._semantic_obs_sub = self.create_subscription(
            SemanticObservation,
            '/semantic_observation',
            self._on_semantic_observation,
            qos,
        )

        self._semantic_xy_pub = self.create_publisher(SemanticXY, '/semantic_xy', qos)

        self.get_logger().info(
            f'semantic_projection_node ready target_frame={self._target_frame} '
            f'fallback_frame={self._fallback_frame} use_lidar_alignment={self._use_lidar_alignment} '
            f'max_scan_age_sec={self._max_scan_age_sec}'
        )

    def _on_scan(self, msg: LaserScan) -> None:
        self._latest_scan = msg

    def _on_camera_info(self, msg: CameraInfo) -> None:
        self._latest_camera_info = msg

    def _on_semantic_observation(self, msg: SemanticObservation) -> None:
        if self._latest_camera_info is None:
            self.get_logger().warn('No CameraInfo received yet; discarding semantic observation.', throttle_duration_sec=2.0)
            return

        if self._latest_scan is None:
            self.get_logger().warn('No LaserScan received yet; discarding semantic observation.', throttle_duration_sec=2.0)
            return

        if not self._use_lidar_alignment:
            self.get_logger().warn('use_lidar_alignment=false; projection is disabled for this phase.', throttle_duration_sec=2.0)
            return

        if self._is_scan_too_old(msg, self._latest_scan):
            self.get_logger().warn('Latest scan too old relative to semantic observation; discarding.', throttle_duration_sec=2.0)
            return

        ray_camera = self._pixel_to_ray(msg, self._latest_camera_info)
        if ray_camera is None:
            self.get_logger().warn('Invalid camera intrinsics; discarding semantic observation.', throttle_duration_sec=2.0)
            return

        ray_base = self._transform_direction_to_base(ray_camera, msg.header.frame_id, msg.header.stamp)
        if ray_base is None:
            self.get_logger().warn('TF camera->base_link unavailable; discarding semantic observation.', throttle_duration_sec=2.0)
            return

        theta = math.atan2(ray_base[1], ray_base[0])
        scan_index = self._ray_to_scan_index(theta, self._latest_scan)
        if scan_index is None:
            self.get_logger().debug('Observation discarded: no valid lidar range for matched beam.')
            return

        local_xy = self._scan_index_to_local_xy(self._latest_scan, scan_index)
        if local_xy is None:
            self.get_logger().debug('Observation discarded: matched scan range invalid.')
            return

        self.get_logger().debug(f'Computed local XY from scan: x={local_xy[0]:.3f} y={local_xy[1]:.3f}')

        world_point, used_frame = self._transform_to_target_frame(local_xy, msg.header.stamp)
        if world_point is None or used_frame is None:
            self.get_logger().warn('TF base_link->world frame unavailable; discarding semantic observation.', throttle_duration_sec=2.0)
            return

        out = SemanticXY()
        out.header.stamp = msg.header.stamp
        out.header.frame_id = used_frame
        out.class_id = msg.class_id
        out.class_label = msg.class_label
        out.confidence = msg.confidence
        out.world_x = world_point[0]
        out.world_y = world_point[1]
        self._semantic_xy_pub.publish(out)

        self.get_logger().debug(
            f'Published /semantic_xy label={out.class_label} frame={used_frame} '
            f'x={out.world_x:.3f} y={out.world_y:.3f}'
        )

    def _is_scan_too_old(self, obs: SemanticObservation, scan: LaserScan) -> bool:
        obs_sec = float(obs.header.stamp.sec) + float(obs.header.stamp.nanosec) * 1e-9
        scan_sec = float(scan.header.stamp.sec) + float(scan.header.stamp.nanosec) * 1e-9
        return abs(obs_sec - scan_sec) > self._max_scan_age_sec

    def _pixel_to_ray(self, obs: SemanticObservation, cam_info: CameraInfo) -> Optional[Tuple[float, float, float]]:
        """Convert pixel observation into normalized camera-frame ray direction."""
        fx = float(cam_info.k[0])
        fy = float(cam_info.k[4])
        cx = float(cam_info.k[2])
        cy = float(cam_info.k[5])

        if fx == 0.0 or fy == 0.0:
            return None

        x_cam = (float(obs.pixel_u) - cx) / fx
        y_cam = (float(obs.pixel_v) - cy) / fy
        z_cam = 1.0

        norm = math.sqrt(x_cam * x_cam + y_cam * y_cam + z_cam * z_cam)
        if norm == 0.0:
            return None

        ray = (x_cam / norm, y_cam / norm, z_cam / norm)
        self.get_logger().debug(
            f'Pixel->ray conversion: u={obs.pixel_u} v={obs.pixel_v} '
            f'-> ray=({ray[0]:.4f},{ray[1]:.4f},{ray[2]:.4f})'
        )
        return ray

    def _transform_direction_to_base(
        self,
        ray_camera: Tuple[float, float, float],
        camera_frame: str,
        stamp,
    ) -> Optional[Tuple[float, float, float]]:
        """Rotate camera-frame ray into base_link frame using TF orientation."""
        try:
            tf = self._tf_buffer.lookup_transform('base_link', camera_frame, stamp, timeout=Duration(seconds=0.1))
        except TransformException:
            return None

        q = tf.transform.rotation
        ray_base = self._rotate_vector_by_quaternion(ray_camera, q.x, q.y, q.z, q.w)
        return ray_base

    def _ray_to_scan_index(self, theta: float, scan: LaserScan) -> Optional[int]:
        """Map base_link ray angle to nearest scan beam index (2D planar scan assumption)."""
        if scan.angle_increment == 0.0:
            return None

        if len(scan.ranges) == 0:
            return None

        theta_norm = math.atan2(math.sin(theta), math.cos(theta))
        raw_index = int(round((theta_norm - float(scan.angle_min)) / float(scan.angle_increment)))
        max_index = len(scan.ranges) - 1
        index = max(0, min(max_index, raw_index))

        self.get_logger().debug(
            f'Beam index selection: theta={theta_norm:.4f} raw_index={raw_index} clamped_index={index}'
        )

        return index

    def _scan_index_to_local_xy(self, scan: LaserScan, index: int) -> Optional[Tuple[float, float]]:
        """Convert matched scan beam into base_link local XY point."""
        if index < 0 or index >= len(scan.ranges):
            return None

        matched_range = float(scan.ranges[index])
        beam_angle = float(scan.angle_min) + float(index) * float(scan.angle_increment)

        if not math.isfinite(matched_range):
            return None

        if matched_range < float(scan.range_min) or matched_range > float(scan.range_max):
            return None

        self.get_logger().debug(
            f'Lidar beam matched: index={index} angle={beam_angle:.4f} range={matched_range:.4f}'
        )

        x_local = float(matched_range * math.cos(beam_angle))
        y_local = float(matched_range * math.sin(beam_angle))
        return (x_local, y_local)

    def _transform_to_target_frame(
        self,
        local_xy: Tuple[float, float],
        stamp,
    ) -> Tuple[Optional[Tuple[float, float]], Optional[str]]:
        """Transform base_link local XY into target frame, with fallback frame support."""
        point3 = (local_xy[0], local_xy[1], 0.0)

        world_tf = self._lookup_transform(self._target_frame, 'base_link', stamp)
        if world_tf is not None:
            world_point = self._apply_transform(point3, world_tf)
            self.get_logger().debug(f'Transform succeeded base_link->{self._target_frame}')
            return (world_point[0], world_point[1]), self._target_frame

        fallback_tf = self._lookup_transform(self._fallback_frame, 'base_link', stamp)
        if fallback_tf is not None:
            world_point = self._apply_transform(point3, fallback_tf)
            self.get_logger().debug(f'Fallback frame used: {self._fallback_frame}')
            return (world_point[0], world_point[1]), self._fallback_frame

        return None, None

    def _lookup_transform(self, target_frame: str, source_frame: str, stamp):
        """Lookup TF transform with short timeout and explicit transform exception handling."""
        try:
            return self._tf_buffer.lookup_transform(target_frame, source_frame, stamp, timeout=Duration(seconds=0.1))
        except TransformException:
            try:
                return self._tf_buffer.lookup_transform(
                    target_frame,
                    source_frame,
                    Time(),
                    timeout=Duration(seconds=0.1),
                )
            except TransformException:
                return None

    def _apply_transform(self, point_xyz: Tuple[float, float, float], tf_msg) -> Tuple[float, float, float]:
        """Apply rigid transform to 3D point using TF translation + quaternion rotation."""
        tx = float(tf_msg.transform.translation.x)
        ty = float(tf_msg.transform.translation.y)
        tz = float(tf_msg.transform.translation.z)

        q = tf_msg.transform.rotation
        rx, ry, rz = self._rotate_vector_by_quaternion(point_xyz, q.x, q.y, q.z, q.w)

        return (rx + tx, ry + ty, rz + tz)

    @staticmethod
    def _rotate_vector_by_quaternion(
        vec: Tuple[float, float, float],
        qx: float,
        qy: float,
        qz: float,
        qw: float,
    ) -> Tuple[float, float, float]:
        vx, vy, vz = vec

        uvx = qy * vz - qz * vy
        uvy = qz * vx - qx * vz
        uvz = qx * vy - qy * vx

        uuvx = qy * uvz - qz * uvy
        uuvy = qz * uvx - qx * uvz
        uuvz = qx * uvy - qy * uvx

        uvx *= 2.0 * qw
        uvy *= 2.0 * qw
        uvz *= 2.0 * qw

        uuvx *= 2.0
        uuvy *= 2.0
        uuvz *= 2.0

        return (vx + uvx + uuvx, vy + uvy + uuvy, vz + uvz + uuvz)


def main() -> None:
    rclpy.init()
    node = SemanticProjectionNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
