# Phase 0 — Plan: Autonomous Robot Stack with SLAM + Navigation + Exploration

**Date**: 2026-05-06  
**Workspace**: /home/monki/Desktop/BNL  
**Target**: Raspberry Pi deployment (Pi 4/5)  
**Mission**: SLAM without prior map + Nav2 navigation + frontier exploration + servo-mounted LiDAR

---

## 1. WORKSPACE ANALYSIS STRATEGY

### 1.1 Package Inventory (Known)

| Package | Status | Purpose |
|---------|--------|---------|
| `wg_bringup` | ✅ Exists | Main launch (`wg.launch.py`) |
| `wg_sensor_pullup` | ✅ Exists | Encoder, IMU, motor nodes |
| `wg_utilities` | ✅ Exists | Nav2/SLAM configs |
| `wg_control_center` | ✅ Exists | Servo control code exists |
| `robot_localization` | ✅ Exists | UKF sensor fusion |
| `ldlidar_stl_ros2` | ✅ Exists | LiDAR driver |
| `wg_yolo_package` | ⚠ Unknown | Object detection |
| `wg_picamera` | ⚠ Unknown | Camera driver |
| `simulation_package` | ⚠ Unknown | Gazebo sim |

### 1.2 Analysis Approach

**Read-only first**:
1. Read all `package.xml` files — confirm build types
2. Read all `setup.py` files — find entry points
3. Read all `*.launch.py` files — trace node dependencies
4. Read YAML configs — verify parameters

**Evidence tracing**:
- For each subsystem, find: launch → node → source → hardware interface
- Mark as CONFIRMED only if user verified or code is complete
- Mark as LIKELY if code exists but untested
- Mark as MISSING if no code found

---

## 2. SUBSYSTEM VERIFICATION PLAN

### 2.1 LiDAR (LD06)

**What to verify**:
- [ ] Launch file: `ld06.launch.py` or `wg.launch.py` lidar_node
- [ ] Device path: `/dev/ttyAMA0` or configurable
- [ ] Baud rate: 230400
- [ ] Topic: `/scan` (LaserScan)
- [ ] Frame ID: `lidar_link`

**Evidence types**:
- Code: `wg.launch.py` lidar_node definition
- User confirmation: "lidar sends scans"
- Hardware doc: UART config in `/boot/firmware/config.txt`

**Risk**: Hardcoded device path may not exist on all Pis

---

### 2.2 Wheel Encoders

**What to verify**:
- [ ] Node: `wheelodom.py` in `wg_sensor_pullup`
- [ ] GPIO pins: BCM 4,5,6,17 (from params)
- [ ] Topic: `/odom` or `/odom/raw` (Odometry)
- [ ] TF: Broadcasts `odom → base_link`
- [ ] Parameters: wheel_radius, wheel_base, encoder_resolution

**Evidence types**:
- Code: `wheelodom.py` source
- User confirmation: "wheels move"
- Hardware doc: GPIO pinout verified

**Risk**: Low — uses standard RPi.GPIO, polling mode

---

### 2.3 Motor Control (H-Bridge)

**What to verify**:
- [ ] Node: `vel_to_pmw.py` in `wg_sensor_pullup`
- [ ] PWM pins: GPIO 12, 13
- [ ] Direction pins: 16, 26 (left), 27, 22 (right)
- [ ] Subscription: `/cmd_vel` (Twist)
- [ ] PD control: kp, kd gains
- [ ] Feedback: `/control_event` (PWM output)

**Evidence types**:
- Code: `vel_to_pmw.py` source
- User confirmation: "wheels move"

**Risk**: Requires battery power (not just USB)

---

### 2.4 IMU (BNO085)

**What to verify**:
- [ ] Node: `imuodom.py` in `wg_sensor_pullup/IMU/`
- [ ] I2C address: 0x4A
- [ ] Topic: `/imu/data` (Imu)
- [ ] Frame ID: `imu_link`
- [ ] Orientation: **UPSIDE-DOWN mount compensation?**

**Evidence types**:
- Code: `imuodom.py` source
- Hardware doc: `i2cdetect -y 1` shows 0x4A

**Risk**: HIGH — IMU upside-down, no rotation transform applied

---

### 2.5 State Estimation (UKF)

**What to verify**:
- [ ] Config: `params/ukf.yaml`
- [ ] Inputs: `/odom/raw`, `/imu/data`
- [ ] Output: `/odom/calibrated`
- [ ] Launch: Is UKF node launched in `wg.launch.py`?

**Evidence types**:
- Config file: `ukf.yaml` contents
- Launch file: Check if UKF is enabled

**Risk**: May not be launched (commented out?)

---

## 3. SLAM + NAVIGATION VERIFICATION

### 3.1 SLAM Toolbox

**What to verify**:
- [ ] Launch: `slam_launch_path` in `wg.launch.py`
- [ ] Config: `slam_params.yaml`
- [ ] Mode: `mapping` (not `localization`)
- [ ] Input: `/scan`
- [ ] Output: `/map` (OccupancyGrid)
- [ ] TF: Publishes `map → odom`

**Evidence types**:
- Launch file: `wg.launch.py` lines 95-103
- Config: `slam_params.yaml`

**Status from docs**: ✅ Configured for online SLAM (no prior map)

---

### 3.2 Nav2 Stack

**What to verify**:
- [ ] Launch: `nav2_launch.py` or `bringup_launch.py`
- [ ] Params: `nav2_param.yaml` complete?
- [ ] Servers: planner, controller, smoother, behavior, BT navigator
- [ ] Costmaps: global (map frame), local (odom frame)
- [ ] AMCL: Should be DISABLED for SLAM mode

**Evidence types**:
- Config: `nav2_param.yaml` (285 lines, complete)
- Docs: `ONLINE_SLAM_README.md`

**Status from docs**: ✅ Complete params, AMCL disabled for SLAM mode

---

## 4. FRONTIER EXPLORATION ANALYSIS

### 4.1 Existing Code

**Found**: `explore.py` (68 lines)

**What it does**:
- Creates ActionClient to `navigate_to_pose`
- Sends goals in expanding spiral pattern
- NOT true frontier exploration (no frontier detection)

**Gap**: This is "dumb exploration" — sends precomputed goals, doesn't detect frontiers

### 4.2 True Frontier Exploration Requirements

**Missing components**:
1. **Frontier detection node**:
   - Subscribes to `/map`
   - Detects boundaries between known/unknown space
   - Publishes frontier centroids as goals

2. **Exploration strategy**:
   - Selects best frontier (closest, largest, etc.)
   - Sends goal via Nav2 `navigate_to_pose` action
   - Re-evaluates when goal reached or blocked

**Packages to consider**:
- `explore_lite` — Lightweight frontier exploration
- `frontier_exploration` — Full-featured (may be heavy)

**Decision**: Start with `explore_lite`, upgrade if needed

---

## 5. SERVO-MOUNTED LIDAR DESIGN

### 5.1 Mechanical Model

**Assumptions** (must verify with hardware):
- Servo rotates LiDAR around vertical axis (yaw)
- Scan plane tilts as servo moves
- Need θ(t) function for servo position at time t

**Proposed θ(t)**:
```python
# Sinusoidal oscillation (smooth, reversible)
θ(t) = θ_center + A * sin(ω * t + φ)

# Parameters:
# θ_center = 90° (straight ahead)
# A = 15° (amplitude, ±15° sweep)
# ω = 2π / T (angular frequency, T = period)
# φ = phase offset (for multi-servo sync, usually 0)
```

### 5.2 Servo Oscillator Node Design

**Node**: `servo_oscillator_node`

**Responsibilities**:
1. Define θ(t) as configurable function
2. Publish servo command (PWM or `/servo_cmd` topic)
3. Publish current angle θ(t) with timestamp

**Interfaces**:
```python
# Parameters
- servo_pin: int = 20 (GPIO pin)
- frequency: int = 50 (PWM frequency Hz)
- theta_center: float = 90.0 (degrees)
- amplitude: float = 15.0 (degrees)
- period: float = 2.0 (seconds per sweep)

# Publishers
- /servo_angle (std_msgs/Float64) — current θ(t)
- /servo_cmd (std_msgs/Float64) — command output

# Optional: GPIO output directly
- Uses RPi.GPIO for PWM
```

**Critical**: Use `node.get_clock().now()` for deterministic timing, not loop counters

---

### 5.3 Scan Angle Compensation Node Design

**Node**: `scan_angle_projection_node`

**Responsibilities**:
1. Subscribe to `/scan` (LiDAR sweeps)
2. Subscribe to `/servo_angle` (current θ(t))
3. For each scan:
   - Get scan timestamp
   - Interpolate servo angle at that timestamp
   - Transform each laser point into 3D, then project to 2D ground plane
4. Publish corrected point cloud

**Interfaces**:
```python
# Subscriptions
- /scan (sensor_msgs/LaserScan)
- /servo_angle (std_msgs/Float64)

# Publishers
- /scan_corrected (sensor_msgs/LaserScan) — angle-compensated
- /point_cloud (sensor_msgs/PointCloud2) — 3D projection

# Parameters
- use_time_approximation: bool = True
- max_latency_ms: float = 50.0
```

**Transformation math**:
```python
# For each laser point (range r, angle α in scan frame):
# Servo angle at scan time: θ
# 
# 3D point in lidar_link frame:
# x = r * cos(α) * cos(θ)
# y = r * sin(α) * cos(θ)
# z = r * sin(θ)
#
# Project to 2D ground plane (for SLAM):
# x_2d = sqrt(x² + y²)
# α_2d = atan2(y, x)
```

**Latency handling**:
- If servo_angle message is older than `max_latency_ms`, mark scan as invalid
- Use message_filters for time synchronization

---

## 6. RASPBERRY PI COMPATIBILITY STRATEGY

### 6.1 Hardware Interface Audit

| Interface | Subsystem | Pi Requirement | Verify |
|-----------|-----------|----------------|--------|
| UART0 | LiDAR | `dtoverlay=uart0` | Check config.txt |
| I2C | IMU | `dtparam=i2c_arm=on` | Check config.txt |
| GPIO | Encoders | None | Standard |
| GPIO PWM | Servo + Motors | None | Standard |

### 6.2 Path Auditing

**Known hardcoded paths** (from prior analysis):
- `/home/bnluser/Desktop/Elias_BNL/...` — Must fix

**Strategy**: Replace with `get_package_share_directory()`

### 6.3 Permission Requirements

```bash
# Groups
sudo usermod -aG dialout $USER  # Serial
sudo usermod -aG i2c $USER       # I2C
sudo usermod -aG gpio $USER      # GPIO
```

---

## 7. WHERE I COULD HALLUCINATE FUNCTIONALITY

### 7.1 High-Risk Assumptions

| Assumption | Risk | Verification Needed |
|------------|------|---------------------|
| "SLAM works" | MEDIUM | Check nav2_param.yaml completeness |
| "UKF is enabled" | HIGH | Check wg.launch.py for commented code |
| "Servo code is ROS2 node" | HIGH | `servo_control.py` is standalone CLI, not ROS2 |
| "Frontier exploration works" | HIGH | `explore.py` is spiral pattern, NOT frontier detection |
| "IMU orientation compensated" | HIGH | Check imuodom.py for rotation transform |

### 7.2 Verification Strategy

**DO NOT trust**:
- Documentation claims without code backup
- "Works in simulation" ≠ "Works on real hardware"
- "Code exists" ≠ "Code is launched"

**DO trust**:
- Code that is complete AND launched
- User-verified functionality
- Hardware detection (i2cdetect, ls /dev/tty*)

---

## 8. EXECUTION TIMELINE

### Phase 1: Discovery (Read-Only)
- Scan all packages, launch files, configs
- Read sensor node source code
- Document what's CONFIRMED vs LIKELY vs MISSING
- Output: `discovery_report.md`

### Phase 1.5: Reality Check
- Challenge all assumptions
- Check for hardcoded paths
- Verify Pi-specific requirements
- Output: Updated `discovery_report.md`

### Phase 2: System Design (New Code)
- Create `servo_oscillator_node` (ROS2 node with θ(t))
- Create `scan_angle_projection_node` (timestamp-based compensation)
- Integrate frontier exploration (`explore_lite` or custom)
- Fix IMU orientation transform
- Output: Working nodes + tests

### Phase 3: Pi-Ready Integration
- Create unified `bringup/robot_bringup.launch.py`
- Create `config/hardware.yaml`, `config/nav2.yaml`
- Fix all hardcoded paths
- Create `setup_instructions.md`
- Output: One-command bringup

### Phase 4: Theoretical Validation
- Simulate fresh Pi install
- Document failure modes
- Output: Final report with confidence levels

---

## 9. CRITIQUE OF THIS PLAN

### Weaknesses

1. **Servo hardware unknown**:
   - Don't know servo model (MG90S? SG90?)
   - Don't know mounting geometry
   - Don't know if PWM conflicts with motor PWM

2. **Scan compensation complexity**:
   - LD06 is 2D LiDAR — servo adds 3rd dimension
   - SLAM toolbox expects 2D scans in horizontal plane
   - May need to disable servo for SLAM, enable only for exploration

3. **Frontier exploration gap**:
   - `explore.py` is NOT real frontier exploration
   - Need to integrate `explore_lite` or write custom node
   - May conflict with manual navigation goals

4. **IMU orientation**:
   - Upside-down mount documented but not fixed
   - Will cause yaw drift in UKF

### Mitigation Strategies

1. **Servo**: Start with existing `servo_control.py`, wrap in ROS2 node
2. **Scan compensation**: Make it optional (parameter to enable/disable)
3. **Exploration**: Use `explore_lite` package first, customize later
4. **IMU**: Add rotation transform in `imuodom.py` as immediate fix

---

## 10. OUTPUT FILES

| File | Phase | Purpose |
|------|-------|---------|
| `agent-output/phase0_plan.md` | 0 | This plan |
| `agent-output/discovery_report.md` | 1 | Subsystem audit |
| `agent-output/reality_check.md` | 1.5 | Pi-specific validation |
| `src/wg_bringup/wg_bringup/servo_oscillator.py` | 2 | Servo node |
| `src/wg_bringup/wg_bringup/scan_projection.py` | 2 | Scan compensation |
| `bringup/robot_bringup.launch.py` | 3 | Unified launch |
| `config/hardware.yaml` | 3 | Device paths, pins |
| `config/nav2.yaml` | 3 | Nav2 parameters |
| `config/slam.yaml` | 3 | SLAM parameters |
| `setup_instructions.md` | 3 | apt/pip/permissions |
| `agent-output/change_log.md` | 3 | All changes logged |
| `agent-output/final_report.md` | 4 | Deployment readiness |

---

## 11. SUCCESS CRITERIA

Phase 0 plan is complete when:
- [ ] All subsystems traced from launch to hardware
- [ ] Gaps identified (servo ROS2 node, scan compensation, frontier exploration)
- [ ] Design specs for new nodes documented
- [ ] Pi compatibility requirements listed
- [ ] Risk mitigation strategies defined

**Proceeding to Phase 1: Discovery**
