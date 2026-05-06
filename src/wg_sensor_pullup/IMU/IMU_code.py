import rclpy
from rclpy.node import Node
import yaml
import os
import numpy as np
import math
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Quaternion
from ament_index_python import get_package_prefix

try:
    from RPi import GPIO
except ImportError:
    GPIO = None


class imu_node_class(Node):
    """IMU node providing inertial measurement data.

    Currently a stub implementation. Full IMU integration requires:
    - I2C device driver (e.g., MPU-6050, BNO055)
    - Sensor calibration and offset configuration
    - Hardware connection verification

    This stub publishes zero-initialized IMU messages at 10 Hz.
    Set environment variable IMU_STUB_FAIL=1 for fail-fast testing.
    """

    def __init__(self):
        super().__init__('imu_node')

        self.get_logger().info("IMU node started (stub implementation)")

        self.imu_publisher = self.create_publisher(Imu, 'imu/data', 10)
        self.timer = self.create_timer(0.1, self.publish_imu_data)

        fail_fast = os.environ.get('IMU_STUB_FAIL', '0') == '1'
        if fail_fast:
            self.get_logger().error('IMU_STUB_FAIL=1: stub mode requested to fail')
            raise RuntimeError('IMU stub fail-fast mode enabled')

    def publish_imu_data(self):
        """Publish stub IMU data (zero values)."""
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'

        msg.linear_acceleration.x = 0.0
        msg.linear_acceleration.y = 0.0
        msg.linear_acceleration.z = 9.81

        msg.angular_velocity.x = 0.0
        msg.angular_velocity.y = 0.0
        msg.angular_velocity.z = 0.0

        msg.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

        self.imu_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    imu_N = imu_node_class()
    rclpy.spin(imu_N)
    imu_N.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

