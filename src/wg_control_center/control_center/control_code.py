import rclpy
from rclpy.node import Node
import yaml
import os
import numpy as np
import math
from data_utilities.qos_profiles import default_qos_profile
from sensor_msgs.msg import Image
from wg_interface.msg import ControlEvent
from ament_index_python import get_package_prefix
from RPi import GPIO
import data_utilities.headers as headers 

class control_node(Node):
    def __init__(self):
        super().__init__('control_node')
        
        self.get_logger().info(f"Node started")

        self.pwm_base_frequency = 500000

        self.pwm_pin_r = 12
        self.pwm_pin_l = 13

        self.direction_pin_r = 16
        self.direction_pin_l = 6

        self.pwm_r = GPIO.PWM(self.pwm_pin_r, self.pwm_base_frequency)
        self.pwm_l = GPIO.PWM(self.pwm_pin_l, self.pwm_base_frequency)

        self.pwm_r.start(0)
        self.pwm_l.start(0)

        self.right_direction = None
        self.left_direction = None

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pwm_pin_r, GPIO.OUT)
        GPIO.setup(self.pwm_pin_l, GPIO.OUT)

        GPIO.setup(self.direction_pin_r, GPIO.OUT)
        GPIO.setup(self.direction_pin_l, GPIO.OUT)

        self.create_subscription(ControlEvent, 'control_event_topic', self.control_event_callback, default_qos_profile)
        

    def control_event_callback(self, msg: ControlEvent):

        type = msg.control_type

        if type == headers.left:
            self.pwm_l.ChangeDutyCycle(msg.left_cycle)
            
            

def main(args=None):
    rclpy.init(args=args)
    control_N = control_node()
    rclpy.spin(control_N)
    control_N.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()


