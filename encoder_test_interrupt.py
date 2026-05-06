#!/usr/bin/env python3
"""Encoder test with interrupt-based edge detection for accurate tick counting"""
import RPi.GPIO as GPIO
import time

# Encoder pins from measurements.yaml
LEFT_PIN_A = 5
LEFT_PIN_B = 6
RIGHT_PIN_A = 4
RIGHT_PIN_B = 17

# Motor pins
GPIO_LEFT_PWM = 13
GPIO_RIGHT_PWM = 12
GPIO_DIR_L_FWD = 16
GPIO_DIR_L_REV = 26
GPIO_DIR_R_FWD = 27
GPIO_DIR_R_REV = 22

encoder_counts = {'left': 0, 'right': 0}

def on_left_encoder(channel):
    """Interrupt callback for left encoder"""
    encoder_counts['left'] += 1

def on_right_encoder(channel):
    """Interrupt callback for right encoder"""
    encoder_counts['right'] += 1

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup encoder inputs with pull-ups
    for pin in [LEFT_PIN_A, LEFT_PIN_B, RIGHT_PIN_A, RIGHT_PIN_B]:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Setup motor pins
    motor_pins = [GPIO_LEFT_PWM, GPIO_RIGHT_PWM, GPIO_DIR_L_FWD, GPIO_DIR_L_REV, 
                  GPIO_DIR_R_FWD, GPIO_DIR_R_REV]
    for pin in motor_pins:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    
    # Add edge detection interrupts on channel A (rising edge means tick)
    GPIO.add_event_detect(LEFT_PIN_A, GPIO.RISING, callback=on_left_encoder, bouncetime=5)
    GPIO.add_event_detect(RIGHT_PIN_A, GPIO.RISING, callback=on_right_encoder, bouncetime=5)
    
    print("✓ GPIO initialized with edge detection")

def set_forward():
    GPIO.output(GPIO_DIR_L_FWD, GPIO.HIGH)
    GPIO.output(GPIO_DIR_L_REV, GPIO.LOW)
    GPIO.output(GPIO_DIR_R_FWD, GPIO.HIGH)
    GPIO.output(GPIO_DIR_R_REV, GPIO.LOW)

def test_encoders():
    pwm_left = GPIO.PWM(GPIO_LEFT_PWM, 100)
    pwm_right = GPIO.PWM(GPIO_RIGHT_PWM, 100)
    
    try:
        pwm_left.start(0)
        pwm_right.start(0)
        
        print("\n" + "="*60)
        print("ENCODER TEST WITH EDGE DETECTION")
        print("="*60)
        
        set_forward()
        print("\n▶ Starting motors at 80% duty cycle for 3 seconds...")
        print("  (Recording encoder ticks via interrupt-based edge detection)\n")
        
        pwm_left.ChangeDutyCycle(80)
        pwm_right.ChangeDutyCycle(80)
        
        # Sample for 3 seconds
        for i in range(3):
            time.sleep(1)
            left_count = encoder_counts['left']
            right_count = encoder_counts['right']
            print(f"[{i+1}s] Left: {left_count:6d} ticks | Right: {right_count:6d} ticks")
        
        print("\n▶ Stopping motors...")
        pwm_left.ChangeDutyCycle(0)
        pwm_right.ChangeDutyCycle(0)
        
        time.sleep(0.5)
        
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        print(f"Left encoder:  {encoder_counts['left']:6d} ticks")
        print(f"Right encoder: {encoder_counts['right']:6d} ticks")
        
        if encoder_counts['left'] > 5 or encoder_counts['right'] > 5:
            print("\n✅ ENCODERS WORKING WELL!")
            print("   You can enable odometry stack for SLAM/Nav2")
        elif encoder_counts['left'] > 0 or encoder_counts['right'] > 0:
            print("\n⚠️  ENCODERS PARTIALLY WORKING")
            print("   Some ticks detected, but check motor speeds and alignment")
        else:
            print("\n❌ NO ENCODER TICKS DETECTED")
            print("   Verify:")
            print("   - Encoder wiring (GPIO 4,5,6,17)")
            print("   - Magnets on wheel hubs")
            print("   - Sensor alignment (usually 2mm gap)")
        print("="*60)
        
        pwm_left.stop()
        pwm_right.stop()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        GPIO.cleanup()
        print("\n✓ GPIO cleaned up")

if __name__ == '__main__':
    setup()
    test_encoders()
