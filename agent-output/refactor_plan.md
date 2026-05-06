# Refactor Plan: Remove robot_localization, Use Pure Kinematic Odometry

## Date: 2026-05-06

---

## Current State Audit

### robot_localization Package
- **Location**: `src/robot_localization/` (fork/clone of upstream package)
- **Contents**: Full EKF/UKF C++ implementation, launch files, params, tests
- **Executables provided**: `ekf_node`, `ukf_node`, `navsat_transform_node`
- **Executables WRONGLY referenced**: `wheel_odom_node`, `imu_odom_node`, `lidar_node` (do not exist)

### Broken Architecture
`wg.launch.py` includes `full_localization.launch.py` which:
1. Tries to launch `wheel_odom_node` from `robot_localization` (doesn't exist)
2. Tries to launch `imu_odom_node` from `robot_localization` (doesn't exist)
3. Tries to launch `lidar_node` from `robot_localization` (doesn't exist)
4. Launches `ukf_node` → fuses `/odom` + `/imu/data` → `/odom/calibrated`

BUT `wg.launch.py` ALSO directly launches the real hardware nodes from `wg_sensor_pullup`.
This is duplicated and broken.

### Odometry Data Flow (Current)
```
Encoder GPIO → wheelodom.py → /odom (nav_msgs/Odometry) + TF: odom→base_link
                                    ↓
                               Nav2 subscribes to /odom
                                    ↓
                           local_costmap uses odom frame

IMU I2C → imuodom.py → /imu/data (sensor_msgs/Imu)
                              ↓
                         UKF subscribes (but publish_tf=False)
                              ↓
                    /odom/calibrated ← UNUSED by Nav2
```

### TF Tree (Current - from wheelodom.py)
```
odom → base_link → lidar_link, imu_link
```
This is already correct and complete without robot_localization.

### Nav2 Configuration
- `nav2_param.yaml` uses `odom_topic: /odom` (raw wheel odometry) ✓
- `global_frame: odom` for local_costmap ✓
- `robot_base_frame: base_link` ✓

---

## What Must Be Removed

1. **Entire `src/robot_localization/` directory** (~200 files, C++ package)
2. **`full_localization` include** from `wg.launch.py`
3. **All references to `robot_localization`** in:
   - `README.md`
   - `README_AUTONOMOUS.md`
   - `setup_instructions.md`
   - `ONLINE_SLAM_README.md`
   - `NAV2_AUDIT.md`
   - `src/wg_sensor_pullup/elias_relay/README.md`
   - `wg_utilities` dependencies (if any)
4. **References to `/odom/calibrated`** and `/odometry/filtered`
5. **References to UKF/EKF fusion**
6. **References to `--allow-overriding robot_localization`** in build instructions

---

## What Must Be Kept / Verified

1. **wheelodom.py** (`wg_sensor_pullup`) — sole odometry source
   - Must publish `/odom`
   - Must publish TF `odom → base_link`
   - Differential drive kinematics already implemented ✓

2. **imuodom.py** (`wg_sensor_pullup`) — keep as sensor publisher
   - Publishes `/imu/data`
   - NOT fused (no robot_localization to consume it)
   - Can be used for monitoring/yaw reference

3. **Nav2 params** — already use `/odom`, no changes needed for topic
   - May need slight covariance tuning

4. **lidar_node** — already from `ldlidar_stl_ros2` package
   - Not affected by this refactor

5. **slam_toolbox** — subscribes to `/scan` and `/odom`
   - Uses scan matching, not dependent on UKF

---

## What Must Be Changed

### 1. wg.launch.py
- Remove `wg_state_est_pkg_path` variable
- Remove `full_localization_launch_path`
- Remove `full_localization` IncludeLaunchDescription
- Remove from `wait_sec_node` actions list
- Keep wheel_odom_node, imu_node, vel_to_pwm_node, lidar_node as-is

### 2. wheelodom.py (minor verification)
- Verify it publishes `/odom` with correct frame_id
- Verify it publishes TF `odom → base_link`
- Covariance values look reasonable for encoder-only odometry

### 3. nav2_param.yaml (minor)
- Currently uses `odom_topic: /odom` — keep
- `use_sim_time: true` should be parameterized or set per-mode
- Consider slightly increasing twist covariance to reflect no-fusion uncertainty

### 4. Documentation
- Replace UKF/robot_localization references with "kinematic odometry"
- Update topic graph: remove `/odom/calibrated`, `/odom/raw`
- Update TF tree: remove UKF mention
- Update build instructions: remove `--allow-overriding robot_localization`
- Update `--symlink-install` references to standard `colcon build`

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Nav2 depends on `/odom` covariances | Values in wheelodom.py already present and reasonable |
| SLAM depends on `/odom` quality | slam_toolbox uses scan matching; odometry is weight-only input |
| IMU data unused | Expected. IMU remains available on `/imu/data` for future use. |
| No yaw drift correction | Acceptable for short runs. BNO085 rotation vector is accurate short-term. |
| Yaw drift accumulates over time | Known limitation of pure encoder odometry. Document clearly. |

---

## Expected Final Architecture

```
Encoder GPIO → wheelodom.py → /odom + TF:odom→base_link
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
                 Nav2          slam_toolbox    (monitors)
               /cmd_vel           /map         /imu/data
                    ↓
              vel_to_pwm.py → Motor PWM
```

---

## IMU Decision

**KEEP IMU node running** (`imuodom.py`):
- Publishes `/imu/data` for diagnostics and potential future use
- Does NOT participate in odometry fusion
- No additional complexity introduced
- Can be optionally used for simple yaw reset (out of scope for this refactor)

---

## Build System Changes

- Remove `--allow-overriding robot_localization` from all docs
- Remove `--symlink-install` recommendation (use standard `colcon build`)
- Verify `wg_sensor_pullup` has no dependency on `robot_localization` in package.xml
- Verify `wg_bringup` has no dependency on `robot_localization` in package.xml
