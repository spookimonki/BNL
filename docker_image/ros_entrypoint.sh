#!/bin/bash
set -e

# setup ros2 environment
source "/opt/ros/${ROS_DISTRO}/setup.bash"

#sudo apt remove --purge rpicam-apps

#sudo apt install -y libcamera-dev libepoxy-dev libjpeg-dev libtiff5-dev libpng-dev libopencv-dev

git clone --recursive "https://github.com/Havlia/BNL"
cd BNL
#colcon build
#source install/setup.bash
#source install/local_setup.bash 
#ros2 launch wg_bringup wg.launch.py mode:=real --
exec "$@"
