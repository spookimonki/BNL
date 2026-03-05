#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from geometry_msgs.msg import PoseStamped
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from nav_msgs.msg import OccupancyGrid
from std_msgs.msg import String
import tf2_ros

from bnl_autonomy.util import XY, yaw_to_quaternion


@dataclass
class _MapMeta:
    width: int
    height: int
    resolution: float
    origin_x: float
    origin_y: float


class FrontierExplorerNode(Node):
    """Compute frontiers from /map and publish a randomized frontier goal."""

    def __init__(self) -> None:
        super().__init__('frontier_explorer_node')

        self.declare_parameter('map_topic', '/map')
        self.declare_parameter('goal_topic', '/autonomy/explore_goal')
        self.declare_parameter('mode_topic', '/autonomy/mode')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('plan_period_sec', 4.0)
        self.declare_parameter('min_frontier_size', 20)
        self.declare_parameter('min_goal_dist', 0.8)
        self.declare_parameter('max_goal_dist', 8.0)
        self.declare_parameter('random_top_k', 4)
        self.declare_parameter('score_noise_std', 0.2)
        self.declare_parameter('escape_sample_prob', 0.10)
        self.declare_parameter('escape_min_dist', 2.0)

        self._mode: str = 'IDLE'
        self._latest_map: Optional[OccupancyGrid] = None

        self._tf_buffer = tf2_ros.Buffer(cache_time=Duration(seconds=10.0))
        self._tf_listener = tf2_ros.TransformListener(self._tf_buffer, self, spin_thread=True)

        map_topic = str(self.get_parameter('map_topic').value)
        self.create_subscription(OccupancyGrid, map_topic, self._on_map, 10)

        mode_topic = str(self.get_parameter('mode_topic').value)
        self.create_subscription(String, mode_topic, self._on_mode, 10)

        goal_topic = str(self.get_parameter('goal_topic').value)
        self._goal_pub = self.create_publisher(PoseStamped, goal_topic, 10)

        period = float(self.get_parameter('plan_period_sec').value)
        self.create_timer(period, self._tick)

        self.get_logger().info(
            f'Frontier explorer active. map_topic={map_topic} goal_topic={goal_topic} period={period}s'
        )

    def _on_mode(self, msg: String) -> None:
        self._mode = str(msg.data)

    def _on_map(self, msg: OccupancyGrid) -> None:
        self._latest_map = msg

    def _robot_xy_map(self) -> Optional[XY]:
        map_frame = str(self.get_parameter('map_frame').value)
        base_frame = str(self.get_parameter('base_frame').value)
        try:
            tf_msg = self._tf_buffer.lookup_transform(map_frame, base_frame, Time())
            return XY(float(tf_msg.transform.translation.x), float(tf_msg.transform.translation.y))
        except Exception:
            return None

    @staticmethod
    def _idx(meta: _MapMeta, x: int, y: int) -> int:
        return y * meta.width + x

    @staticmethod
    def _in_bounds(meta: _MapMeta, x: int, y: int) -> bool:
        return 0 <= x < meta.width and 0 <= y < meta.height

    def _frontier_clusters(self, grid: List[int], meta: _MapMeta) -> List[List[Tuple[int, int]]]:
        """Return clusters of frontier cells (unknown adjacent to free)."""
        frontier = [[False] * meta.width for _ in range(meta.height)]
        for y in range(1, meta.height - 1):
            for x in range(1, meta.width - 1):
                v = grid[self._idx(meta, x, y)]
                if v != -1:
                    continue
                # 4-neighborhood adjacency to free space
                if (
                    grid[self._idx(meta, x + 1, y)] == 0
                    or grid[self._idx(meta, x - 1, y)] == 0
                    or grid[self._idx(meta, x, y + 1)] == 0
                    or grid[self._idx(meta, x, y - 1)] == 0
                ):
                    frontier[y][x] = True

        visited = [[False] * meta.width for _ in range(meta.height)]
        clusters: List[List[Tuple[int, int]]] = []
        for y in range(meta.height):
            for x in range(meta.width):
                if not frontier[y][x] or visited[y][x]:
                    continue
                q = [(x, y)]
                visited[y][x] = True
                cluster: List[Tuple[int, int]] = []
                while q:
                    cx, cy = q.pop()
                    cluster.append((cx, cy))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = cx + dx, cy + dy
                        if not self._in_bounds(meta, nx, ny):
                            continue
                        if visited[ny][nx] or not frontier[ny][nx]:
                            continue
                        visited[ny][nx] = True
                        q.append((nx, ny))
                clusters.append(cluster)

        return clusters

    def _cell_to_world(self, meta: _MapMeta, cell: Tuple[int, int]) -> XY:
        cx, cy = cell
        wx = meta.origin_x + (cx + 0.5) * meta.resolution
        wy = meta.origin_y + (cy + 0.5) * meta.resolution
        return XY(wx, wy)

    def _world_to_cell(self, meta: _MapMeta, xy: XY) -> Optional[Tuple[int, int]]:
        x = int((xy.x - meta.origin_x) / meta.resolution)
        y = int((xy.y - meta.origin_y) / meta.resolution)
        if self._in_bounds(meta, x, y):
            return (x, y)
        return None

    def _is_free_near(self, grid: List[int], meta: _MapMeta, cell: Tuple[int, int], radius_cells: int = 2) -> bool:
        cx, cy = cell
        for dy in range(-radius_cells, radius_cells + 1):
            for dx in range(-radius_cells, radius_cells + 1):
                nx, ny = cx + dx, cy + dy
                if not self._in_bounds(meta, nx, ny):
                    return False
                v = grid[self._idx(meta, nx, ny)]
                if v != 0:
                    return False
        return True

    def _pick_goal(self, occ: OccupancyGrid, robot_xy: XY) -> Optional[XY]:
        meta = _MapMeta(
            width=int(occ.info.width),
            height=int(occ.info.height),
            resolution=float(occ.info.resolution),
            origin_x=float(occ.info.origin.position.x),
            origin_y=float(occ.info.origin.position.y),
        )
        grid = list(occ.data)

        # Escape sampling: random free-space goal within known map
        escape_prob = float(self.get_parameter('escape_sample_prob').value)
        if random.random() < escape_prob:
            goal = self._sample_random_free(grid, meta, robot_xy)
            if goal is not None:
                return goal

        clusters = self._frontier_clusters(grid, meta)
        min_size = int(self.get_parameter('min_frontier_size').value)
        clusters = [c for c in clusters if len(c) >= min_size]
        if not clusters:
            return None

        min_dist = float(self.get_parameter('min_goal_dist').value)
        max_dist = float(self.get_parameter('max_goal_dist').value)
        top_k = max(1, int(self.get_parameter('random_top_k').value))
        noise_std = float(self.get_parameter('score_noise_std').value)

        scored: List[Tuple[float, XY]] = []
        for cluster in clusters:
            # centroid in cell coords
            sx = sum(c[0] for c in cluster)
            sy = sum(c[1] for c in cluster)
            cx = sx / float(len(cluster))
            cy = sy / float(len(cluster))
            cell = (int(cx), int(cy))
            if not self._in_bounds(meta, cell[0], cell[1]):
                continue
            if not self._is_free_near(grid, meta, cell, radius_cells=2):
                continue

            goal_xy = self._cell_to_world(meta, cell)
            dist = math.hypot(goal_xy.x - robot_xy.x, goal_xy.y - robot_xy.y)
            if dist < min_dist or dist > max_dist:
                continue

            info_gain = float(len(cluster))
            score = 0.04 * info_gain - 1.0 * dist
            score += random.gauss(0.0, noise_std)
            scored.append((score, goal_xy))

        if not scored:
            return None

        scored.sort(key=lambda t: t[0], reverse=True)
        choices = scored[: min(top_k, len(scored))]
        _score, choice = random.choice(choices)
        return choice

    def _sample_random_free(self, grid: List[int], meta: _MapMeta, robot_xy: XY) -> Optional[XY]:
        escape_min_dist = float(self.get_parameter('escape_min_dist').value)
        free_cells: List[Tuple[int, int]] = []

        # Randomly probe cells (bounded iterations), avoid scanning full map every tick.
        probes = 2000
        for _ in range(probes):
            x = random.randint(0, meta.width - 1)
            y = random.randint(0, meta.height - 1)
            if grid[self._idx(meta, x, y)] != 0:
                continue
            cell = (x, y)
            if not self._is_free_near(grid, meta, cell, radius_cells=1):
                continue
            goal_xy = self._cell_to_world(meta, cell)
            if math.hypot(goal_xy.x - robot_xy.x, goal_xy.y - robot_xy.y) < escape_min_dist:
                continue
            free_cells.append(cell)
            if len(free_cells) >= 20:
                break

        if not free_cells:
            return None
        return self._cell_to_world(meta, random.choice(free_cells))

    def _tick(self) -> None:
        if self._mode != 'EXPLORE':
            return
        occ = self._latest_map
        if occ is None:
            return
        robot_xy = self._robot_xy_map()
        if robot_xy is None:
            return

        goal_xy = self._pick_goal(occ, robot_xy)
        if goal_xy is None:
            return

        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = str(self.get_parameter('map_frame').value)
        msg.pose.position.x = float(goal_xy.x)
        msg.pose.position.y = float(goal_xy.y)
        msg.pose.position.z = 0.0
        # Leave yaw neutral; controller will handle.
        qx, qy, qz, qw = yaw_to_quaternion(0.0)
        msg.pose.orientation.x = qx
        msg.pose.orientation.y = qy
        msg.pose.orientation.z = qz
        msg.pose.orientation.w = qw
        self._goal_pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = FrontierExplorerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
