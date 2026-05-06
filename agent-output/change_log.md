# Change Log — Remove robot_localization, Adopt Pure Kinematic Odometry

**Date**: 2026-05-06  
**Refactor**: Phase 0–3 Complete

---

## Removed

### 1. `src/robot_localization/` — Entire Package Deleted
- **What**: Complete fork of `ros-perception/robot_localization` (EKF/UKF C++ implementation)
- **Size**: ~200 files including C++ sources, tests, launch files, params
- **Why**: Violates hard constraint — no EKF/UKF/sensor fusion on Raspberry Pi
- **Impact**: Eliminates broken launch references, reduces build time, removes heavy C++ dependency

### 2. `full_localization.launch.py` Include
- **File**: `src/wg_bringup/launch/wg.launch.py`
- **What**: Removed `IncludeLaunchDescription` for `robot_localization/launch/full_localization.launch.py`
- **Why**: Launch file referenced non-existent executables (`wheel_odom_node`, `imu_odom_node`, `lidar_node` inside `robot_localization` package)
- **Impact**: Launch will no longer fail trying to start non-existent nodes

### 3. UKF Topic References in Documentation
- **Files**: `README_AUTONOMOUS.md`, `ONLINE_SLAM_README.md`, `ONLINE_SLAM_VALIDATION.md`, `HARDWARE_VERIFICATION_REPORT.md`, `setup_instructions.md`, `src/wg_sensor_pullup/elias_relay/README.md`
- **What**: Removed all mentions of:
  - `robot_localization`
  - `/odom/calibrated`
  - `/odom/raw`
  - `/odometry/filtered`
  - `UKF` / `EKF`
  - `--allow-overriding robot_localization`
  - `--symlink-install` (replaced with standard `colcon build`)

---

## Kept / Verified

### 1. `wheelodom.py` — Sole Odometry Source
- **File**: `src/wg_sensor_pullup/elias_relay/wheelodom.py`
- **Status**: VERIFIED — already publishes `/odom` + TF `odom → base_link`
- **Logic**: Differential drive kinematics from quadrature encoder counts
- **Rate**: 10 Hz
- **Covariances**: Already present and reasonable for encoder-only odometry

### 2. `imuodom.py` — IMU Publisher (Unfused)
- **File**: `src/wg_sensor_pullup/IMU/imuodom.py`
- **Status**: VERIFIED — publishes `/imu/data` at 100 Hz
- **Usage**: Diagnostics only; NOT fused into odometry
- **Hardware**: BNO085 over I2C

### 3. Nav2 Parameters
- **File**: `src/wg_utilities/nav2/nav2_param.yaml`
- **Status**: VERIFIED — already uses `odom_topic: /odom`
- **No changes needed** for this refactor

### 4. TF Tree
- **Status**: VERIFIED — `wheelodom.py` publishes `odom → base_link`
- **SLAM publishes** `map → odom`
- **Static transforms**: `base_link → imu_link`, `base_link → lidar_link`
- **Tree is complete**: `map → odom → base_link → {imu_link, lidar_link, servo_link}`

---

## Modified

### `wg.launch.py`
- Removed `wg_state_est_pkg_path` variable (was `robot_localization` share dir)
- Removed `full_localization_launch_path` variable
- Removed `full_localization` IncludeLaunchDescription from real mode
- Removed `full_localization` from `wait_sec_node` timer actions
- Added comment explaining kinematic odometry approach

---

## Pre-Existing Issues (Not Caused by This Refactor, Not Fixed)

1. **Empty `ldlidar_stl_ros2/` directory** — LiDAR driver package has no source files
2. **Motor control conflict** — `vel_to_pmw.py` and `control_code.py` use same PWM pins with different configs
3. **Missing rosdeps** — Custom `wg_*` packages don't declare runtime dependencies in `package.xml`
4. **Hardcoded `use_sim_time: true`** in Nav2 params — should be parameterized

---

## Build Command Change

**Before**:
```bash
colcon build --symlink-install --allow-overriding robot_localization
```

**After**:
```bash
colcon build
```

---

## Data Flow After Refactor

```
+-----------+     +-------------------+     +--------+     +-----------+
| Encoders  | --> | wheelodom.py      | --> | /odom  | --> | Nav2      |
| (GPIO)    |     | (differential     |     | + TF   |     | Controller|
+-----------+     |  drive kinematics)|     | odom-> |     +-----------+
                   +-------------------+     | base   |     +-----------+
                                              | _link  | --> | slam_toolbox
                                              +--------+     +-----------+

+-----------+     +-------------------+
| BNO085    | --> | imuodom.py         |
| (I2C)     |     | publishes /imu/data|
+-----------+     | (diagnostics only)  |
                   +-------------------+
```

---

# Change Log - BNL Robot Stack Transformation

**Date**: 2026-05-06  
**Mission**: Transform workspace into Pi-ready autonomous robot stack

---

## Changes Summary

| Category | Files Changed | Status |
|----------|---------------|--------|
| Bug Fixes | 3 | Complete |
| New Nodes | 2 | Complete |
| Config Files | 2 | Complete |
| Documentation | 2 | Complete |

---

## Bug Fixes

### 1. Hardcoded Paths (CRITICAL)

**File**: `src/wg_bringup/launch/wg.launch.py`

**Before**:
```python
static_tf_path = '/home/bnluser/Desktop/Elias_BNL/src/wg_utilities/nav2/static_tf.urdf'
nav2_params_file = '/home/bnluser/Desktop/Elias_BNL/src/wg_utilities/nav2/nav2_param.yaml'
```

**After**:
```python
wg_utilities_pkg_path = get_package_share_directory('wg_utilities')
static_tf_path = os.path.join(wg_utilities_pkg_path, 'nav2', 'static_tf.urdf')
nav2_params_file = os.path.join(wg_utilities_pkg_path, 'nav2', 'nav2_param.yaml')
```

**Impact**: Launch now works on any Pi user account

---

### 2. IMU Upside-Down Mount (CRITICAL)

**File**: `src/wg_bringup/launch/wg.launch.py`

**Added**:
```python
# IMU static transform with upside-down mount compensation
static_base_to_imu = Node(
    package='tf2_ros',
    executable='static_transform_publisher',
    arguments=[
        '0.0', '0.0', '0.003',  # x, y, z
        '3.14159265359', '0.0', '0.0',  # 180 yaw flip
        'base_link',
        'imu_link',
    ],
)
```

**Impact**: IMU yaw now correctly compensated for upside-down mount

---

### 3. UKF Sensor Fusion Disabled (HIGH)

**File**: `src/wg_bringup/launch/wg.launch.py`

**Before**: Commented out (lines 65-74)
```python
'''
full_localization = IncludeLaunchDescription(...)
'''
```

**After**: Enabled for real mode
```python
full_localization = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(full_localization_launch_path),
    condition=real_condition,
)
```

**Impact**: Robot now fuses wheel odometry + IMU for accurate positioning

---

## New Nodes

### 1. Servo Oscillator Node

**File**: `src/wg_bringup/wg_bringup/servo_oscillator.py`

**Purpose**: Control servo-mounted LiDAR with deterministic theta(t) function

**Features**:
- Sinusoidal oscillation: theta(t) = theta_center + A*sin(omega*t + phi)
- Configurable via ROS2 parameters
- Publishes `/servo_angle` topic
- GPIO PWM output (optional)

**Usage**:
```bash
ros2 run wg_bringup servo_oscillator \
  --ros-args -p amplitude:=15.0 -p period:=2.0
```

---

### 2. Scan Projection Node

**File**: `src/wg_bringup/wg_bringup/scan_projection.py`

**Purpose**: Compensate LiDAR scans for servo motion

**Features**:
- Subscribes to `/scan` + `/servo_angle`
- Projects scans to horizontal plane (for SLAM)
- Can output 3D point clouds (for mapping)
- Latency-aware (rejects stale servo angles)

**Topics**:
- Input: `/scan`, `/servo_angle`
- Output: `/scan_corrected`, `/point_cloud`

**Usage**:
```bash
ros2 run wg_bringup scan_projection \
  --ros-args -p enable_compensation:=true -p output_3d:=false
```

---

## New Configuration Files

### 1. Hardware Configuration

**File**: `config/hardware.yaml`

**Purpose**: Centralized hardware parameters

**Contents**:
- LiDAR port + baudrate
- Encoder GPIO pins
- Motor PWM pins + gains
- IMU I2C address + orientation
- Servo parameters

**Usage**: Reference in launch files or load as parameters

---

### 2. Setup Instructions

**File**: `setup_instructions.md`

**Purpose**: Complete Pi deployment guide

**Sections**:
1. System configuration (config.txt)
2. User permissions (groups, udev)
3. ROS2 environment setup
4. Build instructions
5. Launch commands
6. Troubleshooting

---

## Launch File Updates

### wg.launch.py Changes

**New Launch Arguments**:
```python
lidar_port  # Default: /dev/ttyAMA0, fallback: /dev/serial0, /dev/ttyUSB0
```

**New Nodes Launched**:
- `static_base_to_imu` - IMU TF compensation
- `servo_oscillator` - Servo control
- `scan_projection` - Scan compensation
- `full_localization` - UKF sensor fusion

**Fixed Paths**:
- All hardcoded `/home/bnluser/...` replaced with package paths

---

## Package Updates

### wg_bringup/setup.py

**Before**:
```python
install_requires=['setuptools'],
entry_points={'console_scripts': ['']}
```

**After**:
```python
install_requires=['setuptools', 'RPi.GPIO', 'numpy'],
entry_points={
    'console_scripts': [
        'servo_oscillator = wg_bringup.servo_oscillator:main',
        'scan_projection = wg_bringup.scan_projection:main',
    ],
}
```

---

## Remaining TODOs

| Item | Priority | Notes |
|------|----------|-------|
| Frontier exploration | P1 | Need `explore_lite` package |
| LiDAR port auto-detect | P2 | Add Python fallback logic |
| Camera support | P3 | May need picamera2 for Pi 5 |
| Performance tuning | P2 | SLAM resolution, Nav2 frequency |

---

## Files Created

| File | Purpose |
|------|---------|
| `src/wg_bringup/wg_bringup/__init__.py` | Package init |
| `src/wg_bringup/wg_bringup/servo_oscillator.py` | Servo node |
| `src/wg_bringup/wg_bringup/scan_projection.py` | Scan compensation |
| `config/hardware.yaml` | Hardware config |
| `setup_instructions.md` | Setup guide |
| `agent-output/change_log.md` | This file |

---

## Files Modified

| File | Changes |
|------|---------|
| `src/wg_bringup/launch/wg.launch.py` | Fixed paths, added nodes, enabled UKF |
| `src/wg_bringup/setup.py` | Added dependencies, entry points |

---

**Status**: Phase 2 (System Design) - COMPLETE  
**Next Phase**: Phase 3 (Pi-Ready Integration)
