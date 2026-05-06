# Elias Arbeid - Wheel Odometry, IMU, and LiDAR

This folder contains Python nodes for reading encoder, IMU, and LiDAR data from Raspberry Pi hardware and publishing ROS 2 topics.

## Structure

- `wheelodom.py` - Wheel encoder odometry node (quadrature decoder + differential drive kinematics)
- `imuodom.py` - IMU data reader over I2C (publishes `/imu/data` for monitoring)
- `lidar_relay.py` - LD06 LiDAR node over the Raspberry Pi UART
- `measurements.yaml` - Robot physical parameters and hardware notes
- `README.md` - This file

## Quick Start

### Build

```bash
cd ~/Desktop/BNL
colcon build
```

### Run Sensor Nodes

```bash
source install/setup.bash

# Wheel odometry (publishes /odom + TF odom→base_link)
ros2 run wg_sensor_pullup wheelodom

# IMU (publishes /imu/data for diagnostics)
ros2 run wg_sensor_pullup imuodom

# LiDAR relay (publishes /scan)
ros2 run wg_sensor_pullup lidar_relay
```

Or launch all sensors together via the main bringup:
```bash
ros2 launch wg_bringup wg.launch.py mode:=real
```

### Check Topics

```bash
# Wheel odometry (kinematic, encoder-only)
ros2 topic echo /odom

# IMU data
ros2 topic echo /imu/data

# LiDAR scan
ros2 topic echo /scan
```

## Robot Measurements

Edit `measurements.yaml` with your actual robot parameters once you hook up the vehicle:

```yaml
wheel_odom:
  wheel_radius: 0.0275     # meters (update after measurement)
  wheel_base: 0.2          # meters (distance between wheels)
  encoder_resolution: 2048  # ticks per revolution

gpio_pins:
  encoder1_pin_a: 4         # BCM GPIO for encoder 1 channel A
  encoder1_pin_b: 17        # BCM GPIO for encoder 1 channel B
  encoder2_pin_a: 5         # BCM GPIO for encoder 2 channel A
  encoder2_pin_b: 6         # BCM GPIO for encoder 2 channel B

uart:
  lidar_port: /dev/serial0   # Raspberry Pi UART alias for pins 8 (TXD) and 10 (RXD)
  lidar_baudrate: 230400
```

## GPIO Pinout

### Encoder Pins (Raspberry Pi BCM numbering)
- **Motor 1 Encoder**: GPIO 4 (A), GPIO 17 (B)
- **Motor 2 Encoder**: GPIO 5 (A), GPIO 6 (B)

### IMU Pins
- **I2C**: SDA (GPIO 2), SCL (GPIO 3)
- **Address**: 0x4A (BNO085)

### LiDAR Pins
- **UART**: TXD GPIO 14 on pin 8, RXD GPIO 15 on pin 10
- **Device**: `/dev/serial0`
- **Baud**: 230400

## Odometry Integration

The wheel odometry node uses:
1. **Quadrature decoding** — reads encoder A and B channels to determine tick count and direction
2. **Exact arc integration** — integrates motion as a circular arc for accurate pose estimation
3. **Yaw normalization** — keeps heading bounded to $[-\pi, \pi]$
4. **Velocity computation** — publishes linear and angular velocities on `/odom`
5. **TF broadcasting** — publishes `odom → base_link` transform directly

## Tuning

### Covariances

Edit `wheelodom.py` to tune covariance matrices:
- `pose.covariance` — position/orientation uncertainty (grows with encoder error)
- `twist.covariance` — velocity uncertainty

Higher values tell Nav2 to trust scan matching more than odometry.

### Encoder Noise

If encoder readings are noisy:
- Verify encoder resolution matches hardware
- Check GPIO pull-up resistor values
- Ensure encoder wheel is tightly mounted

## Troubleshooting

### Node won't start
- Check GPIO permissions: `sudo usermod -a -G gpio $USER`
- Verify Python dependencies: `pip3 install RPi.GPIO rclpy nav_msgs`

### Odometry drifts
- Verify wheel radius and track width measurements
- Check encoder mounting and alignment
- Increase covariances in wheelodom.py to reflect higher uncertainty

### IMU not publishing
- Check I2C bus: `i2cdetect -y 1`
- Verify sensor address (0x4A for BNO085)

## Next Steps

1. **Measure your robot**: wheel radius, track width, actual encoder resolution
2. **Update `measurements.yaml`** with real values
3. **Test wheelodom alone**: `ros2 topic echo /odom`
4. **Test IMU**: verify `ros2 topic echo /imu/data`
5. **Test LiDAR**: verify `ros2 topic echo /scan` on `/dev/serial0`
6. **Tune covariances**: adjust pose/twist covariance in wheelodom.py based on drift
