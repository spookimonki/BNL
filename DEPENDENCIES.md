# Dependencies (BNL)

This doc is a high-level summary. The authoritative way to install ROS deps is:

```bash
cd BNL
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
```

## ROS 2 packages (expected)

- ROS 2 Jazzy desktop (includes RViz2)
- Gazebo Sim integration + bridge
  - `ros_gz_sim` (launching Gazebo)
  - `ros_gz_bridge` (topic bridge)
- SLAM
  - `slam_toolbox` (Jazzy distro package)
- Navigation
  - Nav2 stack
  - `twist_mux`
- TF / common ROS utilities
  - `tf2_ros`, `ament_index_python`, etc.

## Python dependencies (perception)

If you run `bnl_perception` (YOLACT inference), you typically need:

- `torch` / `torchvision`
- `opencv-python` (or system OpenCV)
- `cv_bridge` (ROS package)
- YOLACT source checkout available on disk

Weights:
- `.pth` model weights are required at runtime but not stored in this repo.
