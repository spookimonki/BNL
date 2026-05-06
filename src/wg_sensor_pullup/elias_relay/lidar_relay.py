#!/usr/bin/env python3
"""Compatibility wrapper for the known-working LD06 ROS 2 driver."""

import os


def main(args=None):
    os.execvp(
        'ros2',
        [
            'ros2',
            'run',
            'ldlidar_stl_ros2',
            'ldlidar_stl_ros2_node',
            '--ros-args',
            '-p', 'product_name:=LDLiDAR_LD06',
            '-p', 'topic_name:=scan',
            '-p', 'frame_id:=lidar_link',
            '-p', 'port_name:=/dev/ttyAMA0',
            '-p', 'port_baudrate:=230400',
            '-p', 'laser_scan_dir:=True',
            '-p', 'enable_angle_crop_func:=False',
            '-p', 'angle_crop_min:=135.0',
            '-p', 'angle_crop_max:=225.0',
        ],
    )


if __name__ == '__main__':
    main()