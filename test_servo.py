#!/usr/bin/env python3
import pigpio
import time
import sys

GPIO_SERVO = 20
MIN_PULSE = 1000      # 1ms - full counterclockwise
CENTER_PULSE = 1500   # 1.5ms - center
MAX_PULSE = 2000      # 2ms - full clockwise

pi = pigpio.pi()
if not pi.connected:
    print("Failed to connect to pigpiod daemon")
    sys.exit(1)

print("GPIO 20 servo test - moving back and forth")
try:
    for cycle in range(3):
        print(f"\nCycle {cycle + 1}")

        # Move to max (2000us)
        print("  -> Max (2000us)")
        pi.set_servo_pulsewidth(GPIO_SERVO, MAX_PULSE)
        time.sleep(1)

        # Move to center (1500us)
        print("  -> Center (1500us)")
        pi.set_servo_pulsewidth(GPIO_SERVO, CENTER_PULSE)
        time.sleep(1)

        # Move to min (1000us)
        print("  -> Min (1000us)")
        pi.set_servo_pulsewidth(GPIO_SERVO, MIN_PULSE)
        time.sleep(1)

    print("\nDone. Stopping servo.")
    pi.set_servo_pulsewidth(GPIO_SERVO, 0)
except KeyboardInterrupt:
    print("\nStopped.")
    pi.set_servo_pulsewidth(GPIO_SERVO, 0)
finally:
    pi.stop()
