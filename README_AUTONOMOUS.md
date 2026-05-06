# BNL Autonomous Robot Stack

**ROS2 Jazzy | Raspberry Pi 4/5 | SLAM + Nav2 Navigation**

Autonomous exploration robot stack with servo-mounted LiDAR, multi-sensor fusion, and Nav2 navigation.

---

## System Overview

### Architecture

```
SENSORS → STATE ESTIMATION → SLAM → NAVIGATION → ACTUATION
   │            │              │         │           │
   ├─ LiDAR     ├─ Kinematic   ├─ map    ├─ Nav2     ├─ Motor PWM
   ├─ Encoders  ├─ TF tree     ├─ odom   ├─ Planner  └─ Servo (LiDAR mount)
   └─ IMU       └─ /odom                └─ Controller
```

### Key Components

| Subsystem | Component | Status |
|-----------|-----------|--------|
| **Sensors** | LD06 LiDAR (UART) | ✅ Working |
| | Wheel encoders (GPIO) | ✅ Working |
| | BNO085 IMU (I2C) | ✅ Working |
| **State Estimation** | Kinematic odometry (encoders) | ✅ Enabled |
| **Mapping** | slam_toolbox | ✅ Configured |
| **Navigation** | Nav2 stack | ✅ Configured |
| **Actuation** | H-bridge motor control | ✅ Working |
| | Servo-mounted LiDAR | ✅ New (θ(t) oscillation) |

---

## Quick Start (Raspberry Pi)

### Prerequisites

- Raspberry Pi 4/5 with Pi OS (Bookworm/Bullseye)
- ROS2 Jazzy installed
- Hardware: LD06 LiDAR, BNO085 IMU, wheel encoders, motor driver

### 1. System Configuration

Enable hardware interfaces in `/boot/firmware/config.txt`:

```ini
[all]
enable_uart=1
dtoverlay=uart0
dtparam=i2c_arm=on
```

### 2. Install Dependencies

```bash
sudo apt install python3-rpi.gpio python3-smbus python3-serial python3-numpy
pip3 install adafruit-circuitpython-bno08x RPi.GPIO
```

### 3. Build and Launch

```bash
cd /path/to/BNL
colcon build --symlink-install
source install/setup.bash

# Launch autonomous stack
ros2 launch wg_bringup wg.launch.py mode:=real
```

### 4. Send Navigation Goal

```bash
ros2 service call /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose_stamped: {header: {frame_id: 'map'}, \
   pose: {position: {x: 2.0, y: 0.0}, orientation: {w: 1.0}}}}"
```

---

## Servo-Mounted LiDAR System

### θ(t) Oscillation Model

The LiDAR is mounted on a servo that oscillates sinusoidally:

```
θ(t) = 90° + 15° · sin(π · t)

Where:
  - Center angle: 90° (straight ahead)
  - Amplitude: ±15° sweep
  - Period: 2 seconds per full cycle
  - Frequency: 0.5 Hz
```

### Scan Compensation

The `scan_projection` node compensates for servo motion:

- **Input**: Raw `/scan` + `/servo_angle`
- **Processing**: Projects 3D points to horizontal plane
- **Output**: `/scan_corrected` (for SLAM)

**Note**: Scans are rejected when servo tilts > 60° from horizontal to prevent artifacts.

---

## Topic Graph

### Published Topics

| Topic | Type | Publisher | Rate |
|-------|------|-----------|------|
| `/scan` | LaserScan | ldlidar_stl_ros2 | 30 Hz |
| `/scan_corrected` | LaserScan | scan_projection | 30 Hz |
| `/odom` | Odometry | wheelodom | 10 Hz |
| `/imu/data` | Imu | imuodom | 100 Hz |
| `/servo_angle` | Float64 | servo_oscillator | 50 Hz |
| `/map` | OccupancyGrid | slam_toolbox | 1 Hz |

### Subscribed Topics

| Topic | Type | Subscriber |
|-------|------|------------|
| `/cmd_vel` | Twist | vel_to_pwm (motor control) |
| `/scan` | LaserScan | scan_projection, slam_toolbox |
| `/servo_angle` | Float64 | scan_projection |

---

## TF Tree

```
map (SLAM)
  ↓
odom (wheelodom)
  ↓
base_link
  ├── lidar_link (+5cm Z)
  ├── imu_link (+3mm Z, 180° yaw flip)
  └── servo_link (+12cm X, +8cm Z)
```

---

## Packages

| Package | Purpose |
|---------|---------|
| `wg_bringup` | Main launch file, servo oscillator, scan projection |
| `wg_sensor_pullup` | Sensor nodes (wheelodom, imuodom, lidar_relay, vel_to_pmw) |
| `wg_utilities` | Nav2/SLAM configurations |
| `wg_sensor_pullup` | Kinematic odometry + sensors |
| `wg_control_center` | Control center utilities |
| `wg_picamera` | Pi camera interface (sim only) |
| `wg_yolo_package` | YOLO object detection (placeholder) |

---

## Known Limitations

### Critical

1. **Exploration is NOT frontier-based**
   - `explore.py` implements spiral pattern, not true frontier detection
   - **Fix**: Install `explore_lite` package: `sudo apt install ros-jazzy-explore-lite`

2. **Servo tracking latency**
   - Standard servos have 100-200ms response time
   - May cause scan artifacts during fast rotation
   - **Mitigation**: Scans rejected when |θ - 90°| > 60°

3. **Encoder odometry drift**
   - No sensor fusion means drift accumulates over time
   - **Mitigation**: Rely on SLAM scan matching for global consistency

### Medium

4. **IMU yaw drift**
   - BNO085 game-vector mode doesn't use magnetometer
   - Long-term yaw drift expected
   - **Fix**: Enable magnetometer fusion if operating near magnetic north

5. **No loop closure validation**
   - SLAM loop closure not empirically tested
   - **Test**: Drive robot in loop, inspect map for duplicate walls

---

## Verification Checklist

Before deployment, verify:

```bash
# 1. TF tree complete
ros2 run tf2_tools view_frames.py

# 2. Odometry active
ros2 topic hz /odom  # Should show ~10 Hz

# 3. Scan compensation working
ros2 topic echo /scan_corrected  # Check: ranges positive

# 4. IMU transform correct
ros2 run tf2_tools tf2_echo base_link imu_link
# Rotate robot 90° CCW, verify yaw increases

# 5. SLAM publishing
ros2 topic hz /map  # Should show ~1 Hz
```

---

## Hardware Configuration

### GPIO Pinout (BCM)

| Component | Pins |
|-----------|------|
| Left encoder | 5 (A), 6 (B) |
| Right encoder | 4 (A), 17 (B) |
| Motor left | 13 (PWM), 16 (FWD), 26 (REV) |
| Motor right | 12 (PWM), 27 (FWD), 22 (REV) |
| Servo | 20 (PWM) |

### Communication Interfaces

| Device | Interface | Port |
|--------|-----------|------|
| LD06 LiDAR | UART | /dev/ttyAMA0 |
| BNO085 IMU | I2C | 0x4A |

---

## Documentation

| File | Purpose |
|------|---------|
| `setup_instructions.md` | Complete Pi deployment guide |
| `agent-output/final_report.md` | System readiness report |
| `agent-output/verification_report.md` | Package/node inventory |
| `agent-output/critique_report.md` | Professor-style critique |
| `agent-output/file_classification.md` | Cleanup classification |
| `config/hardware.yaml` | Hardware parameters |

---

## Troubleshooting

### LiDAR not detected

```bash
# Check serial port
ls -la /dev/ttyAMA0

# Verify user in dialout group
groups $USER

# Test connection
python3 lidar_test.py
```

### IMU not detected

```bash
# Check I2C device
i2cdetect -y 1  # Should show 0x4A

# Verify wiring (SDA=GPIO2, SCL=GPIO3)
# Check I2C enabled in config.txt
```

### Navigation drift

1. Check odometry: `ros2 topic echo /odom`
2. Verify TF tree: `ros2 run tf2_tools view_frames.py`
3. Tune encoder covariances in wheelodom.py if needed

---

## License

MIT License - see `LICENSE` file.

---

**Note**: Original Docker-focused README preserved in `README.docker.md` if needed.
