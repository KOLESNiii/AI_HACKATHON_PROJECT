import json

import pytest
from fastapi.testclient import TestClient

from services.spatial_engine.agent import ModelReply, ToolCall
from services.spatial_engine.feng_shui import FengShuiRequest, assess_feng_shui
from services.spatial_engine.geometry import SpatialInputError
from services.spatial_engine.main import app, get_layout_model
from tests.spatial_engine.test_agent import scene


class RecordedModel:
    def __init__(self, object_id="wardrobe"):
        self.object_id = object_id

    def complete(self, **kwargs):
        self.request = kwargs
        return ModelReply(
            "tool_use",
            [],
            (
                ToolCall(
                    "a",
                    "record_assessment",
                    {
                        "summary": "Partial review",
                        "findings": [
                            {
                                "object_ids": [self.object_id],
                                "principle": "Access",
                                "evidence": "Front access is obstructed",
                                "confidence": "high",
                                "recommendation": "Review placement and re-audit",
                            }
                        ],
                        "missing_information": ["Mirror inventory unknown"],
                    },
                ),
            ),
            100,
        )


def test_payload_preserves_geometry_and_unknowns():
    model = RecordedModel()
    original = scene()
    before = original.model_dump()
    result = assess_feng_shui(FengShuiRequest(scene=original), model)
    assert result.outcome == "completed"
    payload = json.loads(model.request["messages"][0]["content"])
    assert payload["scene"] == before
    assert payload["mirrors"] is None
    assert payload["spatial_audit"]["scene_id"] == original.scene_id
    assert original.model_dump() == before
    assert model.request["timeout_s"] == 60


def test_unknown_references_and_missing_provider():
    assert assess_feng_shui(FengShuiRequest(scene=scene()), None).assessment is None
    assert (
        assess_feng_shui(FengShuiRequest(scene=scene()), RecordedModel("invented")).assessment
        is None
    )
    with pytest.raises(SpatialInputError):
        assess_feng_shui(FengShuiRequest(scene=scene(), main_entry_door_id="unknown"), None)


def test_route():
    app.dependency_overrides[get_layout_model] = lambda: RecordedModel()
    try:
        response = TestClient(app).post("/feng-shui", json={"scene": scene().model_dump()})
        assert response.status_code == 200
        assert response.json()["revision"] == 4
        assert response.json()["outcome"] == "completed"
    finally:
        app.dependency_overrides.clear()
