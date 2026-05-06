#!/usr/bin/env python3
"""Test encoder pulses during motor movement"""
import RPi.GPIO as GPIO
import time
import threading

# Encoder pins from wheelodom.py
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
encoder_last_a = {'left': 0, 'right': 0}

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup encoder inputs
    GPIO.setup(LEFT_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LEFT_PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RIGHT_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RIGHT_PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Setup motor pins
    motor_pins = [GPIO_LEFT_PWM, GPIO_RIGHT_PWM, GPIO_DIR_L_FWD, GPIO_DIR_L_REV, 
                  GPIO_DIR_R_FWD, GPIO_DIR_R_REV]
    for pin in motor_pins:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    
    # Initialize encoder states
    encoder_last_a['left'] = GPIO.input(LEFT_PIN_A)
    encoder_last_a['right'] = GPIO.input(RIGHT_PIN_A)
    
    print("✓ GPIO and encoders initialized")

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
        
        print("\n" + "="*50)
        print("ENCODER TEST - Motor Spinning Forward")
        print("="*50)
        
        set_forward()
        print("\n▶ Starting motors at 60% duty cycle...")
        pwm_left.ChangeDutyCycle(60)
        pwm_right.ChangeDutyCycle(60)
        
        for i in range(5):
            time.sleep(1)
            # Poll encoder A pin state changes
            left_a = GPIO.input(LEFT_PIN_A)
            right_a = GPIO.input(RIGHT_PIN_A)
            
            if left_a != encoder_last_a['left']:
                encoder_counts['left'] += 1
                encoder_last_a['left'] = left_a
            
            if right_a != encoder_last_a['right']:
                encoder_counts['right'] += 1
                encoder_last_a['right'] = right_a
            
            print(f"[{i+1}s] Left: {encoder_counts['left']:4d} pulses | Right: {encoder_counts['right']:4d} pulses | L_A={left_a} R_A={right_a}")
        
        print("\n▶ Stopping motors...")
        pwm_left.ChangeDutyCycle(0)
        pwm_right.ChangeDutyCycle(0)
        
        print("\n" + "="*50)
        if encoder_counts['left'] > 0 or encoder_counts['right'] > 0:
            print("✅ ENCODERS WORKING!")
            print(f"   Left pulses:  {encoder_counts['left']}")
            print(f"   Right pulses: {encoder_counts['right']}")
        else:
            print("❌ NO ENCODER PULSES DETECTED")
            print("   Check:")
            print("   - Encoder wiring (pins 4, 5, 6, 17)")
            print("   - Sensor alignment")
            print("   - Magnet presence on wheels")
        print("="*50)
        
        pwm_left.stop()
        pwm_right.stop()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    setup()
    test_encoders()
