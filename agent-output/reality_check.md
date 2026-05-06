# Phase 1.5 — Reality Check: Pi Deployment Validation

**Date**: 2026-05-06  
**Focus**: Challenge all assumptions for Raspberry Pi deployment

---

## 1. MACHINE-SPECIFIC PATH AUDIT

### Critical Hardcoded Paths (WILL FAIL ON PI)

| File | Line | Current Path | Pi Reality |
|------|------|--------------|------------|
| `wg.launch.py` | 20 | `/home/bnluser/Desktop/Elias_BNL/src/wg_utilities/nav2/static_tf.urdf` | ❌ Path doesn't exist |
| `wg.launch.py` | 29 | `/home/bnluser/Desktop/Elias_BNL/src/wg_utilities/nav2/nav2_param.yaml` | ❌ Path doesn't exist |
| `wg.launch.py` | 99 | `/home/bnluser/Desktop/Elias_BNL/src/wg_utilities/nav2/slam_params.yaml` | ❌ Path doesn't exist |
| `wg.launch.py` | 163 | `/dev/ttyAMA0` | ⚠ May be `/dev/serial0` |
| `wg.launch.py` | 236 | `/home/${USER}/.BNL_venv/.venv` | ⚠ May not exist |

**Impact**: Launch will fail with `FileNotFoundError`

**Fix Strategy**:
```python
# Replace all hardcoded paths with:
from ament_index_python.packages import get_package_share_directory

# Example:
nav2_params_file = os.path.join(
    get_package_share_directory('wg_utilities'),
    'nav2',
    'nav2_param.yaml'
)
```

---

## 2. DEVICE PATH VARIABILITY

### UART (LiDAR)

| Pi Model | Device Path | Config Required |
|----------|-------------|-----------------|
| Pi 4 | `/dev/ttyAMA0` | `dtoverlay=uart0` |
| Pi 5 | `/dev/ttyAMA0` | `dtoverlay=uart0` + `dtoverlay=disable-bt` |
| Pi Zero | `/dev/ttyAMA0` | `dtoverlay=uart0` |
| Any Pi (USB adapter) | `/dev/ttyUSB0` | None |

**Risk**: `/dev/ttyAMA0` may not exist if:
- UART not enabled in config.txt
- Bluetooth using serial0
- Using Pi 5 without disable-bt overlay

**Mitigation**: Add fallback chain in launch:
```python
# Try in order: /dev/ttyAMA0, /dev/serial0, /dev/ttyUSB0
```

### I2C (IMU)

| Interface | Device | Variability |
|-----------|--------|-------------|
| I2C-1 | `/dev/i2c-1` | Standard on all Pis |

**Risk**: Low — I2C device path is consistent

### GPIO (Encoders, Motors, Servo)

| Interface | Variability |
|-----------|-------------|
| GPIO pins | None (BCM numbering consistent) |
| PWM | Pi 5 uses different PWM hardware |

**Risk**: Low for Pi 4, medium for Pi 5

---

## 3. MISSING DEPENDENCIES

### Python Packages (Not in setup.py)

| Package | Used By | Risk |
|---------|---------|------|
| `RPi.GPIO` | wheelodom.py, vel_to_pmw.py, servo_control.py | HIGH — will fail without |
| `python3-smbus` | imuodom.py (I2C) | MEDIUM — may fail |

**Action**: Add to `setup.py`:
```python
install_requires=[
    'setuptools',
    'adafruit-circuitpython-bno08x',
    'pyserial',
    'RPi.GPIO',  # ADD
],
```

### ROS2 Packages

| Package | Required | Status |
|---------|----------|--------|
| `explore_lite` | Frontier exploration | ❌ Not installed |
| `nav2_bringup` | Navigation | ✅ In Docker |
| `slam_toolbox` | SLAM | ✅ In Docker |

---

## 4. PERMISSION REQUIREMENTS

### Linux Groups (Required)

```bash
# Run once on fresh Pi
sudo usermod -aG dialout $USER   # Serial (LiDAR)
sudo usermod -aG i2c $USER        # I2C (IMU)
sudo usermod -aG gpio $USER       # GPIO (encoders, motors, servo)
```

**Symptoms if missing**:
- No `dialout`: `Permission denied` on `/dev/ttyAMA0`
- No `i2c`: `Permission denied` on I2C bus
- No `gpio`: RPi.GPIO may fail or require sudo

### Alternative: udev Rules

Create `/etc/udev/rules.d/99-robot.rules`:
```
KERNEL=="ttyAMA0", MODE="0666"
KERNEL=="i2c-[0-9]*", MODE="0666"
KERNEL=="gpio*", MODE="0666"
```

---

## 5. PERFORMANCE REALITY CHECK

### CPU Load Estimates (Pi 4 Model B @ 1.5GHz)

| Component | Est. Load | Notes |
|-----------|-----------|-------|
| LiDAR node | 5% | Serial read + point cloud |
| Wheel odometry | 2% | GPIO polling @ 10 Hz |
| IMU node | 5% | I2C read @ 100 Hz |
| SLAM toolbox | 30-50% | 5cm resolution, 10 Hz |
| Nav2 planner | 10-20% | 20 Hz planning |
| Nav2 controller | 5-10% | Local path tracking |
| **Total** | **~60-90%** | Pi 4 may throttle |

**Mitigation**:
- Add heatsink + fan (required for sustained operation)
- Reduce SLAM resolution: `0.05` → `0.10` (10cm)
- Reduce `controller_frequency`: `20.0` → `10.0`

### Memory Estimates

| Component | RAM |
|-----------|-----|
| ROS2 core | 200 MB |
| LiDAR node | 50 MB |
| SLAM toolbox | 150 MB |
| Nav2 stack | 200 MB |
| Sensor nodes | 50 MB |
| **Total** | **~650 MB** |

**Pi 4 2GB**: ✅ Sufficient  
**Pi 4 4GB+**: ✅ Comfortable

---

## 6. HARDWARE ASSUMPTION CHALLENGE

### Assumption: "IMU Works"

**Challenge**: IMU is mounted **upside-down** (documented in HARDWARE_VERIFICATION_REPORT.md)

**Current behavior**:
```python
# imuodom.py:117 — raw sensor data, no compensation
quat_i, quat_j, quat_k, quat_real = quaternion
```

**Expected if robot turns right**:
- Robot yaw: +0.1 rad
- IMU reports: -0.1 rad (because upside-down)
- UKF fuses: conflicting data → drift

**Fix**: Add rotation transform:
```python
# 180° rotation around X axis (upside-down mount)
# q_robot = q_mount ⊗ q_sensor
# q_mount = [1, 0, 0, 0] for 180° around X

# Quaternion multiplication
w1, x1, y1, z1 = 1.0, 0.0, 0.0, 0.0  # mount rotation
w2, x2, y2, z2 = quat_real, quat_i, quat_j, quat_k  # sensor

# Hamilton product
w = w1*w2 - x1*x2 - y1*y2 - z1*z2
x = w1*x2 + x1*w2 + y1*z2 - z1*y2
y = w1*y2 - x1*z2 + y1*w2 + z1*x2
z = w1*z2 + x1*y2 - y1*x2 + z1*w2

# Use (x, y, z, w) as corrected quaternion
```

---

### Assumption: "SLAM Works"

**Challenge**: SLAM expects 2D scans in horizontal plane

**Current setup**: LiDAR is flat (no servo motion for SLAM)

**If servo oscillates during SLAM**:
- Scan plane tilts up/down
- SLAM assumes all points are in horizontal plane
- Result: distorted map, failed scan matching

**Mitigation**: 
- Option A: Disable servo during SLAM mapping
- Option B: Use scan compensation node to project to horizontal plane

---

### Assumption: "Navigation Works"

**Challenge**: Navigation requires accurate odometry

**Current status**: UKF is **commented out** — using raw wheel odometry only

**Consequence**:
- Wheel odometry drifts over time
- Nav2 local costmap will be misaligned with global map
- Robot may think it's somewhere it's not

**Fix**: Enable UKF fusion

---

## 7. WHAT WILL FAIL ON FRESH PI

### Guaranteed Failures (100%)

| Issue | Symptom | Fix |
|-------|---------|-----|
| Hardcoded `/home/bnluser/...` | `FileNotFoundError` | Use `get_package_share_directory()` |
| Missing `dialout` group | `Permission denied` on UART | Run `usermod -aG dialout` |
| Missing `RPi.GPIO` | `ModuleNotFoundError` | Add to `setup.py` |
| UART not enabled | `/dev/ttyAMA0` not found | Add `dtoverlay=uart0` to config.txt |

### Likely Failures (50%+)

| Issue | Symptom | Fix |
|-------|---------|-----|
| IMU upside-down | Yaw drift, oscillation | Add rotation transform |
| UKF disabled | Odometry drift | Uncomment launch |
| No frontier exploration | Robot sends goals to unknown space | Install `explore_lite` |

### Possible Failures (20-50%)

| Issue | Symptom | Fix |
|-------|---------|-----|
| Pi 5 PWM conflict | Motors/servo interfere | Use pigpio library |
| Thermal throttling | Slow performance | Add cooling |
| LiDAR port mismatch | No `/scan` topic | Add port fallback |

---

## 8. SINGLE-COMMAND BRINGUP GAP

### Current State

```bash
# What user expects:
ros2 launch wg_bringup wg.launch.py mode:=real

# What will happen:
# 1. FileNotFoundError: /home/bnluser/... (CRASH)
```

### Required Fixes

| Fix | Priority |
|-----|----------|
| Replace hardcoded paths | P0 |
| Add IMU rotation transform | P0 |
| Enable UKF launch | P1 |
| Create setup script for permissions | P1 |
| Add LiDAR port fallback | P2 |

---

## 9. ACTION ITEMS FOR PHASE 2

### Must Implement

1. [ ] Fix all hardcoded paths in `wg.launch.py`
2. [ ] Add IMU orientation compensation to `imuodom.py`
3. [ ] Uncomment and configure UKF launch
4. [ ] Create `servo_oscillator_node` (ROS2 wrapper)
5. [ ] Create `scan_angle_projection_node`
6. [ ] Create `config/hardware.yaml` with device paths

### Should Implement

7. [ ] Install/configure `explore_lite` for frontier exploration
8. [ ] Add LiDAR port auto-detection
9. [ ] Tune SLAM params for Pi CPU

### Nice to Have

10. [ ] Camera support for Pi 5
11. [ ] Web dashboard for debugging

---

**Next Phase**: Phase 2 — Implement fixes and new nodes
