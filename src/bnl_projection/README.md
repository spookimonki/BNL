# pc_projection_pkg

Phase Core projection wrapper package.

## Nodes

- `semantic_projection_node.py` (ACTIVE)
- `semantic_observation_stub_publisher.py` (STUB)
- `semantic_xy_marker_node.py` (ACTIVE)

## I/O

`semantic_projection_node.py`
- Subscribes: `/scan`, `/camera/camera_info`, `/semantic_observation`, `/tf`, `/tf_static`
- Publishes: `/semantic_xy`

`semantic_observation_stub_publisher.py`
- Publishes: `/semantic_observation` with alternating static classes (`chair`, `teddy_bear`)

`semantic_xy_marker_node.py`
- Subscribes: `/semantic_xy`
- Publishes: `/semantic_xy_markers` (`visualization_msgs/MarkerArray`)
- Renders: sphere marker + text label per tracked semantic object in `map` frame
- Supports: class-based color, stable IDs for updates, stale marker cleanup
- Parameters:
	- `marker_scale_m`, `text_scale_m`, `label_height_m`
	- `update_frequency_hz`, `stale_object_sec`, `match_distance_m`
	- `confidence_threshold`, `hide_low_confidence`, `fade_low_confidence`
	- `map_frame`, `force_map_frame`

## Notes

- Projection uses TF target frame `map` with fallback `odom`.
- Stub publisher is simulation-only and should be disabled when detector output is available.
