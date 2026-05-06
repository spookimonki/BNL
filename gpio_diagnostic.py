#!/usr/bin/env python3
"""GPIO Pin Diagnostic - check if pins are actually toggling"""
import RPi.GPIO as GPIO
import time

GPIO_LEFT_PWM = 13
GPIO_RIGHT_PWM = 12
GPIO_DIR_L_FWD = 16
GPIO_DIR_L_REV = 26
GPIO_DIR_R_FWD = 27
GPIO_DIR_R_REV = 22

def test_pins():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    pins = {
        'L_PWM': GPIO_LEFT_PWM,
        'R_PWM': GPIO_RIGHT_PWM,
        'L_FWD': GPIO_DIR_L_FWD,
        'L_REV': GPIO_DIR_L_REV,
        'R_FWD': GPIO_DIR_R_FWD,
        'R_REV': GPIO_DIR_R_REV,
    }

    print("\n📋 GPIO PIN DIAGNOSTIC\n")
    print("Setting up pins as outputs...")
    for name, pin in pins.items():
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    print("✓ All pins configured\n")

    # Test each pin individually
    print("=" * 50)
    print("TESTING EACH PIN INDIVIDUALLY")
    print("=" * 50)

    for name, pin in pins.items():
        print(f"\n→ Testing {name} (GPIO {pin})")
        print(f"  Setting HIGH for 2 seconds...")
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(2)
        print(f"  Setting LOW for 1 second...")
        GPIO.output(pin, GPIO.LOW)
        time.sleep(1)
        print(f"  ✓ {name} test complete")

    # Test PWM pins
    print("\n" + "=" * 50)
    print("TESTING PWM OUTPUT")
    print("=" * 50)

    try:
        pwm_left = GPIO.PWM(GPIO_LEFT_PWM, 100)
        pwm_right = GPIO.PWM(GPIO_RIGHT_PWM, 100)

        print(f"\n→ PWM on L_PWM (GPIO {GPIO_LEFT_PWM}) - 50% duty for 2s")
        pwm_left.start(50)
        time.sleep(2)
        pwm_left.stop()
        print("  ✓ Done")

        print(f"\n→ PWM on R_PWM (GPIO {GPIO_RIGHT_PWM}) - 50% duty for 2s")
        pwm_right.start(50)
        time.sleep(2)
        pwm_right.stop()
        print("  ✓ Done")

    except Exception as e:
        print(f"  ❌ PWM Error: {e}")

    print("\n" + "=" * 50)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 50)
    print("""
If you heard/saw NOTHING:
  ❌ GPIO pins may not be connected to motor driver
  ❌ Motor driver may not have power
  ❌ Wrong pin numbers in the code

If you saw/heard activity on some pins but not others:
  ⚠ Check those specific pin connections

Check these next:
  1. Is motor driver powered? (check LED or measure 5V/12V)
  2. Are GPIO pins actually connected to motor driver inputs?
  3. Are motor power wires connected to motor driver outputs?
    """)

    GPIO.cleanup()

if __name__ == '__main__':
    try:
        test_pins()
    except KeyboardInterrupt:
        print("\n⚠ Interrupted")
        GPIO.cleanup()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        GPIO.cleanup()
