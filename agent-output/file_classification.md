# Phase 1.5 — File Classification Report

**Date**: 2026-05-06  
**Workspace**: /home/monki/Desktop/BNL  
**Purpose**: Classify every file before cleanup (Phase 3)

---

## Classification System

| Category | Criteria | Action |
|----------|----------|--------|
| **ACTIVE** | Referenced in launch/setup.py, required for runtime | KEEP |
| **DOCUMENTATION** | `.md` files with useful information | KEEP |
| **TEST** | Valid test scripts in `src/*/test/` | KEEP |
| **DIAGNOSTIC** | Debug tools, may be useful for troubleshooting | KEEP (mark) |
| **DUPLICATE** | Same functionality exists elsewhere | DELETE |
| **ORPHAN** | No references, unclear purpose | REVIEW |
| **ARTIFACT** | Build artifacts, cache, malformed files | DELETE |

---

## 1. SAFE TO DELETE (Confirmed)

### 1.1 Build Artifacts

| Path | Reason | Size |
|------|--------|------|
| `build/` | Colcon build intermediates (regenerable) | 4KB |
| `install/` | Colcon install space (regenerable) | 120KB |
| `log/` | Build logs (not needed) | - |
| `src/*/__pycache__/` | Python bytecode cache | - |
| `src/*/*.pyc` | Compiled Python files | - |

**Command to remove**:
```bash
rm -rf build install log
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### 1.2 Malformed Files

| Path | Reason | Size |
|------|--------|------|
| `System" : true,` | Malformed filename (JSON fragment), 0 bytes useful | 9KB |

**Command to remove**:
```bash
rm "System\" : true,"
```

### 1.3 Empty/Test Files

| Path | Reason | Size |
|------|--------|------|
| `test.txt` | Empty test file | 6 bytes |
| `test2.txt` | Empty test file | 19 bytes |

**Command to remove**:
```bash
rm test.txt test2.txt
```

### 1.4 Old TF Diagrams

| Path | Reason | Size |
|------|--------|------|
| `frames_2026-04-28_22.51.35.gv` | Old TF diagram (outdated) | 35 bytes |
| `frames_2026-04-28_22.51.35.pdf` | Old TF diagram (outdated) | 6KB |

**Command to remove**:
```bash
rm frames_2026-04-28_22.51.35.gv frames_2026-04-28_22.51.35.pdf
```

---

## 2. PROBABLY UNUSED (High Confidence)

### 2.1 Replaced Diagnostic Scripts

These scripts were replaced by proper ROS2 nodes:

| File | Replaced By | Reason |
|------|-------------|--------|
| `bno085_simple.py` | `src/wg_sensor_pullup/IMU/imuodom.py` | IMU now in package |
| `bno085_test.py` | `src/wg_sensor_pullup/IMU/imuodom.py` | IMU now in package |
| `encoder_test.py` | `src/wg_sensor_pullup/elias_relay/wheelodom.py` | Encoder now in package |
| `encoder_test_fast.py` | `src/wg_sensor_pullup/elias_relay/wheelodom.py` | Encoder now in package |
| `encoder_test_interrupt.py` | `src/wg_sensor_pullup/elias_relay/wheelodom.py` | Encoder now in package |
| `lidar_test.py` | `ldlidar_stl_ros2_node` | LiDAR now external package |
| `lidar_diagnostic.py` | `ldlidar_stl_ros2_node` | LiDAR now external package |
| `quick_lidar_test.py` | `ldlidar_stl_ros2_node` | LiDAR now external package |
| `motor_test_direct.py` | `src/wg_sensor_pullup/elias_relay/vel_to_pmw.py` | Motor control in package |
| `imu_test_direct.py` | `src/wg_sensor_pullup/IMU/imuodom.py` | IMU now in package |

**Recommendation**: Move to `tools/diagnostic/` instead of delete (useful for debugging)

### 2.2 Replaced Utility Scripts

| File | Replaced By | Reason |
|------|-------------|--------|
| `servo_smooth.py` | `src/wg_bringup/wg_bringup/servo_oscillator.py` | Servo now proper ROS2 node |
| `test_servo.py` | `src/wg_bringup/wg_bringup/servo_oscillator.py` | Servo now proper ROS2 node |

**Recommendation**: DELETE (duplicates of proper nodes)

### 2.3 Demo Scripts (Optional)

| File | Purpose | Keep? |
|------|---------|-------|
| `explore.py` | Spiral pattern navigation | KEEP (demo only, NOT frontier) |
| `random_move.py` | Random walk demo | KEEP (demo only) |

**Note**: `explore.py` is NOT frontier exploration — it's a spiral pattern. True frontier detection requires `explore_lite` package.

### 2.4 Utility Scripts

| File | Purpose | Keep? |
|------|---------|-------|
| `gpio_diagnostic.py` | GPIO pin testing | KEEP (useful for debugging) |
| `check_topics.sh` | Topic health check | KEEP (useful for debugging) |

---

## 3. ACTIVE (Required for Runtime)

### 3.1 ROS2 Packages

| Package | Location | Status |
|---------|----------|--------|
| `robot_localization` | `src/robot_localization/` | ✅ ACTIVE (UKF fusion) |
| `wg_bringup` | `src/wg_bringup/` | ✅ ACTIVE (main launch) |
| `wg_sensor_pullup` | `src/wg_sensor_pullup/` | ✅ ACTIVE (sensor nodes) |
| `wg_utilities` | `src/wg_utilities/` | ✅ ACTIVE (nav2 configs) |
| `wg_control_center` | `src/wg_control_center/` | ⚠ PARTIAL (servo_control.py unused) |
| `wg_picamera` | `src/wg_picamera/` | ⚠ SIM ONLY (not launched in real) |
| `wg_yolo_package` | `src/wg_yolo_package/` | ⚠ EMPTY (entry_points empty) |
| `simulation_package` | `src/sim_folder/` | ⚠ SIM ONLY |
| `wg_interface` | `src/wg_interface/` | ✅ MESSAGES ONLY |

### 3.2 Launch Files

| File | Purpose | Status |
|------|---------|--------|
| `src/wg_bringup/launch/wg.launch.py` | Main bringup | ✅ ACTIVE |
| `src/robot_localization/launch/full_localization.launch.py` | UKF launch | ✅ ACTIVE |
| `src/robot_localization/launch/ukf.launch.py` | UKF config | ⚠ REFERENCED |
| `src/robot_localization/launch/nav2_launch.py` | Nav2 wrapper | ⚠ REFERENCED |
| `install/ldlidar_stl_ros2/.../*.launch.py` | LiDAR examples | ⚠ REFERENCE ONLY |

### 3.3 Configuration Files

| File | Purpose | Status |
|------|---------|--------|
| `config/hardware.yaml` | Hardware parameters | ✅ ACTIVE |
| `src/wg_utilities/nav2/nav2_param.yaml` | Nav2 config | ✅ ACTIVE |
| `src/wg_utilities/nav2/slam_params.yaml` | SLAM config | ✅ ACTIVE |
| `src/wg_utilities/nav2/static_tf.urdf` | Robot description | ✅ ACTIVE |
| `src/wg_utilities/nav2/maps/default_map.yaml` | Placeholder map | ⚠ NO .PGM |
| `src/wg_control_center/control_center/twist_mux.yaml` | Twist mux | ⚠ NOT LAUNCHED |
| `src/robot_localization/params/ukf.yaml` | UKF parameters | ✅ ACTIVE |

### 3.4 Node Source Files

| Package | Node Files | Status |
|---------|------------|--------|
| `wg_bringup` | `servo_oscillator.py`, `scan_projection.py` | ✅ ACTIVE |
| `wg_sensor_pullup` | `wheelodom.py`, `imuodom.py`, `lidar_relay.py`, `vel_to_pmw.py` | ✅ ACTIVE |
| `wg_control_center` | `control_code.py` | ⚠ UNUSED (servo_control.py replaced) |
| `wg_picamera` | `camera_interface.py` | ⚠ SIM ONLY |
| `wg_yolo_package` | `ros_yolo_code.py`, `test.py` | ⚠ EMPTY ENTRY_POINTS |

### 3.5 Documentation

| File | Purpose | Status |
|------|---------|--------|
| `setup_instructions.md` | Pi deployment guide | ✅ KEEP |
| `README.md` | Original README | ✅ KEEP (update needed) |
| `HARDWARE_VERIFICATION_REPORT.md` | Hardware audit | ✅ KEEP |
| `LIDAR_SETUP_GUIDE.md` | LiDAR setup | ✅ KEEP |
| `NAV2_AUDIT.md` | Nav2 configuration audit | ✅ KEEP |
| `ONLINE_SLAM_README.md` | SLAM documentation | ✅ KEEP |
| `ONLINE_SLAM_VALIDATION.md` | SLAM validation | ✅ KEEP |
| `LICENSE` | MIT License | ✅ KEEP |

### 3.6 Agent Output (Current Session)

| File | Purpose | Status |
|------|---------|--------|
| `agent-output/cleanup_plan.md` | Phase 0 plan | ✅ KEEP |
| `agent-output/verification_report.md` | Phase 1 report | ✅ KEEP |
| `agent-output/file_classification.md` | Phase 1.5 report | ✅ KEEP (this file) |
| `agent-output/final_report.md` | Previous phase report | ⚠ HISTORICAL |
| `agent-output/change_log.md` | Previous changes | ⚠ HISTORICAL |
| `agent-output/discovery_report.md` | Previous audit | ⚠ HISTORICAL |
| `agent-output/reality_check.md` | Previous validation | ⚠ HISTORICAL |

---

## 4. UNKNOWN (Needs Review)

| File | Question | Recommendation |
|------|----------|----------------|
| `src/wg_control_center/control_center/servo_control.py` | Replaced by `servo_oscillator.py`? | DELETE (old servo code) |
| `src/wg_yolo_package/ros_yolo_node/test.py` | Test file or example? | REVIEW |
| `private_docker/` | Private docker configs? | KEEP (user decision) |
| `.gitmodules` | Empty file (0 bytes) | DELETE if unused |

---

## 5. RECOMMENDED ACTIONS

### Phase 3: Cleanup (Safe)

```bash
# Build artifacts
rm -rf build install log

# Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Malformed/empty files
rm "System\" : true," test.txt test2.txt

# Old diagrams
rm frames_2026-04-28_22.51.35.gv frames_2026-04-28_22.51.35.pdf

# Replaced servo scripts
rm servo_smooth.py test_servo.py
```

### Phase 3: Cleanup (User Decision)

```bash
# Move diagnostic scripts to tools/ (optional)
mkdir -p tools/diagnostic
mv bno085_simple.py bno085_test.py tools/diagnostic/
mv encoder_test*.py tools/diagnostic/
mv lidar_*.py tools/diagnostic/
mv motor_test_direct.py imu_test_direct.py tools/diagnostic/
```

### Phase 3: DO NOT TOUCH

- All files in `src/*/` (packages)
- All `.yaml` config files
- All `.md` documentation
- `config/hardware.yaml`
- `explore.py`, `random_move.py` (demo scripts)
- `gpio_diagnostic.py`, `check_topics.sh` (debug tools)

---

## 6. POST-CLEANUP STRUCTURE

```
BNL/
├── src/                          # ROS2 packages
│   ├── wg_bringup/               # Main bringup + new nodes
│   ├── wg_sensor_pullup/         # Sensor nodes
│   ├── wg_utilities/             # Nav2 configs
│   ├── wg_control_center/        # Control center
│   ├── wg_picamera/              # Camera (sim)
│   ├── wg_yolo_package/          # YOLO (empty)
│   ├── simulation_package/       # Gazebo sim
│   ├── robot_localization/       # UKF (external)
│   └── wg_interface/             # Messages
├── config/                       # Hardware config
│   └── hardware.yaml
├── tools/                        # Diagnostic tools (optional)
│   └── diagnostic/
├── agent-output/                 # Analysis reports
├── setup_instructions.md         # Pi deployment guide
├── README.md                     # Main documentation (update needed)
└── [other .md files]             # Historical documentation
```

---

**Next Phase**: Phase 2 — Professor-Style Critique
