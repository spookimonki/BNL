#!/bin/bash
source /opt/ros/jazzy/setup.bash
source /home/bnluser/Desktop/Elias_BNL/install/setup.bash

echo "=== CHECKING ROS2 TOPICS ==="
echo ""
echo "→ LiDAR /scan topic:"
timeout 2 ros2 topic echo /scan --once 2>/dev/null | head -5 || echo "  ⚠ No data"

echo ""
echo "→ IMU /imu/data topic:"
timeout 2 ros2 topic echo /imu/data --once 2>/dev/null | head -5 || echo "  ⚠ No data"

echo ""
echo "→ Odometry /odom/raw topic:"
timeout 2 ros2 topic echo /odom/raw --once 2>/dev/null | head -5 || echo "  ⚠ No data"

echo ""
echo "✓ Check complete"
