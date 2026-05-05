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
import threading


class ros_picamera(Node):
    def __init__(self):
        super().__init__('picamera_node')

        self.image_publisher = self.create_publisher(Image, 'camera_image', default_qos_profile)
        self.timer = self.create_timer(1/10, self.image_callback)

        self.width = 1920
        self.height = 1080

        self.sub_command = ['rpicam-vid',
                            '-t', '0',
                            #'--nopreview',
                            f'--width={self.width}', f'--height={self.height}',
                            '--mode', '1920:1080:8'
                            '-o', '-', 
                           ]
        self.frame_size = int(self.width*self.height)

        self.proc = sp.Popen(self.sub_command, stdout=sp.PIPE, bufsize=10**8)
    
        self.latest_frame = None
        self.lock = threading.Lock()

        self.thread = threading.Thread(target=self.camera_loop, daemon=True)
        self.thread.start()

    def camera_loop(self):
        while rclpy.ok():
            raw_image = self.proc.stdout.read(self.frame_size)

            if len(raw_image) != self.frame_size:
                continue

            with self.lock:
                self.latest_frame = None

    def image_callback(self):
        with self.lock:
            frame = self.latest_frame
        

        if frame is None:
            return
        
        image_array = np.frombuffer(frame, dtype=np.uint8).reshape((self.width, self.height))

        bgr_image = cv2.cvtColor(image_array, cv2.COLOR_BAYER_BG2BGR)

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

