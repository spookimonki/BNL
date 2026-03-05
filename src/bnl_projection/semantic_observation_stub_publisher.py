#!/usr/bin/env python3
from __future__ import annotations

import rclpy
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from rclpy.node import Node
from bnl_msgs.msg import SemanticObservation


class SemanticObservationStubPublisher(Node):
    def __init__(self) -> None:
        super().__init__('semantic_observation_stub_publisher')

        self.declare_parameter(
            'semantic_observation_topic',
            '/semantic_observation',
            ParameterDescriptor(type=ParameterType.PARAMETER_STRING, description='Semantic observation output topic'),
        )
        self.declare_parameter('frame_id', 'camera_link', ParameterDescriptor(type=ParameterType.PARAMETER_STRING))
        self.declare_parameter('publish_hz', 3.0, ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE))
        self.declare_parameter('confidence', 0.75, ParameterDescriptor(type=ParameterType.PARAMETER_DOUBLE))

        self._topic = self.get_parameter('semantic_observation_topic').get_parameter_value().string_value
        self._frame_id = self.get_parameter('frame_id').get_parameter_value().string_value
        publish_hz = self.get_parameter('publish_hz').get_parameter_value().double_value
        self._confidence = self.get_parameter('confidence').get_parameter_value().double_value
        self._pattern_index = 0
        self._patterns = [
            (56, 'chair', 300, 235),
            (88, 'teddy_bear', 360, 245),
        ]

        if publish_hz <= 0.0:
            raise ValueError('publish_hz must be > 0')

        self._publisher = self.create_publisher(SemanticObservation, self._topic, 10)
        self._timer = self.create_timer(1.0 / publish_hz, self._on_timer)

        self.get_logger().info(f'semantic_observation_stub_publisher ready topic={self._topic} hz={publish_hz}')

    def _on_timer(self) -> None:
        class_id, class_label, pixel_u, pixel_v = self._patterns[self._pattern_index]
        self._pattern_index = (self._pattern_index + 1) % len(self._patterns)

        msg = SemanticObservation()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self._frame_id
        msg.class_id = int(class_id)
        msg.class_label = class_label
        msg.confidence = float(self._confidence)
        msg.pixel_u = int(pixel_u)
        msg.pixel_v = int(pixel_v)
        self._publisher.publish(msg)


def main() -> None:
    rclpy.init()
    node = SemanticObservationStubPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
