# Hardware Verification Report - May 5, 2026

## ✅ Verified Working

### I2C Bus (IMU)
- **Status**: ✓ **CONFIRMED WORKING**
- **Detection**: `i2cdetect -y 1` found device at address **0x4A**
- **I2C Pins**: SDA GPIO 2, SCL GPIO 3 (pins 3 & 5)
- **Device**: BNO08X IMU
- **Code Alignment**: ✓ `imuodom.py` correctly uses 0x4A (confirmed)
- **Note**: measurements.yaml still references 0x68 (outdated documentation) — ignore

**ROS2 Topic**: `/imu/data` (100 Hz, Imu message)
- Publishes: quaternion, linear_acceleration, angular_velocity
- ⚠️ **Orientation Warning**: IMU mounted **upside-down** with Y+ pointing right (horizontal when robot standing)

---

## ⚠️ Issues Found & Actions Required

### 1. **UART/LiDAR - NOT CONFIGURED** 🔴
**Current Status**: `/dev/serial0` does **NOT exist** (expected but not configured)

**Root Cause**: 
- UART0 overlay not loaded in `/boot/firmware/config.txt`
- Pi 4 has UART on GPIO 14/15 (pins 8/10) but device file alias not created

**Fix (requires file edit + reboot)**:
```bash
# Edit /boot/firmware/config.txt and add under [all] section:
dtoverlay=uart0
enable_uart=1
```

**Then reboot**:
```bash
sudo reboot
```

**Verify after reboot**:
```bash
ls -la /dev/serial0
i2cdetect -y 1
```

---

### 2. **Motor Driver PWM Pins Connected But Not Powered** ⚠️
**Motor Driver PWM Pins**:
- Left PWM: GPIO 13 (pin 33)
- Right PWM: GPIO 12 (pin 32)  
- Left Fwd: GPIO 16, Left Rev: GPIO 26
- Right Fwd: GPIO 27, Right Rev: GPIO 22

**Power Status**: 
- ✓ Connected to **Pi 5V GPIO** (correct for now)
- ⚠️ **NO BATTERY** connected yet
- Motors will not drive until battery power is connected to motor driver

**Expected ROS Topic**: `/control_event` (PWM feedback from vel_to_pmw.py)

---

## GPIO Pinout Summary

### Encoder Pins (Wheel Odometry) ✓
| Motor | Pin A | Pin B | GPIO A | GPIO B |
|-------|-------|-------|--------|--------|
| Right | 7     | 11    | 4      | 17     |
| Left  | 29    | 31    | 5      | 6      |

**ROS Topic**: `/odom/raw` (10 Hz, Odometry message)

### I2C Bus ✓
| Function | GPIO | Pin  |
|----------|------|------|
| SDA      | 2    | 3    |
| SCL      | 3    | 5    |
| Device   | 0x4A | —    |

**ROS Topic**: `/imu/data` (100 Hz)

### LIDAR UART (PENDING SETUP)
| Function | GPIO | Pin |
|----------|------|-----|
| TXD      | 14   | 8   |
| RXD      | 15   | 10  |
| Baud     | —    | 230400 |

**Expected ROS Topic**: `/scan` (30 Hz, LaserScan message)

### Motor Driver PWM (5V ONLY, NO BATTERY)
| Function      | GPIO | Pin |
|---------------|------|-----|
| Left PWM      | 13   | 33  |
| Right PWM     | 12   | 32  |
| Left Fwd      | 16   | 36  |
| Left Rev      | 26   | 37  |
| Right Fwd     | 27   | 13  |
| Right Rev     | 22   | 15  |

**Expected ROS Topic**: `/control_event` (PWM output)

---

## ROS2 Topic Map

| Topic | Source | Type | Freq | Status |
|-------|--------|------|------|--------|
| `/odom/raw` | wheel_odom_node | Odometry | 10 Hz | Ready* |
| `/imu/data` | imu_odom_node | Imu | 100 Hz | Ready* |
| `/scan` | lidar_node | LaserScan | 30 Hz | **BLOCKED** (UART not configured) |
| `/cmd_vel` | (controller input) | Twist | — | N/A |
| `/control_event` | vel_to_pwm_node | ControlEvent | — | **BLOCKED** (no battery) |

*Ready when launched, not currently running

---

## Next Steps

### Immediate (Do Now):
1. ✅ **Verify I2C**: `i2cdetect -y 1` → Should show 4a
2. ⚠️ **Enable UART**: Edit `/boot/firmware/config.txt`, add `dtoverlay=uart0` + `enable_uart=1` under `[all]`
3. ⚠️ **Reboot Pi**: `sudo reboot`
4. ⚠️ **Verify UART**: After reboot, `ls -la /dev/serial0` should exist

### Before Full Testing:
1. Connect LiDAR to GPIO 14/15 (UART)
2. Connect battery to motor driver
3. Launch sensor nodes and verify topics

### Calibration Needed:
1. **IMU Orientation**: IMU upside-down → needs rotation matrix in imuodom.py
   - Currently: Y+ points right (horizontal)
   - Expected: Standard orientation for odometry
   - Fix: Add quaternion rotation in publish_imu() around appropriate axis

---

## Hardware Checklist

- [x] I2C bus enabled in config.txt (dtparam=i2c_arm=on)
- [x] IMU detected on I2C at 0x4A
- [ ] UART0 overlay enabled (PENDING)
- [ ] UART alias /dev/serial0 exists (PENDING)
- [ ] LiDAR connected to GPIO 14/15 (NOT YET)
- [ ] Battery connected to motor driver (NOT YET)
- [ ] GPIO permissions configured (VERIFY)

---

## Test Commands (After UART Setup)

```bash
# Source ROS2
source install/setup.bash

# Check I2C
i2cdetect -y 1

# Launch sensor nodes (in separate terminals)
ros2 run wg_sensor_pullup imuodom_node
ros2 run wg_sensor_pullup wheelodom_node
ros2 run wg_sensor_pullup lidar_node

# Monitor topics
ros2 topic echo /imu/data
ros2 topic echo /odom/raw
ros2 topic echo /scan
```

---

## Notes

- **Measurement.yaml mismatch**: Still says IMU at 0x68, but hardware is at 0x4A. Code is correct.
- **IMU Mounting**: Upside-down orientation requires calibration/transformation
- **Empty Control Code**: control_center/control_code.py is incomplete (not all callbacks implemented)
- **IMU Hardware**: BNO08X (9-axis IMU with rotation vector output)
- **Lidar Model**: LD06 (360° scanner, 12 range points per scan)
