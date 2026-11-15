"""The placement metric: each tradition on hand-built geometry, and honest 'not assessed'."""

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
from services.spatial_engine.report import audit_scene


def piece(item_id: str, category: str, x: float, z: float, yaw: float = 0) -> FurnitureItem:
    width, depth = (1.4, 2.0) if category == "bed" else (1.2, 0.7)
    return FurnitureItem(
        id=item_id,
        name=item_id,
        category=category,  # type: ignore[arg-type]
        source="extracted_video",
        glb_url="/mesh.glb",
        bbox_m=BBoxM(width=width, height=0.8, depth=depth),
        pose=Pose2D(x=x, z=z, yaw_deg=yaw),
        requires_front_clear_m=0,
    )


def room(*furniture: FurnitureItem, door: bool = True) -> RoomScene:
    """A 6 m square room; the door is on the north (z=0) wall, centred at x=2.5."""
    return RoomScene(
        scene_id="room",
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in [(0, 0), (6, 0), (6, 6), (0, 6)]],
        walls=[WallSegment(id="north", start=Vec2(x=0, z=0), end=Vec2(x=6, z=0))],
        doors=[DoorOpening(id="door", wall_id="north", hinge_pos=Vec2(x=2, z=0), width_m=1)]
        if door
        else [],
        windows=[],
        furniture=list(furniture),
    )


def verdicts(scene: RoomScene) -> dict[str, str]:
    report = audit_scene(scene).feng_shui
    assert report is not None
    return {s.from_item_id: s.status for s in report.sightlines}


def test_a_desk_facing_the_door_side_of_the_room_is_in_command() -> None:
    # Front +z points into the room, so the sitter is south of the desk, looking north at the door.
    scene = room(piece("desk", "desk", 4.5, 3, yaw=0))
    assert verdicts(scene) == {"desk": "command_position"}
    assert audit_scene(scene).feng_shui.score == 100  # type: ignore[union-attr]


def test_a_desk_with_the_door_behind_the_sitter_is_back_to_door() -> None:
    scene = room(piece("desk", "desk", 4.5, 3, yaw=180))
    assert verdicts(scene) == {"desk": "back_to_door"}
    report = audit_scene(scene).feng_shui
    assert report is not None and report.score == 0
    assert "behind you" in report.sightlines[0].reason


def test_a_bed_whose_foot_points_straight_at_the_door_is_in_coffin_position() -> None:
    assert verdicts(room(piece("bed", "bed", 2.5, 3, yaw=180))) == {"bed": "coffin_alignment"}


def test_a_bed_with_the_door_off_to_the_side_is_in_command() -> None:
    assert verdicts(room(piece("bed", "bed", 4.8, 3, yaw=180))) == {"bed": "command_position"}


def test_a_bed_with_its_head_toward_the_door_cannot_see_it() -> None:
    assert verdicts(room(piece("bed", "bed", 4.8, 3, yaw=0))) == {"bed": "back_to_door"}


def test_the_score_is_the_average_of_the_judged_pieces() -> None:
    scene = room(piece("good", "desk", 4.5, 3, 0), piece("bad", "desk", 1.0, 3, 180))
    report = audit_scene(scene).feng_shui
    assert report is not None and report.score == 50
    assert {s.from_item_id for s in report.sightlines} == {"good", "bad"}


def test_nothing_to_judge_is_not_assessed_rather_than_zero_or_perfect() -> None:
    assert audit_scene(room(piece("sofa", "sofa", 3, 3))).feng_shui is None
    assert audit_scene(room(piece("desk", "desk", 4.5, 3), door=False)).feng_shui is None
    assert audit_scene(room()).feng_shui is None


def test_rotating_a_full_turn_does_not_change_the_verdict() -> None:
    assert verdicts(room(piece("desk", "desk", 4.5, 3, yaw=360))) == {"desk": "command_position"}
    assert verdicts(room(piece("desk", "desk", 4.5, 3, yaw=-180))) == {"desk": "back_to_door"}


@pytest.mark.parametrize("yaw", [0, 90, 180, 270])
def test_every_orientation_gets_a_verdict_and_input_is_unchanged(yaw: float) -> None:
    scene = room(piece("desk", "desk", 4.5, 3, yaw))
    before = scene.model_dump()
    report = audit_scene(scene).feng_shui
    assert report is not None and 0 <= report.score <= 100
    assert scene.model_dump() == before
