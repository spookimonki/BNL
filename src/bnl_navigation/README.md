# BNL Layer-3 Nav2 Bringup (mapping mode)

This package brings up **Nav2 for navigation while SLAM is running**:

- Uses SLAM’s `map→odom` transform (no AMCL)
- Uses `/map` for the global costmap static layer
- Uses `/scan` for obstacle layers
- Publishes velocity commands on `/cmd_vel` (geometry_msgs/Twist)

## Run

From the sim workspace:

`cd /home/monki/meka2002/BNL/src/sim_folder && colcon build --symlink-install`

`source /home/monki/meka2002/BNL/src/sim_folder/install/setup.bash`

### Nav2 only (assumes Layer-1 + SLAM already running)

`ros2 launch bnl_nav2_bringup_pkg bnl_layer3_nav2.launch.py`

### Optional exploration (assumes Nav2 is active)

`ros2 run bnl_nav2_bringup_pkg bnl_explore_random_goals --ros-args -p max_radius:=3.0`
