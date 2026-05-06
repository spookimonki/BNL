#!/usr/bin/env python3
import rclpy
from geometry_msgs.msg import Twist
import time
import math
import random
import os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpio-pin', type=int, default=None, help='GPIO pin number to toggle via sysfs (no RPi.GPIO)')
    args, unknown = parser.parse_known_args()

    gpio = None

    class SysGPIO:
        def __init__(self, pin):
            self.pin = int(pin)
            self.base = f"/sys/class/gpio/gpio{self.pin}"
            try:
                if not os.path.exists(self.base):
                    with open('/sys/class/gpio/export', 'w') as f:
                        f.write(str(self.pin))
                    time.sleep(0.05)
                with open(os.path.join(self.base, 'direction'), 'w') as f:
                    f.write('out')
            except PermissionError:
                raise

        def write(self, val: bool):
            try:
                with open(os.path.join(self.base, 'value'), 'w') as f:
                    f.write('1' if val else '0')
            except Exception:
                pass

        def cleanup(self):
            try:
                if os.path.exists(self.base):
                    with open('/sys/class/gpio/unexport', 'w') as f:
                        f.write(str(self.pin))
            except Exception:
                pass

    rclpy.init()
    node = rclpy.create_node('random_explorer')

    # Try different velocity topic names
    topics_to_try = ['/cmd_vel', '/robot_cmd_vel', '/velocity']
    pub = None

    for topic in topics_to_try:
        pub = node.create_publisher(Twist, topic, 10)
        time.sleep(0.1)
        node.get_logger().info(f"Publishing to {topic}")
        break

    # Initialize sysfs GPIO if requested
    if args.gpio_pin is not None:
        try:
            gpio = SysGPIO(args.gpio_pin)
            node.get_logger().info(f"Sysfs GPIO initialized on pin {args.gpio_pin}")
        except PermissionError:
            node.get_logger().error(f"Permission denied initializing GPIO {args.gpio_pin}. Run as root or grant access.")
            gpio = None
        except Exception as e:
            node.get_logger().error(f"Failed to initialize GPIO {args.gpio_pin}: {e}")
            gpio = None

    node.get_logger().info("🚀 Starting random exploration movement!")

    move_duration = 0
    turn_duration = 0
    is_turning = False
    start_time = time.time()

    while rclpy.ok():
        elapsed = time.time() - start_time

        msg = Twist()

        if not is_turning:
            # Move forward
            msg.linear.x = 0.3  # 30cm/s
            msg.angular.z = 0.0

            # If a gpio was provided, set it HIGH while moving forward
            if gpio:
                gpio.write(True)

            if elapsed > 5.0:  # Move for 5 seconds
                is_turning = True
                start_time = time.time()
                node.get_logger().info("↪️  Turning...")
        else:
            # Turn
            msg.linear.x = 0.0
            msg.angular.z = random.choice([0.5, -0.5])  # Random direction

            # If a gpio was provided, set it LOW while turning
            if gpio:
                gpio.write(False)

            if elapsed > 2.0:  # Turn for 2 seconds
                is_turning = False
                start_time = time.time()
                node.get_logger().info("→ Moving forward...")

        pub.publish(msg)
        time.sleep(0.1)

    rclpy.shutdown()
    if gpio:
        try:
            gpio.write(False)
            gpio.cleanup()
        except Exception:
            pass

if __name__ == '__main__':
    main()
