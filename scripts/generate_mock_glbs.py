"""Generate mock .glb assets for contracts/mock_room/mock_scene.json.

Run: uv run --extra reconstruction python scripts/generate_mock_glbs.py
Writes to services/reconstruction/fixtures/mock_room/ (served by the reconstruction API).

- Furniture boxes follow the asset invariant: bottom-centre at the origin, front faces +Z. Each box
  has a dark strip on the top-front edge so yaw is visible. The strip is inside the bounds, so
  the mesh bounds still equal bbox_m exactly.
- shell.glb follows the shell rules in contracts/schema.py: room coordinates, nodes `floor`,
  `ceiling` and `wall_<id>`, walls on the interior face with thickness along the outward normal,
  door/window openings cut out.
"""

import math
import os
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contracts.schema import RoomScene  # noqa: E402

SCENE_PATH = ROOT / "contracts" / "mock_room" / "mock_scene.json"
OUT_DIR = ROOT / "services" / "reconstruction" / "fixtures" / "mock_room"

COLOURS = {
    "item_bed": [110, 140, 190, 255],
    "item_desk": [185, 145, 105, 255],
    "item_wardrobe": [130, 110, 95, 255],
}
FRONT_MARKER = [30, 30, 35, 255]
WALL_COLOUR = [225, 222, 215, 255]
FLOOR_COLOUR = [170, 160, 145, 255]
CEILING_COLOUR = [240, 240, 238, 255]
SLAB_M = 0.02


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


def cross2(a: np.ndarray, b: np.ndarray) -> float:
    return float(a[0] * b[1] - a[1] * b[0])


def convex_vertices(poly: np.ndarray) -> np.ndarray:
    """Per vertex: True when convex. With the contract winding (positive shoelace), convex is a
    positive turn."""
    return np.array(
        [
            cross2(poly[i] - poly[i - 1], poly[(i + 1) % len(poly)] - poly[i]) > 0
            for i in range(len(poly))
        ]
    )


def triangulate(poly: np.ndarray) -> np.ndarray:
    """Ear clipping for a simple polygon with positive shoelace winding (no extra dependency)."""
    idx, tris = list(range(len(poly))), []
    while len(idx) > 3:
        for k in range(len(idx)):
            a, b, c = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            if cross2(poly[b] - poly[a], poly[c] - poly[b]) < 0:
                continue  # reflex: not an ear
            others = (p for p in idx if p not in (a, b, c))
            if any(
                cross2(poly[b] - poly[a], poly[p] - poly[a]) >= 0
                and cross2(poly[c] - poly[b], poly[p] - poly[b]) >= 0
                and cross2(poly[a] - poly[c], poly[p] - poly[c]) >= 0
                for p in others
            ):
                continue  # another vertex inside: not an ear
            tris.append((a, b, c))
            idx.pop(k)
            break
        else:
            raise ValueError("floor_polygon is not a simple polygon")
    tris.append(tuple(idx))
    return np.array(tris)


def slab(poly: np.ndarray, y0: float, rgba) -> trimesh.Trimesh:
    """The floor polygon extruded from y0 to y0 + SLAB_M."""
    # extrude_triangulation extrudes the 2D (u, v) plane along +w. Feed (x, -z), then rotate -90
    # degrees about X, which maps (u, v, w) to (u, w, -v) = (x, height, z).
    mesh = trimesh.creation.extrude_triangulation(
        poly * [1, -1], triangulate(poly)[:, ::-1], SLAB_M
    )
    mesh.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]))
    mesh.apply_translation([0, y0, 0])
    trimesh.repair.fix_normals(mesh)
    mesh.visual.vertex_colors = rgba
    return mesh


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


def mm_key(p: np.ndarray) -> tuple[int, int]:
    """Vertex lookup key, so wall endpoints match polygon vertices despite float noise."""
    return round(p[0] * 1000), round(p[1] * 1000)


def wall_mesh(scene: dict, wall: dict, convex_at: dict) -> trimesh.Trimesh:
    start = np.array([wall["start"]["x"], wall["start"]["z"]])
    end = np.array([wall["end"]["x"], wall["end"]["z"]])
    length = float(np.linalg.norm(end - start))
    direction = (end - start) / length
    outward = np.array([direction[1], -direction[0]])  # contract winding: (dz, -dx)
    h, th = wall["height_m"], wall["thickness_m"]

    # Openings as (t0, t1, sill, head) along this wall.
    openings = []
    for win in scene["windows"]:
        if win["wall_id"] == wall["id"]:
            t0 = win["offset_along_wall_m"]
            openings.append((t0, t0 + win["width_m"], win["sill_height_m"], win["head_height_m"]))
    for door in scene["doors"]:
        if door["wall_id"] != wall["id"]:
            continue
        hinge = np.array([door["hinge_pos"]["x"], door["hinge_pos"]["z"]])
        swing_side = -outward if door["swings_into_room"] else outward
        # The closed leaf is wall-parallel; a 90-degree turn in the swing direction must point
        # it to the swing side. Clockwise is negative yaw, so closed = swing_side turned back.
        # Independent of swing_angle_deg, which is only how far the door opens.
        closed_dir = rotate_y(swing_side, 90 if door["swing_clockwise"] else -90)
        t_hinge = float(np.dot(hinge - start, direction))
        sign = 1 if np.dot(closed_dir, direction) > 0 else -1
        t_a, t_b = sorted([t_hinge, t_hinge + sign * door["width_m"]])
        openings.append((t_a, t_b, 0.0, door["head_height_m"]))
    openings.sort()

    # At a convex corner extend by the thickness to close the outer corner. At a reflex corner
    # the extension would poke into the room, and the neighbouring wall already covers it.
    cursor = -th if convex_at.get(mm_key(start), False) else 0.0
    stop = length + (th if convex_at.get(mm_key(end), False) else 0.0)
    parts = []
    for t0, t1, sill, head in openings:
        if t0 > cursor:
            parts.append(wall_piece(start, direction, outward, cursor, t0, 0, h, th))
        if sill > 0:
            parts.append(wall_piece(start, direction, outward, t0, t1, 0, sill, th))
        if head < h:
            parts.append(wall_piece(start, direction, outward, t0, t1, head, h, th))
        cursor = t1
    parts.append(wall_piece(start, direction, outward, cursor, stop, 0, h, th))
    return trimesh.util.concatenate(parts)


def shell_scene(scene: dict) -> trimesh.Scene:
    """Mock-only shell; real shells come from Dev 1. Takes a validated RoomScene dump. Assumes a
    flat ceiling at the walls' common height, and right-angle corners of equal wall thickness."""
    poly = np.array([[p["x"], p["z"]] for p in scene["floor_polygon"]])
    heights = {w["height_m"] for w in scene["walls"]}
    if len(heights) != 1:
        raise ValueError("Mock shell generator needs every wall to have the same height")
    convex_at = {mm_key(p): c for p, c in zip(poly, convex_vertices(poly))}

    shell = trimesh.Scene()
    shell.add_geometry(slab(poly, -SLAB_M, FLOOR_COLOUR), node_name="floor", geom_name="floor")
    shell.add_geometry(
        slab(poly, heights.pop(), CEILING_COLOUR), node_name="ceiling", geom_name="ceiling"
    )
    for wall in scene["walls"]:
        name = f"wall_{wall['id']}"
        shell.add_geometry(wall_mesh(scene, wall, convex_at), node_name=name, geom_name=name)
    return shell


def main() -> None:
    scene = RoomScene.model_validate_json(SCENE_PATH.read_text()).model_dump()
    os.makedirs(OUT_DIR, exist_ok=True)

    for item in scene["furniture"]:
        b = item["bbox_m"]
        rgba = COLOURS.get(item["id"], [160, 160, 160, 255])
        mesh = furniture_mesh(b["width"], b["height"], b["depth"], rgba)
        mesh.export(OUT_DIR / Path(item["glb_url"]).name)

    shell_scene(scene).export(OUT_DIR / Path(scene["shell_glb_url"]).name)
    print(f"Exported mock .glb files to {OUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
