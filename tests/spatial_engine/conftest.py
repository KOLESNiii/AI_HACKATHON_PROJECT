"""Shared regression geometry for custom layout access checks."""

import pytest

from contracts.schema import BBoxM, DoorOpening, FurnitureItem, Pose2D, RoomScene, Vec2, WallSegment


@pytest.fixture
def divided_access_room() -> RoomScene:
    """Clearing a wardrobe by moving its blocker behind the divider cuts circulation."""

    def item(item_id: str, x: float, z: float, **kwargs: object) -> FurnitureItem:
        return FurnitureItem.model_validate(
            {
                "id": item_id,
                "name": item_id,
                "category": "wardrobe",
                "source": "extracted_video",
                "glb_url": "/mesh.glb",
                "bbox_m": BBoxM(width=1, height=2, depth=1),
                "pose": Pose2D(x=x, z=z),
                "requires_front_clear_m": 0,
                **kwargs,
            }
        )

    return RoomScene(
        scene_id="divided-room",
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in [(0, 0), (8, 0), (8, 8), (0, 8)]],
        walls=[WallSegment(id="north", start=Vec2(x=0, z=0), end=Vec2(x=8, z=0))],
        doors=[DoorOpening(id="door", wall_id="north", hinge_pos=Vec2(x=1, z=0), width_m=1)],
        windows=[],
        furniture=[
            item("wardrobe", 2, 4, requires_front_clear_m=1),
            item("box", 2, 5.5),
            item("divider", 4, 3.4, is_fixed=True, bbox_m=BBoxM(width=1, height=2, depth=6.8)),
        ],
    )
