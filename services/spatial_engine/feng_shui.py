"""Read-only, evidence-grounded feng shui assessment; no shared contract changes."""

import json
from typing import Literal

from pydantic import Field, ValidationError

from services.spatial_engine.agent import LayoutModel, ProviderError
from services.spatial_engine.feng_shui_inputs import (
    ActivityAnchor as ActivityAnchor,
)
from services.spatial_engine.feng_shui_inputs import (
    DetailModel,
)
from services.spatial_engine.feng_shui_inputs import (
    FengShuiRequest as FengShuiRequest,
)
from services.spatial_engine.feng_shui_inputs import (
    Mirror as Mirror,
)
from services.spatial_engine.feng_shui_inputs import (
    validate_feng_shui_request as validate_feng_shui_request,
)
from services.spatial_engine.feng_shui_skill import load_feng_shui_skill


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
    audit, ids = validate_feng_shui_request(request)
    result = FengShuiResult(
        scene_id=scene.scene_id, revision=scene.revision, outcome="assistant_unavailable"
    )
    if model is None:
        return result
    system = load_feng_shui_skill("assessment")
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
