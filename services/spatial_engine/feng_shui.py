"""Read-only, evidence-grounded feng shui assessment; no shared contract changes."""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from contracts.schema import RoomScene
from services.spatial_engine.agent import LayoutModel, ProviderError
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


class Finding(DetailModel):
    object_ids: list[str] = Field(min_length=1, max_length=20)
    principle: str = Field(max_length=300)
    evidence: str = Field(max_length=1500)
    confidence: Literal["low", "medium", "high"]
    recommendation: str = Field(max_length=1500)


class Assessment(DetailModel):
    summary: str = Field(max_length=2000)
    findings: list[Finding] = Field(max_length=30)
    missing_information: list[str] = Field(max_length=30)


class FengShuiResult(DetailModel):
    scene_id: str
    revision: int
    outcome: Literal["completed", "assistant_unavailable"]
    assessment: Assessment | None = None


def assess_feng_shui(request: FengShuiRequest, model: LayoutModel | None) -> FengShuiResult:
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
    result = FengShuiResult(
        scene_id=scene.scene_id, revision=scene.revision, outcome="assistant_unavailable"
    )
    if model is None:
        return result
    skill = Path(__file__).with_name("skills") / "feng-shui" / "SKILL.md"
    system = skill.read_text().split("---", 2)[2].strip()
    payload = request.model_dump(mode="json")
    payload["spatial_audit"] = audit.model_dump(mode="json")
    try:
        reply = model.complete(
            system=system,
            messages=[{"role": "user", "content": json.dumps(payload, allow_nan=False)}],
            tools=[
                {
                    "name": "record_assessment",
                    "description": "Record evidence-backed findings and missing information.",
                    "input_schema": Assessment.model_json_schema(),
                }
            ],
            timeout_s=60.0,
        )
        if reply.stop_reason != "tool_use" or len(reply.tool_calls) != 1:
            return result
        call = reply.tool_calls[0]
        if call.name != "record_assessment":
            return result
        assessment = Assessment.model_validate(call.arguments)
        if any(set(f.object_ids) - set(ids) for f in assessment.findings):
            return result
    except (ProviderError, ValidationError, ValueError):
        return result
    return result.model_copy(update={"outcome": "completed", "assessment": assessment})
