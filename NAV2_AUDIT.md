# Nav2 Audit Report

> **ARCHIVED / OBSOLETE**: This audit was written before the 2026-05-06 refactor that removed `robot_localization` (UKF/EKF) in favor of pure kinematic odometry. Many findings here reference the old broken architecture. See `agent-output/refactor_plan.md` for current design.

**Generated**: 2026-04-30  
**Workspace**: /home/monki/Desktop/BNL  
**ROS Version**: Jazzy  

---

## Executive Summary

**Overall Status: FAIL (Critical)**

The Nav2 stack is structurally initialized but **non-functional** due to incomplete parameter configuration and missing critical infrastructure components. Launch files reference a Nav2 parameter file (`wg_utilities/nav2/nav2_param.yaml`) that exists but contains only 12 lines of bot_navigator parameters; all mandatory server configurations (planner, controller, smoother, amcl, map_server, costmap layers) are **absent**. Additionally, the full localization pipeline references non-existent node executables (`wheel_odom_node`, `imu_odom_node`, `lidar_node`) from the robot_localization submodule. No map file is provided or loaded, rendering AMCL and global localization inoperative. The system will fail at runtime when Nav2 attempts to load plugins or transition lifecycle states.

**Severity**: **CRITICAL** – Nav2 will not launch successfully; multiple hard failures expected.

---

## Findings

### 1. **Missing/Incomplete Nav2 Parameters File**
**Severity**: CRITICAL  
**File**: `src/wg_utilities/nav2/nav2_param.yaml` (line 1–13)  
**Location**: wg.launch.py line 26, nav2_launch.py line 39

The parameter file referenced in launches exists but is severely truncated:
```yaml
bt_navigator:
  ros__parameters:
    wheel_radius: 0.05
    wheel_base: 0.3
    encoder_resolution_m1: 2048
    encoder_resolution_m2: 2048
    x: 0.0
    y: 0.0
    theta: 0.0
```

**Missing sections**:
- `planner_server` (global planner plugin, costmap params, planner type)
- `controller_server` (local planner, velocity smoother)
- `smoother_server` (path smoothing)
- `amcl` (localization parameters, sensor sources)
- `map_server` (map loading configuration)
- `nav2_bringup_launch` parameters (lifecycle nodes, autostart)
- `costmap_common_params` (footprint, obstacle layers, sensor sources)
- Behavior tree server path and default tree name

**Fix**:
Create a complete `nav2_param.yaml` based on nav2_bringup template. Minimal example:

```yaml
amcl:
  ros__parameters:
    use_sim_time: true
    alpha1: 0.2
    alpha2: 0.2
    alpha3: 0.2
    alpha4: 0.2
    alpha5: 0.2
    base_frame_id: base_link
    beam_search_angle_increment: 0.0349066
    cost_threshold: 0.46
    global_frame_id: map
    lambda_short: 0.1295
    laser_likelihood_max_dist: 2.0
    laser_max_range: 100.0
    laser_min_range: 0.1
    laser_model_type: likelihood_field
    max_beams: 60
    max_particles: 2000
    min_particles: 500
    odom_frame_id: odom
    pf_err: 0.05
    pf_z: 0.99
    recovery_alpha_fast: 0.0
    recovery_alpha_slow: 0.0
    resample_interval: 1
    robot_model_type: differential
    save_pose_rate: 0.5
    sigma_hit: 0.2
    sigma_short: 0.05
    tf_broadcast: true
    transform_tolerance: 1.0
    update_angle_min_degrees: 0.0
    update_min_a: 0.2
    update_min_d: 0.25
    z_hit: 0.5
    z_max: 0.05
    z_rand: 0.5
    z_short: 0.05

planner_server:
  ros__parameters:
    use_sim_time: true
    expected_planner_frequency: 20.0
    planner_plugins: ['GridBased']
    GridBased:
      plugin: nav2_navfn_planner/NavfnPlanner
      tolerance: 0.5
      use_astar: false
      allow_unknown: false

controller_server:
  ros__parameters:
    use_sim_time: true
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    failure_tolerance: 0.3
    progress_checker_plugin: progress_checker
    goal_checker_plugins: ['general_goal_checker']
    controller_plugins: ['FollowPath']

    progress_checker:
      plugin: nav2_controller::SimpleProgressChecker
      required_movement_radius: 0.5
      movement_time_allowance: 10.0

    general_goal_checker:
      stateful: true
      plugin: nav2_controller::SimpleGoalChecker
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25

    FollowPath:
      plugin: nav2_regulated_pure_pursuit_controller/RegulatedPurePursuitController
      desired_linear_vel: 0.5
      lookahead_dist: 0.6
      min_lookahead_dist: 0.3
      max_lookahead_dist: 0.9
      lookahead_time: 1.5
      rotate_to_heading_angular_vel: 1.8
      transform_tolerance: 0.1
      use_velocity_scaled_lookahead_dist: false
      min_amcl_pose_uncertainty: 0.05

smoother_server:
  ros__parameters:
    use_sim_time: true
    smoother_plugins: ['simple_smoother']
    simple_smoother:
      plugin: nav2_smoother::SimpleSmoother
      tolerance: 1e-10
      max_its: 1000
      do_refinement: true

behavior_server:
  ros__parameters:
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/published_footprint
    cycle_frequency: 10.0
    behavior_plugins: ['spin', 'backup', 'drive_on_heading']
    spin:
      plugin: nav2_behaviors/Spin
      simulate_ahead_time: 1.0
      max_rotational_vel: 1.0
      min_rotational_vel: 0.4
      rotational_acc_lim: 3.2

    backup:
      plugin: nav2_behaviors/BackUp
      max_backup_dur: 2.0

    drive_on_heading:
      plugin: nav2_behaviors/DriveOnHeading
      max_speed: 0.26

bt_navigator:
  ros__parameters:
    use_sim_time: true
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    bt_loop_duration: 10
    default_server_timeout: 20
    enable_groot_monitoring: true
    groot_zmq_publisher_port: 1666
    groot_zmq_server_port: 1667
    default_nav_through_poses_bt_xml: /opt/ros/jazzy/share/nav2_bt_navigator/behavior_trees/navigate_through_poses_w_replanning_and_recovery.xml
    default_nav_to_pose_bt_xml: /opt/ros/jazzy/share/nav2_bt_navigator/behavior_trees/navigate_to_pose_w_replanning_and_recovery.xml
    plugin_lib_names:
      - nav2_compute_path_to_pose_action_bt_node
      - nav2_compute_path_through_poses_action_bt_node
      - nav2_follow_path_action_bt_node
      - nav2_spin_action_bt_node
      - nav2_wait_action_bt_node
      - nav2_assisted_teleop_action_bt_node
      - nav2_back_up_action_bt_node
      - nav2_drive_on_heading_bt_node
      - nav2_clear_costmap_service_bt_node
      - nav2_is_stuck_condition_bt_node
      - nav2_goal_updated_condition_bt_node
      - nav2_initial_pose_received_condition_bt_node
      - nav2_goal_reached_condition_bt_node
      - nav2_route_blackboard_updater_bt_node

map_server:
  ros__parameters:
    use_sim_time: true
    yaml_filename: path/to/your/map.yaml

costmap_common_params:
  ros__parameters:
    use_sim_time: true
    update_frequency: 5.0
    publish_frequency: 2.0
    global_frame: map
    robot_base_frame: base_link
    transform_tolerance: 0.3
    plugins: ['static_layer', 'obstacle_layer', 'inflation_layer']
    inflation_layer:
      plugin: nav2_costmap_2d::InflationLayer
      cost_scaling_factor: 3.0
      inflation_radius: 0.55
    obstacle_layer:
      plugin: nav2_costmap_2d::ObstacleLayer
      enabled: true
      observation_sources: scan
      scan:
        topic: /scan
        max_obstacle_height: 2.0
        clearing: true
        marking: true
        data_type: LaserScan
    static_layer:
      plugin: nav2_costmap_2d::StaticLayer
      enabled: true
      map_subscribe_transient_local: true
```

**Why this fixes it**: Nav2 lifecycle manager expects these server sections; without them, plugin loading fails during `configure` state transition.

---

### 2. **Incorrect Parameter File Path Reference**
**Severity**: CRITICAL  
**File**: `src/wg_bringup/launch/wg.launch.py` (line 26)

```python
nav2_params_file = os.path.join(wg_state_est_pkg_path, 'config', 'nav2_params.yaml')
```

The path points to `robot_localization/config/nav2_params.yaml`, which **does not exist**. The actual file is at `wg_utilities/nav2/nav2_param.yaml` (note: `.yaml`, not `.yaml` + different location).

**Fix**:
```python
nav2_params_file = os.path.join(
    get_package_share_directory('wg_utilities'),
    'nav2',
    'nav2_param.yaml'
)
```

Or copy/create `src/wg_state_est/config/nav2_params.yaml` pointing to the complete param file.

---

### 3. **Non-existent Node Executables in full_localization.launch.py**
**Severity**: CRITICAL  
**File**: `src/wg_state_est/launch/full_localization.launch.py` (lines 25–44)

```python
wheel_odom_node = Node(
    package='robot_localization',
    executable='wheel_odom_node',
    ...
)
```

The robot_localization package (both standard and forked) does **not** provide these executables:
- `wheel_odom_node`
- `imu_odom_node`
- `lidar_node`

Standard robot_localization provides: `ekf_node`, `ukf_node` only.

**Fix (two options)**:

**Option A**: If these are custom nodes in the fork, ensure the fork's `setup.py` declares them as entry points:
```python
# In setup.py of wg_state_est (robot_localization fork)
entry_points={
    'console_scripts': [
        'wheel_odom_node = your_module.wheel_odom:main',
        'imu_odom_node = your_module.imu_odom:main',
        'lidar_node = your_module.lidar:main',
    ],
},
```

**Option B**: Replace with standard nodes or custom replacements. Example using `ekf_node` for combined sensor fusion:
```python
# Remove individual nodes, use single UKF for all sensors
ukf_node = LifecycleNode(
    package='robot_localization',
    executable='ukf_node',
    name='ukf_filter_node',
    parameters=[os.path.join(robot_localization_dir, 'params', 'ukf.yaml')],
    remappings=[('odometry/filtered', '/odom/calibrated')],
)
```

**Why it fails**: If executables don't exist, `ros2 launch` will report "cannot find executable" and abort the launch sequence.

---

### 4. **No Map File Provided or Configured**
**Severity**: CRITICAL  
**Issue**: Nav2 AMCL and global localization require a map (`.pgm` or `.yaml` + image pair).

**Current state**: No map is referenced in any launch file or parameter. AMCL will fail to load or initialize without a map.

**Fix**:
1. Create/obtain a map file (from SLAM or pre-built). Example structure:
   ```
   maps/
   └── warehouse.yaml
       warehouse.pgm
   ```

2. Add map_server to nav2_param.yaml:
   ```yaml
   map_server:
     ros__parameters:
       use_sim_time: true
       yaml_filename: /path/to/maps/warehouse.yaml
   ```

3. Or include map server in launch:
   ```python
   map_server = Node(
       package='nav2_map_server',
       executable='map_server',
       name='map_server',
       parameters=[
           {'yaml_filename': map_yaml_file}
       ],
   )
   ```

**Why this fixes it**: AMCL's scan matching (global localization) needs a reference map to match against.

---

### 5. **Missing Behavior Tree Configuration**
**Severity**: HIGH  
**File**: `src/wg_utilities/nav2/nav2_param.yaml` (missing `bt_navigator` full config)

The bt_navigator section is incomplete:
```yaml
bt_navigator:
  ros__parameters:
    wheel_radius: 0.05
    ...
```

These should be in a separate `ekf.yaml` or sensor config, not bt_navigator. The actual bt_navigator needs:
- `global_frame`, `robot_base_frame`, `odom_topic`
- Default BT XML file path (or inline BT XML)
- Plugin library names
- Groot monitoring (optional but useful)

**Fix**: Add to nav2_param.yaml (see Finding #1 example).

---

### 6. **Costmap Configuration Absent**
**Severity**: HIGH  
**File**: `src/wg_utilities/nav2/nav2_param.yaml` (missing entirely)

Both local and global costmaps need plugin layers:
- `static_layer` (from map)
- `obstacle_layer` (from LiDAR/sensors)
- `inflation_layer` (cost scaling around obstacles)

Without these, the planner has no collision information.

**Fix**: Add `costmap_common_params`, `local_costmap`, `global_costmap` sections to nav2_param.yaml (see Finding #1).

---

### 7. **Frame Configuration Incomplete / IMU Offset Defaults to Zero**
**Severity**: MEDIUM  
**File**: `src/wg_state_est/launch/full_localization.launch.py` (lines 18–23, 46–61)

IMU position relative to base_link defaults to (0, 0, 0, 0, 0, 0):
```python
imu_x = DeclareLaunchArgument('imu_x', default_value='0.0')
...
static_base_to_imu = Node(
    ...
    arguments=[
        LaunchConfiguration('imu_x'),
        ...
        'base_link',
        'imu_link',
    ],
)
```

If the IMU is physically offset (e.g., 0.1m forward, 0.05m left), this TF will be wrong, causing:
- Incorrect odometry drift estimates
- LiDAR scans misaligned with robot frame
- UKF convergence issues

**Fix**: Calibrate IMU position and override launch args:
```bash
ros2 launch wg_state_est full_localization.launch.py \
  imu_x:=0.1 imu_y:=-0.05 imu_z:=0.03 imu_yaw:=0.0 imu_pitch:=0.0 imu_roll:=0.0
```

Or hard-code in launch if offset is fixed.

---

### 8. **Gazebo Topic Remappings May Not Match Sensor Drivers**
**Severity**: MEDIUM  
**File**: `src/wg_bringup/launch/wg.launch.py` (lines 48–49)

```python
bridge_node = Node(
    ...
    arguments=['/scan_gpu@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
               '/camera_image@sensor_msgs/msg/Image[gz.msgs.Image'],
    ...
)
```

If the Gazebo world (URDF/SDF) publishes LiDAR as `/scan` (not `/scan_gpu`) or camera as different topic, these remappings won't work. Topics will be empty or mismatched.

**Fix**: Verify Gazebo plugin topics against actual published topics:
```bash
# Inside running Gazebo container
ros2 topic list
```

And update remappings to match. Or check `simulation_package` URDF/SDF for actual plugin topic names.

---

### 9. **Build Issue: wg_interface Symlink Collision**
**Severity**: MEDIUM (blocks build, not runtime)  
**File**: Build system

```
Error: failed to create symbolic link because existing path cannot be removed: Is a directory
```

This happens when mixing ament_cmake and ament_python in the same workspace. `wg_interface` is ament_cmake; it conflicts with overlay.

**Fix**:
```bash
colcon clean
colcon build --symlink-install --allow-overriding robot_localization
```

Or rebuild from scratch:
```bash
rm -rf build install log
colcon build --allow-overriding robot_localization
```

---

### 10. **UKF Sensor Config References Non-Existent Topics**
**Severity**: MEDIUM  
**File**: `src/wg_state_est/params/ekf.yaml` (line 79)

```yaml
odom0: example/odom
```

This references `example/odom`, which doesn't exist. Should be the actual wheel odometry topic. Similarly for IMU (line 162):
```yaml
imu0: example/imu
```

**Fix**: Update to actual sensor topics:
```yaml
odom0: /wheel_odom  # or actual wheel encoder topic
imu0: /imu          # or actual IMU topic
```

If the actual topic names are different, UKF won't fuse them (no incoming measurements → filter drifts).

---

### 11. **No Static Map Provided for Simulation**
**Severity**: MEDIUM  
**Issue**: Simulation mode uses Gazebo, but Nav2 AMCL also runs and expects a map.

Either:
1. Export map from Gazebo world (via SLAM during init), OR
2. Provide pre-built map for Gazebo world

Without this, global localization won't work in simulation.

---

### 12. **Lifecycle Manager Not Explicitly Configured**
**Severity**: LOW  
**Issue**: Nav2 relies on lifecycle manager to transition nodes (Inactive → Active). If misconfigured, nodes may not activate.

**Check**: Verify `nav2_lifecycle_manager` node activates and transitions all servers. Monitor:
```bash
ros2 lifecycle list
```

Expected: `nav2_lifecycle_manager` should list all servers as "active".

---

## Validation Checklist

Run these commands inside Docker after fixes:

### 1. Build System
```bash
colcon build --symlink-install --allow-overriding robot_localization
source install/setup.bash
# Expected: All packages build without error
```

### 2. Frame Validation
```bash
ros2 launch wg_bringup wg.launch.py mode:=sim &
sleep 5
ros2 run tf2_tools view_frames.py
# Expected: Frame tree shows: map → odom → base_link → {imu_link, lidar_link, ...}
```

### 3. Sensor Topics Active
```bash
ros2 topic list | grep -E "(scan|imu|odom)"
# Expected: /scan, /imu, /wheel_odom, /odom, /odom/calibrated all present
```

### 4. Nav2 Lifecycle Status
```bash
ros2 lifecycle list
# Expected: nav2_lifecycle_manager lists all servers (planner, controller, smoother, bt, amcl, etc.)
# All should transition to "active" within 10 seconds
```

### 5. Localization Sanity Check
```bash
ros2 topic echo /amcl_pose
# Expected: pose changes as robot moves (or stays static if stationary)
# Should match /odom frame position approximately
```

### 6. Planner Response (Manual Test)
```bash
# After ensuring map is loaded and robot localized
ros2 action send_goal navigate_to_pose nav2_msgs/action/NavigateToPose \
  "pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}"
# Expected: Path appears in RViz, robot follows it or reports status
```

### 7. TF Lookup (Frame Resolution)
```bash
ros2 run tf2_ros tf2_echo map base_link
# Expected: Stable transform with small drift (if moving)
# If error: "Could not transform map to base_link" → AMCL not running
```

### 8. Topic Pub/Sub Check
```bash
ros2 node info /ukf_filter_node
ros2 node info /amcl
ros2 node info /planner_server
# Expected: Each shows subscriptions to sensor topics and publications
```

---

## Follow-up Tests (Post-Fix)

After implementing fixes, re-run:

```bash
# 1. Full rebuild
colcon clean && colcon build --allow-overriding robot_localization
source install/setup.bash

# 2. Launch full stack
ros2 launch wg_bringup wg.launch.py mode:=sim

# 3. Open RViz (in separate terminal)
ros2 run rviz2 rviz2 -d /opt/ros/jazzy/share/nav2_bringup/rviz/nav2_default_view.rviz

# 4. Monitor key topics in real-time
ros2 topic echo /odom/calibrated           # UKF output
ros2 topic echo /amcl_pose                 # Localization
ros2 topic echo /local_costmap/costmap_raw # Local costmap occupancy

# 5. Send navigation goal via RViz UI or CLI
# In RViz: click "Nav2 Goal" button, then click on map
# Or via CLI:
ros2 action send_goal navigate_to_pose nav2_msgs/action/NavigateToPose \
  "pose: {header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 2.0, z: 0.0}, orientation: {w: 1.0}}}"

# 6. Verify diagnostics are healthy
ros2 topic echo /diagnostics_agg | head -50

# 7. Check log files for errors
cat install/log/latest_build/wg_bringup/*.txt | grep -i "error\|warn\|fail"
```

---

## Token-Preserving Save

**Recommended filename**: `NAV2_AUDIT.md` (this file)

**Storage location**: Root of repo (`/home/monki/Desktop/BNL/NAV2_AUDIT.md`)

**Git commit message**:
```
docs: add nav2 audit report with critical findings and fixes

- Identified 12 critical/high/medium issues blocking nav2 startup
- Missing nav2_param.yaml sections (planner, controller, costmap, amcl, map_server)
- Non-existent node executables in full_localization.launch
- No map file configured for AMCL localization
- Frame calibration and topic remappings need verification
- Provided detailed fixes with yaml snippets and test commands
- Includes validation checklist and follow-up test procedures
```

**To save this file**:
```bash
cd /home/monki/Desktop/BNL
# File is already written; commit it:
git add NAV2_AUDIT.md CLAUDE.md
git commit -m "docs: nav2 audit + claude setup guide"
git push origin main
```

This preserves the audit in version control and provides future developers with exact fix recipes.
