"""Floor-plan images → `ParsedFloorPlan`: every floor and room as contract geometry.

Pipeline per image (see the module docs of each step):

1. `raster`: masks at a fixed working resolution.
2. `annotate`: room labels with printed metric dimensions, floor captions, compass.
3. `regions`: close door/window gaps, then rooms = enclosed free space, floors = wall masses.
4. Scale: each labelled room's printed dimensions against its region's size. The floor's scale
   is the median over rooms whose two dimensions agree. A first segmentation pass runs without
   scale; a second re-runs gap detection with metric door/window limits.
5. Small or narrow unlabelled regions (stair treads, wardrobes, shower enclosures) are merged
   into the neighbour they share the most wall with.
6. `polygon` and `openings`: contract walls, doors and windows, in the floor's metric frame.
"""

from __future__ import annotations

import hashlib
import math
import statistics
from dataclasses import dataclass, field

import cv2
import numpy as np

from contracts.schema import (
    DoorOpening,
    ParsedFloor,
    ParsedFloorPlan,
    ParsedRoom,
    RoomScene,
    Vec2,
    WallSegment,
    WindowOpening,
)

from . import openings as op
from .annotate import FloorCaption, PlanAnnotations, PlanAnnotator, RoomLabel
from .polygon import area, region_polygon
from .raster import Raster, rasterise
from .regions import Bridge, Segmentation, segment

Point = tuple[float, float]

SCALE_AGREEMENT = 0.10
"""A label's two dimensions must imply px/m within this fraction of each other to count."""
LABEL_MISMATCH_WARN = 0.10
SLIVER_SHORT_SIDE_M = 0.6
SLIVER_AREA_M2 = 0.8
MIN_ROOM_AREA_M2 = 0.5
ESTIMATED_DOOR_M = 0.8
ESTIMATED_WALL_M = 0.2
DEFAULT_WALL_HEIGHT_M = 2.6
SHELL_URL = "/api/reconstruction/shells/{scene_id}.glb"
"""Served by the shell generator (next step). Until then the editor's missing-asset path
draws the room from `floor_polygon`/`walls`."""


@dataclass
class Region:
    rid: int
    floor: int
    labels: list[RoomLabel] = field(default_factory=list)

    @property
    def label(self) -> RoomLabel | None:
        return self.labels[0] if len(self.labels) == 1 else None


@dataclass
class FloorScale:
    px_per_m: float
    measured: bool


# --- labels and scale -------------------------------------------------------------------------


def _label_px(label: RoomLabel | FloorCaption, raster: Raster) -> tuple[int, int]:
    h, w = raster.shape
    return min(w - 1, int(label.x * w)), min(h - 1, int(label.y * h))


def _assign_labels(seg: Segmentation, raster: Raster, labels: list[RoomLabel]) -> dict[int, Region]:
    regions = {rid: Region(rid=rid, floor=seg.room_floor[rid]) for rid in seg.room_ids}
    radius = int(2 * raster.wall_px)
    h, w = raster.shape
    for lab in labels:
        x, y = _label_px(lab, raster)
        rid = int(seg.room_labels[y, x])
        if rid not in regions:
            # The label point may sit on a stray stroke; look nearby.
            win = seg.room_labels[max(0, y - radius) : y + radius, max(0, x - radius) : x + radius]
            ids, counts = np.unique(win, return_counts=True)
            ranked = [(c, int(i)) for i, c in zip(ids, counts) if int(i) in regions]
            if not ranked:
                continue
            rid = max(ranked)[1]
        regions[rid].labels.append(lab)
    return regions


def _region_mask(seg: Segmentation, rid: int) -> np.ndarray:
    return np.asarray(seg.room_labels == rid)


def _rect_sides_px(mask: np.ndarray) -> tuple[float, float]:
    pts = cv2.findNonZero(mask.astype(np.uint8))
    (_, _), (a, b), _ = cv2.minAreaRect(pts)
    return max(a, b), min(a, b)


def _room_scale(mask: np.ndarray, label: RoomLabel) -> float | None:
    if label.width_m is None or label.depth_m is None:
        return None
    long_px, short_px = _rect_sides_px(mask)
    long_m, short_m = max(label.width_m, label.depth_m), min(label.width_m, label.depth_m)
    s1, s2 = long_px / long_m, short_px / short_m
    if abs(s1 - s2) / ((s1 + s2) / 2) > SCALE_AGREEMENT:
        return None
    return (s1 + s2) / 2


@dataclass
class ScaleEvidence:
    px_per_m: float
    consistent: bool
    """False when the labelled rooms on the floor imply incompatible scales."""
    rooms: int


def _consensus(candidates: list[float]) -> ScaleEvidence:
    """The scale a strict majority of labelled rooms agree on (each within SCALE_AGREEMENT of
    the cluster's centre). Without a majority the labels contradict each other: their median
    satisfies none of them, so it is returned only as an untrusted estimate."""
    best: list[float] = []
    for c in candidates:
        cluster = [x for x in candidates if abs(x - c) / c <= SCALE_AGREEMENT]
        if len(cluster) > len(best):
            best = cluster
    if len(best) * 2 > len(candidates):
        return ScaleEvidence(statistics.median(best), True, len(candidates))
    return ScaleEvidence(statistics.median(candidates), False, len(candidates))


def _floor_scales(
    seg: Segmentation, regions: dict[int, Region], raster: Raster
) -> dict[int, ScaleEvidence]:
    per_floor: dict[int, list[float]] = {}
    for reg in regions.values():
        if reg.label is None:
            continue
        s = _room_scale(_region_mask(seg, reg.rid), reg.label)
        if s is not None:
            per_floor.setdefault(reg.floor, []).append(s)
    return {f: _consensus(v) for f, v in per_floor.items()}


def _fallback_scale(seg: Segmentation, raster: Raster) -> float:
    """No usable labels: assume interior door gaps are ESTIMATED_DOOR_M wide, else that the
    main walls are ESTIMATED_WALL_M thick."""
    doors = [b.length for b in seg.bridges if b.glazing < 0.3]
    if len(doors) >= 2:
        return statistics.median(doors) / ESTIMATED_DOOR_M
    return raster.wall_px / ESTIMATED_WALL_M


# --- merging ----------------------------------------------------------------------------------


def _bridge_sides(seg: Segmentation, br: Bridge) -> tuple[int, int]:
    """Free-space labels just either side of a bridge."""
    dx, dy = br.b[0] - br.a[0], br.b[1] - br.a[1]
    n = math.hypot(dx, dy) or 1.0
    off = br.width_px / 2 + 3
    nx, ny = -dy / n * off, dx / n * off
    h, w = seg.room_labels.shape
    out = []
    for sgn in (1, -1):
        x = min(w - 1, max(0, int(round(br.mid[0] + sgn * nx))))
        y = min(h - 1, max(0, int(round(br.mid[1] + sgn * ny))))
        out.append(int(seg.room_labels[y, x]))
    return out[0], out[1]


def _merge_slivers(
    seg: Segmentation, regions: dict[int, Region], scales: dict[int, FloorScale], wall_px: float
) -> None:
    """Merge small or narrow unlabelled regions into a neighbour.

    A neighbour on the other side of a bridge comes first: a sliver sealed off by a bridge is
    usually an artefact (a partial wall's ray, e.g. a shower partition). Otherwise the
    neighbour with the most pixels within reach across the wall (~1.5 main walls) wins.
    """
    k = max(5, int(round(wall_px * 3.0)) | 1)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    changed = True
    while changed:
        changed = False
        via_bridge: dict[int, set[int]] = {}
        for br in seg.bridges:
            p, q = _bridge_sides(seg, br)
            if p != q:
                via_bridge.setdefault(p, set()).add(q)
                via_bridge.setdefault(q, set()).add(p)
        for rid, reg in sorted(regions.items()):
            if reg.labels:
                continue
            s = scales[reg.floor].px_per_m
            mask = _region_mask(seg, rid)
            _, short_px = _rect_sides_px(mask)
            area_m2 = float(mask.sum()) / (s * s)
            if short_px / s >= SLIVER_SHORT_SIDE_M and area_m2 >= SLIVER_AREA_M2:
                continue
            grown = cv2.dilate(mask.astype(np.uint8), kernel) > 0
            ids, counts = np.unique(seg.room_labels[grown], return_counts=True)
            cands = [
                (int(i) in via_bridge.get(rid, set()), int(c), int(i))
                for i, c in zip(ids, counts)
                if int(i) != rid and int(i) in regions and regions[int(i)].floor == reg.floor
            ]
            if not cands:
                if area_m2 < MIN_ROOM_AREA_M2:
                    del regions[rid]
                    changed = True
                    break
                continue
            target = max(cands)[2]
            other = cv2.dilate(_region_mask(seg, target).astype(np.uint8), kernel) > 0
            shared = grown & other & seg.enclosure
            seg.room_labels[mask | shared] = target
            del regions[rid]
            changed = True
            break


# --- floors -----------------------------------------------------------------------------------


@dataclass
class FloorInfo:
    label: int
    bbox: tuple[int, int, int, int]
    """x, y, w, h in working pixels."""
    caption: FloorCaption | None = None


def _caption_distance(cap_px: tuple[int, int], bbox: tuple[int, int, int, int]) -> float:
    x, y, w, h = bbox
    dx = max(x - cap_px[0], 0, cap_px[0] - (x + w))
    below = cap_px[1] - (y + h)
    above = y - cap_px[1]
    # Captions usually sit below their plan, so a caption above a plan counts double.
    dy = max(below, 0) + 2 * max(above, 0)
    return math.hypot(dx, dy)


def _match_captions(floors: list[FloorInfo], captions: list[FloorCaption], raster: Raster) -> None:
    pairs = sorted(
        (_caption_distance(_label_px(c, raster), f.bbox), fi, ci)
        for fi, f in enumerate(floors)
        for ci, c in enumerate(captions)
    )
    used_f: set[int] = set()
    used_c: set[int] = set()
    for _, fi, ci in pairs:
        if fi not in used_f and ci not in used_c:
            floors[fi].caption = captions[ci]
            used_f.add(fi)
            used_c.add(ci)


# --- contract geometry ------------------------------------------------------------------------


def _wall_thickness_px(enclosure: np.ndarray, s: Point, e: Point, wall_px: float) -> float:
    ex, ey = e[0] - s[0], e[1] - s[1]
    length = math.hypot(ex, ey)
    out = (ey / length, -ex / length)
    h, w = enclosure.shape
    runs = []
    for f in (0.2, 0.35, 0.5, 0.65, 0.8):
        px, py = s[0] + ex * f, s[1] + ey * f
        run = 0
        for t in range(1, int(3 * wall_px)):
            x, y = int(round(px + out[0] * t)), int(round(py + out[1] * t))
            if not (0 <= x < w and 0 <= y < h) or not enclosure[y, x]:
                break
            run += 1
        if run:
            runs.append(run)
    return float(statistics.median(runs)) if runs else wall_px


def _bearing(nx: float, nz: float) -> float:
    """Plan bearing (clockwise from -Z) of direction (nx, nz)."""
    return math.degrees(math.atan2(nx, -nz)) % 360.0


@dataclass
class RoomGeometry:
    rid: int
    poly_px: list[Point]


def _build_scene(
    scene_id: str,
    geom: RoomGeometry,
    floor_origin: Point,
    s: float,
    enclosure: np.ndarray,
    wall_px: float,
    room_openings: list[tuple[op.EdgeHit, Bridge, str, op.Leaf | None]],
    north: float | None,
) -> RoomScene:
    ox, oy = floor_origin

    def to_m(p: Point) -> Vec2:
        return Vec2(x=round((p[0] - ox) / s, 3), z=round((p[1] - oy) / s, 3))

    poly = geom.poly_px
    n = len(poly)
    walls = []
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        # Capped: an edge beside a chimney breast or a solid block would otherwise read as a
        # metre-thick wall.
        thick = min(_wall_thickness_px(enclosure, a, b, wall_px), 1.5 * wall_px) / s
        walls.append(
            WallSegment(
                id=f"w{i}",
                start=to_m(a),
                end=to_m(b),
                height_m=DEFAULT_WALL_HEIGHT_M,
                thickness_m=round(min(0.5, max(0.05, thick)), 3),
            )
        )

    windows: list[WindowOpening] = []
    doors: list[DoorOpening] = []
    for hit, bridge, kind, leaf in room_openings:
        a, b = poly[hit.edge], poly[(hit.edge + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        elen = math.hypot(ex, ey)
        ux, uy = ex / elen, ey / elen
        if kind == "window":
            bearing = _bearing(uy, -ux)
            windows.append(
                WindowOpening(
                    id=f"win{len(windows)}",
                    wall_id=f"w{hit.edge}",
                    offset_along_wall_m=round(hit.t0 / s, 3),
                    width_m=round((hit.t1 - hit.t0) / s, 3),
                    plan_normal_deg=round(bearing, 2),
                    compass_azimuth_deg=None
                    if north is None
                    else round((bearing - north) % 360, 2),
                )
            )
            continue
        assert leaf is not None
        th = (leaf.hinge[0] - a[0]) * ux + (leaf.hinge[1] - a[1]) * uy
        tf = (leaf.free_end[0] - a[0]) * ux + (leaf.free_end[1] - a[1]) * uy
        th, tf = min(max(th, 0.0), elen), min(max(tf, 0.0), elen)
        sign = 1.0 if tf >= th else -1.0
        cx, cy = ux * sign, uy * sign
        inward = (-uy, ux)
        into = leaf.side[0] * inward[0] + leaf.side[1] * inward[1] > 0
        clockwise = (-cy) * leaf.side[0] + cx * leaf.side[1] > 0
        doors.append(
            DoorOpening(
                id=f"door{len(doors)}",
                wall_id=f"w{hit.edge}",
                hinge_pos=to_m((a[0] + ux * th, a[1] + uy * th)),
                width_m=round(abs(tf - th) / s, 3),
                swing_clockwise=clockwise,
                swings_into_room=into,
            )
        )

    return RoomScene(
        scene_id=scene_id,
        shell_glb_url=SHELL_URL.format(scene_id=scene_id),
        floor_polygon=[to_m(p) for p in poly],
        walls=walls,
        windows=windows,
        doors=doors,
        furniture=[],
        north_compass_deg=north,
    )


# --- per image --------------------------------------------------------------------------------


@dataclass
class ImageFloor:
    image_index: int
    info: FloorInfo
    scale: FloorScale
    rooms: list[tuple[Region, RoomGeometry]]
    seg: Segmentation
    raster: Raster
    north: float | None
    openings: dict[int, list[tuple[op.EdgeHit, Bridge, str, op.Leaf | None]]]


def _parse_image(
    image_index: int, raster: Raster, ann: PlanAnnotations, warnings: list[str]
) -> list[ImageFloor]:
    seg = segment(raster)
    regions = _assign_labels(seg, raster, ann.rooms)
    first = _floor_scales(seg, regions, raster)
    if first:
        seg = segment(raster, statistics.median(e.px_per_m for e in first.values()))
        regions = _assign_labels(seg, raster, ann.rooms)
    evidence = _floor_scales(seg, regions, raster)
    trusted = {f: e.px_per_m for f, e in evidence.items() if e.consistent}

    floor_ids = sorted({r.floor for r in regions.values()})
    sheet = statistics.median(trusted.values()) if trusted else None
    scales: dict[int, FloorScale] = {}
    for f in floor_ids:
        ev = evidence.get(f)
        if ev is not None and ev.consistent:
            scales[f] = FloorScale(ev.px_per_m, True)
        elif ev is not None:
            # The labels contradict each other: never present a compromise as measured.
            scales[f] = FloorScale(sheet if sheet is not None else ev.px_per_m, False)
            warnings.append(
                f"image {image_index}: the {ev.rooms} labelled rooms on one floor imply "
                "conflicting scales; its dimensions are estimated and need correction"
            )
        elif sheet is not None:
            # Same sheet, same drawing scale: borrow the other floors' measurement.
            scales[f] = FloorScale(sheet, True)
        else:
            scales[f] = FloorScale(_fallback_scale(seg, raster), False)
    if not evidence:
        warnings.append(
            f"image {image_index}: no printed room dimensions could be matched; scale is estimated"
        )

    for reg in regions.values():
        if len(reg.labels) > 1:
            names = " / ".join(lab.name for lab in reg.labels)
            warnings.append(f"image {image_index}: one region holds several labels ({names})")

    _merge_slivers(seg, regions, scales, raster.wall_px)

    # Floors that hold at least one room, with their wall bounds.
    infos: dict[int, FloorInfo] = {}
    for f in sorted({r.floor for r in regions.values()}):
        ys, xs = np.nonzero((seg.floor_labels == f) & seg.enclosure)
        infos[f] = FloorInfo(
            label=f, bbox=(int(xs.min()), int(ys.min()), int(np.ptp(xs)), int(np.ptp(ys)))
        )
    _match_captions(list(infos.values()), ann.floors, raster)

    north = ann.compass.north_bearing_deg if ann.compass else None
    tol = raster.wall_px * 1.2 + 3

    geoms: dict[int, RoomGeometry] = {}
    for rid, reg in list(regions.items()):
        s = scales[reg.floor].px_per_m
        mask = _region_mask(seg, rid)
        poly = region_polygon(mask, raster.wall_px)
        if poly is None or area(poly) / (s * s) < MIN_ROOM_AREA_M2:
            if reg.labels:
                warnings.append(f"image {image_index}: could not trace room '{reg.labels[0].name}'")
            del regions[rid]
            continue
        geoms[rid] = RoomGeometry(rid=rid, poly_px=poly)

    room_openings: dict[int, list[tuple[op.EdgeHit, Bridge, str, op.Leaf | None]]] = {
        rid: [] for rid in geoms
    }
    for br in seg.bridges:
        hits = [(rid, h) for rid, g in geoms.items() if (h := op.attach(br, g.poly_px, tol))]
        if not hits:
            continue
        kind = op.kind(br, len(hits))
        leaf = op.door_leaf(raster.ink, raster.structure, br) if kind == "door" else None
        for rid, h in hits:
            room_openings[rid].append((h, br, kind, leaf))

    out = []
    for f, info in infos.items():
        rooms = [(regions[rid], geoms[rid]) for rid in geoms if regions[rid].floor == f]
        if rooms:
            out.append(
                ImageFloor(image_index, info, scales[f], rooms, seg, raster, north, room_openings)
            )
    return out


def plan_id_for(images: list[bytes]) -> str:
    h = hashlib.sha256()
    for data in images:
        h.update(hashlib.sha256(data).digest())
    return "plan-" + h.hexdigest()[:12]


def _floor_order(floors: list[ImageFloor]) -> list[ImageFloor]:
    def key(f: ImageFloor) -> tuple[int, int, int, int, int]:
        cap = f.info.caption
        lvl = cap.level if cap and cap.level is not None else None
        x, y, _, _ = f.info.bbox
        return (0 if lvl is not None else 1, lvl or 0, f.image_index, y // 200, x)

    return sorted(floors, key=key)


def _unique_names(names: list[str]) -> list[str]:
    totals: dict[str, int] = {}
    for n in names:
        totals[n] = totals.get(n, 0) + 1
    seen: dict[str, int] = {}
    out = []
    for n in names:
        if totals[n] > 1:
            seen[n] = seen.get(n, 0) + 1
            out.append(f"{n} {seen[n]}")
        else:
            out.append(n)
    return out


def parse_floor_plan(images: list[tuple[bytes, str]], annotator: PlanAnnotator) -> ParsedFloorPlan:
    """Parse 1..n floor-plan images (bytes, content type) into every floor and room."""
    plan_id = plan_id_for([data for data, _ in images])
    warnings: list[str] = []
    floors: list[ImageFloor] = []
    for i, (data, ctype) in enumerate(images):
        raster = rasterise(data)
        result = annotator.annotate(data, ctype)
        warnings += result.warnings
        floors += _parse_image(i, raster, result.annotations, warnings)

    parsed_floors: list[ParsedFloor] = []
    used_levels: set[int] = set()
    unlabelled = 0
    for n, fl in enumerate(_floor_order(floors)):
        cap = fl.info.caption
        level = (
            cap.level if cap and cap.level is not None and cap.level not in used_levels else None
        )
        if level is None:
            level = max(used_levels, default=-1) + 1
        used_levels.add(level)
        floor_id = f"floor-{n}"
        s = fl.scale.px_per_m
        ox, oy = float(fl.info.bbox[0]), float(fl.info.bbox[1])
        band = max(1.0, 3 * fl.raster.wall_px)
        ordered = sorted(
            fl.rooms,
            key=lambda rg: (
                round(statistics.mean(p[1] for p in rg[1].poly_px) / (band * 10)),
                statistics.mean(p[0] for p in rg[1].poly_px),
            ),
        )
        raw_names = []
        for reg, _ in ordered:
            if reg.labels:
                raw_names.append(" / ".join(lab.name for lab in reg.labels))
            else:
                unlabelled += 1
                raw_names.append(f"Unlabelled space {unlabelled}")
        names = _unique_names(raw_names)

        rooms: list[ParsedRoom] = []
        for k, ((reg, geom), name) in enumerate(zip(ordered, names)):
            room_id = f"{floor_id}-room-{k}"
            scene_id = f"{plan_id}-{room_id}"
            ops = fl.openings.get(geom.rid, [])
            try:
                scene = _build_scene(
                    scene_id, geom, (ox, oy), s, fl.seg.enclosure, fl.raster.wall_px, ops, fl.north
                )
            except ValueError as exc:
                warnings.append(f"{name}: geometry rejected by the contract ({exc})")
                continue
            # Rounding to the millimetre moves hinges off their walls; the audit needs them on.
            scene, door_warnings = op.conform_openings(scene)
            warnings += [f"{name}: {w}" for w in door_warnings]
            correction: list[str] = []
            if not fl.scale.measured:
                correction.append("dimensions")
            if door_warnings or any(leaf is not None and not leaf.found for _, _, _, leaf in ops):
                correction.append("openings")
            if fl.north is None:
                correction.append("orientation")
            lab = reg.label
            poly_m = [(p.x, p.z) for p in scene.floor_polygon]
            if lab and lab.width_m and lab.depth_m:
                long_px, short_px = _rect_sides_px(_region_mask(fl.seg, geom.rid))
                got = sorted((long_px / s, short_px / s), reverse=True)
                want = sorted((lab.width_m, lab.depth_m), reverse=True)
                err = max(abs(g - w) / w for g, w in zip(got, want))
                if err > LABEL_MISMATCH_WARN:
                    if "dimensions" not in correction:
                        correction.append("dimensions")
                    warnings.append(
                        f"{name}: traced {got[0]:.2f} x {got[1]:.2f} m but the plan prints "
                        f"{lab.width_m} x {lab.depth_m} m"
                    )
            rooms.append(
                ParsedRoom(
                    room_id=room_id,
                    name=name,
                    labelled_width_m=lab.width_m if lab else None,
                    labelled_depth_m=lab.depth_m if lab else None,
                    area_m2=round(area(poly_m), 2),
                    dimension_source="measured" if fl.scale.measured else "estimated",
                    correction_needed=correction,  # type: ignore[arg-type]
                    scene=scene,
                )
            )
        parsed_floors.append(
            ParsedFloor(
                floor_id=floor_id,
                name=cap.name if cap else f"Floor {n + 1}",
                level=level,
                source_image_index=fl.image_index,
                rooms=rooms,
            )
        )
    return ParsedFloorPlan(plan_id=plan_id, floors=parsed_floors, warnings=warnings)
