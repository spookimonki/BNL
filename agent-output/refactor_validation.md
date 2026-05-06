# Refactor Validation Report

**Date**: 2026-05-06  
**Scope**: Remove robot_localization, use pure kinematic odometry

---

## VERIFIED Items

### 1. robot_localization Package Removal
- **Status**: VERIFIED
- **Evidence**: `src/robot_localization/` no longer exists
- **Build impact**: Standard `colcon build` now sufficient; no `--allow-overriding` needed

### 2. Odometry Pipeline
- **Status**: VERIFIED
- **Source**: `src/wg_sensor_pullup/elias_relay/wheelodom.py`
- **Topic**: `/odom` (nav_msgs/Odometry)
- **TF**: `odom → base_link` published directly by wheelodom node
- **Method**: Differential drive kinematics from encoder counts
- **Rate**: 10 Hz
- **Kinematics**: Uses exact arc integration (not small-angle approximation)
- **Covariances**: Present and reasonable for encoder-only odometry

### 3. Nav2 Compatibility
- **Status**: VERIFIED
- **Config**: `src/wg_utilities/nav2/nav2_param.yaml`
- **`odom_topic`**: `/odom` — matches wheelodom output
- **`global_frame`**: `map` for planner, `odom` for local_costmap
- **`robot_base_frame`**: `base_link`
- **No AMCL/map_server**: Correct for online SLAM mode
- **Controller**: Regulated Pure Pursuit (appropriate for differential drive)

### 4. SLAM Compatibility
- **Status**: VERIFIED
- **Config**: `src/wg_utilities/nav2/slam_params.yaml`
- **Frames**: `map_frame: map`, `odom_frame: odom`, `base_frame: base_link`
- **Input**: `/scan` from LiDAR
- **Mode**: `mapping` (online SLAM)
- **slam_toolbox publishes**: `map → odom` TF
- **Does NOT depend on filtered odometry** — uses scan matching for localization

### 5. TF Tree Consistency
- **Status**: VERIFIED
- **Chain**: `map → odom → base_link → {lidar_link, imu_link, servo_link}`
- **map → odom**: Published by slam_toolbox
- **odom → base_link**: Published by wheelodom.py
- **base_link → imu_link**: Static transform (180° X rotation for upside-down mount)
- **base_link → lidar_link**: Static transform from URDF
- **No gaps**: Every frame has a publisher

### 6. Launch File Integrity
- **Status**: VERIFIED
- **File**: `src/wg_bringup/launch/wg.launch.py`
- **No references to `robot_localization`**
- **No references to `/odom/calibrated`**
- **Real mode launches**: wheel_odom_node, imu_node, vel_to_pwm_node, lidar_node, servo_oscillator, scan_projection, robot_state_publisher, static_base_to_imu, nav2_navigation, slam_toolbox
- **No broken executable references**

### 7. IMU Node (Unfused)
- **Status**: VERIFIED
- **Publishes**: `/imu/data` (sensor_msgs/Imu)
- **Does NOT**: publish odometry, fuse with encoders, or publish TF
- **Available for**: Diagnostics, future optional yaw correction, monitoring

---

## THEORETICALLY VALID Items

### 1. Nav2 Local Costmap with Raw Odometry
- **Rationale**: Nav2's local costmap uses `odom` frame and `/scan`. The controller follows planned paths. Raw wheel odometry is sufficient for short-horizon local planning.
- **Assumption**: Odometry drift is slow enough that SLAM's `map → odom` correction keeps global consistency.
- **Confidence**: HIGH — this is a standard configuration for diff-drive robots.

### 2. slam_toolbox with Encoder Odometry
- **Rationale**: slam_toolbox uses scan-to-scan matching as its primary localization mechanism. Wheel odometry is used as a motion prior (weight input), not as ground truth.
- **Assumption**: LiDAR scans have sufficient features for matching.
- **Confidence**: HIGH — online_async mode is designed for this use case.

### 3. Encoder Covariances for Nav2
- **Rationale**: Pose covariance `[0.02, 0.02, 1e6, 1e6, 1e6, 0.04]` and twist covariance `[0.05, 0.05, 1e6, 1e6, 1e6, 0.08]` are conservative enough that Nav2 won't over-trust odometry.
- **Confidence**: MEDIUM-HIGH — values are typical for small encoder-based robots.

---

## UNCERTAIN Items

### 1. Encoder Resolution (2048 ticks/rev)
- **Status**: UNCERTAIN
- **Question**: Is 2048 ticks/rev the actual hardware resolution?
- **Impact**: Wrong resolution scales all distances/velocities incorrectly
- **Mitigation**: Empirical calibration (drive 1m, compare odom_x to actual distance)

### 2. Wheel Base Measurement (0.2m)
- **Status**: UNCERTAIN
- **Question**: Is 0.2m the actual axle-to-axle distance?
- **Impact**: Wrong wheel base causes yaw rate errors, leading to curved-line drift
- **Mitigation**: Spin robot 360° in place, compare odom yaw to actual rotation

### 3. Yaw Drift Over Long Runs
- **Status**: UNCERTAIN — expected behavior of pure kinematic odometry
- **No IMU fusion means**: No correction for wheel slippage, uneven floors, or encoder miscounts
- **Impact**: SLAM must compensate via loop closure and scan matching
- **Mitigation**: Keep runs short, rely on SLAM for global consistency

### 4. LiDAR Driver Package (`ldlidar_stl_ros2`)
- **Status**: UNCERTAIN
- **Issue**: Directory is empty in workspace — driver may need to be installed separately
- **Impact**: If not installed system-wide, launch will fail to find `ldlidar_stl_ros2_node`
- **Mitigation**: Install `ros-jazzy-ldlidar-stl-ros2` or equivalent package

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Odometry drift causes SLAM failures | Medium | High | Short runs, feature-rich environments |
| Encoder miscounts from noise | Medium | Medium | Check pull-ups, shield wiring |
| No yaw correction from IMU | Certain (by design) | Low-Medium | Acceptable for this refactor scope |
| Build fails without robot_localization | Low | High | Already verified no package depends on it |
| Nav2 complains about odom covariance | Low | Medium | Values are conservative and present |

---

## Confidence Level

**OVERALL: HIGH**

The architecture is simpler now, not more complex. Removing a broken, resource-heavy dependency and relying on the already-working kinematic odometry node is a net improvement in correctness and maintainability.

The primary uncertainty is encoder calibration (resolution, wheel base), which is a hardware issue, not an architecture issue.
