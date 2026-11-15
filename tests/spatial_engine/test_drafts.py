"""Request-local drafts accept only pose edits of movable items and never mutate stored state."""

import math

import pytest

from contracts.schema import BBoxM, FurnitureItem, Pose2D, RoomScene, Vec2, WallSegment
from services.spatial_engine.drafts import DraftSession, LayoutMoveError, PoseChange
from services.spatial_engine.geometry import SpatialInputError
from services.spatial_engine.report import audit_scene


def item(item_id: str, x: float, z: float, *, fixed: bool = False) -> FurnitureItem:
    return FurnitureItem(
        id=item_id,
        name=item_id,
        category="wardrobe",
        source="extracted_video",
        glb_url="/mesh.glb",
        bbox_m=BBoxM(width=1, height=2, depth=1),
        pose=Pose2D(x=x, z=z),
        requires_front_clear_m=0,
        is_fixed=fixed,
    )


def room(furniture: list[FurnitureItem]) -> RoomScene:
    return RoomScene(
        scene_id="room",
        revision=3,
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in [(0, 0), (8, 0), (8, 8), (0, 8)]],
        walls=[WallSegment(id="north", start=Vec2(x=0, z=0), end=Vec2(x=8, z=0))],
        doors=[],
        windows=[],
        furniture=furniture,
    )


def session(*, locked: tuple[str, ...] = ()) -> DraftSession:
    scene = room([item("bed", 2, 2), item("desk", 6, 6), item("radiator", 6, 2, fixed=True)])
    return DraftSession(scene, locked, session_token="t")


def test_original_draft_is_an_independent_audited_copy() -> None:
    scene = room([item("bed", 2, 2), item("desk", 2.5, 2)])
    expected = audit_scene(scene)
    drafts = DraftSession(scene)
    scene.furniture[1].pose.x = 6  # A later edit by the caller must not leak into the session.

    original = drafts.draft(drafts.original_draft_id)
    assert original.parent_id is None and drafts.draft_count == 1
    assert original.evaluation.report == expected
    assert original.evaluation.report.scene_revision == 3
    assert original.evaluation.report.overall_score is None
    assert not original.evaluation.metrics.passes_critical_checks
    assert original.evaluation.metrics.movement_m == 0
    assert drafts.scene(drafts.original_draft_id).furniture[1].pose.x == 2.5


def test_multi_item_move_creates_a_new_draft_and_changes_nothing_else() -> None:
    scene = room([item("bed", 2, 2), item("desk", 6, 6), item("radiator", 6, 2, fixed=True)])
    snapshot = scene.model_dump()
    drafts = DraftSession(scene)
    before = drafts.draft(drafts.original_draft_id)
    moves = [PoseChange("bed", 3, 2, 90), PoseChange("desk", 5, 6)]

    moved = drafts.apply_moves(before.draft_id, moves)

    assert moved.draft_id != before.draft_id and moved.parent_id == before.draft_id
    assert {pose.item_id: (pose.x, pose.z, pose.yaw_deg) for pose in moved.poses} == {
        "bed": (3, 2, 90),
        "desk": (5, 6, 0),
        "radiator": (6, 2, 0),
    }
    assert moved.evaluation.metrics.moved_item_count == 2
    assert moved.evaluation.metrics.passes_critical_checks
    assert scene.model_dump() == snapshot
    assert drafts.draft(before.draft_id) is before
    assert drafts.scene(before.draft_id).model_dump() == snapshot
    assert moves == [PoseChange("bed", 3, 2, 90), PoseChange("desk", 5, 6)]


def test_draft_scene_preserves_everything_except_poses_and_echoes_the_base_revision() -> None:
    drafts = session()
    moved = drafts.apply_moves(drafts.original_draft_id, [PoseChange("bed", 3, 3, 45)])
    original, candidate = drafts.scene(drafts.original_draft_id), drafts.scene(moved.draft_id)

    assert candidate.furniture[0].pose == Pose2D(x=3, z=3, yaw_deg=45)
    candidate.furniture[0].pose = original.furniture[0].pose
    assert candidate == original
    assert moved.evaluation.report.scene_id == "room"
    assert moved.evaluation.report.scene_revision == 3

    drafts.scene(moved.draft_id).furniture[0].pose.x = 7  # Returned scenes are throwaway copies.
    assert drafts.scene(moved.draft_id).furniture[0].pose.x == 3


def test_invalid_intermediate_draft_is_kept_and_can_be_repaired() -> None:
    drafts = session()
    swapped_one = drafts.apply_moves(drafts.original_draft_id, [PoseChange("bed", 6, 6)])
    assert swapped_one.evaluation.metrics.collision_count == 1
    assert not swapped_one.evaluation.metrics.passes_critical_checks

    swapped_both = drafts.apply_moves(swapped_one.draft_id, [PoseChange("desk", 2, 2)])
    assert swapped_both.evaluation.metrics.passes_critical_checks
    assert swapped_both.evaluation.metrics.moved_item_count == 2
    assert drafts.draft(swapped_one.draft_id).evaluation.metrics.collision_count == 1
    assert drafts.draft_count == 3


def test_movement_is_measured_from_the_original_not_the_parent_draft() -> None:
    drafts = session()
    away = drafts.apply_moves(drafts.original_draft_id, [PoseChange("bed", 4, 2)])
    back = drafts.apply_moves(away.draft_id, [PoseChange("bed", 2, 2)])
    assert away.evaluation.metrics.translation_m == pytest.approx(2)
    assert back.evaluation.metrics.movement_m == 0
    assert back.evaluation.metrics.moved_item_count == 0


def test_out_of_room_move_is_an_invalid_draft_not_a_rejected_request() -> None:
    drafts = session()
    outside = drafts.apply_moves(drafts.original_draft_id, [PoseChange("bed", -3, 2)])
    assert outside.evaluation.report.out_of_bounds_item_ids == ["bed"]


@pytest.mark.parametrize(
    ("moves", "code"),
    [
        ([], "empty_moves"),
        ([PoseChange("bed", 3, 3), PoseChange("bed", 3, 3)], "duplicate_item"),
        ([PoseChange("bed", 3, 3), PoseChange("bed", 4, 4)], "duplicate_item"),
        ([PoseChange("sofa", 3, 3)], "unknown_item"),
        ([PoseChange("radiator", 6, 2)], "fixed_item"),
        ([PoseChange("desk", 6, 6)], "locked_item"),
        ([PoseChange("bed", math.nan, 3)], "non_finite_pose"),
        ([PoseChange("bed", 3, math.inf)], "non_finite_pose"),
        ([PoseChange("bed", 3, 3, -math.inf)], "non_finite_pose"),
        # One bad entry rejects the whole request, including its valid moves.
        ([PoseChange("bed", 3, 3), PoseChange("radiator", 5, 2)], "fixed_item"),
    ],
)
def test_rejected_moves_report_a_code_and_leave_the_session_unchanged(
    moves: list[PoseChange], code: str
) -> None:
    drafts = session(locked=("desk",))
    with pytest.raises(LayoutMoveError) as error:
        drafts.apply_moves(drafts.original_draft_id, moves)
    assert error.value.code == code
    assert drafts.draft_count == 1


def test_unknown_and_foreign_draft_ids_are_rejected() -> None:
    drafts = session()
    other = DraftSession(drafts.scene(drafts.original_draft_id), session_token="other")
    for draft_id in ("draft-t-9", other.original_draft_id, ""):
        with pytest.raises(LayoutMoveError) as error:
            drafts.apply_moves(draft_id, [PoseChange("bed", 3, 3)])
        assert error.value.code == "unknown_draft"
    assert drafts.draft_count == 1
    assert DraftSession(room([])).original_draft_id != DraftSession(room([])).original_draft_id


def test_unknown_locked_item_is_rejected_instead_of_silently_ignored() -> None:
    with pytest.raises(LayoutMoveError) as error:
        DraftSession(room([item("bed", 2, 2)]), ["wardrobe"])
    assert error.value.code == "unknown_item"


def test_error_messages_truncate_untrusted_identifiers() -> None:
    drafts = session()
    with pytest.raises(LayoutMoveError) as error:
        drafts.apply_moves(drafts.original_draft_id, [PoseChange("x" * 5000, 1, 1)])
    assert len(str(error.value)) < 200


def test_unusable_geometry_is_a_safe_input_error_and_stores_nothing() -> None:
    drafts = session()
    with pytest.raises(SpatialInputError):
        drafts.apply_moves(drafts.original_draft_id, [PoseChange("bed", 1e300, 2)])
    assert drafts.draft_count == 1
    with pytest.raises(SpatialInputError):
        DraftSession(room([item("bed", 2, 2), item("bed", 5, 5)]))


def test_identical_arrangements_reuse_the_existing_draft_without_using_budget() -> None:
    scene = room([item("bed", 2, 2), item("desk", 6, 6)])
    drafts = DraftSession(scene, max_evaluations=1, session_token="t")
    assert drafts.evaluations_remaining == 1

    moved = drafts.apply_moves(drafts.original_draft_id, [PoseChange("bed", 3, 2, 90)])
    again = drafts.apply_moves(drafts.original_draft_id, [PoseChange("bed", 3, 2, 450)])
    back = drafts.apply_moves(moved.draft_id, [PoseChange("bed", 2, 2, -360)])
    assert again is moved and back.draft_id == drafts.original_draft_id
    assert (drafts.draft_count, drafts.evaluations_used, drafts.evaluations_remaining) == (2, 1, 0)

    with pytest.raises(LayoutMoveError) as error:
        drafts.apply_moves(drafts.original_draft_id, [PoseChange("bed", 4, 2)])
    assert error.value.code == "budget_exhausted" and drafts.draft_count == 2


def test_failed_evaluations_consume_the_shared_budget() -> None:
    drafts = DraftSession(room([item("bed", 2, 2)]), max_evaluations=1)
    with pytest.raises(SpatialInputError):
        drafts.apply_moves(drafts.original_draft_id, [PoseChange("bed", 1e300, 2)])
    assert drafts.evaluations_remaining == 0
    assert DraftSession(room([item("bed", 2, 2)])).evaluations_remaining is None
    with pytest.raises(SpatialInputError):
        DraftSession(room([item("bed", 2, 2)]), max_evaluations=-1)
