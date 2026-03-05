# BNL Workspace Architecture (ROS 2 + Gazebo)

This document describes the **BNL** ROS 2 workspace under `BNL/src/`.

## Goals and contract

**Primary goal:** a stable, reviewable bringup pipeline for mapping + navigation in Gazebo.

**Hard frame policy (Option A):**

- No fake `base_link` / `base_footprint` frames in the active pipeline.
- The robot base frame is `chassis` (must match the SDF link name).
- TF chain:
  - `map → odom` is published by SLAM Toolbox.
  - `odom → chassis` is published by Gazebo (bridged `/tf`).
  - `chassis → <scan_frame>` is a single static shim (so LaserScan can transform into base).

**Velocity contract:**

- Navigation outputs `geometry_msgs/msg/Twist` (unstamped).
- Command chain:
  - Nav2 publishes `/cmd_vel`
  - `twist_mux` republishes `/cmd_vel_mux`
  - `ros_gz_bridge` bridges `/cmd_vel_mux` to Gazebo `/cmd_vel`

## Layering (entrypoints)

- **Layer 1:** `bnl_bringup/launch/bnl_layer1_sim.launch.py` (Gazebo + `ros_gz_bridge` + TF shim)
- **Layer 2:** `bnl_slam/launch/bnl_layer2_slam.launch.py` (SLAM Toolbox async mapping)
- **Layer 3:** `bnl_navigation/launch/bnl_layer3_nav2.launch.py` (Nav2 + `twist_mux`)
- **All-in-one:** `bnl_bringup/launch/sim.launch.py` (Layers 1–3 + optional RViz)

## Node graph (conceptual)

```mermaid
flowchart LR
  subgraph GZ[Gazebo (gz-sim)]
    GZscan[/scan_gpu (LaserScan)/]
    GZodom[/odom (Odometry)/]
    GZtf[/tf (Pose_V)/]
    GZcam[/camera_image (Image)/]
    GZcmd[/cmd_vel (Twist)/]
  end

  subgraph BR[Layer 1: Bridge + TF shim]
    BRbridge[ros_gz_bridge parameter_bridge]
    BRshim[tf2_ros static_transform_publisher\nchassis→scan_frame]
  end

  subgraph SLAM[Layer 2: SLAM]
    SLAMtb[slam_toolbox (async mapping)]
    MAP[/map/]
  end

  subgraph NAV[Layer 3: Nav2]
    NAV2[Nav2 servers\n(planner/controller/BT/behavior)]
    MUX[twist_mux\n(use_stamped: false)]
  end

  %% Gazebo -> bridge
  GZscan --> BRbridge
  GZodom --> BRbridge
  GZtf --> BRbridge
  GZcam --> BRbridge

  %% Bridge -> ROS topics
  BRbridge -->|remap| SCAN[/scan/]
  BRbridge --> ODOM[/odom/]
  BRbridge --> TF[/tf/]

  %% TF shim
  BRshim --> TF

  %% SLAM
  SCAN --> SLAMtb
  TF --> SLAMtb
  ODOM --> SLAMtb
  SLAMtb --> MAP
  SLAMtb -->|publishes| TF

  %% Nav2
  MAP --> NAV2
  SCAN --> NAV2
  TF --> NAV2
  ODOM --> NAV2
  NAV2 --> CMD[/cmd_vel/]
  CMD --> MUX
  MUX --> CMDMUX[/cmd_vel_mux/]

  %% ROS -> Gazebo cmd
  CMDMUX --> BRbridge
  BRbridge --> GZcmd
```

## Packages and responsibilities

BNL packages (under `BNL/src/`):

- `bnl_sim`
  - Gazebo worlds/models installed into package share (used by Layer 1)
- `bnl_bringup`
  - Layer 1 launch: Gazebo + `ros_gz_bridge` + single TF shim `chassis→scan_frame`
  - Top-level launch: `sim.launch.py` composing Layers 1–3 with startup delays
  - Owns the stable sim topic contract: `/scan`, `/odom`, `/tf`, `/clock`, `/cmd_vel_mux`, `/camera/image_raw`
- `bnl_slam`
  - Layer 2 launch: SLAM Toolbox mapping (lifecycle activation, RViz optional)
  - Owns SLAM params files for the sim contract
- `bnl_navigation`
  - Layer 3 launch: Nav2 servers + `twist_mux` (unstamped `Twist`)
  - Owns Nav2 params + RViz config(s)
- `bnl_perception` (optional)
  - Semantic observation node (YOLACT-based) publishing `bnl_msgs/SemanticObservation` and serving `bnl_msgs/DetectBanana`
- `bnl_projection` (optional)
  - Projects semantic observations + LaserScan + CameraInfo into `bnl_msgs/SemanticXY`
- `bnl_autonomy` (optional)
  - Example autonomy nodes (exploration/task execution)
- `bnl_msgs`
  - Minimal custom interfaces

## Operational notes

- Gazebo Transport discovery can be pinned via `GZ_IP` (passed into `ros_gz_bridge`).
- The frame contract assumes the robot base link is named `chassis` in the SDF.
