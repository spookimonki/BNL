# BNL Robot - Raspberry Pi Setup Instructions

Complete setup guide for deploying the BNL autonomous robot stack on a Raspberry Pi.

---

## Prerequisites

- Raspberry Pi 4 or Pi 5 (4GB+ RAM recommended)
- SD card with Raspberry Pi OS (Bookworm or Bullseye)
- Internet connection
- SSH access (optional but recommended)

---

## 1. System Configuration

### 1.1 Enable Hardware Interfaces

Edit `/boot/firmware/config.txt` (or `/boot/config.txt` on older systems):

```ini
[all]
# Enable UART for LiDAR
enable_uart=1
dtoverlay=uart0

# For Pi 5: disable Bluetooth to free UART0
dtoverlay=disable-bt

# Enable I2C for IMU
dtparam=i2c_arm=on

# Enable SPI (optional, for future sensors)
dtparam=spi=on
```

**Reboot after changes:**
```bash
sudo reboot
```

### 1.2 Verify Hardware Interfaces

After reboot, verify devices exist:

```bash
# UART (LiDAR) - should show /dev/ttyAMA0 or /dev/serial0
ls -la /dev/ttyAMA0 /dev/serial0

# I2C (IMU) - should show /dev/i2c-1
ls -la /dev/i2c-1

# I2C devices - should show 0x4A for BNO085 IMU
i2cdetect -y 1
```

Expected output from `i2cdetect`:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- 4a -- -- -- -- --
```

---

## 2. User Permissions

### 2.1 Add User to Hardware Groups

```bash
# Serial (LiDAR UART)
sudo usermod -aG dialout $USER

# I2C (IMU)
sudo usermod -aG i2c $USER

# GPIO (encoders, motors, servo)
sudo usermod -aG gpio $USER

# SPI (optional, for future sensors)
sudo usermod -aG spi $USER
```

**Log out and back in** for group changes to take effect.

### 2.2 Alternative: udev Rules (No Reboot Required)

Create `/etc/udev/rules.d/99-robot.rules`:

```udev
# LiDAR serial
KERNEL=="ttyAMA0", MODE="0666"
KERNEL=="serial0", MODE="0666"

# I2C
KERNEL=="i2c-[0-9]*", MODE="0666"

# GPIO
KERNEL=="gpio*", MODE="0666"
KERNEL=="spidev*", MODE="0666"
```

Reload rules:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

## 3. ROS2 Environment

### 3.1 Install ROS2 (If Not Using Docker)

This workspace is designed for ROS2 Jazzy:

```bash
# Add ROS2 repository
sudo apt update && sudo apt install curl gnupg lsb-release
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo apt-key add -
echo "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/ros2.list

# Install ROS2 Jazzy
sudo apt update
sudo apt install ros-jazzy-desktop-full

# Source ROS2
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 3.2 Install System Dependencies

```bash
sudo apt install \
    python3-rpi.gpio \
    python3-smbus \
    i2c-tools \
    python3-serial \
    python3-pip \
    python3-numpy \
    python3-scipy
```

### 3.3 Install Python Dependencies

```bash
pip3 install --user \
    adafruit-circuitpython-bno08x \
    RPi.GPIO \
    numpy
```

---

## 4. Build Workspace

### 4.1 Clone and Build

```bash
# Navigate to workspace
cd /home/bnluser/Desktop/BNL  # Adjust path as needed

# Clean previous builds (optional)
rm -rf build install log

# Build
colcon build --symlink-install --allow-overriding robot_localization

# Source workspace
source install/setup.bash
```

### 4.2 Verify Build

```bash
# Check all packages built
ros2 pkg list | grep wg_

# Expected output:
# wg_bringup
# wg_control_center
# wg_picamera
# wg_sensor_pullup
# wg_utilities
# wg_yolo_package
```

---

## 5. Launch Robot Stack

### 5.1 Real Robot Mode

```bash
cd /home/bnluser/Desktop/BNL
source install/setup.bash

# Full stack launch
ros2 launch wg_bringup wg.launch.py mode:=real
```

### 5.2 Simulation Mode (Gazebo)

```bash
cd /home/bnluser/Desktop/BNL
source install/setup.bash

# Simulation with Gazebo
ros2 launch wg_bringup wg.launch.py mode:=sim
```

### 5.3 With Custom LiDAR Port

If LiDAR is on USB adapter:

```bash
ros2 launch wg_bringup wg.launch.py mode:=real lidar_port:=/dev/ttyUSB0
```

---

## 6. Verify System Health

### 6.1 Check Topics

```bash
# List all topics
ros2 topic list

# Expected topics:
# /scan           - LiDAR scans
# /odom           - Wheel odometry
# /imu/data       - IMU data
# /cmd_vel        - Velocity commands
# /map            - SLAM map
```

### 6.2 Check Topic Data

```bash
# LiDAR scans (should show ~30 Hz)
ros2 topic hz /scan

# Odometry (should show ~10 Hz)
ros2 topic hz /odom

# IMU (should show ~100 Hz)
ros2 topic hz /imu/data
```

### 6.3 Check TF Tree

```bash
# Generate TF tree diagram
ros2 run tf2_tools view_frames.py

# View frames.pdf to verify:
# map -> odom -> base_link -> {lidar_link, imu_link}
```

### 6.4 Check Nodes

```bash
# List all running nodes
ros2 node list

# Expected nodes:
# /lidar_node
# /wheel_odom_node
# /vel_to_pwm_node
# /imu_odom_node
# /servo_oscillator_node
# /scan_projection_node
# /slam_toolbox
# /bt_navigator
# /planner_server
# /controller_server
```

---

## 7. Navigation Testing

### 7.1 Send Navigation Goal

```bash
# Navigate to (2, 0) in map frame
ros2 service call /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose_stamped: {header: {frame_id: 'map'}, \
   pose: {position: {x: 2.0, y: 0.0, z: 0.0}, \
   orientation: {w: 1.0}}}}"
```

### 7.2 Monitor SLAM Map

```bash
# Watch map updates
ros2 topic hz /map

# Should show ~1 Hz (map updates as robot explores)
```

---

## 8. Troubleshooting

### LiDAR Not Working

```bash
# Check serial port exists
ls -la /dev/ttyAMA0

# Check user in dialout group
groups $USER

# Test serial connection
python3 lidar_test.py
```

### IMU Not Detected

```bash
# Check I2C device
i2cdetect -y 1

# Should show 0x4A. If not:
# 1. Check wiring (SDA=GPIO2, SCL=GPIO3)
# 2. Check I2C enabled in config.txt
# 3. Check power to IMU
```

### Motors Not Moving

```bash
# Check GPIO pins
gpio readall  # If wiringPi installed

# Check battery connected to motor driver
# Check PWM signals with oscilloscope
```

### SLAM Not Publishing Map

```bash
# Check /scan has data
ros2 topic echo /scan --once

# Check slam_toolbox is running
ros2 node list | grep slam

# Check SLAM params
ros2 param dump /slam_toolbox
```

---

## 9. Performance Tuning

### Reduce SLAM CPU Load

Edit `config/slam.yaml`:
```yaml
slam_toolbox:
  ros__parameters:
    resolution: 0.10  # Increase from 0.05 to reduce CPU
```

### Reduce Nav2 Frequency

Edit `config/nav2.yaml`:
```yaml
controller_server:
  ros__parameters:
    controller_frequency: 10.0  # Reduce from 20.0
```

### Monitor CPU Temperature

```bash
# Check Pi temperature
vcgencmd measure_temp

# If > 80C, add heatsink/fan
```

---

## 10. Quick Reference

### Start Robot
```bash
source install/setup.bash
ros2 launch wg_bringup wg.launch.py mode:=real
```

### Stop Robot
```bash
Ctrl+C in launch terminal
```

### Check Logs
```bash
cat ~/.ros/log/latest/*.log
```

### Save SLAM Map
```bash
ros2 service call /slam_toolbox/save_map \
  slam_toolbox/srv/SaveMap "{name: {data: 'my_map'}}"
```

---

## 11. Hardware Checklist

Before first launch, verify:

- [ ] UART enabled in config.txt
- [ ] I2C enabled in config.txt
- [ ] User in dialout, i2c, gpio groups
- [ ] LiDAR connected to UART pins (8/10)
- [ ] IMU connected to I2C pins (3/5)
- [ ] Encoders connected to GPIO pins
- [ ] Motor driver connected to PWM pins
- [ ] Battery connected to motor driver
- [ ] Servo connected to GPIO 20

---

**Next Steps**: After successful setup, proceed to:
1. Map your environment using SLAM
2. Test navigation with manual goals
3. Configure frontier exploration (optional)
