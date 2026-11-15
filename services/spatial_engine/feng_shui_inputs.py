"""Shared Feng Shui inputs and validation, independent of the model harness."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from contracts.schema import AuditReport, RoomScene
from services.spatial_engine.geometry import SpatialInputError
from services.spatial_engine.report import audit_scene


class DetailModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Mirror(DetailModel):
    id: str = Field(min_length=1, max_length=100)
    x: float
    y: float = Field(ge=0)
    z: float
    width_m: float = Field(gt=0)
    height_m: float = Field(gt=0)
    normal_yaw_deg: float
    is_fixed: bool = True


class ActivityAnchor(DetailModel):
    item_id: str
    kind: Literal["seated", "headboard"]
    x: float
    z: float
    facing_yaw_deg: float


class FengShuiRequest(DetailModel):
    scene: RoomScene
    room_use: str = Field(default="unspecified", max_length=200)
    main_entry_door_id: str | None = None
    mirrors: list[Mirror] | None = Field(default=None, max_length=60)
    activities: list[ActivityAnchor] = Field(default_factory=list, max_length=120)
    observations: str = Field(default="", max_length=3000)
    """Optional observed beams, clutter, materials, lighting and other non-geometric context."""


def validate_feng_shui_request(request: FengShuiRequest) -> tuple[AuditReport, list[str]]:
    """Shared validation for the assessment and the score; returns the audit and object IDs."""
    scene = request.scene
    if len(scene.furniture) > 60:
        raise SpatialInputError("Feng shui assessments support at most 60 furniture items")
    # Validate the complete scene at the same boundary as the deterministic audit.
    audit = audit_scene(scene)
    item_ids = {i.id for i in scene.furniture}
    door_ids = {d.id for d in scene.doors}
    if request.main_entry_door_id is not None and request.main_entry_door_id not in door_ids:
        raise SpatialInputError("Unknown main entry door")
    if any(a.item_id not in item_ids for a in request.activities):
        raise SpatialInputError("Activity anchor references unknown furniture")
    ids = (
        [i.id for i in scene.furniture]
        + [d.id for d in scene.doors]
        + [w.id for w in scene.windows]
        + [w.id for w in scene.walls]
    )
    ids.extend(m.id for m in request.mirrors or [])
    if len(ids) != len(set(ids)):
        raise SpatialInputError("Assessment object IDs must be unique across object types")
    return audit, ids
