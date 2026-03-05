# Install / Setup (BNL)

This workspace targets **ROS 2 Jazzy** (Ubuntu 24.04).

## 1) System prerequisites

- Ubuntu 24.04 (recommended)
- ROS 2 Jazzy installed (Desktop is convenient for RViz)
- Gazebo Sim + ROS↔Gazebo bridge packages (via ROS packages or your distro)

If you already have ROS Jazzy working:

```bash
source /opt/ros/jazzy/setup.bash
```

## 2) ROS dependencies via rosdep

From the repo root:

```bash
cd BNL
source /opt/ros/jazzy/setup.bash

# First-time only on a machine:
#   sudo rosdep init
#   rosdep update

rosdep install --from-paths src --ignore-src -r -y
```

## 3) Build

```bash
cd BNL
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 4) Run simulation bringup

```bash
ros2 launch bnl_bringup sim.launch.py
```

## 5) Optional: perception (YOLACT)

`bnl_perception` expects a local YOLACT checkout and a `.pth` weights file.

Provide paths via environment variables (recommended):

```bash
export YOLACT_REPO_PATH=/abs/path/to/yolact
export YOLACT_MODEL_PATH=/abs/path/to/yolact/weights/<weights>.pth
```

Then launch autonomy (which starts the semantic observation service):

```bash
ros2 launch bnl_autonomy autonomy.launch.py
```

Notes:
- ML weights are intentionally not committed to git.
- If you want CPU-only inference, `bnl_autonomy/launch/autonomy.launch.py` already forces CPU by clearing `CUDA_VISIBLE_DEVICES`.
