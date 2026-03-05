# pc_detection_pkg

Phase Core detection wrapper boundary package.
Subscribes/publishes only; estimation and state logic stays external.

## Banana MVP

This package provides a minimal YOLACT-based banana detector driven by a bridged Gazebo camera.

**Inputs**
- `/camera/image_raw` (`sensor_msgs/msg/Image`) — bridged from Gazebo (see BNL layer1 sim launch).

**Outputs**
- `/semantic_observation` (`shared_interfaces_pkg/msg/SemanticObservation`) — published for allowlisted classes.

**Service (MVP)**
- `/detect_banana` (`pc_detection_pkg/srv/DetectBanana`)
	- Returns the latest cached banana detection from continuous inference.
	- `pose_map` is the robot pose (`base_frame`) expressed in `map` if TF is available; otherwise it falls back to `odom`, then `base_frame`.
	- Pixel `(u,v)` is the detection center-bottom point used for downstream projection.

**Tools**
- `poll_detect_banana.py` — polls `/detect_banana` and prints one-line notifications.
