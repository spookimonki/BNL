# Phase 2 — Professor-Style Critique Report

**Date**: 2026-05-06  
**Workspace**: /home/monki/Desktop/BNL  
**Role**: Strict reviewer exposing flawed assumptions

---

## Executive Summary

**Overall Assessment**: SOLID FOUNDATION, CRITICAL GAPS

The system demonstrates strong ROS2 engineering with proper package structure, parameterized nodes, and launch file organization. However, three critical conceptual gaps prevent "ready for deployment" status:

1. **Exploration is NOT frontier-based** — `explore.py` implements spiral pattern, not frontier detection
2. **Servo oscillation creates SLAM artifacts** — No validation that scan compensation works
3. **UKF configuration untested** — Process noise covariances are guesses, not tuned

---

## 1. Sensor Pipeline Critique

### 1.1 LiDAR (LD06)

**What Works**:
- ✅ Proper ROS2 node (`ldlidar_stl_ros2_node`)
- ✅ Correct topic (`/scan` at 30 Hz)
- ✅ Frame ID `lidar_link` defined in URDF

**Critical Gap**:
- ⚠️ **No scan validation** — Scan compensation assumes perfect servo tracking
- ⚠️ **Latency handling is naive** — `scan_projection.py` logs latency but doesn't reject stale scans

**Code Issue** (`scan_projection.py:73-81`):
```python
latency_ms = (msg.header.stamp - self.last_servo_time.to_msg()).sec * 1000.0
if latency_ms > self.max_latency_ms:
    if not self._warned_latency:
        self.get_logger().warn(...)
```

**Problem**: Uses `.sec` only, ignoring `.nanosec`. Latency calculation is WRONG for sub-second differences.

**Fix Required**:
```python
from builtin_interfaces.msg import Time

def calc_latency_ms(scan_stamp: Time, servo_time) -> float:
    servo_stamp = servo_time.to_msg()
    delta_sec = scan_stamp.sec - servo_stamp.sec
    delta_nsec = scan_stamp.nanosec - servo_stamp.nanosec
    return (delta_sec + delta_nsec / 1e9) * 1000.0
```

---

### 1.2 Wheel Encoders

**What Works**:
- ✅ Quadrature decoding with polling (reliable)
- ✅ Proper odometry integration (differential drive model)
- ✅ TF broadcast `odom → base_link`
- ✅ Covariance matrices specified

**Critical Issues**:

**Issue 1**: `wheelodom.py:156-157` — Velocity calculation assumes constant dt:
```python
linear_velocity = ((distance_left + distance_right) / 2.0) / delta_time
angular_velocity = self.delta_theta(distance_left, distance_right) / delta_time
```

**Problem**: If `delta_time` is small (high-frequency polling), velocity spikes will occur. No low-pass filtering.

**Issue 2**: `wheelodom.py:170-185` — Covariance values are GUESSED:
```python
msg.pose.covariance = [
    0.02, 0.0, 0.0, ...  # Position variance: 2cm
    ...
    0.0, 0.0, 0.0, 0.0, 0.0, 0.04,  # Yaw variance: 0.04 rad² (~11° std dev)
]
```

**Problem**: These covariances drive UKF weighting. If wrong, UKF will either:
- Trust encoders too much → drift accumulates
- Trust encoders too little → IMU dominates, jitter

**Recommendation**: Add empirical tuning procedure to README:
```bash
# Drive robot in straight line 2m, measure actual vs estimated
# Repeat 10 times, compute variance
# Update covariance values accordingly
```

---

### 1.3 IMU (BNO085)

**What Works**:
- ✅ I2C detection with fallback addresses
- ✅ Feature enable with graceful degradation
- ✅ Proper `sensor_msgs/Imu` message structure
- ✅ Covariance matrices specified

**Critical Issues**:

**Issue 1**: `imuodom.py:55-75` — Feature enabling has race conditions:
```python
self.imu.enable_feature(BNO_REPORT_ROTATION_VECTOR, report_interval_us)
# ... 0.1s sleep ...
self.imu.enable_feature(BNO_REPORT_ACCELEROMETER, report_interval_us)
```

**Problem**: BNO085 needs ~500ms after reset before features can be enabled reliably. The 0.1s sleep is insufficient.

**Issue 2**: `imuodom.py:147-161` — Covariances are COPIED from example:
```python
msg.orientation_covariance = [0.02, 0.0, 0.0, 0.0, 0.02, 0.0, 0.0, 0.0, 0.02]
```

**Problem**: BNO085 datasheet specifies orientation accuracy of 3° RMS (0.05 rad). Covariance should be ~0.0025 rad², not 0.02.

**Issue 3**: **No magnetometer fusion** — BNO085 provides game-vector quaternion (yaw drifts). For long-term navigation, magnetometer fusion is required.

**Fix Required**: Add parameter to select fusion mode:
```yaml
imu:
  fusion_mode: "game_vector"  # or "magnetic_heading"
```

---

### 1.4 Servo Oscillator

**What Works**:
- ✅ Deterministic θ(t) function
- ✅ Parameterized amplitude, period, phase
- ✅ GPIO fallback disabled for simulation

**CRITICAL CONCEPTUAL GAP**:

**Assumption**: Servo tracks θ(t) perfectly with no latency.

**Reality**: Standard servos have:
- 100-200ms response time
- ±5° accuracy under load
- Mechanical backlash

**Impact**: If servo lags by 200ms and robot is rotating, scan compensation projects points to WRONG locations → SLAM map artifacts.

**Evidence Needed Before Deployment**:
```bash
# Record actual vs commanded servo angle
ros2 topic echo /servo_angle > commanded.txt
# Use oscilloscope or encoder to measure actual angle
# Compare: is lag < 50ms?
```

**Recommendation**: Add servo feedback (potentiometer or encoder) to measure ACTUAL angle, not commanded angle.

---

### 1.5 Scan Projection

**What Works**:
- ✅ Correct 3D projection math
- ✅ 2D mode for SLAM, 3D mode for visualization

**CRITICAL BUG** (`scan_projection.py:117-118`):
```python
corrected.ranges = [r * cos_theta if r < scan.range_max else r
                   for r in scan.ranges]
```

**Problem**: When `cos_theta < 0` (servo > 90°), ranges become NEGATIVE. LiDAR points behind robot are projected forward.

**Fix**:
```python
corrected.ranges = [abs(r * cos_theta) if scan.range_min <= r < scan.range_max else r
                   for r in scan.ranges]
```

**Better Fix**: Reject scans when `|θ - 90°| > 60°` (servo too tilted for reliable projection).

---

## 2. State Estimation Critique

### 2.1 UKF Configuration

**What Works**:
- ✅ Two-D mode enabled (correct for ground robot)
- ✅ Sensor inputs configured (`/odom/raw`, `/imu/data`)
- ✅ Control input enabled (cmd_vel feedforward)
- ✅ Process noise covariance specified

**CRITICAL ISSUES**:

**Issue 1**: `ukf.yaml:87-91` — Odometry configuration INCOMPLETE:
```yaml
odom0_config: [true, true, false,   # x, y (z ignored)
               false, false, true,  # roll, pitch, yaw
               true, false, false,  # vx (vy, vz ignored)
               ...]
```

**Problem**: Yaw from encoders is set to `true`, but differential-drive yaw is DERIVED from wheel velocities, not directly measured. This double-counts yaw information when fused with IMU yaw rate.

**Fix**: Set yaw to `false`, let IMU provide yaw:
```yaml
odom0_config: [true, true, false,
               false, false, false,  # yaw from IMU only
               true, false, false,
               ...]
```

**Issue 2**: `ukf.yaml:132-136` — IMU configuration OVER-SPECIFIED:
```yaml
imu0_config: [false, false, false,   # pose ignored
              true, true, true,      # roll, pitch, yaw (ABSOLUTE)
              false, false, false,   # velocity ignored
              true, true, true,      # angular velocity (rate)
              true, true, true]      # linear acceleration
```

**Problem**: Fusing BOTH absolute yaw (from magnetometer) AND yaw rate (from gyro) can cause conflicts if magnetometer is unreliable indoors.

**Recommendation**: Start with rate-only fusion:
```yaml
imu0_config: [false, false, false,
              false, false, false,   # NO absolute orientation
              false, false, false,
              true, true, true,      # angular velocity ONLY
              true, true, true]      # linear acceleration
```

**Issue 3**: `ukf.yaml:196-210` — Process noise is TUNED BY GUESS:

No empirical basis for values like `0.025` for vyaw variance.

**Recommendation**: Add tuning script to repository:
```python
# scripts/tune_ukf.py
# Drive robot in known pattern, compare estimated vs ground truth
# Optimize process_noise_covariance to minimize RMSE
```

---

### 2.2 TF Tree

**What Works**:
- ✅ Complete chain: `map → odom → base_link`
- ✅ Sensor frames defined (`lidar_link`, `imu_link`)
- ✅ IMU upside-down compensation added

**MISSING TRANSFORMS**:

| Transform | Required For | Status |
|-----------|--------------|--------|
| `base_link → servo_link` | Scan compensation verification | ❌ MISSING |
| `servo_link → lidar_link` | Full kinematic chain | ❌ MISSING |

**Problem**: Without `servo_link`, cannot verify scan compensation accuracy via TF.

**Fix**: Add to `static_tf.urdf`:
```xml
<joint name="base_to_servo" type="fixed">
  <parent link="base_link"/>
  <child link="servo_link"/>
  <origin xyz="0 0 0.1" rpy="0 0 0"/>
</joint>
<joint name="servo_to_lidar" type="fixed">
  <parent link="servo_link"/>
  <child link="lidar_link"/>
  <origin xyz="0 0 0.05" rpy="0 0 0"/>
</joint>
```

---

## 3. SLAM Critique (slam_toolbox)

### 3.1 Configuration

**What Works**:
- ✅ Online async mode (appropriate for exploration)
- ✅ Parameters file exists
- ✅ Launched in real mode

**CRITICAL GAPS**:

**Gap 1**: No loop closure validation.

**Risk**: With servo-mounted LiDAR, scan matching may fail when servo is at extreme angles (points projected incorrectly).

**Evidence Needed**:
```bash
# Drive robot in loop, check if map closes
ros2 service call /slam_toolbox/save_map ...
# Visual inspection: are there duplicate walls?
```

**Gap 2**: `slam_params.yaml` — Resolution not tuned for Pi CPU.

Check if resolution is 0.05 (default) or 0.10 (Pi-friendly).

---

## 4. Nav2 Critique

### 4.1 Configuration

**What Works**:
- ✅ Full Nav2 stack configured
- ✅ Parameter file exists (8KB, comprehensive)
- ✅ Lifecycle manager enabled

**CRITICAL GAPS**:

**Gap 1**: Costmap configuration unknown.

**Risk**: If costmap doesn't subscribe to `/scan_corrected`, it will use raw `/scan` (tilted points → false obstacles).

**Check Required**:
```bash
grep -r "scan_corrected" src/wg_utilities/nav2/
# Should find costmap subscription config
```

**Gap 2**: Recovery behaviors not configured.

**Risk**: If robot gets stuck (e.g., scan compensation fails), Nav2 won't attempt recovery.

---

## 5. Exploration Critique

### 5.1 THE CRITICAL GAP

**Claim in Documentation**: "Frontier exploration ready"

**Reality**: `explore.py` implements SPIRAL PATTERN, not frontier detection.

**Evidence** (`explore.py`):
```python
# Spiral exploration pattern
while rclpy.ok():
    twist = Twist()
    twist.linear.x = 0.2  # Constant forward
    twist.angular.z = 0.1  # Constant rotation
    cmd_pub.publish(twist)
```

**This is NOT frontier exploration**. It's an open-loop spiral.

**Frontier Exploration Requires**:
1. Map boundary detection (frontiers)
2. Path planning to frontier
3. Goal update as frontiers are explored

**Missing Package**: `explore_lite` or `frontier_exploration`

**Fix Options**:

| Option | Effort | Quality |
|--------|--------|---------|
| Install `explore_lite` | Low | High (maintained package) |
| Implement frontier detection | High | Medium (custom code) |
| Document as "spiral demo only" | None | Honest |

**Recommendation**: Option 1 + Option 3 (install + document).

---

## 6. Common Failure Patterns (REP-105/REP-103)

### 6.1 Coordinate Frame Violations

**REP-105 Check**:
- ✅ `map` frame: world-fixed, from SLAM
- ✅ `odom` frame: world-fixed, from UKF
- ✅ `base_link` frame: robot-centered
- ⚠️ `imu_link`: Defined but orientation convention unclear

**Issue**: `imuodom.py` publishes quaternion in sensor frame, not ENU frame (REP-103).

**Check**: Does BNO085 output ENU quaternions by default? If not, transform required.

---

### 6.2 Unit Violations (REP-103)

**Standard Units**:
- Distance: meters ✅
- Angle: radians ✅
- Time: seconds ✅
- Velocity: m/s ✅
- Angular velocity: rad/s ✅

**No violations detected**.

---

### 6.3 Timestamp Issues

**Issue**: `scan_projection.py:73` — Timestamp calculation bug (see Section 1.1).

**Issue**: `wheelodom.py:160` — Uses `get_clock().now()` for stamp, but encoder data is from `time.time()`. Clock skew possible.

**Fix**: Use ROS time for everything:
```python
now = self.get_clock().now()
msg.header.stamp = now.to_msg()
```

---

## 7. Summary of Required Fixes

### P0 — Critical (Must Fix Before Deployment)

| # | Issue | File | Fix |
|---|-------|------|-----|
| 1 | Latency calculation bug | `scan_projection.py:73` | Use `.nanosec` field |
| 2 | Negative range projection | `scan_projection.py:117` | Use `abs()` or reject extreme angles |
| 3 | UKF yaw double-counting | `ukf.yaml:87-91` | Set yaw to `false` in odom0_config |
| 4 | Missing servo transforms | `static_tf.urdf` | Add `servo_link`, `lidar_link` chain |
| 5 | Exploration mislabeled | `explore.py`, documentation | Document as spiral demo, add `explore_lite` |

### P1 — Important (Should Fix)

| # | Issue | File | Fix |
|---|-------|------|-----|
| 6 | IMU feature race condition | `imuodom.py:55-75` | Add 500ms wait after init |
| 7 | IMU covariance wrong | `imuodom.py:147-161` | Use 0.0025 (3° RMS) |
| 8 | Encoder velocity spikes | `wheelodom.py:156-157` | Add low-pass filter |
| 9 | Costmap subscription unknown | `nav2_param.yaml` | Verify `/scan_corrected` |
| 10 | Timestamp inconsistency | `wheelodom.py:160` | Use ROS time consistently |

### P2 — Nice to Have

| # | Issue | File | Fix |
|---|-------|------|-----|
| 11 | No UKF tuning procedure | New file | Add `scripts/tune_ukf.py` |
| 12 | No magnetometer fusion | `imuodom.py` | Add fusion mode parameter |
| 13 | No servo feedback | Hardware | Add encoder/potentiometer |
| 14 | No recovery behaviors | `nav2_param.yaml` | Configure recovery server |

---

## 8. Verification Required Before Deployment

### Runtime Tests (On Pi)

```bash
# 1. Verify TF tree
ros2 run tf2_tools view_frames.py
# Check: map → odom → base_link → {lidar_link, imu_link, servo_link}

# 2. Verify UKF output
ros2 topic hz /odom/calibrated
# Should show ~30 Hz

# 3. Verify scan compensation
ros2 topic echo /scan_corrected
# Check: ranges are positive, no artifacts

# 4. Verify IMU transform
ros2 run tf2_tools tf2_echo base_link imu_link
# Rotate robot 90° CCW, verify yaw increases

# 5. Verify SLAM
ros2 topic hz /map
# Should show ~1 Hz
```

### Empirical Covariance Tuning

```bash
# Drive robot 2m straight, 10 trials
# Record encoder estimate vs actual
# Compute variance, update covariance
```

---

## 9. Conceptual Gaps Summary

| Assumption | Reality | Risk |
|------------|---------|------|
| "Servo tracks θ(t) perfectly" | Servo has 100-200ms lag | Scan artifacts |
| "Spiral = exploration" | Spiral is open-loop, not frontier | Won't explore efficiently |
| "Guessed covariances work" | Covariances drive UKF weighting | Poor fusion |
| "Scan compensation works" | No validation, has bugs | SLAM failures |
| "IMU yaw is absolute" | BNO085 game-vector drifts | Long-term drift |

---

**Next Phase**: Phase 2.5 — Apply Obvious Fixes (P0 items 1-5)
