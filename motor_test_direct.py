#!/usr/bin/env python3
"""Direct motor control via PWM - for testing motor driver wiring"""
import RPi.GPIO as GPIO
import time
import sys

# Motor pins (from vel_to_pmw.py)
GPIO_LEFT_PWM = 13
GPIO_RIGHT_PWM = 12
GPIO_DIR_L_FWD = 16
GPIO_DIR_L_REV = 26
GPIO_DIR_R_FWD = 27
GPIO_DIR_R_REV = 22

PWM_FREQ = 100  # Hz

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    pins = [GPIO_LEFT_PWM, GPIO_RIGHT_PWM, GPIO_DIR_L_FWD, GPIO_DIR_L_REV, GPIO_DIR_R_FWD, GPIO_DIR_R_REV]
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    print("✓ GPIO initialized")
    return GPIO.PWM(GPIO_LEFT_PWM, PWM_FREQ), GPIO.PWM(GPIO_RIGHT_PWM, PWM_FREQ)

def set_direction(direction):
    """direction: 1=forward, -1=reverse, 0=coast"""
    if direction > 0:  # Forward
        GPIO.output(GPIO_DIR_L_FWD, GPIO.HIGH)
        GPIO.output(GPIO_DIR_L_REV, GPIO.LOW)
        GPIO.output(GPIO_DIR_R_FWD, GPIO.HIGH)
        GPIO.output(GPIO_DIR_R_REV, GPIO.LOW)
        return "FWD"
    elif direction < 0:  # Reverse
        GPIO.output(GPIO_DIR_L_FWD, GPIO.LOW)
        GPIO.output(GPIO_DIR_L_REV, GPIO.HIGH)
        GPIO.output(GPIO_DIR_R_FWD, GPIO.LOW)
        GPIO.output(GPIO_DIR_R_REV, GPIO.HIGH)
        return "REV"
    else:  # Coast/brake
        GPIO.output(GPIO_DIR_L_FWD, GPIO.LOW)
        GPIO.output(GPIO_DIR_L_REV, GPIO.LOW)
        GPIO.output(GPIO_DIR_R_FWD, GPIO.LOW)
        GPIO.output(GPIO_DIR_R_REV, GPIO.LOW)
        return "COAST"

def test_sequence(pwm_left, pwm_right):
    """Run a test sequence"""
    try:
        pwm_left.start(0)
        pwm_right.start(0)

        tests = [
            (1, 30, 3, "Fwd 30% for 3s"),
            (0, 0, 1, "Coast 1s"),
            (1, 60, 3, "Fwd 60% for 3s"),
            (0, 0, 1, "Coast 1s"),
            (-1, 30, 2, "Rev 30% for 2s"),
            (0, 0, 1, "Coast 1s"),
            (1, 80, 2, "Fwd 80% for 2s"),
            (0, 0, 1, "Stop"),
        ]

        for direction, duty, duration, desc in tests:
            dir_str = set_direction(direction)
            print(f"\n→ {desc} (Dir:{dir_str}, Duty:{duty}%)")
            pwm_left.ChangeDutyCycle(duty)
            pwm_right.ChangeDutyCycle(duty)
            time.sleep(duration)

        pwm_left.ChangeDutyCycle(0)
        pwm_right.ChangeDutyCycle(0)
        print("\n✓ Test sequence complete")

    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user")
        pwm_left.stop()
        pwm_right.stop()
        GPIO.cleanup()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║         DIRECT MOTOR PWM TEST (No ROS)                     ║
║  Pins: L_PWM=13, R_PWM=12, Dir_Pins=16,26,27,22          ║
╚════════════════════════════════════════════════════════════╝
    """)

    try:
        pwm_left, pwm_right = setup_gpio()
        test_sequence(pwm_left, pwm_right)

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            pwm_left.stop()
            pwm_right.stop()
        except:
            pass
        GPIO.cleanup()
        print("\n✓ GPIO cleaned up")

if __name__ == '__main__':
    if __name__ != '__main__':
        print("❌ Please run as root: sudo python3 this_script.py")
        sys.exit(1)
    main()
