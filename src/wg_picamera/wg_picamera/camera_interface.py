import rclpy
from rclpy.node import Node
import yaml
import os
import numpy as np
import math

from picamera2 import Picamera2
from sensor_msgs.msg import Image
from data_utilities.qos_profiles import default_qos_profile
from ament_index_python import get_package_prefix
import cv2
import datetime as dt
from hashlib import sha256
from time import sleep


class ros_picamera(Node):
    def __init__(self):
        super().__init__('picamera_node')

        self.camera = Picamera2()
        self.config = self.camera.create_still_configuration({"format" : "RGB888"})
        self.camera.configure(self.config)
        self.camera.start()
        
        self.get_logger().info(f"Kamera starta.")

        self.image_publisher = self.create_publisher(Image, 'camera_image', default_qos_profile)

        sleep(1)

        self.timer = self.create_timer(0.1, self.image_callback)

    def image_callback(self):
        image_array = self.camera.capture_array("main")
        image_msg = Image()

        image_msg.encoding = 'bgr8'
        image_msg.data = image_array
        image_msg.width = (self.config["size"])[0]
        image_msg.height = (self.config["size"])[1]
        image_msg.is_bigendian = 0

        self.image_publisher.publish(image_msg)

def main(args=None):
    rclpy.init(args=args)
    picamera_N = ros_picamera()
    rclpy.spin(picamera_N)
    picamera_N.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

