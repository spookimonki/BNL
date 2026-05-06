#!/usr/bin/env python3
import pigpio
import time

GPIO_SERVO = 20
CENTER_PULSE = 1500  # 90° (neutral/safe)
SWEEP_RANGE = 100    # ±100us from center
MIN_PULSE = CENTER_PULSE - SWEEP_RANGE
MAX_PULSE = CENTER_PULSE + SWEEP_RANGE
CYCLES = 10
SMOOTH_STEPS = 30

pi = pigpio.pi()
if not pi.connected:
    print("pigpiod not running")
    exit(1)

try:
    # Center servo first (safe starting position)
    print("Centering servo at 90°...")
    pi.set_servo_pulsewidth(GPIO_SERVO, CENTER_PULSE)
    time.sleep(1)

    print(f"Starting {CYCLES} smooth cycles between {MIN_PULSE}-{MAX_PULSE}us")
    for cycle in range(CYCLES):
        # Smooth sweep: center -> max
        for step in range(SMOOTH_STEPS):
            pulse = CENTER_PULSE + SWEEP_RANGE * (step / SMOOTH_STEPS)
            pi.set_servo_pulsewidth(GPIO_SERVO, pulse)
            time.sleep(0.02)

        # Smooth sweep: max -> min
        for step in range(SMOOTH_STEPS):
            pulse = MAX_PULSE - SWEEP_RANGE * 2 * (step / SMOOTH_STEPS)
            pi.set_servo_pulsewidth(GPIO_SERVO, pulse)
            time.sleep(0.02)

        # Smooth sweep: min -> center
        for step in range(SMOOTH_STEPS):
            pulse = MIN_PULSE + SWEEP_RANGE * (step / SMOOTH_STEPS)
            pi.set_servo_pulsewidth(GPIO_SERVO, pulse)
            time.sleep(0.02)

        print(f"  Cycle {cycle + 1}/{CYCLES}")

    # Return to center
    pi.set_servo_pulsewidth(GPIO_SERVO, CENTER_PULSE)
    print("Done. Servo at center.")
finally:
    pi.set_servo_pulsewidth(GPIO_SERVO, 0)
    pi.stop()
