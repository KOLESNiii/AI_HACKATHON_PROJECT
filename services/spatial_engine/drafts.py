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


def _arrangement(poses: tuple[PoseChange, ...]) -> tuple[tuple[str, float, float, float], ...]:
    """Identity of a layout: equal yaws modulo a full turn are the same arrangement."""
    return tuple((pose.item_id, pose.x, pose.z, pose.yaw_deg % 360 % 360) for pose in poses)


class DraftSession:
    """Drafts for one request. Not shared, persisted or reused across scene revisions.

    Only poses of known, movable furniture can change. Room data, dimensions, assets,
    fixed items and the caller's locked items are never altered. Stored drafts are
    never modified: accepted moves create a new draft, or return the existing draft
    when that exact arrangement was already evaluated.

    `max_evaluations` is one allowance for the whole request. Every attempted
    evaluation after the original consumes it, including one that fails.
    """

    def __init__(
        self,
        scene: RoomScene,
        locked_item_ids: Iterable[str] = (),
        *,
        near_window_item_ids: Iterable[str] = (),
        measure_brightness: bool = True,
        measure_feng_shui: bool = False,
        max_evaluations: int | None = None,
        session_token: str | None = None,
    ) -> None:
        if max_evaluations is not None and max_evaluations < 0:
            raise SpatialInputError("Evaluation budget must not be negative")
        self._measure_brightness = measure_brightness
        self._measure_feng_shui = measure_feng_shui
        self._original = scene.model_copy(deep=True)
        self._near_window_item_ids = tuple(near_window_item_ids)
        self._max_evaluations = max_evaluations
        self.evaluations_used = 0
        # Evaluating first rejects invalid geometry and duplicate IDs before they are indexed.
        evaluation = self._evaluate(self._original)
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
        self._by_arrangement: dict[tuple[tuple[str, float, float, float], ...], str] = {}
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
        self._by_arrangement[_arrangement(poses)] = draft_id
        return draft

    def _evaluate(self, scene: RoomScene) -> LayoutEvaluation:
        return evaluate_layout(
            self._original,
            scene,
            measure_brightness=self._measure_brightness,
            measure_feng_shui=self._measure_feng_shui,
            near_window_item_ids=self._near_window_item_ids,
        )

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

    @property
    def evaluations_remaining(self) -> int | None:
        """None means unlimited."""
        if self._max_evaluations is None:
            return None
        return max(0, self._max_evaluations - self.evaluations_used)

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

        Rejected requests raise `LayoutMoveError` and store no draft. A draft with
        collisions or other critical issues is still created, so that several items
        can be rearranged over successive drafts. An arrangement that was already
        evaluated returns its existing draft without using the budget; compare
        `draft_count` before and after to tell. `budget_exhausted` is raised once
        the request's evaluation allowance is spent.
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
        existing = self._by_arrangement.get(_arrangement(ordered))
        if existing is not None:
            return self._drafts[existing]
        if self.evaluations_remaining == 0:
            raise LayoutMoveError(
                "budget_exhausted", "No layout evaluations remain for this request"
            )
        self.evaluations_used += 1
        return self._store(base.draft_id, ordered, self._evaluate(self._scene_with(ordered)))
