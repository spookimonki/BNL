import rclpy
from rclpy.node import Node
import yaml
import os
import numpy as np
import math
from sensor_msgs.msg import Image
from data_utilities.qos_profiles import default_qos_profile
from ament_index_python import get_package_prefix
import cv2
import cv_bridge
import datetime as dt
from hashlib import sha256
from time import sleep
import subprocess as sp


class ros_picamera(Node):
    def __init__(self):
        super().__init__('picamera_node')

        self.image_publisher = self.create_publisher(Image, 'camera_image', default_qos_profile)
        self.timer = self.create_timer(1/10, self.image_callback)

        self.width = 1280
        self.height = 720

        self.sub_command = ['rpicam-vid',
                            '-t', '0',
                            '--nopreview',
                            f'--width={self.width}', f'--height={self.height}',
                            '--codec', 'yuv420',
                            '-o', '-', 
                           ]
        self.frame_size = int(self.width*self.height*1.5)   #   YUV greier med formatteringa.

        self.proc = sp.Popen(self.sub_command, stdout=sp.PIPE, bufsize=10**8)
        #self.buff = b""
            
    def image_callback(self):
        
        raw_image = self.proc.stdout.read(self.frame_size)

        if len(raw_image) < self.frame_size:
            return
        
        yuv_data = np.frombuffer(raw_image, dtype=np.uint8).reshape((self.height*3//2, self.width))

        bgr_image = cv2.cvtColor(yuv_data, cv2.COLOR_YUV2BGR_I420)

        image_msg = cv_bridge.CvBridge.cv2_to_imgmsg(bgr_image)
        
        self.image_publisher.publish(image_msg)

def main(args=None):
    rclpy.init(args=args)
    picamera_N = ros_picamera()
    rclpy.spin(picamera_N)
    picamera_N.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

