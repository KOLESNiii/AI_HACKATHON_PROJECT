"""Furniture alignment (Dev 1.4): plan geometry, hint and default placement, and the records."""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from pathlib import Path

import pytest

from contracts.schema import (
    BBoxM,
    DoorOpening,
    FurnitureItem,
    Pose2D,
    RoomScene,
    Vec2,
    WallSegment,
)
from services.reconstruction.assets.models import EvidenceFrame, FurnitureAsset
from services.reconstruction.demo_assets import (
    BROWSER_ROOT,
    demo_floors,
    demo_room_scene,
    demo_rooms,
)
from services.reconstruction.room import footprint as fp
from services.reconstruction.room.align import (
    AlignmentResult,
    align_assets,
    wall_relative,
)
from services.reconstruction.room.observe import (
    FixedObserver,
    FrameSource,
    NullObserver,
    PlacementHint,
    PlacementHints,
)

ROOT = Path(__file__).resolve().parents[1]
MOCKS = ROOT / "contracts/mock_room"
EVIDENCE = json.loads((ROOT / "services/reconstruction/assets/fixtures/evidence.json").read_text())
RECEPTION_HINTS = ROOT / "services/reconstruction/room/fixtures/reception.hints.json"
RECEPTION_ASSETS = ROOT / "services/reconstruction/room/fixtures/reception.assets.json"
NO_SOURCE = {"frames": [{"frame_index": 7, "timestamp_s": 0.25}], "primary_frame_index": 7}


def _scene(name: str) -> RoomScene:
    return RoomScene.model_validate_json((MOCKS / f"{name}_scene.json").read_text())


def _asset(item: FurnitureItem) -> FurnitureAsset:
    evidence = EVIDENCE.get(item.id, NO_SOURCE)
    return FurnitureAsset.model_validate(
        {**item.model_dump(exclude={"pose"}), "evidence": evidence}
    )


def _emptied(room: RoomScene) -> tuple[RoomScene, list[FurnitureAsset]]:
    """A room without its furniture, and that furniture as pose-less assets."""
    return room.model_copy(update={"furniture": []}), [_asset(f) for f in room.furniture]


FIXTURE = _scene("mock")
MOCK_ROOMS = [FIXTURE] + [
    room for room in (demo_room_scene(room_id) for room_id in demo_rooms()) if room.furniture
]
ROOM_IDS = [room.scene_id for room in MOCK_ROOMS]


def _room(width: float = 4.0, depth: float = 3.0, doors: Sequence[DoorOpening] = ()) -> RoomScene:
    """A plain rectangular room: walls `n` (z=0), `e`, `s`, `w`, wound as the contract requires."""
    corners = [(0.0, 0.0), (width, 0.0), (width, depth), (0.0, depth)]
    return _polygon_room(corners, ["n", "e", "s", "w"], doors)


def _polygon_room(
    corners: Sequence[tuple[float, float]], ids: Sequence[str], doors: Sequence[DoorOpening] = ()
) -> RoomScene:
    points = [Vec2(x=x, z=z) for x, z in corners]
    walls = [
        WallSegment(id=ids[i], start=points[i], end=points[(i + 1) % len(points)])
        for i in range(len(points))
    ]
    return RoomScene(
        scene_id="test_room",
        shell_glb_url="/shells/test_room.glb",
        floor_polygon=points,
        walls=walls,
        windows=[],
        doors=list(doors),
        furniture=[],
    )


def _box(
    asset_id: str,
    width: float = 1.0,
    depth: float = 0.5,
    height: float = 0.8,
    category: str = "storage",
    **fields: object,
) -> FurnitureAsset:
    return FurnitureAsset.model_validate(
        {
            "id": asset_id,
            "name": asset_id,
            "category": category,
            "source": "extracted_video",
            "glb_url": f"/assets/{asset_id}.glb",
            "bbox_m": {"width": width, "height": height, "depth": depth},
            "evidence": NO_SOURCE,
            **fields,
        }
    )


def _hint(asset_id: str, wall_id: str, along: float, **fields: object) -> PlacementHint:
    return PlacementHint.model_validate(
        {"asset_id": asset_id, "wall_id": wall_id, "along_frac": along, "confidence": 0.9, **fields}
    )


def _inside(room: RoomScene, item: FurnitureItem) -> bool:
    polygon = [(p.x, p.z) for p in room.floor_polygon]
    return fp.covered_by(fp.footprint(item.bbox_m, item.pose).points, polygon)


def _collisions(items: Sequence[FurnitureItem]) -> list[tuple[str, str]]:
    return [
        (a.id, b.id)
        for i, a in enumerate(items)
        for b in items[i + 1 :]
        if fp.any_overlap(fp.item_occupied(a), fp.item_occupied(b))
    ]


def _swept(room: RoomScene, items: Sequence[FurnitureItem]) -> list[tuple[str, str]]:
    frames = {w.id: fp.wall_frame(w) for w in room.walls}
    hits = []
    for door in room.doors:
        frame = frames[door.wall_id]
        sweep = fp.door_sweep(door, frame) if frame else None
        for item in items:
            if sweep and fp.any_overlap([sweep], fp.item_occupied(item)):
                hits.append((door.id, item.id))
    return hits


# --- geometry ---------------------------------------------------------------------------------


def _square(x: float, z: float, size: float = 1.0, y0: float = 0.0, y1: float = 1.0) -> fp.Prism:
    return fp.Prism(((x, z), (x + size, z), (x + size, z + size), (x, z + size)), y0, y1)


def test_overlap_follows_the_contract_thresholds() -> None:
    a = _square(0, 0)
    assert not fp.prisms_overlap(a, _square(1.0, 0))  # touching is not overlap
    assert not fp.prisms_overlap(a, _square(0.99995, 0))  # 0.5 cm2 is below the 1 cm2 limit
    assert fp.prisms_overlap(a, _square(0.999, 0))  # 10 cm2
    assert not fp.prisms_overlap(a, _square(0.5, 0, y0=1.0, y1=2.0))  # stacked, not overlapping
    assert not fp.prisms_overlap(a, _square(0.5, 0, y0=0.996, y1=2.0))  # 4 mm of shared height
    assert fp.prisms_overlap(a, _square(0.5, 0, y0=0.99, y1=2.0))


def test_overlap_area_of_rotated_squares() -> None:
    diamond = [(0.5, -0.5), (1.5, 0.5), (0.5, 1.5), (-0.5, 0.5)]
    square = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    assert fp.overlap_area(square, diamond) == pytest.approx(1.0)
    assert fp.overlap_area(square, list(reversed(diamond))) == pytest.approx(1.0)  # either winding


def test_fixture_nesting_is_not_a_collision_but_pushing_through_is() -> None:
    items = {f.id: f for f in FIXTURE.furniture}
    assert _collisions(list(items.values())) == []
    chair = items["vid-chair-01"]
    # Slide the chair sideways into the desk's side panel.
    moved = chair.model_copy(update={"pose": Pose2D(x=2.1 + 0.5, z=2.7, yaw_deg=180)})
    assert _collisions([items["vid-desk-01"], moved]) == [("vid-desk-01", "vid-chair-01")]


def test_covered_by_allows_contact_and_rejects_leaving_the_room() -> None:
    room = [(0.0, 0.0), (4.0, 0.0), (4.0, 3.0), (0.0, 3.0)]
    bbox = BBoxM(width=1.0, height=1.0, depth=0.5)
    flush = fp.footprint(bbox, Pose2D(x=0.5, z=0.25, yaw_deg=0))
    assert fp.covered_by(flush.points, room)
    assert not fp.covered_by(fp.footprint(bbox, Pose2D(x=0.5, z=0.249, yaw_deg=0)).points, room)
    assert fp.covered_by(fp.footprint(bbox, Pose2D(x=2.0, z=1.5, yaw_deg=33)).points, room)


def test_covered_by_sees_a_reflex_corner() -> None:
    # L-shape: the top-right 2 x 1.5 m is outside the room.
    ell = [(0.0, 0.0), (2.0, 0.0), (2.0, 1.5), (4.0, 1.5), (4.0, 3.0), (0.0, 3.0)]
    bbox = BBoxM(width=1.0, height=1.0, depth=1.0)
    assert fp.covered_by(fp.footprint(bbox, Pose2D(x=1.0, z=1.0, yaw_deg=0)).points, ell)
    # All four corners of this one are inside or on the boundary, but it spans the notch.
    wide = BBoxM(width=2.0, height=1.0, depth=1.0)
    spanning = fp.footprint(wide, Pose2D(x=2.0, z=1.5, yaw_deg=0))
    assert not fp.covered_by(spanning.points, ell)


def test_door_sweep_matches_the_contract_example() -> None:
    # Wall along +X with the room on +Z, swinging clockwise into the room: the closed leaf
    # extends toward +X and the open leaf points +Z.
    door = DoorOpening(id="d", wall_id="n", hinge_pos=Vec2(x=1.0, z=0.0), width_m=0.8)
    room = _room(doors=[door])
    frame = fp.wall_frame(room.walls[0])
    assert frame is not None
    sweep = fp.door_sweep(door, frame)
    assert sweep is not None
    assert sweep.points[1] == pytest.approx((1.8, 0.0))
    assert sweep.points[-1] == pytest.approx((1.0, 0.8))
    assert abs(fp.shoelace(sweep.points)) / 2 == pytest.approx(math.pi * 0.8**2 / 4, rel=1e-3)
    approach = fp.door_approach(door, frame, 0.5)
    assert approach.bounds == pytest.approx((1.0, 0.0, 1.8, 0.5))


def test_yaw_follows_the_contract_front_direction() -> None:
    for yaw in (0.0, 90.0, 180.0, 270.0, 33.0):
        assert fp.yaw_of(fp.front_direction(yaw)) == pytest.approx(yaw)
    assert fp.front_direction(90.0) == pytest.approx((1.0, 0.0))  # yaw 90 faces +X


def test_demo_rooms_are_the_rooms_the_editor_opens() -> None:
    """`demo_room_scene` follows `roomScene` in frontend/src/data/demoHome.ts: rooms named by
    wall prefix, furniture by pose-in-outline, browser URLs for the served shell and models."""
    rooms = {room_id: demo_room_scene(room_id) for room_id in demo_rooms()}
    reception = rooms["g-reception"]
    assert reception.scene_id == "g-reception"
    assert reception.shell_glb_url == f"{BROWSER_ROOT}/shells/g-reception.glb"
    assert {f.id for f in reception.furniture} == {f"g-reception-o0{i}" for i in range(1, 8)}
    assert all(f.glb_url.startswith(f"{BROWSER_ROOT}/assets/") for f in reception.furniture)
    for floor in demo_floors().values():
        on_floor = [r for r in rooms.values() if r.walls[0] in floor.walls]
        assert sorted(w.id for r in on_floor for w in r.walls) == sorted(w.id for w in floor.walls)
        assert sorted(d.id for r in on_floor for d in r.doors) == sorted(d.id for d in floor.doors)
        # Every item stands in exactly one room.
        assert sorted(f.id for r in on_floor for f in r.furniture) == sorted(
            f.id for f in floor.furniture
        )
    with pytest.raises(KeyError):
        demo_room_scene("no-such-room")


# --- default placement (no hints) -------------------------------------------------------------


@pytest.mark.parametrize("room", MOCK_ROOMS, ids=ROOM_IDS)
def test_default_layout_is_valid_and_flagged(room: RoomScene) -> None:
    empty, assets = _emptied(room)
    result = align_assets(empty, assets, NullObserver())

    assert [item.id for item in result.items] == [a.id for a in assets]
    assert list(result.records) == [a.id for a in assets]
    for item, asset in zip(result.items, assets):
        record = result.records[item.id]
        assert record.method == "default" and record.fits and record.wall_id is not None
        assert record.primary_frame_index == asset.evidence.primary_frame_index
        assert {"placement", "orientation"} <= set(item.correction_needed)
        assert set(asset.correction_needed) <= set(item.correction_needed)
        assert item.model_dump(exclude={"pose", "correction_needed"}) == asset.model_dump(
            exclude={"evidence", "correction_needed"}
        )
        assert _inside(empty, item)
    assert _collisions(result.items) == []
    assert _swept(empty, result.items) == []


@pytest.mark.parametrize("room", MOCK_ROOMS, ids=ROOM_IDS)
def test_default_layout_passes_the_spatial_audit(room: RoomScene) -> None:
    pytest.importorskip("shapely")
    from services.spatial_engine import audit

    empty, assets = _emptied(room)
    aligned = align_assets(empty, assets, NullObserver()).place_in(empty)
    assert audit.detect_collisions(aligned.furniture) == []
    assert audit.detect_out_of_bounds(aligned) == []
    try:
        blocked = audit.detect_blocked_doors(aligned)
    except ValueError:
        return  # the audit rejects this mock's door geometry (hinge off its wall line)
    assert blocked == []


def test_default_layout_does_not_depend_on_asset_order() -> None:
    empty, assets = _emptied(FIXTURE)
    forward = align_assets(empty, assets, NullObserver())
    backward = align_assets(empty, list(reversed(assets)), NullObserver())
    assert {i.id: i.pose for i in forward.items} == {i.id: i.pose for i in backward.items}
    assert forward == align_assets(empty, assets, NullObserver())


def test_default_layout_keeps_doorways_and_windows_clear() -> None:
    door = DoorOpening(id="d", wall_id="s", hinge_pos=Vec2(x=3.0, z=3.0), width_m=0.8)
    room = _room(doors=[door])
    result = align_assets(room, [_box("a", width=3.9, height=2.0)], NullObserver())
    # The longest free wall is `n`; `s` would put the item across the doorway.
    assert result.records["a"].wall_id == "n"
    assert result.items[0].pose == Pose2D(x=1.95, z=0.25, yaw_deg=0.0)


def test_default_layout_in_an_l_shaped_room() -> None:
    corners = [(0.0, 0.0), (2.0, 0.0), (2.0, 1.5), (4.0, 1.5), (4.0, 3.0), (0.0, 3.0)]
    room = _polygon_room(corners, ["a", "b", "c", "d", "e", "f"])
    assets = [_box(f"box-{i}", width=1.2, depth=0.6) for i in range(5)]
    result = align_assets(room, assets, NullObserver())
    assert all(_inside(room, item) for item in result.items)
    assert all(r.fits for r in result.records.values())
    assert _collisions(result.items) == []


def test_an_asset_that_cannot_fit_is_still_returned() -> None:
    room = _room()
    result = align_assets(room, [_box("huge", width=6.0, depth=5.0)], NullObserver())
    record = result.records["huge"]
    assert not record.fits and record.method == "default"
    assert "does not fit" in " ".join(record.notes)
    assert result.items[0].correction_needed == ["placement", "orientation"]


# --- placement from hints ---------------------------------------------------------------------


def test_a_confident_hint_places_the_item_flush_and_unflagged() -> None:
    room = _room()
    hints = [
        _hint("a", "n", 0.5, facing="into_room"),
        _hint("b", "e", 0.5, facing="into_room"),
        _hint("c", "s", 0.25, facing="wall_end", offset_m=0.4),
    ]
    assets = [_box("a"), _box("b"), _box("c", correction_needed=["dimensions"])]
    result = align_assets(room, assets, FixedObserver(hints))
    a, b, c = result.items
    assert (a.pose.x, a.pose.z, a.pose.yaw_deg) == pytest.approx((2.0, 0.25, 0.0))
    assert (b.pose.x, b.pose.z, b.pose.yaw_deg) == pytest.approx((3.75, 1.5, 270.0))
    # `s` runs from (4, 3) to (0, 3): a quarter along is x = 3, facing its end is -X, and the
    # item's side (its 1.0 m width) stands 0.4 m off the wall.
    assert (c.pose.x, c.pose.z, c.pose.yaw_deg) == pytest.approx((3.0, 2.1, 270.0))
    assert a.correction_needed == [] and b.correction_needed == []
    assert c.correction_needed == ["dimensions"]  # what the asset already carried
    assert all(r.method == "hint" and r.confidence == 0.9 for r in result.records.values())
    assert result.records["c"].wall_id == "s" and result.records["c"].moved_m == 0


def test_uncertain_hints_are_flagged_for_correction() -> None:
    room = _room()
    hints = [
        _hint("unsure", "n", 0.3, facing="into_room", confidence=0.4),
        _hint("no-front", "s", 0.5, facing=None),
    ]
    result = align_assets(room, [_box("unsure"), _box("no-front")], FixedObserver(hints))
    unsure, no_front = result.items
    assert unsure.correction_needed == ["placement", "orientation"]
    assert no_front.correction_needed == ["orientation"]
    assert no_front.pose.yaw_deg == pytest.approx(180.0)  # back to wall `s`, as a best guess


def test_a_corner_hint_keeps_the_item_on_its_wall() -> None:
    result = align_assets(_room(), [_box("a")], FixedObserver([_hint("a", "n", 0.0)]))
    assert (result.items[0].pose.x, result.items[0].pose.z) == pytest.approx((0.5, 0.25))
    assert result.records["a"].moved_m == 0 and result.items[0].correction_needed == ["orientation"]


def test_clashing_hints_are_separated_and_the_moved_item_is_flagged() -> None:
    room = _room()
    hints = [
        _hint("first", "n", 0.5, facing="into_room", confidence=0.95),
        _hint("second", "n", 0.5, facing="into_room", confidence=0.8),
    ]
    result = align_assets(room, [_box("second"), _box("first")], FixedObserver(hints))
    second, first = result.items
    assert first.pose.x == pytest.approx(2.0)  # the more confident hint keeps its spot
    assert _collisions(result.items) == [] and _inside(room, second)
    record = result.records["second"]
    assert record.moved_m == pytest.approx(0.5, abs=0.051)  # pushed out past the first item
    assert second.correction_needed == ["placement"] and first.correction_needed == []


def test_a_hinted_item_in_a_door_swing_stays_and_is_flagged() -> None:
    door = DoorOpening(id="d", wall_id="n", hinge_pos=Vec2(x=1.0, z=0.0), width_m=0.8)
    room = _room(doors=[door])
    hint = _hint("a", "n", 0.4, facing="into_room")
    result = align_assets(room, [_box("a")], FixedObserver([hint]))
    assert result.items[0].pose.x == pytest.approx(1.6) and result.records["a"].moved_m == 0
    assert result.items[0].correction_needed == ["placement"]
    assert "in the swing of d" in result.records["a"].notes


def test_a_seated_chair_is_pushed_in_at_its_desk() -> None:
    items = {f.id: f for f in FIXTURE.furniture}
    desk, chair = items["vid-desk-01"], items["vid-chair-01"]
    room = FIXTURE.model_copy(update={"furniture": [desk]})
    hint = _hint(chair.id, "w_south", 0.5, facing="toward_wall", seated_at=desk.id)
    result = align_assets(room, [_asset(chair)], FixedObserver([hint]))
    placed = result.items[0]
    assert placed.pose.yaw_deg == pytest.approx(chair.pose.yaw_deg)
    assert math.hypot(placed.pose.x - chair.pose.x, placed.pose.z - chair.pose.z) < 0.1
    assert _collisions([desk, placed]) == []
    assert f"pushed in at {desk.id}" in result.records[chair.id].notes
    assert result.place_in(room).furniture == [desk, placed]


def test_seated_at_an_item_placed_in_the_same_run() -> None:
    room = _room()
    desk = _asset(next(f for f in FIXTURE.furniture if f.id == "vid-desk-01"))
    chair = _asset(next(f for f in FIXTURE.furniture if f.id == "vid-chair-01"))
    hints = [
        _hint(chair.id, "n", 0.5, facing="toward_wall", seated_at=desk.id),
        _hint(desk.id, "n", 0.5, facing="into_room"),
    ]
    result = align_assets(room, [chair, desk], FixedObserver(hints))
    placed_chair, placed_desk = result.items
    assert placed_chair.pose.yaw_deg == pytest.approx(180.0)
    assert placed_chair.pose.x == pytest.approx(placed_desk.pose.x)
    assert _collisions(result.items) == [] and _inside(room, placed_chair)


def test_bad_hints_are_ignored_with_a_warning() -> None:
    room = _room()
    hints = [
        _hint("ghost", "n", 0.5),
        _hint("a", "no-such-wall", 0.5),
        _hint("b", "e", 0.5, facing="into_room", seated_at="ghost"),
        _hint("c", "s", 0.5, facing="into_room", seated_at="b"),  # `b` is no desk or table
    ]
    result = align_assets(room, [_box("a"), _box("b"), _box("c")], FixedObserver(hints))
    assert result.records["a"].method == "default"
    assert result.records["b"].method == "hint" and result.records["b"].wall_id == "e"
    assert result.records["c"].wall_id == "s" and result.records["c"].notes == []
    assert len(result.warnings) == 4
    assert result.items[0].correction_needed == ["placement", "orientation"]


def test_an_observer_that_fails_does_not_lose_furniture() -> None:
    class Broken:
        def observe(
            self, scene: RoomScene, assets: Sequence[FurnitureAsset], frames: FrameSource
        ) -> list[PlacementHint]:
            raise RuntimeError("provider down")

    result = align_assets(_room(), [_box("a"), _box("b")], Broken())
    assert [r.method for r in result.records.values()] == ["default", "default"]
    assert result.warnings and "RuntimeError" in result.warnings[0]


def test_the_observer_receives_the_evidence_frames() -> None:
    seen: list[tuple[str, int, bytes | None]] = []

    class Recording:
        def observe(
            self, scene: RoomScene, assets: Sequence[FurnitureAsset], frames: FrameSource
        ) -> list[PlacementHint]:
            for asset in assets:
                frame = asset.evidence.frames[0]
                seen.append((asset.id, frame.frame_index, frames(asset.id, frame)))
            return []

    def source(asset_id: str, frame: EvidenceFrame) -> bytes | None:
        return f"{asset_id}@{frame.frame_index}".encode()

    align_assets(_room(), [_box("a")], Recording(), source)
    align_assets(_room(), [_box("b")], Recording())  # no source: frames are simply unavailable
    assert seen == [("a", 7, b"a@7"), ("b", 7, None)]


# --- identity ---------------------------------------------------------------------------------


def test_items_already_in_the_scene_are_never_moved() -> None:
    empty, assets = _emptied(FIXTURE)
    first = align_assets(empty, assets, NullObserver())
    aligned = first.place_in(empty)

    # The user moves one item; a re-run with the same assets plus a new one leaves all alone.
    moved = aligned.furniture[0].model_copy(update={"pose": Pose2D(x=2.0, z=1.8, yaw_deg=45)})
    edited = aligned.model_copy(update={"furniture": [moved, *aligned.furniture[1:]]})
    again = align_assets(edited, [*assets, _box("new")], NullObserver())
    assert again.items[: len(assets)] == edited.furniture
    assert all(again.records[a.id].method == "kept" for a in assets)
    new = again.items[-1]
    assert again.records["new"].method == "default"
    assert _collisions([*edited.furniture, new]) == [] and _inside(edited, new)
    assert [f.id for f in again.place_in(edited).furniture] == [a.id for a in assets] + ["new"]


def test_duplicate_asset_ids_are_rejected() -> None:
    with pytest.raises(ValueError, match="unique"):
        align_assets(_room(), [_box("a"), _box("a")], NullObserver())


def test_fixture_evidence_with_null_fields_is_tolerated() -> None:
    assets = [_asset(f) for f in FIXTURE.furniture if f.id in EVIDENCE]
    assert assets and all(a.evidence.frames[0].bbox_px is None for a in assets)
    result = align_assets(FIXTURE.model_copy(update={"furniture": []}), assets, NullObserver())
    assert {r.primary_frame_index for r in result.records.values()} == {0}


# --- against the reference scenes -------------------------------------------------------------


def _error(reference: FurnitureItem, item: FurnitureItem) -> tuple[float, float]:
    distance = math.hypot(reference.pose.x - item.pose.x, reference.pose.z - item.pose.z)
    return distance, abs((reference.pose.yaw_deg - item.pose.yaw_deg + 180) % 360 - 180)


@pytest.mark.parametrize("room", MOCK_ROOMS, ids=ROOM_IDS)
def test_wall_relative_hints_reproduce_the_reference_poses(room: RoomScene) -> None:
    empty, assets = _emptied(room)
    hints = [wall_relative(room, item) for item in room.furniture]
    assert all(h is not None for h in hints)
    result = align_assets(empty, assets, FixedObserver([h for h in hints if h]))
    swept = {item_id for _, item_id in _swept(room, room.furniture)}
    for reference, item, asset in zip(room.furniture, result.items, assets):
        distance, yaw = _error(reference, item)
        # Position is exact; yaw snaps square to the wall, which these plans skew by up to 1 deg.
        assert distance < 0.01 and yaw < 1.5, item.id
        record = result.records[item.id]
        assert record.method == "hint" and record.moved_m == 0
        extra = set(item.correction_needed) - set(asset.correction_needed)
        assert extra == ({"placement"} if item.id in swept and "placement" in extra else set())


def _reception() -> RoomScene:
    return demo_room_scene("g-reception")


def test_recorded_reception_hints_place_the_video_furniture() -> None:
    """The four items of the reviewed `three_floor_3.mp4` opening room, with Dev 2's reviewed
    boxes as evidence, placed from the reviewed hints (see `room/fixtures/README.md`).

    The hints follow the video, which disagrees with the mock scene's poses for both sofas, so
    this checks the placement against the hints and the room, not against the mock.
    """
    room = _reception()
    assets = [FurnitureAsset.model_validate(a) for a in json.loads(RECEPTION_ASSETS.read_text())]
    hints = PlacementHints.model_validate_json(RECEPTION_HINTS.read_text()).hints
    ids = [a.id for a in assets]
    assert ids == [h.asset_id for h in hints] == [f"g-reception-o0{i}" for i in (1, 2, 3, 4)]
    assert all(a.evidence.frames[0].bbox_px is not None for a in assets)  # real source boxes
    fixed = [f for f in room.furniture if f.id not in ids]
    start = room.model_copy(update={"furniture": fixed})
    result = align_assets(start, assets, FixedObserver(hints))

    assert _collisions([*fixed, *result.items]) == []
    walls = {w.id: fp.wall_frame(w) for w in room.walls}
    for item, hint, asset in zip(result.items, hints, assets):
        record = result.records[item.id]
        assert _inside(room, item)
        assert record.method == "hint" and record.wall_id == hint.wall_id
        assert record.moved_m <= 0.5 and record.primary_frame_index == 0
        # Reviewed by eye, not measured: below the confidence that settles a placement.
        assert {"placement", "orientation"} <= set(item.correction_needed)
        frame = walls[hint.wall_id]
        assert frame is not None
        along, _ = frame.locate((item.pose.x, item.pose.z))
        assert abs(along / frame.length - hint.along_frac) < 0.15
    sofa_west, sofa_north = result.items[0], result.items[1]
    assert sofa_west.pose.yaw_deg == pytest.approx(90, abs=1.5)  # back to the west wall
    assert sofa_north.pose.yaw_deg == pytest.approx(0, abs=1.5)  # back to the north wall


def test_result_types_round_trip_as_json() -> None:
    empty, assets = _emptied(FIXTURE)
    result = align_assets(empty, assets, NullObserver())
    assert AlignmentResult.model_validate_json(result.model_dump_json()) == result
