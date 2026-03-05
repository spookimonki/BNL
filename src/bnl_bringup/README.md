# BNL Layer-1 Bringup (Simulation + Sensors + TF)

This package owns the **stable Layer-1 contract** for the BNL sim workspace:

- Gazebo Sim GUI
- Single `ros_gz_bridge` instance
- Minimal static TF shims to connect the known working TF chain
- Optional RViz2 for sensor visualization

## Run

From the sim workspace:

1) Build

`cd /home/monki/meka2002/BNL/src/sim_folder && colcon build --symlink-install`

2) Source

`source /home/monki/meka2002/BNL/src/sim_folder/install/setup.bash`

3) Launch Layer-1

`ros2 launch bnl_bringup_pkg bnl_layer1_sim.launch.py rviz:=true`

## One-click full autonomy (Layer1 + SLAM + Nav2 + optional exploration)

See the dedicated top-level package `bnl_autonomy_bringup_pkg`.

## Contract checks

- `ros2 topic echo /scan --once` (frame_id should be `two_wheel_robot/lidar_link/lidar`)
- `ros2 topic echo /odom --once` (frame_id `odom`, child_frame_id `chassis`)
- `ros2 topic info /tf /tf_static`

## Notes

- This launch refuses to start if an older bringup is still running (it detects node-name collisions and exits). Stop the older launch cleanly (Ctrl-C) and retry.
