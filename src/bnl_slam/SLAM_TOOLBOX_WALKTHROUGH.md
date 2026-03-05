# BNL SLAM Toolbox (Layer 2) Walkthrough

This document explains how **BNL sim_folder** wires **Gazebo (gz-sim) → ROS 2 → slam_toolbox** for live mapping.

Scope:
- Layer 1 simulation + bridging + TF shims
- Layer 2 slam_toolbox async mapping (LifecycleNode)

Non-scope (covered elsewhere): Nav2 (Layer 3), exploration behaviors, perception.

## Quick entrypoints

- Layer 2 SLAM session wrapper (starts Layer 1 + Layer 2):
  - [bnl_slam_layer2.launch.py](launch/bnl_slam_layer2.launch.py)
- Layer 2 only (assumes Layer 1 already running):
  - [bnl_layer2_slam.launch.py](launch/bnl_layer2_slam.launch.py)

If you run full autonomy, it conditionally includes SLAM and Nav2:
- [bnl_full_autonomy.launch.py](../../bnl_autonomy_bringup_pkg/launch/bnl_full_autonomy.launch.py)

## Architecture overview

The runtime pipeline is:

1. **Gazebo** publishes simulation topics (clock, lidar scan, odom, TF, camera).
2. **ros_gz_bridge** bridges those into ROS 2 topics.
3. **Static TF shims** fill the missing links between frames so slam_toolbox can resolve transforms.
4. **slam_toolbox** consumes `/scan` and TF (`odom -> chassis` and `chassis -> scan_frame`) to produce a live `map`.

## Layer 1: simulation + bridge + TF shims

File:
- [bnl_layer1_sim.launch.py](../../bnl_bringup_pkg/launch/bnl_layer1_sim.launch.py)

### What it launches

1) Gazebo simulator include:
- Includes `ros_gz_sim/launch/gz_sim.launch.py` with `-r <world.sdf>`.

2) Bridge node:
- `ros_gz_bridge/parameter_bridge` named `/ros_gz_bridge`.

3) Static TF publishers:
- `/tf_chassis_to_scan_frame`

### Bridge contract (topics)

The bridge uses the `parameter_bridge` argument syntax:

`/topic@<ros_msg_type>[<gz_msg_type` for Gazebo → ROS 2

`/topic@<ros_msg_type>]<gz_msg_type` for ROS 2 → Gazebo

Key bridges:
- `/clock` (GZ → ROS): simulation time
- `/scan_gpu` (GZ → ROS): lidar LaserScan (remapped to `/scan`)
- `/odom` (GZ → ROS): odometry message
- `/tf` (GZ → ROS): TF frames coming from simulation (notably `odom -> chassis`)
- `/cmd_vel` (ROS → GZ): drive commands (remapped from `/cmd_vel` to `/cmd_vel_mux` in BNL)

### TF shim contract (frames)

slam_toolbox fundamentally needs to transform each incoming scan into the base frame over time.
In this stack we ensure the TF chain exists:

`map -> odom -> chassis -> <scan_frame>`

Where:
- `odom -> chassis` comes from Gazebo via bridged `/tf`
- `chassis -> <scan_frame>` is provided by the static TF shim in Layer 1

The important launch arguments are:
- `base_frame` (defaults to `chassis`)
- `scan_frame` (defaults to `two_wheel_robot/lidar_link/lidar`)
- `laser_z` (defaults to `0.13` meters)

If slam_toolbox fails to start mapping, the first thing to check is:
- Does `tf2_echo odom chassis` work?
- Does `tf2_echo chassis <scan_frame>` work?

## Layer 2: slam_toolbox async mapping

File:
- [bnl_layer2_slam.launch.py](launch/bnl_layer2_slam.launch.py)

### LifecycleNode and why it matters

slam_toolbox is launched as a **LifecycleNode** (`async_slam_toolbox_node`).

LifecycleNodes start in the `unconfigured` state and must be transitioned:
- `configure` → `inactive`
- `activate` → `active`

This launch file provides an `autostart` option.

### Autostart logic (no external lifecycle manager)

When:
- `autostart:=true`
- `use_lifecycle_manager:=false`

the launch emits lifecycle transition events itself:
- Immediately after the slam delay: emit `CONFIGURE`
- When the node reaches `inactive`: emit `ACTIVATE`

When `use_lifecycle_manager:=true`, slam_toolbox expects an external bond-based lifecycle manager,
so this file intentionally does not emit transitions.

### Parameter layering (YAML + overrides)

slam_toolbox parameters are loaded in two steps:

1) Load YAML:
- [slam_toolbox_async.yaml](config/slam_toolbox_async.yaml)

2) Override a small set of bringup-critical values in launch:
- `use_sim_time`
- `scan_topic` (forced to `/scan`)
- `map_frame`, `odom_frame`
- `base_frame` (from launch arg)

Reason: it keeps the mapping contract deterministic even if someone edits the YAML.

## The slam_toolbox params file

File:
- [slam_toolbox_async.yaml](config/slam_toolbox_async.yaml)

Key intent of this file:
- `mode: mapping` to build a map live
- `publish_tf: true` so slam_toolbox publishes `map -> odom`
- Reasonable timeouts/buffer for simulation startup and bridge latency

## How to run + validate

### Run SLAM session (Layer 1 + Layer 2)

In the sim_folder workspace (after `colcon build` and sourcing `install/setup.bash`):

```bash
ros2 launch bnl_slam_bringup_pkg bnl_slam_layer2.launch.py
```

### Validate that slam_toolbox is active

```bash
ros2 lifecycle get /slam_toolbox
```

Expected: `active`.

### Validate topics

```bash
ros2 topic info /scan --verbose
ros2 topic info /map --verbose
ros2 topic info /tf --verbose
```

Expected:
- `/scan` has a publisher (bridge)
- `/map` has a publisher (`slam_toolbox`)

### Validate TF chain

```bash
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom chassis
ros2 run tf2_ros tf2_echo chassis two_wheel_robot/lidar_link/lidar
```

If either fails:
- check that Layer 1 is running and the bridge is publishing
- check that `scan_frame` matches the LaserScan `header.frame_id`
