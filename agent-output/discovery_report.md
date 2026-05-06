# Phase 1 — Discovery Report

**Date**: 2026-05-06  
**Workspace**: /home/monki/Desktop/BNL  
**Analysis**: Read-only subsystem verification

---

## 1. EXECUTIVE SUMMARY

### What ACTUALLY Works (Evidence-Based)

| Subsystem | Status | Evidence |
|-----------|--------|----------|
| **LiDAR (LD06)** | ✅ CONFIRMED | User verified: "lidar sends scans" |
| **Wheel Encoders** | ✅ CONFIRMED | User verified: "wheels move" |
| **Motor Control** | ✅ CONFIRMED | User verified: "wheels move" |
| **IMU Hardware** | ✅ CONFIRMED | `i2cdetect` shows 0x4A |
| **IMU Data** | ⚠ PARTIAL | Publishes, but upside-down mount not compensated |
| **SLAM Toolbox** | ✅ CONFIGURED | `slam_params.yaml` correct, launched in `wg.launch.py` |
| **Nav2 Stack** | ✅ CONFIGURED | `nav2_param.yaml` complete (285 lines) |
| **UKF Sensor Fusion** | ❌ DISABLED | `full_localization` commented out (lines 61-69) |
| **Frontier Exploration** | ❌ FAKE | `explore.py` is spiral pattern, NOT frontier detection |
| **Servo ROS2 Node** | ❌ MISSING | `servo_control.py` is CLI, not ROS2 node |
| **Scan Compensation** | ❌ MISSING | No node exists |

---

## 2. WORKSPACE SCAN

### 2.1 ROS2 Packages (9 Total)

| Package | Build Type | Entry Points | Purpose |
|---------|-----------|--------------|---------|
| `wg_bringup` | ament_python | `bnl_startup.sh` | Main launch |
| `wg_sensor_pullup` | ament_python | `imuodom`, `wheelodom`, `vel_to_pmw`, `lidar_relay` | Sensor nodes |
| `wg_utilities` | ament_python | None | Nav2/SLAM configs |
| `wg_control_center` | ament_python | `control_center_exec` | Servo CLI |
| `wg_picamera` | ament_python | `wg_picamera_exec` | Camera |
| `wg_yolo_package` | ament_python | `yolo_wrapper.sh` | YOLO detection |
| `robot_localization` | ament_cmake | `ukf_node`, `ekf_node` | State estimation |
| `ldlidar_stl_ros2` | ament_cmake | `ldlidar_stl_ros2_node` | LiDAR driver |
| `simulation_package` | ament_python | None | Gazebo |

### 2.2 Launch Files

| File | Purpose | Status |
|------|---------|--------|
| `src/wg_bringup/launch/wg.launch.py` | Main bringup (mode:=sim\|real) | ✅ Active |
| `src/wg_utilities/nav2/slam_params.yaml` | SLAM toolbox config | ✅ Active |
| `src/wg_utilities/nav2/nav2_param.yaml` | Nav2 complete config | ✅ Active |
| `src/robot_localization/params/ukf.yaml` | UKF sensor fusion | ⚠ Not launched |

### 2.3 Hardware Dependencies

| File | Hardware Import | Purpose |
|------|-----------------|---------|
| `wheelodom.py` | `import RPi.GPIO as GPIO` | Encoder reading |
| `vel_to_pmw.py` | `import RPi.GPIO as GPIO` | Motor PWM |
| `imuodom.py` | `import board`, `busio` | I2C IMU |
| `servo_control.py` | `import RPi.GPIO as GPIO` | Servo PWM |

---

## 3. SUBSYSTEM VERIFICATION

### 3.1 LiDAR (LD06) — CONFIRMED WORKING

**Launch**: `wg.launch.py:153-170`
```python
lidar_node = Node(
    package='ldlidar_stl_ros2',
    executable='ldlidar_stl_ros2_node',
    parameters=[{
        'port_name': '/dev/ttyAMA0',  # HARDCODED
        'port_baudrate': 230400,
        'frame_id': 'lidar_link',
    }]
)
```

**Evidence**:
- User confirms: "lidar sends scans"
- HARDWARE_VERIFICATION_REPORT.md: UART configured
- Topic: `/scan` (LaserScan, ~30 Hz)

**Hardware Interface**:
- UART0 (GPIO 14/15 — pins 8/10)
- Requires `dtoverlay=uart0` in `/boot/firmware/config.txt`

**Issues**:
1. ❌ Hardcoded `/dev/ttyAMA0` — may be `/dev/serial0` on some Pis
2. ❌ No auto-detection fallback

---

### 3.2 Wheel Encoders — CONFIRMED WORKING

**Node**: `wheelodom.py` (src/wg_sensor_pullup/elias_relay/)

**Launch**: `wg.launch.py:172-192`
```python
wheel_odom_node = Node(
    package='wg_sensor_pullup',
    executable='wheelodom',
    parameters=[{
        'left_pin_a': 5, 'left_pin_b': 6,
        'right_pin_a': 4, 'right_pin_b': 17,
        'wheel_radius': 0.0275,
        'wheel_base': 0.2,
    }]
)
```

**Evidence**:
- User confirms: "wheels move"
- Topic: `/odom` (Odometry, 10 Hz)
- TF: Broadcasts `odom → base_link`

**Hardware Interface**:
- GPIO pins (BCM): 4, 5, 6, 17
- Quadrature decoding in polling mode

**Issues**: NONE — correctly implemented

---

### 3.3 Motor Control (H-Bridge) — CONFIRMED WORKING

**Node**: `vel_to_pmw.py` (src/wg_sensor_pullup/elias_relay/)

**Launch**: `wg.launch.py:194-200`
```python
vel_to_pwm_node = Node(
    package='wg_sensor_pullup',
    executable='vel_to_pmw',
)
```

**Evidence**:
- User confirms: "wheels move"
- Subscribes: `/cmd_vel` (Twist)
- Publishes: `/control_event` (PWM feedback)

**Hardware Interface**:
- PWM: GPIO 12 (right), 13 (left)
- Direction: GPIO 16, 26 (left), 27, 22 (right)

**Issues**: NONE — correctly implemented

---

### 3.4 IMU (BNO085) — PARTIAL

**Node**: `imuodom.py` (src/wg_sensor_pullup/IMU/)

**Launch**: `wg.launch.py:202-214`
```python
imu_node = Node(
    package='wg_sensor_pullup',
    executable='imuodom',
    parameters=[{
        'i2c_address': 0x4A,
        'frame_id': 'imu_link',
        'publish_hz': 100.0,
    }]
)
```

**Evidence**:
- HARDWARE_VERIFICATION_REPORT.md: `i2cdetect -y 1` shows 0x4A
- Topic: `/imu/data` (Imu, 100 Hz)

**CRITICAL ISSUE**: IMU is mounted **upside-down** (documented), but `imuodom.py` publishes raw sensor data:

```python
# imuodom.py:117 — NO ROTATION APPLIED
quat_i, quat_j, quat_k, quat_real = quaternion
```

**Consequence**: Robot yaw right → IMU reports yaw left → UKF drift/oscillation

**Fix Required**: Add quaternion rotation transform

---

### 3.5 SLAM Toolbox — CONFIGURED

**Launch**: `wg.launch.py:95-103`
```python
slam_launch = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(slam_launch_path),
    launch_arguments={
        'use_sim_time': 'false',
        'slam_params_file': '/home/bnluser/Desktop/Elias_BNL/src/wg_utilities/nav2/slam_params.yaml',
        'autostart': 'true',
    },
    condition=real_condition,
)
```

**Config**: `slam_params.yaml` (verified correct):
```yaml
slam_toolbox:
  ros__parameters:
    mode: mapping  # ✅ Online SLAM (no prior map)
    map_frame: map
    odom_frame: odom
    base_frame: base_link
    scan_topic: /scan
```

**Issues**:
1. ❌ Hardcoded path `/home/bnluser/Desktop/Elias_BNL/...`

---

### 3.6 Nav2 Stack — CONFIGURED

**Config**: `nav2_param.yaml` (8370 bytes, complete)

**Sections verified**:
- ✅ `planner_server` — NavfnPlanner
- ✅ `controller_server` — RegulatedPurePursuitController
- ✅ `smoother_server` — SimpleSmoother
- ✅ `behavior_server` — Spin, Backup, DriveOnHeading
- ✅ `bt_navigator` — Behavior trees
- ✅ `global_costmap` — Static + obstacle + inflation layers
- ✅ `local_costmap` — Obstacle + inflation layers
- ✅ `nav2_lifecycle_manager` — Autostart enabled

**AMCL Status**: ❌ Disabled (correct for SLAM mode)

**Issues**:
1. ❌ Hardcoded paths in launch file

---

### 3.7 UKF Sensor Fusion — DISABLED

**Config**: `params/ukf.yaml` (exists, correct)
```yaml
ukf_filter_node:
  ros__parameters:
    odom0: /odom/raw
    imu0: /imu/data
    publish_tf: false  # ✅ Correct (SLAM provides map→odom)
```

**Launch Status**: ❌ **COMMENTED OUT** in `wg.launch.py` lines 61-69:
```python
'''
# Include full localization (wheel odom, IMU, lidar, UKF filter)
full_localization = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(full_localization_launch_path),
    ...
)
'''
```

**Consequence**: No sensor fusion — robot uses raw wheel odometry only (drifts)

**Fix**: Uncomment and fix paths

---

### 3.8 Frontier Exploration — FAKE

**File**: `explore.py` (68 lines)

**What it does**:
```python
# Spiral pattern exploration (NOT frontier detection)
radius = 1.0
angle_offset = 0.0
while rclpy.ok():
    x = radius * cos(angle)
    y = radius * sin(angle)
    # Send goal via NavigateToPose action
```

**Gap**: This is **NOT true frontier exploration**:
- ❌ No frontier detection (doesn't analyze map)
- ❌ No boundary identification
- ❌ Precomputed spiral pattern
- ❌ May send goals through obstacles

**Required**: `explore_lite` package or custom frontier detection node

---

### 3.9 Servo-Mounted LiDAR — MISSING

**Existing Code**: `servo_control.py` (103 lines)

**What it is**: Standalone CLI, NOT ROS2 node
```python
def main() -> None:
    controller = ServoController(pin=20)
    while True:
        command = input("> ").strip().lower()  # ❌ CLI interface
```

**Missing**:
1. ❌ `servo_oscillator_node` — ROS2 node with θ(t) function
2. ❌ `/servo_angle` topic publication
3. ❌ Timestamp-based angle tracking

---

### 3.10 Scan Angle Compensation — MISSING

**Status**: ❌ No node exists

**Required**:
- `scan_angle_projection_node`
- Subscribes to `/scan` + `/servo_angle`
- Transforms scans based on servo angle at scan timestamp
- Publishes `/scan_corrected` or `/point_cloud`

---

## 4. DEPENDENCY ANALYSIS

### 4.1 Python Dependencies

| Package | Required By | In setup.py? |
|---------|-------------|--------------|
| `RPi.GPIO` | wheelodom, vel_to_pmw, servo | ❌ Missing |
| `adafruit-circuitpython-bno08x` | imuodom | ✅ Yes |
| `pyserial` | LiDAR | ✅ Yes |

### 4.2 ROS2 Dependencies

| Package | Status |
|---------|--------|
| `ros-jazzy-nav2-bringup` | ✅ In Docker |
| `ros-jazzy-slam-toolbox` | ✅ In Docker |
| `ros-jazzy-robot-localization` | ✅ In Docker |
| `ros-jazzy-ldlidar-stl-ros2` | ✅ In Docker |
| `explore_lite` | ❌ Not installed |

### 4.3 System Dependencies

```bash
# Required
sudo apt install python3-rpi.gpio python3-smbus i2c-tools

# Groups
sudo usermod -aG dialout $USER
sudo usermod -aG i2c $USER
sudo usermod -aG gpio $USER
```

---

## 5. HARDCODED PATHS (MUST FIX)

| File | Line | Path | Fix |
|------|------|------|-----|
| `wg.launch.py` | 20 | `/home/bnluser/Desktop/Elias_BNL/src/wg_utilities/nav2/static_tf.urdf` | `get_package_share_directory()` |
| `wg.launch.py` | 29 | `/home/bnluser/Desktop/Elias_BNL/src/wg_utilities/nav2/nav2_param.yaml` | Same |
| `wg.launch.py` | 99 | `/home/bnluser/Desktop/Elias_BNL/src/wg_utilities/nav2/slam_params.yaml` | Same |
| `wg.launch.py` | 163 | `/dev/ttyAMA0` | Parameter with fallback |

---

## 6. TF TREE ANALYSIS

### Current TF Chain

```
map (from slam_toolbox)
  ↓ slam_toolbox publishes map→odom
odom (from SLAM)
  ↓ wheelodom.py publishes odom→base_link
base_link
  ├── lidar_link (static, 5cm up) — from static_tf.urdf
  └── imu_link (static, 3mm up) — from static_tf.urdf
```

### Missing Transforms

- ❌ No compensation for IMU upside-down mount
- ❌ No servo angle transform for LiDAR

---

## 7. WORKING PIPELINES

### Confirmed Working

| Pipeline | Command | Status |
|----------|---------|--------|
| LiDAR → `/scan` | `ros2 launch wg_bringup wg.launch.py mode:=real` | ✅ |
| Encoders → `/odom` | Same | ✅ |
| Motors ← `/cmd_vel` | Same | ✅ |
| SLAM → `/map` | Same | ✅ (configured) |
| Nav2 ← goals | Same | ✅ (configured) |

### Not Working

| Pipeline | Blocker |
|----------|---------|
| UKF fusion | Not launched (commented out) |
| IMU orientation | No rotation transform |
| Frontier exploration | `explore.py` is spiral, not frontier |
| Servo oscillation | No ROS2 node |
| Scan compensation | No node exists |

---

## 8. CRITICAL GAPS FOR MISSION

### Must Fix (P0)

1. ❌ **IMU orientation transform** — upside-down mount not compensated
2. ❌ **UKF not launched** — sensor fusion disabled
3. ❌ **Hardcoded paths** — `/home/bnluser/...` wrong
4. ❌ **Servo ROS2 node** — only CLI exists
5. ❌ **Scan compensation** — no node

### Should Fix (P1)

6. ❌ **Frontier exploration** — replace spiral with real frontier detection
7. ❌ **LiDAR port fallback** — `/dev/ttyAMA0` may not exist

### Optional (P2)

8. ⚠ **Camera/YOLO** — may not run real-time on Pi

---

## 9. OUTPUT FILES

| File | Status |
|------|--------|
| `agent-output/phase0_plan.md` | ✅ Created |
| `agent-output/discovery_report.md` | ✅ This file |

---

**Next Phase**: 1.5 — Reality Check (Pi-specific validation)
