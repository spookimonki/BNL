#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROS_DISTRO="${ROS_DISTRO:-jazzy}"

# Avoid picking up stale overlay prefixes from a previously sourced workspace.
unset AMENT_PREFIX_PATH 2>/dev/null || true
unset COLCON_PREFIX_PATH 2>/dev/null || true
unset CMAKE_PREFIX_PATH 2>/dev/null || true
unset ROS_PACKAGE_PATH 2>/dev/null || true
unset PYTHONPATH 2>/dev/null || true

set +u
source "/opt/ros/${ROS_DISTRO}/setup.bash"
set -u

cd "$ROOT"
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install

echo "Build complete. Source with: source $ROOT/install/setup.bash"