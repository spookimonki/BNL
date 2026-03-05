#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROS_DISTRO="${ROS_DISTRO:-jazzy}"

unset AMENT_PREFIX_PATH 2>/dev/null || true
unset COLCON_PREFIX_PATH 2>/dev/null || true
unset CMAKE_PREFIX_PATH 2>/dev/null || true
unset ROS_PACKAGE_PATH 2>/dev/null || true

set +u
source "/opt/ros/${ROS_DISTRO}/setup.bash"
source "$ROOT/install/setup.bash"
set -u

exec ros2 launch bnl_autonomy autonomy.launch.py "$@"