#!/usr/bin/env python3
from __future__ import annotations

import colorsys
import math
from dataclasses import dataclass
from typing import Dict, Optional

import rclpy
from builtin_interfaces.msg import Duration
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from rclpy.node import Node
from bnl_msgs.msg import SemanticXY
from visualization_msgs.msg import Marker, MarkerArray


@dataclass
class TrackedObject:
    object_id: int
    class_id: int
    class_label: str
    confidence: float
    world_x: float
    world_y: float
    frame_id: str
    last_seen_sec: float


class SemanticXYMarkerNode(Node):
    def __init__(self) -> None:
        super().__init__('semantic_xy_marker_node')

        self.declare_parameter(
            'mode',
            'real',
            ParameterDescriptor(
                type=ParameterType.PARAMETER_STRING,
                description='Marker mode: real=sub to /semantic_xy, stub=publish a fixed test marker',
            ),
        )

        self.declare_parameter(
            'semantic_xy_topic',
            '/semantic_xy',
            ParameterDescriptor(type=ParameterType.PARAMETER_STRING),
        )
        self.declare_parameter(
            'marker_topic',
            '/semantic_xy_markers',
            ParameterDescriptor(type=ParameterType.PARAMETER_STRING),
        )

        self.declare_parameter(
            'marker_ns_points',
            'semantic_xy_points',
            ParameterDescriptor(type=ParameterType.PARAMETER_STRING),
        )
        self.declare_parameter(
            'marker_ns_labels',
            'semantic_xy_labels',
            ParameterDescriptor(type=ParameterType.PARAMETER_STRING),
        )

        self.declare_parameter(
            'text_show_confidence',
            True,
            ParameterDescriptor(type=ParameterType.PARAMETER_BOOL),
        )

        self.declare_parameter(
            'stub_frame_id',
            'map',
            ParameterDescriptor(type=ParameterType.PARAMETER_STRING),
        )
        self.declare_parameter(
            'stub_x',
            0.0,
            ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE),
        )
        self.declare_parameter(
            'stub_y',
            0.0,
            ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE),
        )
        self.declare_parameter(
            'stub_class_id',
            1,
            ParameterDescriptor(type=ParameterType.PARAMETER_INTEGER),
        )
        self.declare_parameter(
            'stub_class_label',
            'banana',
            ParameterDescriptor(type=ParameterType.PARAMETER_STRING),
        )
        self.declare_parameter(
            'stub_confidence',
            1.0,
            ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE),
        )
        self.declare_parameter(
            'map_frame',
            'map',
            ParameterDescriptor(type=ParameterType.PARAMETER_STRING),
        )
        self.declare_parameter(
            'force_map_frame',
            True,
            ParameterDescriptor(type=ParameterType.PARAMETER_BOOL),
        )
        self.declare_parameter(
            'update_frequency_hz',
            10.0,
            ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE),
        )
        self.declare_parameter(
            'marker_scale_m',
            0.20,
            ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE),
        )
        self.declare_parameter(
            'text_scale_m',
            0.16,
            ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE),
        )
        self.declare_parameter(
            'label_height_m',
            0.45,
            ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE),
        )
        self.declare_parameter(
            'marker_lifetime_sec',
            0.0,
            ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE),
        )
        self.declare_parameter(
            'stale_object_sec',
            2.0,
            ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE),
        )
        self.declare_parameter(
            'match_distance_m',
            0.60,
            ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE),
        )
        self.declare_parameter(
            'confidence_threshold',
            0.35,
            ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE),
        )
        self.declare_parameter(
            'hide_low_confidence',
            False,
            ParameterDescriptor(type=ParameterType.PARAMETER_BOOL),
        )
        self.declare_parameter(
            'fade_low_confidence',
            True,
            ParameterDescriptor(type=ParameterType.PARAMETER_BOOL),
        )

        self._mode = self.get_parameter('mode').get_parameter_value().string_value.strip().lower()
        self._semantic_xy_topic = self.get_parameter('semantic_xy_topic').get_parameter_value().string_value
        self._marker_topic = self.get_parameter('marker_topic').get_parameter_value().string_value
        self._ns_points = self.get_parameter('marker_ns_points').get_parameter_value().string_value
        self._ns_labels = self.get_parameter('marker_ns_labels').get_parameter_value().string_value
        self._text_show_confidence = self.get_parameter('text_show_confidence').get_parameter_value().bool_value
        self._map_frame = self.get_parameter('map_frame').get_parameter_value().string_value
        self._force_map_frame = self.get_parameter('force_map_frame').get_parameter_value().bool_value
        self._update_frequency_hz = self.get_parameter('update_frequency_hz').get_parameter_value().double_value
        self._marker_scale = self.get_parameter('marker_scale_m').get_parameter_value().double_value
        self._text_scale = self.get_parameter('text_scale_m').get_parameter_value().double_value
        self._label_height = self.get_parameter('label_height_m').get_parameter_value().double_value
        self._marker_lifetime_sec = self.get_parameter('marker_lifetime_sec').get_parameter_value().double_value
        self._stale_object_sec = self.get_parameter('stale_object_sec').get_parameter_value().double_value
        self._match_distance_m = self.get_parameter('match_distance_m').get_parameter_value().double_value
        self._confidence_threshold = self.get_parameter('confidence_threshold').get_parameter_value().double_value
        self._hide_low_confidence = self.get_parameter('hide_low_confidence').get_parameter_value().bool_value
        self._fade_low_confidence = self.get_parameter('fade_low_confidence').get_parameter_value().bool_value

        self._stub_frame_id = self.get_parameter('stub_frame_id').get_parameter_value().string_value
        self._stub_x = self.get_parameter('stub_x').get_parameter_value().double_value
        self._stub_y = self.get_parameter('stub_y').get_parameter_value().double_value
        self._stub_class_id = int(self.get_parameter('stub_class_id').get_parameter_value().integer_value)
        self._stub_class_label = self.get_parameter('stub_class_label').get_parameter_value().string_value
        self._stub_confidence = self.get_parameter('stub_confidence').get_parameter_value().double_value

        if self._update_frequency_hz <= 0.0:
            raise ValueError('update_frequency_hz must be > 0')

        self._objects: Dict[int, TrackedObject] = {}
        self._next_object_id = 1

        self._marker_pub = self.create_publisher(MarkerArray, self._marker_topic, 10)
        self._semantic_sub = None
        if self._mode not in ('real', 'stub'):
            raise ValueError("mode must be 'real' or 'stub'")

        if self._mode == 'real':
            self._semantic_sub = self.create_subscription(SemanticXY, self._semantic_xy_topic, self._on_semantic_xy, 10)
        self._timer = self.create_timer(1.0 / self._update_frequency_hz, self._publish_markers)

        self.get_logger().info(
            'semantic_xy_marker_node ready '
            f'mode={self._mode} semantic_xy_topic={self._semantic_xy_topic} marker_topic={self._marker_topic} '
            f'frame={self._map_frame} force_map_frame={self._force_map_frame}'
        )

    def _on_semantic_xy(self, msg: SemanticXY) -> None:
        confidence = float(msg.confidence)
        if self._hide_low_confidence and confidence < self._confidence_threshold:
            return

        frame_id = msg.header.frame_id if msg.header.frame_id else self._map_frame
        if self._force_map_frame and frame_id != self._map_frame:
            self.get_logger().warn(
                f'Incoming SemanticXY frame {frame_id} differs from map frame {self._map_frame}; rendering in map frame.',
                throttle_duration_sec=5.0,
            )

        now_sec = self._now_sec()
        object_id = self._match_or_create_object(
            class_id=int(msg.class_id),
            class_label=msg.class_label,
            world_x=float(msg.world_x),
            world_y=float(msg.world_y),
            frame_id=frame_id,
        )

        self._objects[object_id] = TrackedObject(
            object_id=object_id,
            class_id=int(msg.class_id),
            class_label=msg.class_label,
            confidence=confidence,
            world_x=float(msg.world_x),
            world_y=float(msg.world_y),
            frame_id=frame_id,
            last_seen_sec=now_sec,
        )

    def _match_or_create_object(
        self,
        class_id: int,
        class_label: str,
        world_x: float,
        world_y: float,
        frame_id: str,
    ) -> int:
        best_id: Optional[int] = None
        best_dist = self._match_distance_m

        for object_id, obj in self._objects.items():
            if obj.class_id != class_id:
                continue
            if obj.class_label != class_label:
                continue
            if obj.frame_id != frame_id:
                continue

            dist = math.hypot(world_x - obj.world_x, world_y - obj.world_y)
            if dist <= best_dist:
                best_dist = dist
                best_id = object_id

        if best_id is not None:
            return best_id

        new_id = self._next_object_id
        self._next_object_id += 1
        return new_id

    def _publish_markers(self) -> None:
        if self._mode == 'stub':
            self._publish_stub_markers()
            return

        now = self.get_clock().now().to_msg()
        now_sec = self._now_sec()
        marker_array = MarkerArray()
        markers = []
        stale_ids = []

        for object_id, obj in self._objects.items():
            if (now_sec - obj.last_seen_sec) > self._stale_object_sec:
                stale_ids.append(object_id)
                markers.append(self._make_delete_marker(now, obj, text=False))
                markers.append(self._make_delete_marker(now, obj, text=True))
                continue

            markers.append(self._make_point_marker(now, obj))
            markers.append(self._make_text_marker(now, obj))

        for object_id in stale_ids:
            del self._objects[object_id]

        marker_array.markers = markers
        self._marker_pub.publish(marker_array)

    def _publish_stub_markers(self) -> None:
        now = self.get_clock().now().to_msg()
        marker_array = MarkerArray()

        obj = TrackedObject(
            object_id=1,
            class_id=self._stub_class_id,
            class_label=self._stub_class_label,
            confidence=float(self._stub_confidence),
            world_x=float(self._stub_x),
            world_y=float(self._stub_y),
            frame_id=self._stub_frame_id,
            last_seen_sec=self._now_sec(),
        )

        marker_array.markers = [
            self._make_point_marker(now, obj),
            self._make_text_marker(now, obj),
        ]
        self._marker_pub.publish(marker_array)

    def _make_point_marker(self, now, obj: TrackedObject) -> Marker:
        marker = Marker()
        marker.header.stamp = now
        marker.header.frame_id = self._map_frame if self._force_map_frame else obj.frame_id
        marker.ns = self._ns_points
        marker.id = obj.object_id * 2
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        marker.pose.position.x = obj.world_x
        marker.pose.position.y = obj.world_y
        marker.pose.position.z = 0.0
        marker.pose.orientation.w = 1.0

        marker.scale.x = self._marker_scale
        marker.scale.y = self._marker_scale
        marker.scale.z = self._marker_scale

        red, green, blue = self._color_for_class(obj.class_id)
        marker.color.r = red
        marker.color.g = green
        marker.color.b = blue
        marker.color.a = self._alpha_for_confidence(obj.confidence)

        marker.lifetime = self._duration_from_seconds(self._marker_lifetime_sec)
        return marker

    def _make_text_marker(self, now, obj: TrackedObject) -> Marker:
        marker = Marker()
        marker.header.stamp = now
        marker.header.frame_id = self._map_frame if self._force_map_frame else obj.frame_id
        marker.ns = self._ns_labels
        marker.id = obj.object_id * 2 + 1
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD

        marker.pose.position.x = obj.world_x
        marker.pose.position.y = obj.world_y
        marker.pose.position.z = self._label_height
        marker.pose.orientation.w = 1.0

        marker.scale.z = self._text_scale
        if self._text_show_confidence:
            marker.text = f'{obj.class_label} ({obj.confidence:.2f})'
        else:
            marker.text = f'{obj.class_label}'

        red, green, blue = self._color_for_class(obj.class_id)
        marker.color.r = red
        marker.color.g = green
        marker.color.b = blue
        marker.color.a = self._alpha_for_confidence(obj.confidence)

        marker.lifetime = self._duration_from_seconds(self._marker_lifetime_sec)
        return marker

    def _make_delete_marker(self, now, obj: TrackedObject, text: bool) -> Marker:
        marker = Marker()
        marker.header.stamp = now
        marker.header.frame_id = self._map_frame if self._force_map_frame else obj.frame_id
        marker.ns = self._ns_labels if text else self._ns_points
        marker.id = obj.object_id * 2 + 1 if text else obj.object_id * 2
        marker.action = Marker.DELETE
        return marker

    def _alpha_for_confidence(self, confidence: float) -> float:
        if not self._fade_low_confidence:
            return 0.95
        if confidence >= self._confidence_threshold:
            return 0.95
        if self._confidence_threshold <= 0.0:
            return 0.25
        return max(0.12, min(0.95, confidence / self._confidence_threshold))

    @staticmethod
    def _color_for_class(class_id: int):
        hue = ((class_id * 0.1618) % 1.0)
        red, green, blue = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
        return red, green, blue

    @staticmethod
    def _duration_from_seconds(seconds: float) -> Duration:
        if seconds <= 0.0:
            return Duration(sec=0, nanosec=0)
        sec = int(seconds)
        nanosec = int((seconds - sec) * 1e9)
        return Duration(sec=sec, nanosec=nanosec)

    def _now_sec(self) -> float:
        now = self.get_clock().now().to_msg()
        return float(now.sec) + float(now.nanosec) * 1e-9


def main() -> None:
    rclpy.init()
    node = SemanticXYMarkerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
