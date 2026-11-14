"""Debug CLI: parse floor-plan images and write the JSON plus an overlay per floor.

    uv run python -m services.reconstruction.room examples/one_floor.jpg --out /tmp/plan \
        --annotations services/reconstruction/room/fixtures/one_floor.annotations.json

Without --annotations it calls fal.ai when FAL_KEY is set, otherwise runs unlabelled.

`python -m services.reconstruction.room align ...` places furniture in a room instead; see
`align_debug.py`.
"""

from __future__ import annotations

import argparse
import math
import mimetypes
import sys
from pathlib import Path

import cv2
import numpy as np

from contracts.schema import ParsedFloor

from .annotate import FalVisionAnnotator, FixedAnnotator, PlanAnnotations, PlanAnnotator
from .parse import parse_floor_plan


def render_floor(floor: ParsedFloor, px_per_m: float = 80.0) -> np.ndarray:
    """Draw the contract geometry exactly as returned (metres), not the source image: this is
    what the editor will build from."""
    pts = [(p.x, p.z) for r in floor.rooms for p in r.scene.floor_polygon]
    if not pts:
        return np.full((100, 100, 3), 255, np.uint8)
    max_x = max(x for x, _ in pts) + 1.0
    max_z = max(z for _, z in pts) + 1.0
    pad = 0.5
    img = np.full((int((max_z + pad) * px_per_m), int((max_x + pad) * px_per_m), 3), 255, np.uint8)

    def px(x: float, z: float) -> tuple[int, int]:
        return int((x + pad) * px_per_m), int((z + pad) * px_per_m)

    rng = np.random.default_rng(7)
    for room in floor.rooms:
        sc = room.scene
        poly = np.array([px(p.x, p.z) for p in sc.floor_polygon], np.int32)
        colour = tuple(int(c) for c in rng.integers(170, 245, 3))
        cv2.fillPoly(img, [poly], colour)
    for room in floor.rooms:
        sc = room.scene
        walls = {w.id: w for w in sc.walls}
        for w in sc.walls:
            t = max(1, int(w.thickness_m * px_per_m))
            dx, dz = w.end.x - w.start.x, w.end.z - w.start.z
            ln = math.hypot(dx, dz) or 1.0
            ox, oz = dz / ln * w.thickness_m / 2, -dx / ln * w.thickness_m / 2
            cv2.line(
                img,
                px(w.start.x + ox, w.start.z + oz),
                px(w.end.x + ox, w.end.z + oz),
                (40, 40, 40),
                t,
            )
        for win in sc.windows:
            w = walls[win.wall_id]
            dx, dz = w.end.x - w.start.x, w.end.z - w.start.z
            ln = math.hypot(dx, dz)
            ux, uz = dx / ln, dz / ln
            a = (w.start.x + ux * win.offset_along_wall_m, w.start.z + uz * win.offset_along_wall_m)
            b = (a[0] + ux * win.width_m, a[1] + uz * win.width_m)
            cv2.line(img, px(*a), px(*b), (230, 160, 30), 5)
        for d in sc.doors:
            w = walls[d.wall_id]
            dx, dz = w.end.x - w.start.x, w.end.z - w.start.z
            ln = math.hypot(dx, dz)
            ux, uz = dx / ln, dz / ln
            inward = (-uz, ux)
            side = inward if d.swings_into_room else (-inward[0], -inward[1])
            # Closed leaf: rotating it 90 deg in the swing direction must point to `side`.
            for sgn in (1.0, -1.0):
                cx, cz = ux * sgn, uz * sgn
                cw = (-cz, cx)
                if (cw[0] * side[0] + cw[1] * side[1] > 0) == d.swing_clockwise:
                    break
            h = (d.hinge_pos.x, d.hinge_pos.z)
            closed = (h[0] + cx * d.width_m, h[1] + cz * d.width_m)
            opened = (h[0] + side[0] * d.width_m, h[1] + side[1] * d.width_m)
            cv2.line(img, px(*h), px(*closed), (40, 40, 220), 4)
            cv2.line(img, px(*h), px(*opened), (40, 40, 220), 2)
            cv2.circle(img, px(*h), 4, (0, 0, 160), -1)
        cx_ = sum(p.x for p in sc.floor_polygon) / len(sc.floor_polygon)
        cz_ = sum(p.z for p in sc.floor_polygon) / len(sc.floor_polygon)
        text = f"{room.name} {room.area_m2:.1f}m2"
        cv2.putText(img, text, px(cx_ - 0.8, cz_), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
    return img


def render_shell_section(floor: ParsedFloor, y: float = 1.0, px_per_m: float = 80.0) -> np.ndarray:
    """Cut every room's shell horizontally at height y and draw the cut, like an architectural
    plan: walls show as outlines, and door and window openings show as gaps."""
    import trimesh

    from .shell import build_shell

    pts = [(p.x, p.z) for r in floor.rooms for p in r.scene.floor_polygon]
    if not pts:
        return np.full((100, 100, 3), 255, np.uint8)
    pad = 0.5
    w = int((max(x for x, _ in pts) + 2 * pad + 0.5) * px_per_m)
    h = int((max(z for _, z in pts) + 2 * pad + 0.5) * px_per_m)
    img = np.full((h, w, 3), 255, np.uint8)

    def px(x: float, z: float) -> tuple[int, int]:
        return int((x + pad) * px_per_m), int((z + pad) * px_per_m)

    for room in floor.rooms:
        poly = np.array([px(p.x, p.z) for p in room.scene.floor_polygon], np.int32)
        cv2.fillPoly(img, [poly], (235, 235, 225))
        shell = build_shell(room.scene)
        for node in shell.graph.nodes_geometry:
            if not node.startswith("wall_"):
                continue
            mesh = shell.geometry[shell.graph[node][1]]
            lines = trimesh.intersections.mesh_plane(  # type: ignore[no-untyped-call]
                mesh, [0, 1, 0], [0, y, 0]
            )
            for a, b in lines:
                cv2.line(img, px(a[0], a[2]), px(b[0], b[2]), (30, 30, 30), 2)
    return img


def main() -> None:
    ap = argparse.ArgumentParser(prog="python -m services.reconstruction.room")
    ap.add_argument("images", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument(
        "--annotations",
        type=Path,
        nargs="*",
        default=None,
        help="recorded PlanAnnotations JSON, one per image",
    )
    ap.add_argument(
        "--shells",
        action="store_true",
        help="also write each room's shell .glb and a per-floor section of the shells at 1 m",
    )
    args = ap.parse_args()

    annotator: PlanAnnotator
    if args.annotations:
        anns = [PlanAnnotations.model_validate_json(p.read_text()) for p in args.annotations]
        annotator = FixedAnnotator(anns)
    else:
        annotator = FalVisionAnnotator()

    images = []
    for p in args.images:
        ctype = mimetypes.guess_type(p.name)[0] or "image/png"
        images.append((p.read_bytes(), ctype))
    plan = parse_floor_plan(images, annotator)

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "plan.json").write_text(plan.model_dump_json(indent=2))
    for floor in plan.floors:
        print(
            f"{floor.floor_id} level={floor.level} '{floor.name}' "
            f"(image {floor.source_image_index})"
        )
        for room in floor.rooms:
            sc = room.scene
            label = (
                f" label {room.labelled_width_m} x {room.labelled_depth_m}"
                if room.labelled_width_m
                else ""
            )
            print(
                f"  {room.room_id:<18} {room.name:<22} {room.area_m2:6.2f} m2  "
                f"walls={len(sc.walls):<2} doors={len(sc.doors)} windows={len(sc.windows)} "
                f"{room.dimension_source}{label} {room.correction_needed}"
            )
        out_png = args.out / f"{floor.floor_id}.png"
        out_png.write_bytes(cv2.imencode(".png", render_floor(floor))[1].tobytes())
        if args.shells:
            from .shell import shell_glb

            for room in floor.rooms:
                (args.out / f"{room.room_id}.glb").write_bytes(shell_glb(room.scene))
            section = render_shell_section(floor)
            out_sec = args.out / f"{floor.floor_id}-shell-section.png"
            out_sec.write_bytes(cv2.imencode(".png", section)[1].tobytes())
    for w in plan.warnings:
        print("warning:", w)


if __name__ == "__main__":
    if sys.argv[1:2] == ["align"]:
        from .align_debug import main as align_main

        raise SystemExit(align_main(sys.argv[2:]))
    main()
