# BNL Layer-2 SLAM Bringup (slam_toolbox mapping)

This package owns the **stable Layer-2 SLAM mapping** entrypoint for BNL.

- Uses the Layer-1 platform contract: `/scan`, `/odom`, bridged `/tf`, and a single TF shim `chassis→<scan_frame>`
- Starts `slam_toolbox` in **mapping** mode
- Ensures `slam_toolbox` lifecycle transitions to `active` (required for `/map` output)

## Run

From the sim workspace:

`cd /home/monki/meka2002/BNL/src/sim_folder && colcon build --symlink-install`

`source /home/monki/meka2002/BNL/src/sim_folder/install/setup.bash`

### Single-command SLAM session (includes Layer-1)

`ros2 launch bnl_slam_bringup_pkg bnl_slam_layer2.launch.py`

### Layered (recommended when using the full autonomy pipeline)

1) Launch Layer-1

`ros2 launch bnl_bringup_pkg bnl_layer1_sim.launch.py`

2) Launch Layer-2

`ros2 launch bnl_slam_bringup_pkg bnl_layer2_slam.launch.py`

## Proof checklist

- `ros2 lifecycle get /slam_toolbox` → `active [3]`
- `ros2 topic echo /map --once`
- `ros2 run tf2_ros tf2_echo map odom`
