# Phase 0 — Plan: ROS2 Workspace Analysis & Raspberry Pi Bringup

**Date**: 2026-05-06  
**Workspace**: /home/monki/Desktop/BNL  
**Target**: Raspberry Pi (Pi 4/5 confirmed from hardware docs)

---

## 1. WORKSPACE ANALYSIS STRATEGY

### 1.1 Package Inventory
Scan all ROS2 packages in `src/`:
- `wg_sensor_pullup` — Encoder, IMU, motor control nodes (Python, RPi.GPIO)
- `wg_bringup` — Main launch file (`wg.launch.py`)
- `ldlidar_stl_ros2` — LiDAR driver (UART serial)
- `robot_localization` — State estimation (EKF/UKF)
- `wg_interface` — Custom message definitions
- `wg_utilities` — Nav2 config, SLAM params
- `wg_picamera` — Camera driver (Pi-specific)
- `wg_yolo_package` — Object detection
- `wg_control_center` — Control interface
- `sim_folder/simulation_package` — Gazebo simulation

### 1.2 Launch File Mapping
Identify all entry points:
- `src/wg_bringup/launch/wg.launch.py` — **PRIMARY BRINGUP** (mode:=sim|real)
- `src/robot_localization/launch/*` — EKF/UKF configs
- `install/ldlidar_stl_ros2/.../ld06.launch.py` — LiDAR standalone

### 1.3 Code Inspection Priority
1. **wg.launch.py** — Understands mode switching, node orchestration
2. **wheelodom.py** — GPIO encoder reading (BCM pin mapping)
3. **vel_to_pmw.py** — H-bridge PWM control (GPIO direction + PWM)
4. **imuodom.py** — I2C IMU initialization
5. **lidar_relay.py** — UART auto-detection logic

---

## 2. SUBSYSTEM VERIFICATION STRATEGY

### 2.1 LiDAR (LD06)
**Evidence to find**:
- Launch file: `ld06.launch.py` confirms `/dev/ttyAMA0`, 230400 baud
- Hardware doc: UART overlay enabled in `/boot/firmware/config.txt`
- Test file: `lidar_test.py`, `lidar_diagnostic.py`

**Pi verification**:
- [ ] UART device `/dev/ttyAMA0` or `/dev/serial0` exists after boot
- [ ] User in `dialout` group for serial access
- [ ] LiDAR node parameter matches actual device path

**Risk**: UART requires `dtoverlay=uart0` + reboot (documented in LIDAR_SETUP_GUIDE.md)

### 2.2 Encoders (Wheel Odometry)
**Evidence to find**:
- `wheelodom.py` lines 60-84: GPIO pins 4,5,6,17 (BCM)
- HARDWARE_VERIFICATION_REPORT.md: Confirmed working on pins 7,11,29,31 (physical)

**Pi verification**:
- [ ] GPIO pins match physical wiring
- [ ] User has GPIO access (no sudo required for RPi.GPIO)
- [ ] Polling mode (not interrupts) — more reliable for ROS2

**Risk**: Low — uses standard RPi.GPIO, already tested

### 2.3 Motor Control (H-Bridge)
**Evidence to find**:
- `vel_to_pmw.py` lines 42-58: GPIO setup for PWM + direction
- PWM pins: GPIO 12 (right), 13 (left)
- Direction pins: 16,26 (left), 27,22 (right)

**Pi verification**:
- [ ] PWM frequency (100 Hz) compatible with motor driver
- [ ] 5V logic level matches H-bridge input
- [ ] Battery power required (not USB)

**Risk**: Hardware not powered during dev — untested under load

### 2.4 IMU (BNO085)
**Evidence to find**:
- `imuodom.py` lines 38-51: I2C init, address 0x4A
- HARDWARE_VERIFICATION_REPORT.md: `i2cdetect -y 1` confirmed 0x4A

**Pi verification**:
- [ ] I2C enabled in `/boot/firmware/config.txt`
- [ ] User in `i2c` group
- [ ] Mounting orientation (upside-down noted — needs transform)

**Risk**: Orientation transform not applied — will give wrong yaw

### 2.5 Camera (PiCamera)
**Evidence to find**:
- `wg_picamera` package — executable `wg_picamera_exec`
- Likely uses `picamera2` or `rpicam-apps` (Pi 5)

**Pi verification**:
- [ ] Camera module connected to CSI port
- [ ] Camera enabled in `raspi-config`
- [ ] Correct library for Pi model (Pi 5 uses different stack)

**Risk**: High — camera stack changed on Pi 5, may need rewrite

---

## 3. PIPELINE RECONSTRUCTION STRATEGY

### 3.1 Known Working Paths
From documentation:
1. **LiDAR**: `ros2 launch ldlidar_stl_ros2 ld06.launch.py` → `/scan`
2. **Encoders**: `ros2 run wg_sensor_pullup wheelodom` → `/odom`
3. **IMU**: `ros2 run wg_sensor_pullup imuodom` → `/imu/data`
4. **Motors**: `ros2 run wg_sensor_pullup vel_to_pmw` ← `/cmd_vel`

### 3.2 Full Stack Launch
Primary entry point:
```bash
ros2 launch wg_bringup wg.launch.py mode:=real
```

**What it should launch** (real mode):
- `lidar_node` (UART)
- `wheel_odom_node` (GPIO)
- `imu_odom_node` (I2C)
- `vel_to_pwm_node` (GPIO PWM)
- `slam_toolbox` (SLAM)
- `nav2_bringup/navigation_launch.py` (Nav2 without AMCL)

**What it should NOT launch** (real mode):
- Gazebo simulation
- Nav2 SLAM mode (uses slam_toolbox instead)

### 3.3 Gaps to Fill
From NAV2_AUDIT.md:
- `nav2_param.yaml` is incomplete (missing planner, controller, costmap)
- No map file for AMCL (not needed if using SLAM)
- `full_localization.launch.py` references non-existent nodes

**Action**: Use SLAM mode (slam_toolbox) for initial bringup, add AMCL later

---

## 4. RASPBERRY PI COMPATIBILITY STRATEGY

### 4.1 Hardware Interface Audit

| Interface | Subsystem | Pi Requirement | Status |
|-----------|-----------|----------------|--------|
| UART0     | LiDAR     | `dtoverlay=uart0` | ⚠ Needs config |
| I2C       | IMU       | `dtparam=i2c_arm=on` | ✅ Confirmed |
| GPIO      | Encoders  | None (default) | ✅ Confirmed |
| GPIO PWM  | Motors    | None (hardware PWM) | ⚠ Untested |
| CSI       | Camera    | `camera-auto-alloc=1` | ? Unknown |
| USB       | Fallback  | None | ✅ Available |

### 4.2 Dependency Analysis

**Python packages** (from setup.py):
- `RPi.GPIO` — GPIO access (preinstalled on Pi)
- `adafruit-circuitpython-bno08x` — IMU driver
- `pyserial` — UART communication

**System packages** (to verify):
- `i2c-tools` — for `i2cdetect`
- `python3-smbus` — I2C userspace
- `pigpio` — alternative PWM (not currently used)

**ROS2 packages**:
- `ros-humble-nav2-*` or `ros-jazzy-nav2-*` (workspace uses Jazzy)
- `ros-humble-slam-toolbox` or `ros-jazzy-slam-toolbox`
- `ros-humble-robot-localization` or `ros-jazzy-robot-localization`

### 4.3 Runtime Constraints

**CPU load** (Pi 4/5 considerations):
- SLAM toolbox: ~20-40% on Pi 4, acceptable on Pi 5
- Nav2 planner: Can spike — tune `planner_frequency`
- YOLO detection: May need Coral TPU or downsample

**Memory**:
- Nav2 + SLAM + YOLO: ~500MB-1GB
- Pi 4 4GB: Sufficient
- Pi 5 8GB: Comfortable

**Permissions**:
```bash
# Required groups
sudo usermod -aG dialout $USER  # Serial (LiDAR)
sudo usermod -aG i2c $USER       # I2C (IMU)
sudo usermod -aG gpio $USER      # GPIO (encoders, motors)
```

---

## 5. WHAT COULD BREAK ON PI (RISK ASSESSMENT)

### 5.1 Machine-Specific Assumptions
**Found in code**:
- `/dev/ttyAMA0` hardcoded in `wg.launch.py:163` — may be `/dev/serial0` or `/dev/ttyUSB0`
- `/home/bnluser/Desktop/Elias_BNL/...` — absolute paths in launch file
- `use_sim_time` logic may conflict with real-time sensor timestamps

### 5.2 Performance Assumptions
- SLAM `resolution: 0.05` (5cm) — may be too fine for Pi CPU
- Nav2 `controller_frequency: 20.0` — may need reduction
- No CPU governor tuning (Pi 5 throttles under load)

### 5.3 Hardware Dependencies
- **Pi 5 vs Pi 4**: GPIO pinout same, but:
  - Pi 5 uses `rp1-cgpio` for some pins
  - PWM may require `dtoverlay=pwm-2chan`
  - I2C baud rate may need adjustment

### 5.4 Detection Strategy
- Grep for `/dev/`, `/home/`, `GPIO.BCM`, `board.` patterns
- Check for `sudo` requirements in any node
- Verify all file paths are package-relative, not absolute

---

## 6. EXECUTION PLAN

### Phase 1: Discovery (Read-Only)
1. List all packages with `package.xml`
2. Extract all launch files
3. Read sensor node source (wheelodom, imuodom, vel_to_pmw)
4. Read LiDAR driver config
5. Read nav2 params
6. Output: `agent-output/discovery_report.md`

### Phase 1.5: Reality Check
1. Flag all `/dev/*` paths
2. Flag all absolute paths
3. Check for missing Python deps
4. Verify GPIO/I2C/UART permissions
5. Append to: `agent-output/discovery_report.md`

### Phase 2: Pi-Ready Organization
1. Create `config/hardware.yaml` with device paths
2. Create `bringup/robot_bringup.launch.py` (unified launch)
3. Fix hardcoded paths in `wg.launch.py`
4. Create `setup_instructions.md` (apt/pip/permissions)
5. Output: Organized structure, change log

### Phase 3: Theoretical Validation
1. Simulate fresh Pi install
2. Document exact bringup commands
3. List failure modes and recovery
4. Output: Final report with confidence levels

---

## 7. CRITIQUE OF THIS PLAN

### Potential Weaknesses
1. **Assumes Pi 4/5** — Should confirm exact model from hardware docs
2. **No mention of power** — Motor driver needs battery, not just GPIO
3. **Camera stack unknown** — Pi 5 camera API changed significantly
4. **YOLO real-time feasibility** — May not run at acceptable FPS on Pi CPU

### Mitigation
- Label uncertain items as `UNCONFIRMED` in discovery report
- Document power requirements separately from code
- Mark camera/YOLO as optional for initial bringup
- Prioritize "sensors + nav" over "full stack with vision"

### What This Plan Misses
- Actual Pi model and OS version (Bookworm? Bullseye?)
- Whether workspace was built on Pi or cross-compiled
- Current state of `install/` folder (built or stale?)

**Action**: First discovery step should be `cat /etc/os-release` and `uname -m` to confirm Pi environment.

---

## 8. SUCCESS CRITERIA

Phase 0 plan is complete when:
- [ ] All ROS2 packages identified
- [ ] All hardware interfaces mapped to GPIO/UART/I2C
- [ ] All launch files traced to nodes
- [ ] Missing dependencies listed
- [ ] Pi-specific risks documented
- [ ] Evidence-based confidence per subsystem

**Output location**: `agent-output/plan.md` (this file)
