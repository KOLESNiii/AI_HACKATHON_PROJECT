"""Reconstructed scenes round coordinates; openings a fraction of a millimetre off still count."""

import pytest

from contracts.schema import DoorOpening, RoomScene, Vec2, WallSegment, WindowOpening
from services.spatial_engine.brightness import calculate_brightness_approximation
from services.spatial_engine.geometry import SpatialInputError
from services.spatial_engine.report import audit_scene


def room(hinge_z: float, window_width: float = 2.0) -> RoomScene:
    return RoomScene(
        scene_id="room",
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in [(0, 0), (4, 0), (4, 3), (0, 3)]],
        walls=[
            WallSegment(id="north", start=Vec2(x=0, z=0), end=Vec2(x=4, z=0)),
            WallSegment(id="south", start=Vec2(x=4, z=3), end=Vec2(x=0, z=3)),
        ],
        doors=[DoorOpening(id="door", wall_id="north", hinge_pos=Vec2(x=1, z=hinge_z))],
        windows=[
            WindowOpening(
                id="window",
                wall_id="south",
                offset_along_wall_m=2,
                width_m=window_width,
                plan_normal_deg=180,
            )
        ],
        furniture=[],
    )


@pytest.mark.parametrize("offset", [0.0, 3e-7, -3e-7, 5e-4, -5e-4])
def test_slightly_misaligned_openings_are_audited_and_the_room_stays_reachable(
    offset: float,
) -> None:
    scene = room(hinge_z=offset, window_width=2 + abs(offset))
    report = audit_scene(scene)
    assert report.blocked_doors == []
    assert report.walkable_floor_ratio == pytest.approx(0.98, abs=0.02)
    assert calculate_brightness_approximation(scene).openness_ratio == 1


def test_clearly_misplaced_openings_are_still_rejected() -> None:
    with pytest.raises(SpatialInputError, match="hinge must lie on its wall"):
        audit_scene(room(hinge_z=0.01))
    with pytest.raises(SpatialInputError, match="fit within its wall"):
        calculate_brightness_approximation(room(hinge_z=0, window_width=2.01))
