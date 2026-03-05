# BNL

BNL is a ROS 2 (Jazzy) workspace for running a Gazebo simulation with a stable mapping + navigation pipeline, plus optional perception/autonomy layers.

The core contract (frames + topics) is documented in [ARCHITECTURE.md](ARCHITECTURE.md).

## Workspace layout

- `BNL/src/*`: primary ROS 2 packages
    - `bnl_bringup`: simulation bringup + top-level launch entrypoints
    - `bnl_sim`: installs Gazebo worlds/models into package share
    - `bnl_slam`: SLAM Toolbox layer
    - `bnl_navigation`: Nav2 + `twist_mux` layer
    - `bnl_perception`: YOLACT-based semantic observation (optional)
    - `bnl_projection`: projects semantic pixels into 2D map coordinates
    - `bnl_autonomy`: simple autonomy/exploration nodes (optional)
    - `bnl_msgs`: minimal custom interfaces (msgs/srvs)
- `BNL/docker_image/` and `BNL/private_docker/`: Dockerfiles used by the team
- `BNL/src/sim_folder/`: legacy workspace kept for reference (not the primary build)

## Quick start (native)

Prereqs: ROS 2 Jazzy installed and your system can run Gazebo. See [INSTALL.md](INSTALL.md).

Build:

```bash
cd BNL
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Or use the helper script:

```bash
./scripts/build.sh
```

Run simulation (+ SLAM + Nav2 + RViz):

```bash
ros2 launch bnl_bringup sim.launch.py
```

Or:

```bash
./scripts/run_sim.sh
```

Show launch args:

```bash
ros2 launch bnl_bringup sim.launch.py --show-args
```

## Optional: autonomy + perception

Perception depends on an external YOLACT checkout + a `.pth` weights file.

You can provide paths via environment variables:

```bash
export YOLACT_REPO_PATH=/abs/path/to/yolact
export YOLACT_MODEL_PATH=/abs/path/to/yolact/weights/<weights>.pth
```

Then launch autonomy (includes the semantic observation service):

```bash
ros2 launch bnl_autonomy autonomy.launch.py
```

Or:

```bash
./scripts/run_autonomy.sh
```

## Quick start (Docker)

This repo includes two Docker contexts:

- `docker_image/`: base image
- `private_docker/`: developer image (clones a Git repo inside the image)

Build (base image):

```bash
cd BNL
sudo docker build -t bnl:ros-image docker_image
```

Run (no GUI):

```bash
sudo docker run --rm -it bnl:ros-image
```

If you need GUI apps (Gazebo/RViz), run Docker with X11 support (e.g. via `rocker`).

## Notes

- This workspace intentionally uses the ROS-distributed `slam_toolbox` on Jazzy; any vendored/incompatible copy should remain excluded from the build.
- ML weights are not committed; put them in a local `weights/` directory or inside your YOLACT checkout.
```

Kjør bringup:

```console
ros2 launch bnl_bringup_pkg bnl_layer1_sim.launch.py
```

Valgfritt: start RViz (sensor view):

```console
ros2 launch bnl_bringup_pkg bnl_layer1_sim.launch.py rviz:=true
```

Note: For å unngå duplikate TF-publishere må du ikke ha gamle `static_transform_publisher`-prosesser kjørende samtidig.

## One-click full autonomy (Layer 1 + SLAM + Nav2)

Dette starter Gazebo + SLAM Toolbox (mapping) + Nav2 (mapping mode) + RViz, med samme kontrakt som over.

```console
ros2 launch bnl_autonomy_bringup_pkg bnl_full_autonomy.launch.py explore:=true
```
