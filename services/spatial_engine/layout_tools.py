"""Validated layout-exploration tools for an agent.

The agent only proposes poses. This module validates every call, owns the shared
evaluation budget and remembers the best fully valid draft, so a final proposal
never depends on what the agent claims.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from shapely.errors import ShapelyError  # type: ignore[import-untyped]

from contracts.schema import LayoutGoal, RoomScene
from services.spatial_engine.drafts import DraftSession, LayoutDraft, LayoutMoveError, PoseChange
from services.spatial_engine.geometry import (
    SpatialInputError,
    door_swing_sector,
    room_floor_polygon,
    window_plan_segment,
)
from services.spatial_engine.objective import (
    NEAR_WINDOW_M,
    LayoutComparison,
    LayoutEvaluation,
    compare_evaluations,
)

DEFAULT_MAX_EVALUATIONS = 24
MAX_MOVES_PER_CALL = 32
MAX_COORDINATE_M = 1000.0
MAX_YAW_DEG = 3600.0
_ID_LIMIT = 64
_NAME_LIMIT = 40
_ERROR_LIMIT = 300

_CONVENTIONS = (
    "Units are metres in plan view: x is width, z is depth. An item's x/z is the centre of "
    "its footprint. yaw_deg rotates counter-clockwise seen from above: at 0 the item's front "
    "faces +z and its footprint spans width_m along x and depth_m along z; at 90 the front "
    "faces +x and the spans swap; 180 faces -z; 270 faces -x."
)

TOOL_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "name": "inspect_layout",
        "description": (
            "Return one draft's room geometry, furniture poses and sizes, current findings and "
            "metrics. Does not use the evaluation budget. " + _CONVENTIONS
        ),
        "input_schema": {
            "type": "object",
            "properties": {"draft_id": {"type": "string", "description": "A draft ID."}},
            "required": ["draft_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "evaluate_moves",
        "description": (
            "Create a new draft by applying pose changes to an existing draft, audit it, and "
            "return its findings, metrics and how it ranks against the original and the best "
            "draft so far. Items not listed keep their pose from the base draft. Only items "
            "marked movable may be listed, each at most once. A draft with collisions is still "
            "created and can be repaired in a later call, but only a draft whose "
            "passes_critical_checks is true can become the recommendation. Each new draft uses "
            "one evaluation from the shared budget. " + _CONVENTIONS
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "base_draft_id": {"type": "string", "description": "Draft to start from."},
                "moves": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": MAX_MOVES_PER_CALL,
                    "items": {
                        "type": "object",
                        "properties": {
                            "item_id": {"type": "string"},
                            "x": {"type": "number"},
                            "z": {"type": "number"},
                            "yaw_deg": {"type": "number"},
                        },
                        "required": ["item_id", "x", "z", "yaw_deg"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["base_draft_id", "moves"],
            "additionalProperties": False,
        },
    },
    {
        "name": "compare_layouts",
        "description": (
            "Rank the second draft against the first under the user's goal and report which "
            "metric decided it. Does not use the evaluation budget."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "first_draft_id": {"type": "string"},
                "second_draft_id": {"type": "string"},
            },
            "required": ["first_draft_id", "second_draft_id"],
            "additionalProperties": False,
        },
    },
)


@dataclass(frozen=True)
class LayoutPreferences:
    """What the user asked for, already validated by the server."""

    goal: LayoutGoal = "balanced"
    near_window_item_ids: tuple[str, ...] = ()


class _Arguments(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class _InspectArguments(_Arguments):
    draft_id: str = Field(max_length=_ID_LIMIT)


class _Move(_Arguments):
    item_id: str = Field(max_length=_ID_LIMIT)
    x: float = Field(ge=-MAX_COORDINATE_M, le=MAX_COORDINATE_M)
    z: float = Field(ge=-MAX_COORDINATE_M, le=MAX_COORDINATE_M)
    yaw_deg: float = Field(ge=-MAX_YAW_DEG, le=MAX_YAW_DEG)


class _EvaluateArguments(_Arguments):
    base_draft_id: str = Field(max_length=_ID_LIMIT)
    moves: list[_Move] = Field(min_length=1, max_length=MAX_MOVES_PER_CALL)


class _CompareArguments(_Arguments):
    first_draft_id: str = Field(max_length=_ID_LIMIT)
    second_draft_id: str = Field(max_length=_ID_LIMIT)


# Tool output uses plain names; a deciding metric always names a key of `metrics`.
_METRIC_NAMES = {
    "clearance_deficit": "front_clearance_deficit",
    "brightness_openness": "window_openness",
}


def _ranking(comparison: LayoutComparison) -> dict[str, Any]:
    metric = comparison.deciding_metric
    return {
        "outcome": comparison.outcome,
        "deciding_metric": None if metric is None else _METRIC_NAMES.get(metric, metric),
    }


def _num(value: float | None) -> float | None:
    return None if value is None else round(float(value), 4)


def _point(x: float, z: float) -> list[float | None]:
    return [_num(x), _num(z)]


def _metrics(evaluation: LayoutEvaluation) -> dict[str, Any]:
    metrics = evaluation.metrics
    return {
        "passes_critical_checks": metrics.passes_critical_checks,
        "critical_issue_count": metrics.critical_issue_count,
        "critical_violation_area_m2": _num(metrics.critical_violation_area_m2),
        "front_clearance_deficit": _num(metrics.clearance_deficit),
        "reachable_floor_ratio": _num(metrics.reachable_floor_ratio),
        "window_openness": _num(metrics.brightness_openness),
        "near_window_shortfall_m": _num(metrics.near_window_shortfall_m),
        "movement_m": _num(metrics.movement_m),
        "moved_item_count": metrics.moved_item_count,
    }


def _findings(evaluation: LayoutEvaluation) -> dict[str, Any]:
    report = evaluation.report
    return {
        "collisions": [
            {"item_a": c.item_a, "item_b": c.item_b, "overlap_area_m2": _num(c.overlap_area_m2)}
            for c in report.collisions
        ],
        "out_of_bounds_item_ids": list(report.out_of_bounds_item_ids),
        "blocked_doors": [
            {"door_id": b.door_id[:_ID_LIMIT], "blocked_by_item_id": b.blocked_by_item_id}
            for b in report.blocked_doors
        ],
        "front_clearance_issues": [
            {
                "item_id": c.item_id,
                "required_m": _num(c.required_m),
                "actual_m": _num(c.actual_m),
                "blocked_by_item_id": c.blocked_by_item_id,
            }
            for c in report.clearance_issues
        ],
    }


class LayoutToolbox:
    """The three exploration tools for one request, over one `DraftSession`.

    `call` never raises for anything the agent sent: bad names, arguments and
    moves come back as `{"ok": False, "error": {"code", "message"}}` so the agent
    can correct itself. Programming errors still propagate.
    """

    def __init__(
        self,
        scene: RoomScene,
        *,
        locked_item_ids: Iterable[str] = (),
        preferences: LayoutPreferences | None = None,
        max_evaluations: int = DEFAULT_MAX_EVALUATIONS,
        session_token: str | None = None,
    ) -> None:
        self.preferences = LayoutPreferences() if preferences is None else preferences
        self.session = DraftSession(
            scene,
            locked_item_ids,
            near_window_item_ids=self.preferences.near_window_item_ids,
            measure_brightness=(self.preferences.goal == "brighter"),
            max_evaluations=max_evaluations,
            session_token=session_token,
        )
        self.best_draft_id = self.session.original_draft_id
        """The best draft that passes critical checks and beats every earlier one under the
        user's goal. It stays the original until such a draft exists."""
        original = self.session.scene(self.session.original_draft_id)
        self._room = self._describe_room(original)
        self._items = {
            item.id: {
                "id": item.id,
                "name": item.name[:_NAME_LIMIT],
                "category": item.category,
                "width_m": _num(item.bbox_m.width),
                "depth_m": _num(item.bbox_m.depth),
                "height_m": _num(item.bbox_m.height),
                "needs_front_clear_m": _num(item.requires_front_clear_m),
                "movable": item.id not in self.session.fixed_item_ids
                and item.id not in self.session.locked_item_ids,
            }
            for item in original.furniture
        }
        self._handlers: dict[str, tuple[type[_Arguments], Callable[[Any], dict[str, Any]]]] = {
            "inspect_layout": (_InspectArguments, self._inspect_layout),
            "evaluate_moves": (_EvaluateArguments, self._evaluate_moves),
            "compare_layouts": (_CompareArguments, self._compare_layouts),
        }

    @property
    def improved(self) -> bool:
        return self.best_draft_id != self.session.original_draft_id

    @property
    def best_draft(self) -> LayoutDraft:
        return self.session.draft(self.best_draft_id)

    def call(self, name: object, arguments: object) -> dict[str, Any]:
        handler = self._handlers.get(name) if isinstance(name, str) else None
        if handler is None:
            return self._error("unknown_tool", "Unknown tool name")
        model, method = handler
        try:
            parsed = model.model_validate(arguments)
        except ValidationError as exc:
            details = "; ".join(
                f"{'.'.join(str(part) for part in error['loc']) or 'arguments'}: {error['msg']}"
                for error in exc.errors(include_input=False, include_context=False)[:3]
            )
            return self._error("invalid_arguments", details)
        try:
            result = method(parsed)
        except LayoutMoveError as exc:
            return self._error(exc.code, str(exc))
        except SpatialInputError as exc:
            return self._error("invalid_layout", str(exc))
        except (ValidationError, ShapelyError, ArithmeticError):
            return self._error("invalid_layout", "The proposed layout could not be evaluated")
        return {"ok": True, **result, **self._status()}

    def _status(self) -> dict[str, Any]:
        return {
            "best_draft_id": self.best_draft_id,
            "evaluations_remaining": self.session.evaluations_remaining,
        }

    def _error(self, code: str, message: str) -> dict[str, Any]:
        error = {"code": code, "message": message[:_ERROR_LIMIT]}
        return {"ok": False, "error": error, **self._status()}

    @staticmethod
    def _describe_room(scene: RoomScene) -> dict[str, Any]:
        walls = {wall.id: wall for wall in scene.walls}
        floor = room_floor_polygon(scene.floor_polygon)
        windows = []
        for window in scene.windows:
            (x0, z0), (x1, z1) = window_plan_segment(window, walls[window.wall_id]).coords
            windows.append(
                {
                    "id": window.id[:_ID_LIMIT],
                    "start": _point(x0, z0),
                    "end": _point(x1, z1),
                    "sill_height_m": _num(window.sill_height_m),
                    "head_height_m": _num(window.head_height_m),
                }
            )
        doors = []
        for door in scene.doors:
            swing = door_swing_sector(door, walls[door.wall_id], scene.floor_polygon)
            inside = swing.intersection(floor)
            bounds = None if inside.is_empty else [_num(value) for value in inside.bounds]
            doors.append(
                {
                    "id": door.id[:_ID_LIMIT],
                    "hinge": _point(door.hinge_pos.x, door.hinge_pos.z),
                    "width_m": _num(door.width_m),
                    "keep_clear_min_x_min_z_max_x_max_z": bounds,
                }
            )
        return {
            "floor_polygon": [_point(point.x, point.z) for point in scene.floor_polygon],
            "windows": windows,
            "doors": doors,
        }

    def _describe_draft(self, draft: LayoutDraft) -> dict[str, Any]:
        return {
            "draft_id": draft.draft_id,
            "is_original": draft.draft_id == self.session.original_draft_id,
            "findings": _findings(draft.evaluation),
            "metrics": _metrics(draft.evaluation),
        }

    def _inspect_layout(self, arguments: _InspectArguments) -> dict[str, Any]:
        draft = self.session.draft(arguments.draft_id)
        furniture = [
            {
                **self._items[pose.item_id],
                "x": _num(pose.x),
                "z": _num(pose.z),
                "yaw_deg": _num(pose.yaw_deg),
            }
            for pose in draft.poses
        ]
        return {
            **self._describe_draft(draft),
            "request": {
                "goal": self.preferences.goal,
                "near_window_item_ids": list(self.preferences.near_window_item_ids),
                "near_window_within_m": NEAR_WINDOW_M,
            },
            "room": self._room,
            "furniture": furniture,
        }

    def _evaluate_moves(self, arguments: _EvaluateArguments) -> dict[str, Any]:
        drafts_before = self.session.draft_count
        draft = self.session.apply_moves(
            arguments.base_draft_id,
            [PoseChange(move.item_id, move.x, move.z, move.yaw_deg) for move in arguments.moves],
        )
        already_evaluated = self.session.draft_count == drafts_before
        goal = self.preferences.goal
        original = self.session.draft(self.session.original_draft_id)
        versus_original = compare_evaluations(original.evaluation, draft.evaluation, goal)
        versus_best = compare_evaluations(self.best_draft.evaluation, draft.evaluation, goal)
        if draft.evaluation.metrics.passes_critical_checks and versus_best.outcome == "better":
            self.best_draft_id = draft.draft_id
        return {
            **self._describe_draft(draft),
            "already_evaluated": already_evaluated,
            "versus_original": _ranking(versus_original),
            "versus_previous_best": _ranking(versus_best),
            "is_best": draft.draft_id == self.best_draft_id,
        }

    def _compare_layouts(self, arguments: _CompareArguments) -> dict[str, Any]:
        first = self.session.draft(arguments.first_draft_id)
        second = self.session.draft(arguments.second_draft_id)
        comparison = compare_evaluations(first.evaluation, second.evaluation, self.preferences.goal)
        return {
            "second_versus_first": _ranking(comparison),
            "goal": self.preferences.goal,
            "first": _metrics(first.evaluation),
            "second": _metrics(second.evaluation),
        }
