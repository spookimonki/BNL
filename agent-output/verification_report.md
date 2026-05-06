# Phase 1 — Verification Report

**Date**: 2026-05-06  
**Type**: Read-only factual baseline  
**Workspace**: /home/monki/Desktop/BNL

---

## 1. PACKAGE INVENTORY

### 1.1 ROS2 Packages (9 Total)

| Package | Build Type | Location | Entry Points |
|---------|-----------|----------|--------------|
| `robot_localization` | ament_cmake | src/robot_localization | ukf_node, ekf_node (external) |
| `simulation_package` | ament_python | src/sim_folder/src/ | None |
| `wg_bringup` | ament_python | src/wg_bringup | servo_oscillator, scan_projection |
| `wg_control_center` | ament_python | src/wg_control_center | control_center_exec |
| `wg_interface` | ament_python | src/wg_interface | None (messages only) |
| `wg_picamera` | ament_python | src/wg_picamera | wg_picamera_exec |
| `wg_sensor_pullup` | ament_python | src/wg_sensor_pullup | imuodom, wheelodom, vel_to_pmw, lidar_relay |
| `wg_utilities` | ament_python | src/wg_utilities | None (configs only) |
| `wg_yolo_package` | ament_python | src/wg_yolo_package | None (empty entry_points) |

### 1.2 Launch Files (23 Total)

**Active Launch Files**:
| File | Purpose | Status |
|------|---------|--------|
| `src/wg_bringup/launch/wg.launch.py` | Main bringup (sim/real) | ✅ Active |
| `src/robot_localization/launch/full_localization.launch.py` | UKF sensor fusion | ✅ Active |
| `src/robot_localization/launch/ukf.launch.py` | UKF config | ⚠ Referenced |
| `install/ldlidar_stl_ros2/.../ld06.launch.py` | LiDAR standalone | ⚠ Alternative |

**Test Launch Files** (in robot_localization/test/):
- 10 test launch files for bag testing
- Not used in production

---

## 2. NODE INVENTORY

### 2.1 Sensor Nodes

| Node | Package | Executable | Topic(s) | Hardware |
|------|---------|------------|----------|----------|
| `wheelodom` | wg_sensor_pullup | elias_relay/wheelodom.py | /odom (pub) | GPIO 4,5,6,17 |
| `imuodom` | wg_sensor_pullup | IMU/imuodom.py | /imu/data (pub) | I2C 0x4A |
| `lidar_relay` | wg_sensor_pullup | elias_relay/lidar_relay.py | /scan (pub) | UART /dev/ttyAMA0 |
| `vel_to_pmw` | wg_sensor_pullup | elias_relay/vel_to_pmw.py | /cmd_vel (sub), /control_event (pub) | GPIO 12,13,16,22,26,27 |

### 2.2 New Nodes (Added in Phase 2)

| Node | Package | Executable | Topic(s) | Purpose |
|------|---------|------------|----------|---------|
| `servo_oscillator` | wg_bringup | wg_bringup/servo_oscillator.py | /servo_angle (pub) | θ(t) servo control |
| `scan_projection` | wg_bringup | wg_bringup/scan_projection.py | /scan (sub), /servo_angle (sub), /scan_corrected (pub), /point_cloud (pub) | Scan angle compensation |

### 2.3 External Nodes

| Node | Package | Purpose |
|------|---------|---------|
| `ldlidar_stl_ros2_node` | ldlidar_stl_ros2 | LiDAR driver |
| `ukf_node` | robot_localization | UKF sensor fusion |
| `slam_toolbox` | slam_toolbox | SLAM mapping |
| `nav2_*` | nav2_bringup | Navigation stack |

---

## 3. STANDALONE SCRIPTS (Root Directory)

| File | Purpose | Used By | Status |
|------|---------|---------|--------|
| `bno085_simple.py` | IMU test | None | ⚠ Diagnostic |
| `bno085_test.py` | IMU detailed test | None | ⚠ Diagnostic |
| `encoder_test.py` | Encoder interrupt test | None | ⚠ Diagnostic |
| `encoder_test_fast.py` | Encoder polling test | None | ⚠ Diagnostic |
| `encoder_test_interrupt.py` | Encoder edge detection | None | ⚠ Diagnostic |
| `explore.py` | Spiral navigation | None | ⚠ Demo (not frontier) |
| `gpio_diagnostic.py` | GPIO pin test | None | ⚠ Diagnostic |
| `imu_test_direct.py` | IMU direct I2C test | None | ⚠ Diagnostic |
| `lidar_diagnostic.py` | LiDAR serial test | None | ⚠ Diagnostic |
| `lidar_test.py` | LiDAR connection test | None | ⚠ Diagnostic |
| `motor_test_direct.py` | Motor PWM test | None | ⚠ Diagnostic |
| `quick_lidar_test.py` | LiDAR auto-detect test | None | ⚠ Diagnostic |
| `random_move.py` | Random cmd_vel publisher | None | ⚠ Demo |
| `servo_smooth.py` | Servo test (pigpio) | None | ⚠ Replaced by servo_oscillator |
| `test_servo.py` | Servo test (pigpio) | None | ⚠ Duplicate |
| `check_topics.sh` | Topic check script | None | ⚠ Utility |

**Assessment**: All root scripts are diagnostic/demo tools. None are required for production launch.

---

## 4. DEPENDENCY ANALYSIS

### 4.1 Python Dependencies (by setup.py)

| Package | Dependencies |
|---------|-------------|
| wg_sensor_pullup | setuptools, adafruit-circuitpython-bno08x, pyserial |
| wg_bringup | setuptools, RPi.GPIO, numpy |
| wg_picamera | setuptools |
| wg_control_center | setuptools |
| wg_yolo_package | setuptools |
| wg_utilities | setuptools |
| simulation_package | setuptools |

**Missing Dependencies** (used but not declared):
- `RPi.GPIO` — Used in wheelodom.py, vel_to_pmw.py, servo_control.py
- `numpy` — Used in scan_projection.py (added to wg_bringup)
- `sensor_msgs_py` — Used in scan_projection.py

### 4.2 System Dependencies

| Package | Used By | Declared |
|---------|---------|----------|
| python3-rpi.gpio | wheelodom, vel_to_pmw, servo | ⚠ In wg_bringup setup.py |
| python3-smbus | imuodom (I2C) | ❌ Not declared |
| python3-serial | lidar_relay | ✅ As pyserial |
| python3-numpy | scan_projection | ✅ In wg_bringup |

---

## 5. CONFIGURATION FILES

### 5.1 YAML Configs

| File | Purpose | Status |
|------|---------|--------|
| `config/hardware.yaml` | Hardware parameters | ✅ New, complete |
| `src/wg_utilities/nav2/nav2_param.yaml` | Nav2 stack config | ✅ Complete (8370 bytes) |
| `src/wg_utilities/nav2/slam_params.yaml` | SLAM toolbox config | ✅ Complete |
| `src/wg_utilities/nav2/maps/default_map.yaml` | Placeholder map | ⚠ No .pgm file |
| `src/robot_localization/params/ukf.yaml` | UKF config | ✅ Complete |
| `src/robot_localization/params/ekf.yaml` | EKF config (example) | ⚠ Example topics |
| `src/wg_control_center/control_center/twist_mux.yaml` | Twist mux | ⚠ Not launched |

### 5.2 URDF Files

| File | Purpose | Status |
|------|---------|--------|
| `src/wg_utilities/nav2/static_tf.urdf` | Robot description (real) | ✅ Used |
| `src/sim_folder/.../full_robot.urdf` | Gazebo robot model | ⚠ Sim only |

---

## 6. TF TREE ANALYSIS

### 6.1 Static Transforms (from static_tf.urdf)

```
base_link
  ├── lidar_link (xyz: 0,0,0.05)
  └── imu_link (xyz: 0,0,0.003)
```

### 6.2 Dynamic Transforms

| Transform | Publisher | Source |
|-----------|-----------|--------|
| `odom → base_link` | wheelodom.py | Encoder odometry |
| `map → odom` | slam_toolbox | SLAM |

### 6.3 Added Transforms (Phase 2)

| Transform | Publisher | Purpose |
|-----------|-----------|---------|
| `base_link → imu_link` (180° yaw) | static_transform_publisher | IMU upside-down compensation |

### 6.4 Missing Transforms

| Transform | Required For | Status |
|-----------|--------------|--------|
| `servo_link` | Scan compensation | ⚠ Not defined |
| `camera_link` | Camera integration | ⚠ Not defined (if camera used) |

---

## 7. TOPIC GRAPH

### 7.1 Published Topics

| Topic | Type | Publisher | Rate |
|-------|------|-----------|------|
| `/scan` | LaserScan | ldlidar_stl_ros2_node | 30 Hz |
| `/odom` | Odometry | wheelodom_node | 10 Hz |
| `/imu/data` | Imu | imu_odom_node | 100 Hz |
| `/servo_angle` | Float64 | servo_oscillator_node | 50 Hz |
| `/scan_corrected` | LaserScan | scan_projection_node | 30 Hz |
| `/map` | OccupancyGrid | slam_toolbox | 1 Hz |
| `/control_event` | ControlEvent | vel_to_pwm_node | 10 Hz |

### 7.2 Subscribed Topics

| Topic | Type | Subscriber | Purpose |
|-------|------|------------|---------|
| `/cmd_vel` | Twist | vel_to_pwm_node | Motor control |
| `/odom` | Odometry | vel_to_pwm_node | Feedback |
| `/scan` | LaserScan | scan_projection_node, slam_toolbox | Mapping |
| `/servo_angle` | Float64 | scan_projection_node | Compensation |

### 7.3 Topic Mismatches

| Issue | Severity |
|-------|----------|
| `explore.py` uses `/navigate_to_pose` action — correct | ✅ |
| `random_move.py` publishes `/cmd_vel` — conflicts with Nav2 | ⚠ Demo only |
| No frontier detection node — `explore.py` is spiral pattern | ⚠ Gap |

---

## 8. LAUNCH FILE TRACING

### 8.1 wg.launch.py Flow

```
wg.launch.py
├── startup_node (bnl_startup.sh)
├── TimerAction (2s delay)
│   ├── gz_start_node (sim only)
│   ├── bridge_node (sim only)
│   ├── nav2_launch (sim only)
│   ├── nav2_navigation_launch (real only)
│   ├── slam_launch (real only)
│   ├── full_localization (real only) ← UKF enabled
│   ├── robot_state_publisher (real only)
│   ├── static_base_to_imu (real only) ← IMU compensation
│   ├── servo_oscillator (real only) ← NEW
│   ├── scan_projection (real only) ← NEW
│   ├── lidar_node (real only)
│   ├── imu_node (real only)
│   ├── wheel_odom_node (real only)
│   ├── vel_to_pwm_node (real only)
│   ├── wrapper_node (sim only)
│   └── picamera_node (sim only)
```

### 8.2 Path Resolution

**Before Phase 2**:
- Hardcoded: `/home/bnluser/Desktop/Elias_BNL/...`

**After Phase 2**:
- Package-relative: `get_package_share_directory('wg_utilities')`

---

## 9. BUILD ARTIFACTS

| Directory | Contents | Safe to Remove |
|-----------|----------|----------------|
| `build/` | Build intermediates | ✅ Yes |
| `install/` | Built packages | ✅ Yes (rebuildable) |
| `log/` | Build logs | ✅ Yes |
| `agent-output/backups/` | Old backups | ⚠ Review first |
| `agent-output/logs/` | Analysis logs | ⚠ Keep for now |

---

## 10. FILE CLASSIFICATION (Preliminary)

### ACTIVE (Required for Launch)
- All `src/*/` packages
- `config/hardware.yaml`
- `src/wg_utilities/nav2/*.yaml`

### DIAGNOSTIC (Useful for Debugging)
- All `*_test.py`, `*_diagnostic.py` in root
- `check_topics.sh`

### DEMO (Optional Examples)
- `explore.py` (spiral pattern)
- `random_move.py`

### DUPLICATE/REPLACED
- `servo_smooth.py`, `test_servo.py` — Replaced by `servo_oscillator.py`
- `encoder_test*.py` — Replaced by `wheelodom.py`
- `bno085_*.py` — Replaced by `imuodom.py`
- `lidar_*.py` — Replaced by `lidar_node`

### ARTIFACTS (Safe to Delete)
- `build/`, `install/`, `log/`
- `*.pyc`, `__pycache__/`
- `frames_*.gv`, `frames_*.pdf`
- `test.txt`, `test2.txt`
- `System" : true,` (malformed filename)

---

## 11. VERIFICATION SUMMARY

### Verified (Code Evidence)

| Component | Status | Evidence |
|-----------|--------|----------|
| LiDAR node | ✅ Complete | Launched in wg.launch.py |
| Encoder node | ✅ Complete | Launched, GPIO configured |
| Motor node | ✅ Complete | Launched, PWM configured |
| IMU node | ✅ Complete | Launched, I2C configured |
| UKF fusion | ✅ Enabled | full_localization uncommented |
| Servo node | ✅ New | Created, registered in setup.py |
| Scan compensation | ✅ New | Created, registered |
| IMU transform | ✅ Added | static_transform_publisher |

### Theoretically Valid (Not Runtime Tested)

| Component | Reason |
|-----------|--------|
| GPIO functionality | No Pi hardware |
| UART communication | No LiDAR connected |
| I2C communication | No IMU connected |
| SLAM performance | No environment |
| Nav2 navigation | No robot motion |

### Unknown/Gaps

| Component | Gap |
|-----------|-----|
| Frontier exploration | `explore.py` is spiral, not frontier |
| Camera support | Not launched in real mode |
| Twist mux | Config exists, not launched |
| YOLO detection | Empty entry_points |

---

**Next Phase**: 1.5 — Safety Check (deletion classification)
