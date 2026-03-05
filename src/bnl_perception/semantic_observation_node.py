#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import threading
from typing import Dict, List, Tuple

from geometry_msgs.msg import PoseStamped
import rclpy
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from bnl_msgs.srv import DetectBanana
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.time import Time
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image
from bnl_msgs.msg import SemanticObservation
import tf2_ros
import yaml


@dataclass
class _CachedDetection:
    stamp: Time
    confidence: float
    pixel_u: int
    pixel_v: int
    pose_map: PoseStamped


class SemanticObservationNode(Node):
    def __init__(self) -> None:
        super().__init__('semantic_observation_node')

        self._image_cb_group = ReentrantCallbackGroup()
        self._service_cb_group = ReentrantCallbackGroup()
        self._cache_lock = threading.Lock()

        default_filter_path = str(
            Path(get_package_share_directory('bnl_perception')) / 'config' / 'detection_filter.yaml'
        )

        self.declare_parameter('image_topic', '/camera/image_raw')
        # YOLACT is treated as an external dependency. Prefer providing paths via:
        #   - parameters (yolact_repo_path, yolact_model_path), or
        #   - env vars (YOLACT_REPO_PATH, YOLACT_MODEL_PATH).
        self.declare_parameter('yolact_repo_path', os.environ.get('YOLACT_REPO_PATH', ''))
        self.declare_parameter('yolact_model_path', os.environ.get('YOLACT_MODEL_PATH', ''))
        self.declare_parameter('score_threshold', 0.15)
        self.declare_parameter('top_k', 15)
        self.declare_parameter('ground_offset_px', 5)
        self.declare_parameter('filter_config_file', default_filter_path)
        # Banana MVP: service + TF settings.
        self.declare_parameter('detect_banana_service', '/detect_banana')
        self.declare_parameter('base_frame', 'chassis')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('fallback_frame', 'odom')
        self.declare_parameter('cache_timeout_sec', 2.0)

        self._bridge = CvBridge()
        self._ground_offset_px = int(self.get_parameter('ground_offset_px').value)
        self._active_classes, self._confidence_threshold = self._load_filter_config()

        self._class_name_to_id: Dict[str, int] = {}
        self._class_id_to_name: Dict[int, str] = {}
        self._yolact, self._fast_base_transform, self._postprocess, self._torch, self._device = self._init_yolact_runtime()

        self.get_logger().info(f"YOLACT inference device: {self._device}")

        self._tf_buffer = tf2_ros.Buffer(cache_time=Duration(seconds=10.0))
        self._tf_listener = tf2_ros.TransformListener(self._tf_buffer, self, spin_thread=True)

        self._banana_cache: _CachedDetection | None = None

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        image_topic = str(self.get_parameter('image_topic').value)
        self._sub = self.create_subscription(
            Image,
            image_topic,
            self._on_image,
            qos,
            callback_group=self._image_cb_group,
        )
        self._pub = self.create_publisher(SemanticObservation, '/semantic_observation', qos)

        detect_srv = str(self.get_parameter('detect_banana_service').value)
        self._srv = self.create_service(
            DetectBanana,
            detect_srv,
            self._on_detect_banana,
            callback_group=self._service_cb_group,
        )

        self.get_logger().info(
            f'SemanticObservation node active. image_topic={image_topic} '
            f'active_classes={sorted(self._active_classes)} conf_threshold={self._confidence_threshold}'
        )

    def _on_detect_banana(self, _request: DetectBanana.Request, response: DetectBanana.Response) -> DetectBanana.Response:
        with self._cache_lock:
            cache = self._banana_cache
        if cache is None:
            response.found = False
            response.confidence = 0.0
            response.pose_map = PoseStamped()
            response.pixel_u = -1
            response.pixel_v = -1
            return response

        timeout = Duration(seconds=float(self.get_parameter('cache_timeout_sec').value))
        age = self.get_clock().now() - cache.stamp
        if age > timeout:
            response.found = False
            response.confidence = 0.0
            response.pose_map = PoseStamped()
            response.pixel_u = -1
            response.pixel_v = -1
            return response

        response.found = True
        response.confidence = float(cache.confidence)
        response.pose_map = cache.pose_map
        response.pixel_u = int(cache.pixel_u)
        response.pixel_v = int(cache.pixel_v)
        return response

    def _robot_pose_for_stamp(self, stamp_msg) -> PoseStamped:
        """Best-effort TF lookup for robot pose; used to tag the latest banana detection.

        NOTE: This pose is the robot base pose (base_frame) expressed in map/fallback frame,
        not a metrically triangulated banana 3D position (no depth in this MVP).
        """
        base_frame = str(self.get_parameter('base_frame').value)
        map_frame = str(self.get_parameter('map_frame').value)
        fallback_frame = str(self.get_parameter('fallback_frame').value)

        query_time = Time.from_msg(stamp_msg)

        def _pose_from_transform(target_frame: str):
            tf_msg = self._tf_buffer.lookup_transform(target_frame, base_frame, query_time, timeout=Duration(seconds=0.10))
            pose = PoseStamped()
            pose.header.stamp = stamp_msg
            pose.header.frame_id = target_frame
            pose.pose.position.x = float(tf_msg.transform.translation.x)
            pose.pose.position.y = float(tf_msg.transform.translation.y)
            pose.pose.position.z = float(tf_msg.transform.translation.z)
            pose.pose.orientation = tf_msg.transform.rotation
            return pose

        try:
            return _pose_from_transform(map_frame)
        except Exception:
            try:
                return _pose_from_transform(fallback_frame)
            except Exception:
                pose = PoseStamped()
                pose.header.stamp = stamp_msg
                pose.header.frame_id = base_frame
                pose.pose.orientation.w = 1.0
                return pose

    def _load_filter_config(self) -> Tuple[set[str], float]:
        config_file = Path(str(self.get_parameter('filter_config_file').value))
        if not config_file.exists():
            raise FileNotFoundError(f'detection filter config not found: {config_file}')

        with config_file.open('r', encoding='utf-8') as f:
            payload = yaml.safe_load(f) or {}

        active_classes_raw = payload.get('active_classes', ['chair'])
        active_classes = {str(class_name).strip() for class_name in active_classes_raw if str(class_name).strip()}
        if not active_classes:
            active_classes = {'chair'}
        confidence_threshold = float(payload.get('confidence_threshold', 0.5))
        return active_classes, confidence_threshold

    def _resolve_existing_dir(self, candidates: List[Path]) -> Path | None:
        for candidate in candidates:
            try:
                resolved = candidate.expanduser().resolve()
            except Exception:
                continue
            if resolved.exists() and resolved.is_dir():
                return resolved
        return None

    def _resolve_existing_file(self, candidates: List[Path]) -> Path | None:
        for candidate in candidates:
            try:
                resolved = candidate.expanduser().resolve()
            except Exception:
                continue
            if resolved.exists() and resolved.is_file():
                return resolved
        return None

    def _find_yolact_repo(self) -> Path:
        raw = str(self.get_parameter('yolact_repo_path').value).strip()
        if raw:
            candidate = Path(raw).expanduser().resolve()
            if candidate.exists() and candidate.is_dir():
                return candidate

        cwd = Path.cwd()
        home = Path.home()
        candidates: List[Path] = [
            cwd / 'yolact',
            cwd / 'AI_cam' / 'yolact',
            cwd.parent / 'AI_cam' / 'yolact',
            home / 'yolact',
            home / 'AI_cam' / 'yolact',
        ]

        # Walk up a few levels and try common layouts (e.g. monorepo with BNL + AI_cam siblings).
        parent = cwd
        for _ in range(6):
            candidates.append(parent / 'AI_cam' / 'yolact')
            candidates.append(parent / 'yolact')
            parent = parent.parent

        resolved = self._resolve_existing_dir(candidates)
        if resolved is None:
            raise FileNotFoundError(
                'YOLACT repo path not found. Set parameter yolact_repo_path or env var YOLACT_REPO_PATH '
                '(e.g. export YOLACT_REPO_PATH=/abs/path/to/yolact).'
            )

        # Minimal sanity check: ensure it looks like a YOLACT checkout.
        if not (resolved / 'yolact.py').exists():
            raise FileNotFoundError(f'Provided YOLACT repo does not look valid (missing yolact.py): {resolved}')
        return resolved

    def _find_yolact_weights(self, yolact_repo_path: Path) -> Path:
        raw = str(self.get_parameter('yolact_model_path').value).strip()
        if raw:
            candidate = Path(raw).expanduser().resolve()
            if candidate.exists() and candidate.is_file():
                return candidate

        # Default to a common filename if present; otherwise pick the first .pth in weights/.
        weights_dir = yolact_repo_path / 'weights'
        candidates: List[Path] = [
            weights_dir / 'yolact_base_54_800000.pth',
        ]
        resolved = self._resolve_existing_file(candidates)
        if resolved is not None:
            return resolved

        if weights_dir.exists() and weights_dir.is_dir():
            any_pth = sorted(weights_dir.glob('*.pth'))
            if any_pth:
                return any_pth[0].resolve()

        raise FileNotFoundError(
            'YOLACT weights not found. Set parameter yolact_model_path or env var YOLACT_MODEL_PATH '
            '(e.g. export YOLACT_MODEL_PATH=/abs/path/to/yolact/weights/<file>.pth).'
        )

    def _init_yolact_runtime(self):
        yolact_repo_path = self._find_yolact_repo()
        model_path = self._find_yolact_weights(yolact_repo_path)

        import sys

        sys.path.insert(0, str(yolact_repo_path))

        import torch
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        from data import cfg, set_cfg
        from layers.output_utils import postprocess
        from utils.augmentations import FastBaseTransform
        from yolact import Yolact

        set_cfg('yolact_base_config')

        yolact = Yolact()
        yolact.load_weights(str(model_path))
        yolact.to(device)
        yolact.eval()

        class_names = list(cfg.dataset.class_names)
        self._class_name_to_id = {name: idx for idx, name in enumerate(class_names)}
        self._class_id_to_name = {idx: name for name, idx in self._class_name_to_id.items()}

        return yolact, FastBaseTransform, postprocess, torch, device

    def _on_image(self, image_msg: Image) -> None:
        try:
            image_bgr = self._bridge.imgmsg_to_cv2(image_msg, desired_encoding='bgr8')
            detections = self._infer_detections(image_bgr)
            self._publish_observations(image_msg, detections)
        except Exception as exc:
            self.get_logger().error(f'detection callback failed: {exc}')

    def _infer_detections(self, image_bgr) -> List[Tuple[str, float, int, int, int, int]]:
        torch = self._torch

        with torch.no_grad():
            height, width = image_bgr.shape[:2]
            frame = torch.from_numpy(image_bgr).float()
            frame = frame.to(self._device)
            batch = self._fast_base_transform()(frame.unsqueeze(0))
            preds = self._yolact(batch)

            score_threshold = float(self.get_parameter('score_threshold').value)
            top_k = int(self.get_parameter('top_k').value)

            classes, scores, boxes, _masks = self._postprocess(
                preds,
                width,
                height,
                score_threshold=score_threshold,
            )

            if hasattr(classes, 'numel') and classes.numel() == 0:
                return []

            classes = classes.detach().cpu().numpy()
            scores = scores.detach().cpu().numpy()
            boxes = boxes.detach().cpu().numpy()

            if top_k > 0:
                classes = classes[:top_k]
                scores = scores[:top_k]
                boxes = boxes[:top_k]

        output: List[Tuple[str, float, int, int, int, int]] = []
        for class_idx, confidence, box in zip(classes, scores, boxes):
            class_name = self._class_id_to_name.get(int(class_idx))
            if class_name is None:
                continue

            xmin, ymin, xmax, ymax = [int(v) for v in box]
            output.append((class_name, float(confidence), xmin, ymin, xmax, ymax))

        return output

    def _publish_observations(
        self,
        image_msg: Image,
        detections: List[Tuple[str, float, int, int, int, int]],
    ) -> None:
        for class_label, confidence, xmin, _ymin, xmax, ymax in detections:
            if class_label not in self._active_classes:
                continue
            if confidence < self._confidence_threshold:
                continue

            u_center = max(0, int((xmin + xmax) / 2))
            v_ground = max(0, int(ymax - self._ground_offset_px))

            observation = SemanticObservation()
            observation.header.stamp = image_msg.header.stamp
            observation.header.frame_id = image_msg.header.frame_id
            observation.class_label = class_label
            observation.class_id = int(self._class_name_to_id.get(class_label, 0))
            observation.confidence = float(confidence)
            observation.pixel_u = min(65535, u_center)
            observation.pixel_v = min(65535, v_ground)
            self._pub.publish(observation)

            # Banana MVP: cache the latest accepted banana detection for the service.
            if class_label == 'banana':
                pose_map = self._robot_pose_for_stamp(image_msg.header.stamp)
                with self._cache_lock:
                    self._banana_cache = _CachedDetection(
                        stamp=self.get_clock().now(),
                        confidence=float(confidence),
                        pixel_u=int(u_center),
                        pixel_v=int(v_ground),
                        pose_map=pose_map,
                    )


def main() -> None:
    rclpy.init()
    node = SemanticObservationNode()
    try:
        executor = MultiThreadedExecutor(num_threads=2)
        executor.add_node(node)
        executor.spin()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
