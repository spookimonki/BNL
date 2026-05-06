#!/usr/bin/env python3
"""
Servo oscillator node for LiDAR mount.

Defines theta(t) as sinusoidal oscillation and publishes current angle.
Used for scan angle compensation in 3D point cloud projection.

theta(t) = theta_center + amplitude * sin(omega * t + phase)
"""

import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import RPi.GPIO as GPIO  # type: ignore[import-not-found]


class ServoOscillator(Node):
    def __init__(self):
        super().__init__('servo_oscillator_node')

        # Parameters
        self.declare_parameter('servo_pin', 20)
        self.declare_parameter('pwm_frequency', 50)  # Hz (standard servo)
        self.declare_parameter('theta_center', 90.0)  # degrees
        self.declare_parameter('amplitude', 15.0)  # degrees
        self.declare_parameter('period', 2.0)  # seconds per full cycle
        self.declare_parameter('phase', 0.0)  # radians
        self.declare_parameter('publish_rate', 50.0)  # Hz
        self.declare_parameter('enable_gpio', True)  # Set False for simulation

        self.servo_pin = int(self.get_parameter('servo_pin').value)
        self.pwm_frequency = int(self.get_parameter('pwm_frequency').value)
        self.theta_center = float(self.get_parameter('theta_center').value)
        self.amplitude = float(self.get_parameter('amplitude').value)
        self.period = float(self.get_parameter('period').value)
        self.phase = float(self.get_parameter('phase').value)
        self.publish_rate = float(self.get_parameter('publish_rate').value)
        self.enable_gpio = bool(self.get_parameter('enable_gpio').value)

        # Precompute omega
        self.omega = 2.0 * math.pi / self.period  # rad/s

        # Publishers
        self.angle_pub = self.create_publisher(Float64, '/servo_angle', 10)

        # GPIO setup (optional - can run without GPIO for testing)
        self._pwm = None
        if self.enable_gpio:
            try:
                GPIO.setwarnings(False)
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.servo_pin, GPIO.OUT)
                self._pwm = GPIO.PWM(self.servo_pin, self.pwm_frequency)
                self._pwm.start(0)
                self.get_logger().info(f'GPIO initialized on pin {self.servo_pin}')
            except Exception as e:
                self.get_logger().warn(f'GPIO setup failed: {e}. Running without servo output.')
                self.enable_gpio = False

        # Start time reference
        self.start_time = None
        self.last_angle_sent = None

        # Timer
        timer_period = 1.0 / self.publish_rate
        self.timer = self.create_timer(timer_period, self.tick)

        self.get_logger().info(
            f'Servo oscillator initialized: theta(t) = {self.theta_center} + {self.amplitude} * sin({self.omega:.2f} * t + {self.phase})'
        )

    def theta(self, t: float) -> float:
        """Compute servo angle at time t (degrees)."""
        return self.theta_center + self.amplitude * math.sin(self.omega * t + self.phase)

    def angle_to_duty_cycle(self, angle: float) -> float:
        """Convert angle (0-180) to PWM duty cycle (2.5-12.5 for 50Hz)."""
        angle = max(0.0, min(180.0, float(angle)))
        return 2.5 + (angle / 18.0)

    def set_servo_angle(self, angle: float) -> None:
        """Set servo to angle (degrees)."""
        if not self.enable_gpio or self._pwm is None:
            return
        duty = self.angle_to_duty_cycle(angle)
        self._pwm.ChangeDutyCycle(duty)

    def tick(self) -> None:
        """Timer callback - compute theta(t) and publish."""
        if self.start_time is None:
            self.start_time = self.get_clock().now()

        now = self.get_clock().now()
        t = (now - self.start_time).nanoseconds / 1e9  # seconds since start

        angle = self.theta(t)

        # Publish angle
        msg = Float64()
        msg.data = angle
        self.angle_pub.publish(msg)

        # Update servo position (if GPIO enabled and angle changed significantly)
        if self.enable_gpio:
            if self.last_angle_sent is None or abs(angle - self.last_angle_sent) > 0.5:
                self.set_servo_angle(angle)
                self.last_angle_sent = angle

        # Log at 1 Hz
        if int(t * 10) % 10 == 0:
            self.get_logger().debug(f't={t:.2f}s, theta={angle:.1f} deg')

    def destroy_node(self) -> None:
        """Cleanup GPIO on shutdown."""
        if self._pwm is not None:
            self._pwm.stop()
        GPIO.cleanup()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ServoOscillator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
