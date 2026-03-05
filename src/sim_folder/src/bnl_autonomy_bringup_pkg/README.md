# BNL Full Autonomy Bringup

Single deterministic entrypoint to start:

- Gazebo GUI (Layer-1)
- slam_toolbox mapping (Layer-2)
- Nav2 navigation (Layer-3)
- RViz2 configured for SLAM + Nav2
- Optional exploration behavior (random goal selection validated by planner)

## Run

From the sim workspace:

`cd /home/monki/meka2002/BNL/src/sim_folder && colcon build --symlink-install`

`source /home/monki/meka2002/BNL/src/sim_folder/install/setup.bash`

`ros2 launch bnl_autonomy_bringup_pkg bnl_full_autonomy.launch.py explore:=false`

Enable exploration:

`ros2 launch bnl_autonomy_bringup_pkg bnl_full_autonomy.launch.py explore:=true`

## Launch arguments (most useful)

- `slam` (default: true): enable slam_toolbox mapping layer
- `nav2` (default: true): enable Nav2 navigation layer (no AMCL)
- `explore` (default: false): random-goal exploration (requires `nav2:=true`)
- `rviz` (default: true): bring up RViz
- `use_sim_time` (default: true): keep true for all nodes

Frame/topic contract inputs (defaults match current sim):

- `base_frame` (default: `chassis`)
- `scan_frame` (default: `two_wheel_robot/lidar_link/lidar`)

## What you should see (verification checklist)

1) Simulation + bridge + TF shims are up:

`ros2 node list | egrep 'ros_gz_bridge|tf_'`

2) SLAM is publishing a map (when `slam:=true`):

`ros2 topic echo -n 1 /map --no-arr`

3) TF has `map -> odom` from SLAM and `odom -> chassis` from sim/TF shims:

`ros2 run tf2_ros tf2_echo map odom`

`ros2 run tf2_ros tf2_echo odom chassis`

4) Nav2 servers are active (when `nav2:=true`):

`ros2 node list | egrep 'controller_server|planner_server|bt_navigator|behavior_server|waypoint_follower'`

5) Sending a Nav2 goal produces `/cmd_vel` (Gazebo contract):

`ros2 topic echo -n 1 /cmd_vel`

If any preflight check fails, this launch will exit early (it will not kill running processes). Stop the previous bringup cleanly (Ctrl-C) and retry.
