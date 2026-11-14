"""Check the spatial engine against the shared demo home.

Free (no network): audit every demo room and print timings.
    uv run --extra spatial --extra reconstruction python scripts/check_layout_demo.py

Paid (calls Claude with ANTHROPIC_API_KEY from .env, a few cents per request):
    uv run --extra spatial --extra reconstruction python scripts/check_layout_demo.py \
        --solve g-bed2 "Give me more walking space"

Prints timings, token counts and results only; never the key or raw model payloads.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shapely.geometry import Point, Polygon  # noqa: E402

from contracts.schema import OptimiseRequest, RoomScene  # noqa: E402
from services.reconstruction.demo_assets import FIXTURE_ROOT, demo_rooms  # noqa: E402
from services.spatial_engine.agent import ProviderError, propose_layout  # noqa: E402
from services.spatial_engine.main import get_interpreter_model, get_layout_model  # noqa: E402
from services.spatial_engine.report import audit_scene  # noqa: E402

FLOORS = {"g": "ground", "f": "first", "s": "second"}


def demo_room_scenes() -> dict[str, RoomScene]:
    """Each demo room with the furniture standing in it, as the editor builds them."""
    furniture = {
        prefix: RoomScene.model_validate_json(
            (FIXTURE_ROOT / f"three_floor_{floor}_scene.json").read_text(encoding="utf-8")
        ).furniture
        for prefix, floor in FLOORS.items()
    }
    scenes = {}
    for room_id, room in demo_rooms().items():
        outline = Polygon([(p.x, p.z) for p in room.floor_polygon])
        inside = [i for i in furniture[room_id[0]] if outline.contains(Point(i.pose.x, i.pose.z))]
        scenes[room_id] = room.model_copy(update={"furniture": inside})
    return scenes


def profile(scenes: dict[str, RoomScene]) -> None:
    times = []
    for room_id, scene in scenes.items():
        start = time.perf_counter()
        report = audit_scene(scene)
        times.append((time.perf_counter() - start) * 1000)
        movable = sum(not item.is_fixed for item in scene.furniture)
        walk = report.walkable_floor_ratio
        print(
            f"{room_id:12} items={len(scene.furniture):2} movable={movable:2} "
            f"collisions={len(report.collisions)} outside={len(report.out_of_bounds_item_ids)} "
            f"blocked_doors={len({b.door_id for b in report.blocked_doors})} "
            f"access_issues={len(report.clearance_issues)} "
            f"reachable={'unknown' if walk is None else f'{walk:.0%}'} {times[-1]:.1f} ms"
        )
    times.sort()
    print(
        f"{len(times)} rooms audited: median {times[len(times) // 2]:.1f} ms, "
        f"max {times[-1]:.1f} ms"
    )


class Timed:
    def __init__(self, inner: Any, label: str) -> None:
        self.inner, self.label = inner, label

    def complete(self, **request: Any) -> Any:
        start = time.perf_counter()
        try:
            reply = self.inner.complete(**request)
        except ProviderError as exc:
            print(f"  {self.label}: failed ({exc.kind}) after {time.perf_counter() - start:.1f} s")
            raise
        tools = [call.name for call in reply.tool_calls]
        print(
            f"  {self.label}: {time.perf_counter() - start:.1f} s, {reply.tokens} tokens, "
            f"stop={reply.stop_reason}, tools={tools}"
        )
        return reply


def solve(scene: RoomScene, instruction: str) -> None:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        name, sep, value = line.strip().partition("=")
        if sep and name.startswith(("ANTHROPIC_", "SPACESHIFT_")) and value.strip():
            os.environ.setdefault(name, value.strip().strip("\"'"))
    model, reader = get_layout_model(), get_interpreter_model()
    if model is None or reader is None:
        sys.exit("ANTHROPIC_API_KEY is not set in .env")
    before = audit_scene(scene)
    start = time.perf_counter()
    proposal = propose_layout(
        OptimiseRequest(scene=scene, instruction=instruction),
        Timed(model, "layout"),
        interpreter=Timed(reader, "reading"),
    )
    names = {item.id: item.name for item in scene.furniture}
    print(f"total {time.perf_counter() - start:.1f} s")
    print(f"improved={proposal.improved} outcome={proposal.outcome} goal={proposal.goal}")
    for item_id, pose in proposal.poses.items():
        print(f"  move {names[item_id]}: x={pose.x:.2f} z={pose.z:.2f} yaw={pose.yaw_deg:.0f}")
    for label, report in (("before", before), ("after", proposal.report)):
        print(
            f"  {label}: collisions={len(report.collisions)} "
            f"blocked_doors={len({b.door_id for b in report.blocked_doors})} "
            f"access_issues={len(report.clearance_issues)} "
            f"reachable={report.walkable_floor_ratio}"
        )
    print("explanation:", proposal.explanation)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--solve", nargs=2, metavar=("ROOM_ID", "INSTRUCTION"))
    arguments = parser.parse_args()
    rooms = demo_room_scenes()
    if arguments.solve is None:
        profile(rooms)
    elif arguments.solve[0] not in rooms:
        sys.exit(f"Unknown room. Choose from: {', '.join(rooms)}")
    else:
        print(json.dumps(arguments.solve))
        solve(rooms[arguments.solve[0]], arguments.solve[1])
