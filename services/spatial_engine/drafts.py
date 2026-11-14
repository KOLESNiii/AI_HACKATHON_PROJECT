"""Request-local immutable layout drafts: pose-only edits audited against one original."""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from math import isfinite
from secrets import token_hex

from contracts.schema import RoomScene
from services.spatial_engine.geometry import SpatialInputError
from services.spatial_engine.objective import LayoutEvaluation, evaluate_layout

_ECHO_LIMIT = 64


class LayoutMoveError(SpatialInputError):
    """A rejected draft request. `code` is stable for tool feedback; the message is safe to show."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class PoseChange:
    """One item's requested floor pose, using the shared `Pose2D` conventions."""

    item_id: str
    x: float
    z: float
    yaw_deg: float = 0.0


@dataclass(frozen=True)
class LayoutDraft:
    draft_id: str
    parent_id: str | None
    """The draft these moves were applied to; None for the original layout."""
    poses: tuple[PoseChange, ...]
    """Every item's pose in this draft, sorted by item ID."""
    evaluation: LayoutEvaluation
    """Audit and metrics of this draft; movement is measured from the original layout.
    Critical issues are allowed here: check `metrics.passes_critical_checks` before proposing."""


def _echo(value: object) -> str:
    """Quote untrusted text for an error message without letting it grow unbounded."""
    return repr(str(value)[:_ECHO_LIMIT])


class DraftSession:
    """Drafts for one request. Not shared, persisted or reused across scene revisions.

    Only poses of known, movable furniture can change. Room data, dimensions, assets,
    fixed items and the caller's locked items are never altered. Stored drafts are
    never modified: every accepted set of moves creates a new draft.
    """

    def __init__(
        self,
        scene: RoomScene,
        locked_item_ids: Iterable[str] = (),
        *,
        session_token: str | None = None,
    ) -> None:
        self._original = scene.model_copy(deep=True)
        # Evaluating first rejects invalid geometry and duplicate IDs before they are indexed.
        evaluation = evaluate_layout(self._original, self._original, measure_brightness=True)
        item_ids = {item.id for item in self._original.furniture}
        locked = frozenset(locked_item_ids)
        unknown = sorted(locked - item_ids)
        if unknown:
            raise LayoutMoveError("unknown_item", f"Locked item {_echo(unknown[0])} is not known")
        self.fixed_item_ids = frozenset(i.id for i in self._original.furniture if i.is_fixed)
        self.locked_item_ids = locked
        # Draft IDs carry a per-session token so an ID from another request is never accepted.
        self._token = token_hex(4) if session_token is None else session_token
        self._drafts: dict[str, LayoutDraft] = {}
        poses = tuple(
            PoseChange(item.id, item.pose.x, item.pose.z, item.pose.yaw_deg)
            for item in sorted(self._original.furniture, key=lambda item: item.id)
        )
        self.original_draft_id = self._store(None, poses, evaluation).draft_id

    def _store(
        self, parent_id: str | None, poses: tuple[PoseChange, ...], evaluation: LayoutEvaluation
    ) -> LayoutDraft:
        draft_id = f"draft-{self._token}-{len(self._drafts)}"
        draft = LayoutDraft(draft_id, parent_id, poses, evaluation)
        self._drafts[draft.draft_id] = draft
        return draft

    def _scene_with(self, poses: tuple[PoseChange, ...]) -> RoomScene:
        """A fresh scene at the base revision, so its audit identifies the submitted scene."""
        by_id = {pose.item_id: pose for pose in poses}
        scene = self._original.model_copy(deep=True)
        for item in scene.furniture:
            pose = by_id[item.id]
            item.pose = item.pose.model_copy(
                update={"x": pose.x, "z": pose.z, "yaw_deg": pose.yaw_deg}
            )
        return scene

    @property
    def draft_count(self) -> int:
        return len(self._drafts)

    def draft(self, draft_id: str) -> LayoutDraft:
        found = self._drafts.get(draft_id) if isinstance(draft_id, str) else None
        if found is None:
            raise LayoutMoveError(
                "unknown_draft", f"Draft {_echo(draft_id)} does not exist in this request"
            )
        return found

    def scene(self, draft_id: str) -> RoomScene:
        """The draft as a new `RoomScene`; changing the returned copy affects nothing stored."""
        return self._scene_with(self.draft(draft_id).poses)

    def apply_moves(self, base_draft_id: str, moves: Sequence[PoseChange]) -> LayoutDraft:
        """Create and audit a new draft from `base_draft_id` with `moves` applied.

        Rejected requests raise `LayoutMoveError` and leave the session unchanged.
        A draft with collisions or other critical issues is still created, so that
        several items can be rearranged over successive drafts.
        """
        base = self.draft(base_draft_id)
        if not moves:
            raise LayoutMoveError("empty_moves", "At least one move is required")
        poses = {pose.item_id: pose for pose in base.poses}
        seen: set[str] = set()
        for move in moves:
            if move.item_id in seen:
                raise LayoutMoveError(
                    "duplicate_item", f"Item {_echo(move.item_id)} appears in more than one move"
                )
            seen.add(move.item_id)
            if move.item_id not in poses:
                raise LayoutMoveError("unknown_item", f"Item {_echo(move.item_id)} is not known")
            if move.item_id in self.fixed_item_ids:
                raise LayoutMoveError(
                    "fixed_item", f"Item {_echo(move.item_id)} is part of the room and cannot move"
                )
            if move.item_id in self.locked_item_ids:
                raise LayoutMoveError(
                    "locked_item", f"Item {_echo(move.item_id)} is locked by the user"
                )
            if not all(isfinite(value) for value in (move.x, move.z, move.yaw_deg)):
                raise LayoutMoveError(
                    "non_finite_pose", f"Pose for item {_echo(move.item_id)} must be finite numbers"
                )
            poses[move.item_id] = PoseChange(
                move.item_id, float(move.x), float(move.z), float(move.yaw_deg)
            )
        ordered = tuple(poses[item_id] for item_id in sorted(poses))
        evaluation = evaluate_layout(
            self._original, self._scene_with(ordered), measure_brightness=True
        )
        return self._store(base.draft_id, ordered, evaluation)
