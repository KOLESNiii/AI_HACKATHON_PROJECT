"""Generate mock .glb assets for contracts/mock_room/mock_scene.json.

Run: uv run --extra reconstruction python scripts/generate_mock_glbs.py
Writes to frontend/public/mock_room/ (served by Vite at /mock_room/).

- Furniture boxes follow the asset invariant: bottom-centre at the origin, front faces +Z. Each box
  has a dark strip on the top-front edge so yaw is visible. The strip is inside the bounds, so
  the mesh bounds still equal bbox_m exactly.
- shell.glb is in room coordinates (not normalised): a floor plus walls whose start/end lie on
  the interior face, with thickness extending outward, and door/window openings cut out.
"""

import json
import math
import os
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent.parent
SCENE_PATH = ROOT / "contracts" / "mock_room" / "mock_scene.json"
OUT_DIR = ROOT / "frontend" / "public" / "mock_room"

COLOURS = {
    "item_bed": [110, 140, 190, 255],
    "item_desk": [185, 145, 105, 255],
    "item_wardrobe": [130, 110, 95, 255],
}
FRONT_MARKER = [30, 30, 35, 255]
WALL_COLOUR = [225, 222, 215, 255]
FLOOR_COLOUR = [170, 160, 145, 255]
DOOR_HEAD_HEIGHT_M = 2.05


def coloured_box(extents, rgba, centre) -> trimesh.Trimesh:
    box = trimesh.creation.box(extents=extents)
    box.apply_translation(centre)
    box.visual.vertex_colors = rgba
    return box


def furniture_mesh(w: float, h: float, d: float, rgba) -> trimesh.Trimesh:
    # The marker is a raised strip on the front of the top face. The body stops below it, so
    # no faces overlap (no z-fighting) and the combined bounds are still exactly w x h x d.
    marker_h, marker_d = min(0.02, h / 4), min(0.06, d / 4)
    body_h = h - marker_h
    body = coloured_box([w, body_h, d], rgba, [0, body_h / 2, 0])
    marker = coloured_box(
        [w * 0.8, marker_h, marker_d],
        FRONT_MARKER,
        [0, body_h + marker_h / 2, d / 2 - marker_d / 2],
    )
    mesh = trimesh.util.concatenate([body, marker])
    assert np.allclose(mesh.bounds, [[-w / 2, 0, -d / 2], [w / 2, h, d / 2]]), mesh.bounds
    return mesh


def rotate_y(v: np.ndarray, deg: float) -> np.ndarray:
    """Counter-clockwise about +Y viewed from above (yaw convention), on an (x, z) vector."""
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return np.array([v[0] * c + v[1] * s, -v[0] * s + v[1] * c])


def wall_piece(start, direction, outward, t0, t1, y0, y1, thickness) -> trimesh.Trimesh:
    """Box spanning [t0, t1] along the wall and [y0, y1] vertically, extruded outward."""
    length = t1 - t0
    mid = start + direction * (t0 + length / 2) + outward * (thickness / 2)
    box = trimesh.creation.box(extents=[length, y1 - y0, thickness])
    # Local X -> wall direction. Rotation about +Y by a maps local +X to (cos a, -sin a).
    angle = math.atan2(-direction[1], direction[0])
    box.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 1, 0]))
    box.apply_translation([mid[0], (y0 + y1) / 2, mid[1]])
    box.visual.vertex_colors = WALL_COLOUR
    return box


def assert_convex(poly: np.ndarray) -> None:
    edges = np.roll(poly, -1, axis=0) - poly
    cross = (
        edges[:, 0] * np.roll(edges, -1, axis=0)[:, 1]
        - edges[:, 1] * np.roll(edges, -1, axis=0)[:, 0]
    )
    if not (np.all(cross >= -1e-9) or np.all(cross <= 1e-9)):
        raise ValueError("Mock shell generator only supports convex floor polygons")


def shell_mesh(scene: dict) -> trimesh.Trimesh:
    """Mock-only shell. Assumes a convex floor polygon (outward side found from the centroid,
    floor drawn as the bounding rectangle); real shells come from Dev 1's pipeline."""
    poly = np.array([[p["x"], p["z"]] for p in scene["floor_polygon"]])
    assert_convex(poly)
    centroid = poly.mean(axis=0)
    (min_x, min_z), (max_x, max_z) = poly.min(axis=0), poly.max(axis=0)
    parts = [
        coloured_box(
            [max_x - min_x, 0.02, max_z - min_z],
            FLOOR_COLOUR,
            [(min_x + max_x) / 2, -0.01, (min_z + max_z) / 2],
        )
    ]

    for wall in scene["walls"]:
        start = np.array([wall["start"]["x"], wall["start"]["z"]])
        end = np.array([wall["end"]["x"], wall["end"]["z"]])
        length = float(np.linalg.norm(end - start))
        direction = (end - start) / length
        normal = np.array([-direction[1], direction[0]])
        outward = normal if np.dot((start + end) / 2 - centroid, normal) > 0 else -normal
        h, th = wall["height_m"], wall["thickness_m"]

        # Openings as (t0, t1, sill, head) along this wall.
        openings = []
        for win in scene["windows"]:
            if win["wall_id"] == wall["id"]:
                t0 = win["offset_along_wall_m"]
                t1 = t0 + win["width_m"]
                openings.append((t0, t1, win["sill_height_m"], win["head_height_m"]))
        for door in scene["doors"]:
            if door["wall_id"] != wall["id"]:
                continue
            hinge = np.array([door["hinge_pos"]["x"], door["hinge_pos"]["z"]])
            swing_side = -outward if door.get("swings_into_room", True) else outward
            # The closed leaf is wall-parallel; a 90-degree turn in the swing direction must point
            # it to the swing side. Clockwise is negative yaw, so closed = swing_side turned back.
            # Independent of swing_angle_deg, which is only how far the door opens.
            closed_dir = rotate_y(swing_side, 90 if door["swing_clockwise"] else -90)
            t_hinge = float(np.dot(hinge - start, direction))
            sign = 1 if np.dot(closed_dir, direction) > 0 else -1
            t_a, t_b = sorted([t_hinge, t_hinge + sign * door["width_m"]])
            openings.append((t_a, t_b, 0.0, DOOR_HEAD_HEIGHT_M))
        openings.sort()

        # Extend each wall by its thickness at both ends to close the outer corners.
        cursor = -th
        for t0, t1, sill, head in openings:
            if t0 > cursor:
                parts.append(wall_piece(start, direction, outward, cursor, t0, 0, h, th))
            if sill > 0:
                parts.append(wall_piece(start, direction, outward, t0, t1, 0, sill, th))
            if head < h:
                parts.append(wall_piece(start, direction, outward, t0, t1, head, h, th))
            cursor = t1
        parts.append(wall_piece(start, direction, outward, cursor, length + th, 0, h, th))

    return trimesh.util.concatenate(parts)


def main() -> None:
    scene = json.loads(SCENE_PATH.read_text())
    os.makedirs(OUT_DIR, exist_ok=True)

    for item in scene["furniture"]:
        b = item["bbox_m"]
        rgba = COLOURS.get(item["id"], [160, 160, 160, 255])
        mesh = furniture_mesh(b["width"], b["height"], b["depth"], rgba)
        mesh.export(OUT_DIR / Path(item["glb_url"]).name)

    shell_mesh(scene).export(OUT_DIR / Path(scene["shell_glb_url"]).name)
    print(f"Exported mock .glb files to {OUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
