# Online SLAM + Nav2 Navigation - Configuration Summary

## Overview

The BNL robot is now configured to start in a completely unknown environment and perform online SLAM while supporting manual "Navigate To Pose" goals. No preloaded maps are required.

## Architecture

```
Sensors                      Odometry                        Nav2 Stack
├── LiDAR (/scan)      ──┐
├── Wheel Encoders     ──┼──→ wheelodom.py ──→ /odom  ──→ Planner Server
├── IMU (/imu/data)    ──┘    (kinematic)                  Local Path Tracking
└── Camera                                                   Behavior Tree Navigator

SLAM
├── Input: /scan (LiDAR)
├── Mode: mapping
├── Output: /map (live occupancy grid)
└── TF: map → odom (published continuously)

TF Chain (Complete)
├── map (from slam_toolbox) — initialized at first scan, continuously updated
├── odom (from slam_toolbox) — transformed from map based on robot motion
├── base_link (from hardware odometry)
│   ├── imu_link (static offset)
│   ├── lidar_link (static)
│   └── camera_link (static)
```

## Files Modified

### 1. `src/wg_state_est/launch/nav2_launch.py`

**Changed line 31:**
```python
# Before:
'use_localization': 'True',

# After:
'use_localization': 'False',
```

**Effect:**
- Nav2 bringup now only includes `slam_launch.py` (SLAM enabled)
- Excludes `localization_launch.py` (AMCL disabled)
- Result: Only slam_toolbox publishes `map → odom`, no AMCL conflicts

### 2. `src/wg_utilities/nav2/nav2_param.yaml`

**Removed sections:**
- `map_server` (lines 60-71) — No static map file loaded
- `amcl` (lines 16-58) — AMCL localization disabled
- Updated `lifecycle_manager.node_names`: removed `map_server` and `amcl`

**Updated header comments:**
- Changed from "Uses SLAM-generated or pre-built map"
- To "Uses SLAM-generated live map for navigation (online SLAM mode)"
- Notes that no preloaded map file is required

**Unchanged (correct for online SLAM):**
- `planner_server` — Global path planning
- `controller_server` — Local path tracking
- `costmap` layers — Use live /map from SLAM
- `bt_navigator` — Behavior tree navigation

### 3. `src/wg_utilities/nav2/slam_params.yaml`

**No changes needed** — Already correctly configured:
- `mode: mapping` — Online SLAM (not localization)
- `map_frame: map`, `odom_frame: odom`, `base_frame: base_link`
- `use_sim_time: false` — Handled via launch parameter override

### 4. Odometry Pipeline

**Kinematic odometry only** — No sensor fusion:
- `wheelodom.py` reads encoder GPIO, publishes `/odom` + TF `odom → base_link`
- `imuodom.py` publishes `/imu/data` for monitoring (not fused)
- Nav2 subscribes directly to `/odom`
- slam_toolbox uses `/scan` for localization, `/odom` as motion prior

## Launch Sequence

When you run:
```bash
ros2 launch wg_bringup wg.launch.py mode:=sim
```

**Startup order (after 2-second timer):**

1. **Gazebo** (sim mode only)
   - Loads robot model and world
   - Provides simulated `/scan` via ros_gz_bridge

2. **Odometry** (wheel_odom_node)
   - wheelodom.py reads encoders via GPIO
   - Publishes `/odom` (nav_msgs/Odometry)
   - Publishes TF `odom → base_link`
   - imu_odom_node publishes `/imu/data` for diagnostics

3. **Nav2 + SLAM** (nav2_launch.py → bringup_launch.py)
   - slam_launch.py starts slam_toolbox
   - slam_toolbox:
     - Subscribes to `/scan` (LiDAR)
     - Builds map in real-time
     - Publishes `/map` topic
     - **Publishes TF: map → odom** (50 Hz)
   - Nav2 nodes start:
     - planner_server (global planning)
     - controller_server (local tracking)
     - bt_navigator (behavior tree)
     - costmap servers (use live /map)
   - No AMCL, no map_server

**TF Tree (after 5-10 seconds):**
```
map (from slam_toolbox)
  ↓ slam_toolbox publishes map→odom transform
odom (continuously updated by SLAM)
  ↓ wheelodom.py publishes odom→base_link
base_link
  ↓ static transforms
imu_link, lidar_link, camera_link
```

## Navigation Workflow

### User sends "Navigate To Pose" goal (via RViz or service call):
```bash
ros2 service call /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose_stamped: {header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 2.0}, orientation: {w: 1.0}}}}"
```

### Nav2 Behavior Tree:
1. **BT Navigator** receives goal in `map` frame
2. **Planner Server** plans path:
   - Queries global costmap (uses `/map` from SLAM)
   - Computes path avoiding obstacles
3. **Controller Server** tracks path:
   - Uses local costmap (rolling window in `odom` frame)
   - Generates `/cmd_vel` commands
4. **Robot moves:**
   - Wheel velocity commands executed
   - LiDAR continues scanning
   - SLAM updates map in real-time
   - Goal reached or recovery behaviors triggered if stuck

## Key Differences from Localization Mode

| Aspect | Before (Localization) | After (Online SLAM) |
|--------|----------------------|-------------------|
| **Map** | Pre-built, static file | Live, continuously updated |
| **Localization** | AMCL particle filter | slam_toolbox (visual/LiDAR scan matching) |
| **map→odom** | Published by AMCL | Published by slam_toolbox |
| **Startup** | Needs map_server to load file | None - SLAM creates map from scans |
| **Nodes** | amcl, map_server, nav2 | slam_toolbox, nav2 only |
| **Unknown areas** | Can't navigate, no map | Maps area as robot explores |
| **Re-localization** | AMCL corrects drift | SLAM continuous tracking |

## Advantages

✅ **No pre-built maps needed** — Robot can explore unknown environments
✅ **Adaptive** — Map updates with real-time scans
✅ **Lower complexity** — Fewer nodes, fewer conflicts
✅ **Continuous mapping** — Area behind robot is remembered
✅ **Manual control** — User can send goals anytime, anywhere

## Limitations

⚠️ **SLAM drift** — Long-term drift possible without loop closure
⚠️ **Large maps** — Memory usage increases with area size
⚠️ **Featureless areas** — SLAM performance degrades without distinctive features
⚠️ **No pre-recorded maps** — Can't pre-plan global routes

## Verification Checklist

Run commands in `ONLINE_SLAM_VALIDATION.md` to verify:
- ✅ SLAM builds map in RViz (live occupancy grid)
- ✅ TF tree: `map ← odom ← base_link`
- ✅ No `/amcl` or `/map_server` nodes
- ✅ `/map` topic publishes at ~1 Hz
- ✅ Nav2 accepts "Navigate To Pose" goals
- ✅ Robot navigates toward goal using live map
- ✅ Costmaps use live obstacle data

## Troubleshooting

**No `/map` topic:**
- Check slam_toolbox is running: `ros2 node list | grep slam`
- Check `/scan` is publishing: `ros2 topic hz /scan`
- Review slam_toolbox output: `ros2 node info /slam_toolbox`

**AMCL or map_server running:**
- Kill: `pkill -f amcl_node && pkill -f map_server_node`
- Check `use_localization: 'False'` in nav2_launch.py
- Verify lifecycle_manager doesn't list them

**TF warnings:**
- Wait 5-10 seconds after launch for SLAM to initialize
- Check: `ros2 tf2_monitor base_link map`
- Verify both transforms exist: `ros2 topic echo /tf`

**Navigation failures:**
- Check costmap using live map: `ros2 topic echo /global_costmap/costmap`
- Verify path is computable: Check for obstacles at goal location
- Review BT navigator logs: `ros2 node info /bt_navigator`

## Future Enhancements

1. **Loop Closure:** Enable slam_toolbox loop closure for large areas
2. **Map Saving:** Save SLAM-generated maps for localization mode re-use
3. **Multi-robot SLAM:** Extend to coordinate multiple robots
4. **Visual SLAM:** Integrate RGB-D or stereo camera for feature-rich mapping
5. **Dynamic Map Updates:** Save and update map as environment changes

## References

- **SLAM Toolbox:** http://docs.ros.org/en/jazzy/p/slam_toolbox/
- **Nav2 Docs:** https://docs.nav2.org/
- **Differential Drive Kinematics:** Standard encoder-based odometry (no fusion)
- **REP-105 (Frames):** http://www.ros.org/reps/rep-0105.html
