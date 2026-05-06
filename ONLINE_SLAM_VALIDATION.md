# Online SLAM with Nav2 Navigation - Validation Checklist

This document provides step-by-step validation of the online SLAM + Nav2 navigation setup.

## Configuration Changes Made

✅ `src/wg_state_est/launch/nav2_launch.py`:
   - Set `use_localization: 'False'` (disables AMCL)
   - Kept `slam: 'True'` (enables slam_toolbox)

✅ `src/wg_utilities/nav2/nav2_param.yaml`:
   - Removed `map_server` section (no static map file loaded)
   - Removed AMCL configuration
   - Removed `map_server` and `amcl` from lifecycle_manager node_names
   - Updated header comments for online SLAM mode

✅ `src/wg_utilities/nav2/slam_params.yaml`:
   - Already configured: `mode: mapping`
   - TF frames correct: `map_frame`, `odom_frame`, `base_frame`

## Pre-Launch Setup

### 1. Build and Source (Inside Docker Container)

```bash
cd /bnl_git

# Clean and build
colcon build

# Source the install
source install/setup.bash

# Verify build
echo "Build successful: $(ls install/setup.bash)"
```

### 2. Verify Node Availability

```bash
# Check SLAM toolbox is available
ros2 pkg list | grep slam_toolbox

# Check Nav2 bringup is available
ros2 pkg list | grep nav2_bringup

# Expected output: Both packages should be listed
```

---

## Launch and Validation (Simulation Mode)

### Terminal 1: Launch the System

```bash
cd /bnl_git
source install/setup.bash

# Launch in SIM mode
ros2 launch wg_bringup wg.launch.py mode:=sim
```

**Expected output:**
- Gazebo should start (or at least initialize)
- State estimation nodes starting
- "SLAM enabled" or slam_toolbox messages
- No "AMCL" or "map_server" messages
- No errors about missing map files

Wait ~5-10 seconds for full startup.

---

### Terminal 2: Verify TF Tree

```bash
sleep 5

# Check available nodes (should NOT include amcl or map_server)
ros2 node list

# Expected: No /amcl or /map_server nodes
# Should see: /slam_toolbox, /bt_navigator, /planner_server, etc.

# Generate TF tree
ros2 run tf2_tools view_frames.py

# Expected: Should create frames.pdf with tree: map → odom → base_link
```

**TF tree should show:**
```
map (from slam_toolbox)
  └── odom (SLAM-generated)
      └── base_link (from hardware/odometry)
          ├── imu_link (static)
          ├── lidar_link (static)
          └── camera_link (static)
```

---

### Terminal 3: Verify SLAM is Running

```bash
# Check slam_toolbox node info
ros2 node info /slam_toolbox

# Expected: Node is active, no error state

# Monitor map publishing frequency
ros2 topic hz /map

# Expected: Should show ~1 Hz (map updates ~once per second)

# Check map content
ros2 topic echo /map --once

# Expected: OccupancyGrid message with header, resolution, data array
# Data should show some occupancy grid information from the LiDAR scan
```

---

### Terminal 4: Check Costmaps are Using Live Map

```bash
# Global costmap should use /map from SLAM
ros2 topic echo /global_costmap/costmap --once

# Expected output should include:
# - header.frame_id: 'map' (NOT 'odom')
# - resolution: 0.05
# - data: [array of occupancy values]

# Local costmap should use odom frame
ros2 topic echo /local_costmap/costmap --once

# Expected output should include:
# - header.frame_id: 'odom' (rolling window)
# - rolling_window: true
```

---

### Terminal 5: Verify No Conflicts

```bash
# Check node list for conflicting nodes
ros2 node list | grep -E 'amcl|map_server|localization'

# Expected: Empty (no matches)
# If anything appears, those nodes should NOT be running in SLAM mode

# Check TF sources (should only see slam_toolbox publishing map→odom)
ros2 topic echo /tf --once | head -20

# Expected: Single map→odom transform from slam_toolbox
# Should NOT see AMCL's /tf_static with map frame broadcasts
```

---

## Visual Verification (RViz)

### Terminal 6: Launch RViz

```bash
rviz2
```

### RViz Configuration Steps:

1. **Set Fixed Frame:**
   - Left panel → "Fixed Frame" dropdown
   - Select "map"
   - Expected: No warnings about map frame not available

2. **Add Map Display:**
   - Add → Map
   - Topic: `/map`
   - Expected: Occupancy grid appears (initially mostly black/empty)
   - As time passes: Grid should populate with obstacles as robot moves and scans area

3. **Add TF Display:**
   - Add → TF
   - Expected: Frame tree visible showing map → odom → base_link

4. **Add Robot Model (Optional):**
   - Add → RobotModel
   - Expected: Robot model appears at origin, correctly positioned in map frame

5. **Monitor /map Updates:**
   - In RViz display, watch the map occupancy grid
   - Move robot (or send goals)
   - Expected: Map continuously updates with new LiDAR scans

---

## Manual Navigation Test

### Terminal 7: Send Navigation Goal

```bash
# Send a goal 2 meters forward in the map frame
ros2 service call /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose_stamped: {header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"

# Expected:
# - Goal accepted
# - Robot starts moving toward goal
# - No "No map" errors
# - Local costmap shows immediate obstacles
# - Robot navigates avoiding obstacles
```

**Monitor navigation feedback:**
```bash
# In another terminal, monitor BT navigator status
ros2 node info /bt_navigator

# Check active action servers
ros2 action list
```

---

## Diagnostic Commands

### Quick Health Check

```bash
#!/bin/bash
echo "=== Online SLAM Health Check ==="

echo -e "\n1. SLAM Toolbox Node:"
ros2 node info /slam_toolbox 2>/dev/null && echo "✓ Running" || echo "✗ NOT running"

echo -e "\n2. Nav2 Lifecycle Manager:"
ros2 node info /lifecycle_manager_navigation 2>/dev/null && echo "✓ Running" || echo "✗ NOT running"

echo -e "\n3. Map Topic Publishing:"
ros2 topic hz /map 2>/dev/null | head -1

echo -e "\n4. AMCL Status (should NOT exist):"
ros2 node info /amcl 2>/dev/null && echo "✗ ERROR: AMCL is running!" || echo "✓ AMCL correctly disabled"

echo -e "\n5. Map Server Status (should NOT exist):"
ros2 node info /map_server 2>/dev/null && echo "✗ ERROR: map_server is running!" || echo "✓ map_server correctly disabled"

echo -e "\n6. TF Tree:"
ros2 run tf2_tools view_frames.py 2>/dev/null && echo "✓ TF tree saved" || echo "✗ TF error"

echo -e "\n=== Health Check Complete ==="
```

### Troubleshooting

**Issue: No /map topic**
```bash
ros2 topic list | grep -i map
# If /map doesn't exist, slam_toolbox may not have started
# Check: ros2 node list | grep slam
```

**Issue: TF warnings about missing frames**
```bash
ros2 tf2_monitor base_link map
# Should show transform chain without warnings
```

**Issue: AMCL or map_server still running**
```bash
# Kill them manually
pkill -f amcl_node
pkill -f map_server_node

# Then verify they don't restart
sleep 5 && ros2 node list | grep -E 'amcl|map_server'
```

**Issue: Costmap not using /map**
```bash
# Check costmap parameters
ros2 param get /global_costmap global_costmap.global_frame
# Should return: "map"
```

---

## Expected Success Criteria

✅ **System boots without map files**
   - No error: "Could not find map file..."
   - No error: "Waiting for map..."

✅ **SLAM builds map in real time**
   - `/map` topic exists and publishes
   - RViz shows occupancy grid growing
   - Map resolution ~5cm

✅ **TF tree: map ← odom ← base_link**
   - `ros2 run tf2_tools view_frames.py` shows correct tree
   - No AMCL transforms
   - Single slam_toolbox publisher for map→odom

✅ **Nav2 accepts "Navigate To Pose" goals**
   - Service `/navigate_to_pose` exists
   - Goal sent successfully
   - No "No global costmap" errors

✅ **Robot navigates using live SLAM map**
   - Robot moves toward goal
   - Costmaps show obstacles from /map
   - No static map conflicts

✅ **No AMCL or map_server nodes running**
   - `ros2 node list` does NOT show /amcl
   - `ros2 node list` does NOT show /map_server
   - Only slam_toolbox provides map frame

✅ **Costmaps use live map data**
   - Global costmap `frame_id = 'map'` (from SLAM)
   - Local costmap `frame_id = 'odom'` (rolling window)
   - Both update in real-time

---

## Saving the SLAM-Generated Map (Future Use)

Once satisfied with a mapped area:

```bash
# Save the map
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap \
  "{name: {data: 'my_environment_map'}}"

# This creates: my_environment_map.yaml and my_environment_map.pgm

# Copy to project:
mkdir -p /opt/ros/jazzy/share/wg_utilities/nav2/maps/
cp my_environment_map.* /opt/ros/jazzy/share/wg_utilities/nav2/maps/

# To use in localization mode (future): Update nav2_param.yaml with map file path
```

---

## Next Steps

1. ✅ Verify all success criteria above
2. ✅ Test real robot mode: `ros2 launch wg_bringup wg.launch.py mode:=real`
3. ✅ Tune SLAM parameters if performance issues (see slam_params.yaml)
4. ✅ Save maps from successful mapping runs
5. ✅ Document any hardware-specific calibrations (IMU offset, wheel radius, etc.)
