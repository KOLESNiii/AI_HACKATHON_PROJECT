"""Placing an imported item: audited, against a wall when preferred, never in a door swing."""

import pytest
from fastapi.testclient import TestClient

from contracts.schema import (
    BBoxM,
    CollisionPart,
    DoorOpening,
    FurnitureItem,
    Pose2D,
    RoomScene,
    Vec2,
    WallSegment,
)
from services.spatial_engine.geometry import SpatialInputError, furniture_footprint
from services.spatial_engine.main import app
from services.spatial_engine.placement import place_item
from services.spatial_engine.report import audit_scene


def room(*furniture: FurnitureItem) -> RoomScene:
    corners = [(0, 0), (4, 0), (4, 3), (0, 3)]
    walls = [
        WallSegment(id=f"w{i}", start=Vec2(x=a[0], z=a[1]), end=Vec2(x=b[0], z=b[1]))
        for i, (a, b) in enumerate(zip(corners, corners[1:] + corners[:1], strict=True))
    ]
    return RoomScene(
        scene_id="place-room",
        revision=2,
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in corners],
        walls=walls,
        doors=[DoorOpening(id="door", wall_id="w0", hinge_pos=Vec2(x=0.2, z=0), width_m=0.9)],
        windows=[],
        furniture=list(furniture),
    )


def item(width: float = 1.2, depth: float = 0.5, **changes: object) -> FurnitureItem:
    return FurnitureItem.model_validate(
        {
            "id": "cat-desk",
            "name": "Desk",
            "category": "desk",
            "source": "catalog_search",
            "glb_url": "/api/reconstruction/assets/desk.glb",
            "bbox_m": BBoxM(width=width, depth=depth, height=0.75),
            "pose": Pose2D(x=0, z=0),
            "dimension_source": "catalog",
            **changes,
        }
    )


def test_wall_flush_item_backs_onto_a_wall_and_passes_the_audit() -> None:
    scene = room()
    placement = place_item(scene, item())
    placed = placement.item
    assert placement.against_wall
    candidate = scene.model_copy(update={"furniture": [placed]})
    report = audit_scene(candidate)
    assert report == placement.report
    assert not report.collisions and not report.out_of_bounds_item_ids
    assert not report.blocked_doors
    # Back within a few cm of a wall: one footprint edge lies on the floor boundary.
    minx, minz, maxx, maxz = furniture_footprint(placed).bounds
    assert min(minx, minz, 4 - maxx, 3 - maxz) < 0.05
    assert placed.bbox_m == item().bbox_m and placed.id == "cat-desk"


def test_existing_furniture_is_avoided_and_never_moved() -> None:
    sofa = item(3.9, 0.9, id="sofa", name="Sofa", category="sofa", pose=Pose2D(x=2, z=2.5))
    scene = room(sofa)
    placed = place_item(scene, item()).item
    assert scene.furniture == [sofa]
    assert not furniture_footprint(placed).intersects(furniture_footprint(sofa).buffer(-1e-3))


def test_free_standing_item_prefers_open_floor() -> None:
    assert not place_item(room(), item(0.8, 0.8, wall_flush_preferred=False)).against_wall


def test_item_nests_under_a_tabletop_when_the_audit_allows_it() -> None:
    # The reviewer's repro: only the tabletop is occupied, so the chair fits beneath it.
    table = item(
        0.9,
        0.9,
        id="table",
        name="Table",
        category="table",
        pose=Pose2D(x=0.5, z=0.5),
        collision_parts=[CollisionPart(x=0, z=0, width=0.9, depth=0.9, y_min=0.7, y_max=0.75)],
    )
    scene = room(table).model_copy(
        update={
            "floor_polygon": [Vec2(x=x, z=z) for x, z in [(0, 0), (1, 0), (1, 1), (0, 1)]],
            "walls": [],
            "doors": [],
        }
    )
    chair = item(0.4, 0.4, id="chair", name="Chair", category="chair")
    chair = chair.model_copy(update={"bbox_m": BBoxM(width=0.4, depth=0.4, height=0.5)})
    placement = place_item(scene, chair)
    assert not placement.report.collisions
    assert furniture_footprint(placement.item).intersects(furniture_footprint(table))


def test_too_big_item_is_refused() -> None:
    with pytest.raises(SpatialInputError, match="No free spot"):
        place_item(room(), item(5, 4))


def test_place_endpoint_returns_an_audited_addition() -> None:
    scene = room()
    response = TestClient(app).post(
        "/place",
        json={"scene": scene.model_dump(mode="json"), "item": item().model_dump(mode="json")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["additions"][0]["id"] == "cat-desk"
    assert body["report"]["scene_revision"] == 2 and body["poses"] == {}


def test_place_endpoint_reports_no_space_as_422() -> None:
    response = TestClient(app).post(
        "/place",
        json={
            "scene": room().model_dump(mode="json"),
            "item": item(5, 4).model_dump(mode="json"),
        },
    )
    assert response.status_code == 422
