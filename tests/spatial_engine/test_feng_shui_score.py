from fastapi.testclient import TestClient

from contracts.schema import (
    BBoxM,
    DoorOpening,
    FurnitureItem,
    Pose2D,
    RoomScene,
    Vec2,
    WallSegment,
    WindowOpening,
)
from services.spatial_engine.feng_shui import ActivityAnchor, FengShuiRequest, Mirror
from services.spatial_engine.feng_shui_score import AUDIT_CAP, score_feng_shui
from services.spatial_engine.main import app

CORNERS = [(0, 0), (4, 0), (4, 4), (0, 4)]
WALLS = [
    WallSegment(id=name, start=Vec2(x=a[0], z=a[1]), end=Vec2(x=b[0], z=b[1]))
    for name, a, b in zip("nesw", CORNERS, CORNERS[1:] + CORNERS[:1])
]
# Door centre (0.925, 0) on the north wall, opening into the room (+Z).
DOOR = DoorOpening(id="door", wall_id="n", hinge_pos=Vec2(x=0.5, z=0))


def item(item_id, category, x, z, yaw, width, depth, height=0.6) -> FurnitureItem:
    return FurnitureItem(
        id=item_id,
        name=item_id,
        category=category,
        source="catalog_search",
        glb_url="/mesh.glb",
        bbox_m=BBoxM(width=width, height=height, depth=depth),
        pose=Pose2D(x=x, z=z, yaw_deg=yaw),
        requires_front_clear_m=0,
    )


def bed(x=2.6, z=3.0):
    """Headboard on the south wall, facing the door side of the room (-Z)."""
    return item("bed", "bed", x, z, 180, 1.5, 2.0, 0.5)


def room(*furniture, doors=(DOOR,), windows=()) -> RoomScene:
    return RoomScene(
        scene_id="fs",
        revision=2,
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in CORNERS],
        walls=WALLS,
        doors=list(doors),
        windows=list(windows),
        furniture=list(furniture),
    )


def rules(result, name):
    return [r for r in result.rules if r.rule == name]


def statuses(result):
    return {(s.from_item_id, s.status) for s in result.sightlines}


def test_command_position_scores_high():
    result = score_feng_shui(FengShuiRequest(scene=room(bed()), mirrors=[]))
    assert ("bed", "command_position") in statuses(result)
    assert result.score is not None and result.score >= 85
    assert not result.capped_by_audit
    assert result.coverage == 1.0
    assert rules(result, "backing")[0].score == 1.0


def test_coffin_alignment_scores_lower():
    good = score_feng_shui(FengShuiRequest(scene=room(bed())))
    coffin = score_feng_shui(FengShuiRequest(scene=room(bed(x=0.925))))
    assert ("bed", "coffin_alignment") in statuses(coffin)
    assert rules(coffin, "door_axis")[0].score == 0.0
    assert coffin.score is not None and good.score is not None
    assert coffin.score < good.score


def test_desk_facing_wall_has_back_to_door():
    desk = item("desk", "desk", 1.0, 3.7, 180, 1.2, 0.6, 0.75)
    result = score_feng_shui(FengShuiRequest(scene=room(desk)))
    assert ("desk", "back_to_door") in statuses(result)
    assert rules(result, "door_visible")[0].score == 0.0


def test_anchor_overrides_default_facing():
    desk = item("desk", "desk", 1.0, 3.7, 180, 1.2, 0.6, 0.75)
    anchor = ActivityAnchor(item_id="desk", kind="seated", x=1.0, z=2.95, facing_yaw_deg=180)
    result = score_feng_shui(FengShuiRequest(scene=room(desk), activities=[anchor]))
    assert ("desk", "back_to_door") not in statuses(result)
    assert rules(result, "door_visible")[0].score == 1.0
    assert "anchored occupant" in rules(result, "door_visible")[0].detail


def test_headboard_under_window_loses_backing():
    window = WindowOpening(
        id="win", wall_id="s", offset_along_wall_m=0.65, width_m=1.5, plan_normal_deg=180
    )
    result = score_feng_shui(FengShuiRequest(scene=room(bed(), windows=[window])))
    assert rules(result, "backing")[0].score == 0.0


def test_unassessable_rooms_return_null_score():
    no_door = score_feng_shui(FengShuiRequest(scene=room(bed(), doors=())))
    assert no_door.score is None and no_door.coverage < 1
    wardrobe = item("wardrobe", "wardrobe", 3.5, 3.7, 180, 1.0, 0.6, 2.0)
    no_key_item = score_feng_shui(FengShuiRequest(scene=room(wardrobe)))
    assert no_key_item.score is None
    assert any("command position" in u for u in no_key_item.unassessed)


def test_missing_mirror_inventory_reduces_coverage():
    result = score_feng_shui(FengShuiRequest(scene=room(bed())))
    assert result.coverage < 1
    assert any(u.startswith("mirror_reflection") for u in result.unassessed)


def test_mirror_facing_bed_is_penalised():
    mirror = Mirror(id="mirror", x=2.6, y=1.0, z=0.05, width_m=0.6, height_m=1.2, normal_yaw_deg=0)
    result = score_feng_shui(FengShuiRequest(scene=room(bed()), mirrors=[mirror]))
    assert rules(result, "mirror_reflection")[0].score == 0.0


def test_audit_issues_cap_score():
    box = item("box", "storage", 2.6, 3.0, 0, 0.5, 0.5)
    result = score_feng_shui(FengShuiRequest(scene=room(bed(), box)))
    assert result.capped_by_audit
    assert result.score is not None and result.score <= AUDIT_CAP


def test_deterministic_and_read_only():
    scene = room(bed())
    before = scene.model_dump()
    first = score_feng_shui(FengShuiRequest(scene=scene))
    assert score_feng_shui(FengShuiRequest(scene=scene)) == first
    assert scene.model_dump() == before


def test_route():
    client = TestClient(app)
    payload = {"scene": room(bed()).model_dump(mode="json")}
    response = client.post("/feng-shui/score", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["revision"] == 2 and isinstance(body["score"], int)
    bad = client.post("/feng-shui/score", json={**payload, "main_entry_door_id": "nope"})
    assert bad.status_code == 422
