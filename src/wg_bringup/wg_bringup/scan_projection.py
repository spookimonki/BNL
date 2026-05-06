#!/usr/bin/env python3
"""
Scan angle projection node for servo-mounted LiDAR.

Takes LiDAR scans and servo angle, compensates for servo motion,
and outputs corrected 2D scans or 3D point clouds.

For SLAM: Projects scans to horizontal plane.
For exploration: Can output full 3D point cloud.
"""

import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud2, PointField
from std_msgs.msg import Float64
from sensor_msgs_py import point_cloud2  # type: ignore[import-not-found]
import numpy as np  # type: ignore[import-not-found]


class ScanAngleProjection(Node):
    def __init__(self):
        super().__init__('scan_angle_projection_node')

        # Parameters
        self.declare_parameter('enable_compensation', True)
        self.declare_parameter('max_latency_ms', 50.0)  # Max servo angle age
        self.declare_parameter('output_3d', False)  # Output 3D point cloud vs 2D scan
        self.declare_parameter('theta_center', 90.0)  # For fallback if no servo msg

        self.enable_compensation = bool(self.get_parameter('enable_compensation').value)
        self.max_latency_ms = float(self.get_parameter('max_latency_ms').value)
        self.output_3d = bool(self.get_parameter('output_3d').value)
        self.theta_center = float(self.get_parameter('theta_center').value)

        # Subscriptions
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10
        )
        self.servo_angle_sub = self.create_subscription(
            Float64, '/servo_angle', self.servo_callback, 10
        )

        # Publishers
        self.scan_corrected_pub = self.create_publisher(
            LaserScan, '/scan_corrected', 10
        )
        self.point_cloud_pub = self.create_publisher(
            PointCloud2, '/point_cloud', 10
        )

        # State
        self.last_servo_angle = self.theta_center
        self.last_servo_time = None
        self._warned_latency = False

        self.get_logger().info('Scan angle projection node initialized')

    def servo_callback(self, msg: Float64) -> None:
        """Store latest servo angle."""
        self.last_servo_angle = msg.data
        self.last_servo_time = self.get_clock().now()

    def scan_callback(self, msg: LaserScan) -> None:
        """Process incoming LiDAR scan."""
        if not self.enable_compensation:
            # Pass through unchanged
            self.scan_corrected_pub.publish(msg)
            return

        # Check servo angle latency (FIXED: use nanoseconds for accuracy)
        if self.last_servo_time is not None:
            servo_stamp = self.last_servo_time.to_msg()
            latency_ms = (
                (msg.header.stamp.sec - servo_stamp.sec) * 1000.0 +
                (msg.header.stamp.nanosec - servo_stamp.nanosec) / 1e6
            )
            if latency_ms > self.max_latency_ms:
                if not self._warned_latency:
                    self.get_logger().warn(
                        f'Servo angle latency {latency_ms:.1f}ms > {self.max_latency_ms}ms'
                    )
                    self._warned_latency = True
            else:
                self._warned_latency = False

        # Current servo angle (theta)
        theta_deg = self.last_servo_angle
        theta_rad = math.radians(theta_deg)

        # Reject scans when servo is too tilted (|θ - 90°| > 60°)
        # This prevents projecting points from behind the robot
        theta_from_horizontal = abs(theta_deg - 90.0)
        if theta_from_horizontal > 60.0:
            self.get_logger().debug(
                f'Rejecting scan at servo angle {theta_deg:.1f}° (too tilted)'
            )
            # Still publish uncorrected scan as fallback
            self.scan_corrected_pub.publish(msg)
            return

        # Transform scans based on servo angle
        if self.output_3d:
            # Output 3D point cloud
            self.publish_point_cloud(msg, theta_rad)
        else:
            # Output corrected 2D scan (projected to horizontal plane)
            self.publish_corrected_scan(msg, theta_rad)

    def publish_corrected_scan(self, scan: LaserScan, theta_rad: float) -> None:
        """
        Project LiDAR points to horizontal plane.

        For a scan point at range r and angle alpha:
        - 3D point: (r*cos(alpha)*cos(theta), r*sin(alpha)*cos(theta), r*sin(theta))
        - Projected to 2D: r_2d = r * cos(theta)

        FIXED: Use abs() to prevent negative ranges when servo tilts.
        """
        cos_theta = math.cos(theta_rad)

        corrected = LaserScan()
        corrected.header = scan.header
        corrected.header.frame_id = 'lidar_link_corrected'
        corrected.angle_min = scan.angle_min
        corrected.angle_max = scan.angle_max
        corrected.angle_increment = scan.angle_increment
        corrected.time_increment = scan.time_increment
        corrected.scan_time = scan.scan_time
        corrected.range_min = scan.range_min
        corrected.range_max = scan.range_max

        # Scale ranges by cos(theta) to project to horizontal plane
        # FIXED: Use abs() to prevent negative ranges, preserve invalid ranges
        corrected.ranges = [
            abs(r * cos_theta) if scan.range_min <= r < scan.range_max else r
            for r in scan.ranges
        ]
        corrected.intensities = scan.intensities

        self.scan_corrected_pub.publish(corrected)

    def publish_point_cloud(self, scan: LaserScan, theta_rad: float) -> None:
        """
        Convert LiDAR scan to 3D point cloud.

        For each point (range r, angle alpha in scan plane):
        - Rotate by servo angle theta around Y axis
        - Output 3D point (x, y, z)
        """
        points = []
        cos_theta = math.cos(theta_rad)
        sin_theta = math.sin(theta_rad)

        alpha = scan.angle_min
        for i, r in enumerate(scan.ranges):
            if scan.range_min <= r < scan.range_max:
                # Point in LiDAR frame (scan plane is XZ when theta=0)
                # x = r * cos(alpha)
                # z = r * sin(alpha)
                # Rotate around Y axis by theta:
                # x' = x * cos(theta) - z * sin(theta)
                # y' = r * sin(alpha)  (perpendicular to scan plane)
                # z' = x * sin(theta) + z * cos(theta)

                x = r * math.cos(alpha)
                z = r * math.sin(alpha)

                x_prime = x * cos_theta - z * sin_theta
                y_prime = r * math.sin(alpha) * cos_theta  # Perpendicular component
                z_prime = x * sin_theta + z * cos_theta

                points.append([x_prime, y_prime, z_prime])

            alpha += scan.angle_increment

        if not points:
            return

        # Create PointCloud2
        cloud_msg = PointCloud2()
        cloud_msg.header = scan.header
        cloud_msg.header.frame_id = 'lidar_link_3d'
        cloud_msg.height = 1
        cloud_msg.width = len(points)
        cloud_msg.fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        ]
        cloud_msg.is_bigendian = False
        cloud_msg.point_step = 12  # 3 floats * 4 bytes
        cloud_msg.row_step = cloud_msg.point_step * len(points)
        cloud_msg.is_dense = True

        # Convert to binary data
        cloud_data = np.array(points, dtype=np.float32).tobytes()
        cloud_msg.data = cloud_data

        self.point_cloud_pub.publish(cloud_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ScanAngleProjection()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
