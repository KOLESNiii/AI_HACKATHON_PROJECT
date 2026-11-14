"""RoomScene → room shell `.glb` (contracts/schema.py module doc; spec §7.2).

- Room coordinates with identity transforms; the floor's top surface is at Y=0.
- Nodes `floor`, `ceiling` and `wall_<wall_id>`, with door and window openings cut.
- Each wall stands on its interior face line and extends `thickness_m` along its outward normal
  (dz, -dx). Corners are mitred: a wall's outer end is where its outer face meets the
  neighbouring wall's outer face, so convex and reflex corners, 45° bays and walls of
  different thickness all close without poking into the room.

The shell is derived and never authoritative: the JSON geometry wins, and the audit never
reads it. Every piece is a vertical prism over a 2D polygon, extruded without shapely.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import trimesh
from numpy.typing import NDArray

from contracts.schema import RoomScene, WallSegment

Vec = NDArray[np.float64]

SLAB_M = 0.02
"""Floor and ceiling slab thickness. The floor slab sits below Y=0."""
COLLINEAR_DEG = 5.0
"""Neighbouring walls closer to straight than this get a square end instead of a miter."""
MITER_LIMIT = 2.0
"""A miter reaching further than this many wall thicknesses from the corner is squared off
(90° corners need 1.41, 45° bays 1.08; only sharp angles exceed it)."""
MIN_PIECE_M = 0.001

WALL_COLOUR = [225, 222, 215, 255]
FLOOR_COLOUR = [170, 160, 145, 255]
CEILING_COLOUR = [240, 240, 238, 255]


def _cross(a: Vec, b: Vec) -> float:
    return float(a[0] * b[1] - a[1] * b[0])


def _shoelace(poly: Vec) -> float:
    x, z = poly[:, 0], poly[:, 1]
    return float(np.sum(np.roll(x, 1) * z - x * np.roll(z, 1)))


def triangulate(poly: Vec) -> NDArray[np.int64]:
    """Ear clipping for a simple polygon with positive shoelace winding (contract winding)."""
    idx = list(range(len(poly)))
    tris: list[tuple[int, int, int]] = []
    while len(idx) > 3:
        for k in range(len(idx)):
            a, b, c = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            if _cross(poly[b] - poly[a], poly[c] - poly[b]) <= 0:
                continue  # reflex or degenerate: not an ear
            others = (p for p in idx if p not in (a, b, c))
            if any(
                _cross(poly[b] - poly[a], poly[p] - poly[a]) >= 0
                and _cross(poly[c] - poly[b], poly[p] - poly[b]) >= 0
                and _cross(poly[a] - poly[c], poly[p] - poly[c]) >= 0
                for p in others
            ):
                continue  # another vertex inside: not an ear
            tris.append((a, b, c))
            idx.pop(k)
            break
        else:
            raise ValueError("polygon is not simple")
    tris.append((idx[0], idx[1], idx[2]))
    return np.array(tris, dtype=np.int64)


def prism(poly: Vec, y0: float, y1: float, rgba: list[int]) -> trimesh.Trimesh:
    """A 2D (x, z) polygon extruded vertically from y0 to y1."""
    poly = np.asarray(poly, dtype=np.float64)
    if _shoelace(poly) < 0:
        poly = poly[::-1]
    # extrude_triangulation extrudes the (u, v) plane along +w. Feed (x, -z), then rotate -90°
    # about X, which maps (u, v, w) to (u, w, -v) = (x, height, z).
    mesh = trimesh.creation.extrude_triangulation(
        poly * [1.0, -1.0], triangulate(poly)[:, ::-1], y1 - y0
    )
    # The x-axis rotation is written out (trimesh's helpers are untyped).
    mesh.apply_transform(
        np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], dtype=np.float64)
    )
    mesh.apply_translation([0.0, y0, 0.0])
    # Orient outward without fix_normals(), which needs SciPy (not in the reconstruction extra).
    if mesh.volume < 0:
        mesh.invert()
    mesh.visual = trimesh.visual.ColorVisuals(mesh, vertex_colors=rgba)
    return mesh


# --- walls ------------------------------------------------------------------------------------


@dataclass(frozen=True)
class WallFrame:
    wall: WallSegment
    start: Vec
    end: Vec
    length: float
    d: Vec
    """Unit direction start -> end."""
    out: Vec
    """Unit outward normal (dz, -dx)."""

    @staticmethod
    def of(wall: WallSegment) -> WallFrame:
        s = np.array([wall.start.x, wall.start.z], dtype=np.float64)
        e = np.array([wall.end.x, wall.end.z], dtype=np.float64)
        length = float(np.linalg.norm(e - s))
        if length == 0:
            raise ValueError(f"wall {wall.id} has zero length")
        d = (e - s) / length
        return WallFrame(wall, s, e, length, d, np.array([d[1], -d[0]]))

    @property
    def thickness(self) -> float:
        return self.wall.thickness_m

    def inner(self, t: float) -> Vec:
        return self.start + self.d * t

    def outer(self, t: float) -> Vec:
        return self.start + self.d * t + self.out * self.thickness


def _key(p: Vec) -> tuple[int, int]:
    return round(float(p[0]) * 1000), round(float(p[1]) * 1000)


def _miter(here: WallFrame, other: WallFrame, corner: Vec, at_start: bool) -> Vec:
    """Outer corner point shared with `other` at `corner`, or a square end when the walls are
    nearly collinear or the miter would be too long."""
    square = here.outer(0.0 if at_start else here.length)
    if abs(_cross(here.d, other.d)) < math.sin(math.radians(COLLINEAR_DEG)):
        return square
    p, r = here.outer(0.0), here.d
    q, s = other.outer(0.0), other.d
    t = _cross(q - p, s) / _cross(r, s)
    hit = p + r * t
    if float(np.linalg.norm(hit - corner)) > MITER_LIMIT * max(here.thickness, other.thickness):
        return square
    return hit


@dataclass(frozen=True)
class Opening:
    t0: float
    t1: float
    sill: float
    head: float


def _door_span(
    frame: WallFrame, hinge: Vec, width: float, clockwise: bool, into: bool
) -> tuple[float, float]:
    """The closed leaf lies along the wall from the hinge; rotating it 90° in the swing
    direction must point it to the swing side (DoorOpening docstring)."""
    side = -frame.out if into else frame.out
    # Clockwise viewed from above maps c to (-cz, cx); invert that for the closed direction.
    closed = np.array([side[1], -side[0]]) if clockwise else np.array([-side[1], side[0]])
    t_hinge = float(np.dot(hinge - frame.start, frame.d))
    sign = 1.0 if float(np.dot(closed, frame.d)) > 0 else -1.0
    a, b = sorted((t_hinge, t_hinge + sign * width))
    return a, b


def _openings(scene: RoomScene, frame: WallFrame) -> list[Opening]:
    """The wall's openings clipped to the wall, each with its own sill and head."""
    wall_id = frame.wall.id
    raw: list[Opening] = []
    for win in scene.windows:
        if win.wall_id == wall_id:
            t0 = win.offset_along_wall_m
            raw.append(Opening(t0, t0 + win.width_m, win.sill_height_m, win.head_height_m))
    for door in scene.doors:
        if door.wall_id == wall_id:
            hinge = np.array([door.hinge_pos.x, door.hinge_pos.z])
            a, b = _door_span(
                frame, hinge, door.width_m, door.swing_clockwise, door.swings_into_room
            )
            raw.append(Opening(a, b, 0.0, door.head_height_m))
    h = frame.wall.height_m
    clipped = [
        Opening(max(0.0, o.t0), min(frame.length, o.t1), max(0.0, o.sill), min(h, o.head))
        for o in raw
    ]
    return [o for o in clipped if o.t1 - o.t0 > MIN_PIECE_M and o.head - o.sill > MIN_PIECE_M]


def _solid_ranges(openings: list[Opening], h: float) -> tuple[tuple[float, float], ...]:
    """[0, h] minus the union of the openings' [sill, head] ranges."""
    gaps = sorted((o.sill, o.head) for o in openings)
    out: list[tuple[float, float]] = []
    y = 0.0
    for lo, hi in gaps:
        if lo > y + MIN_PIECE_M:
            out.append((y, lo))
        y = max(y, hi)
    if h > y + MIN_PIECE_M:
        out.append((y, h))
    return tuple(out)


@dataclass(frozen=True)
class Section:
    """One wall piece: a vertical prism over `poly` (x, z) from y0 to y1."""

    poly: Vec
    y0: float
    y1: float


def _clip(poly: Vec, frame: WallFrame, ta: float, tb: float) -> Vec:
    """Sutherland-Hodgman: keep the part of a convex polygon with ta <= t <= tb, where t is the
    distance along the wall."""
    pts = [np.asarray(p, dtype=np.float64) for p in poly]
    for bound, keep_above in ((ta, True), (tb, False)):
        out: list[Vec] = []
        n = len(pts)
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            tp = float(np.dot(p - frame.start, frame.d))
            tq = float(np.dot(q - frame.start, frame.d))
            p_in = tp >= bound if keep_above else tp <= bound
            q_in = tq >= bound if keep_above else tq <= bound
            if p_in:
                out.append(p)
            if p_in != q_in:
                out.append(p + (q - p) * ((bound - tp) / (tq - tp)))
        pts = out
        if len(pts) < 3:
            return np.zeros((0, 2))
    return np.array(pts)


def _is_simple_quad(q: Vec) -> bool:
    signs = [_cross(q[(i + 1) % 4] - q[i], q[(i + 2) % 4] - q[(i + 1) % 4]) for i in range(4)]
    return all(c > 0 for c in signs) or all(c < 0 for c in signs)


def wall_footprint(frame: WallFrame, outer_start: Vec, outer_end: Vec) -> Vec:
    """The whole wall in plan: interior face plus mitred outer face. Inner and outer edges are
    parallel, so a simple footprint is convex. When the miters cross (a wall shorter than its
    miter offsets), the ends are squared instead."""
    quad = np.array([frame.inner(0.0), frame.inner(frame.length), outer_end, outer_start])
    if _is_simple_quad(quad):
        return quad
    return np.array(
        [frame.inner(0.0), frame.inner(frame.length), frame.outer(frame.length), frame.outer(0.0)]
    )


def wall_sections(
    scene: RoomScene, frame: WallFrame, outer_start: Vec, outer_end: Vec
) -> list[Section]:
    """Solid pieces of one wall. The wall is split at every opening boundary; each interval
    keeps everything outside the union of the openings covering it, so neighbouring openings
    with different sills or heads keep their own heights. Each piece's footprint is the
    wall's footprint clipped to its interval, so it is always a valid convex polygon."""
    h = frame.wall.height_m
    openings = _openings(scene, frame)
    cuts = sorted({0.0, frame.length, *(o.t0 for o in openings), *(o.t1 for o in openings)})
    # (ta, tb, solid ranges) per interval, merging neighbours with identical ranges.
    spans: list[tuple[float, float, tuple[tuple[float, float], ...]]] = []
    for ta, tb in zip(cuts, cuts[1:]):
        if tb - ta <= MIN_PIECE_M:
            continue
        mid = (ta + tb) / 2
        solid = _solid_ranges([o for o in openings if o.t0 <= mid <= o.t1], h)
        if spans and spans[-1][2] == solid and abs(spans[-1][1] - ta) <= MIN_PIECE_M:
            spans[-1] = (spans[-1][0], tb, solid)
        else:
            spans.append((ta, tb, solid))
    footprint = wall_footprint(frame, outer_start, outer_end)
    # The end intervals include the miter, which can reach past t = 0 or t = length.
    reach = 2 * MITER_LIMIT * frame.thickness
    out: list[Section] = []
    for i, (ta, tb, solid) in enumerate(spans):
        lo = -reach if i == 0 and ta <= MIN_PIECE_M else ta
        hi = (
            frame.length + reach if i == len(spans) - 1 and tb >= frame.length - MIN_PIECE_M else tb
        )
        poly = _clip(footprint, frame, lo, hi)
        if len(poly) < 3 or abs(_shoelace(poly)) / 2 < 1e-8:
            continue
        out.extend(Section(poly, y0, y1) for y0, y1 in solid)
    return out


def wall_mesh(
    scene: RoomScene, frame: WallFrame, outer_start: Vec, outer_end: Vec
) -> trimesh.Trimesh:
    parts = [
        prism(sec.poly, sec.y0, sec.y1, WALL_COLOUR)
        for sec in wall_sections(scene, frame, outer_start, outer_end)
    ]
    if not parts:
        raise ValueError(f"wall {frame.wall.id} is entirely open")
    merged: trimesh.Trimesh = trimesh.util.concatenate(parts)
    return merged


def wall_ends(scene: RoomScene) -> list[tuple[WallFrame, Vec, Vec]]:
    """Each wall with its mitred outer start and end points."""
    frames = [WallFrame.of(w) for w in scene.walls]
    by_start = {_key(f.start): f for f in frames}
    by_end = {_key(f.end): f for f in frames}
    out = []
    for f in frames:
        prev = by_end.get(_key(f.start))
        nxt = by_start.get(_key(f.end))
        o_start = _miter(f, prev, f.start, True) if prev and prev is not f else f.outer(0.0)
        o_end = _miter(f, nxt, f.end, False) if nxt and nxt is not f else f.outer(f.length)
        out.append((f, o_start, o_end))
    return out


# --- shell ------------------------------------------------------------------------------------


def build_shell(scene: RoomScene) -> trimesh.Scene:
    """The room shell as a trimesh Scene with nodes `floor`, `ceiling`, `wall_<id>`."""
    poly = np.array([[p.x, p.z] for p in scene.floor_polygon], dtype=np.float64)
    if _shoelace(poly) <= 0:
        raise ValueError("floor_polygon must use the contract winding")
    height = max((w.height_m for w in scene.walls), default=2.6)

    shell = trimesh.Scene()
    shell.add_geometry(
        prism(poly, -SLAB_M, 0.0, FLOOR_COLOUR), node_name="floor", geom_name="floor"
    )
    shell.add_geometry(
        prism(poly, height, height + SLAB_M, CEILING_COLOUR),
        node_name="ceiling",
        geom_name="ceiling",
    )
    for f, o_start, o_end in wall_ends(scene):
        name = f"wall_{f.wall.id}"
        shell.add_geometry(wall_mesh(scene, f, o_start, o_end), node_name=name, geom_name=name)
    return shell


def shell_glb(scene: RoomScene) -> bytes:
    data = build_shell(scene).export(file_type="glb")  # type: ignore[no-untyped-call]
    assert isinstance(data, bytes)
    return data
