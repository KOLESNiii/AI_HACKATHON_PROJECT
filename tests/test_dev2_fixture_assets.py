"""Dev 2.1: the fixture assets honour the contract and the normalisation invariant."""

import json
import pathlib

import pytest
import trimesh

from contracts.schema import FurnitureItem

FIXTURES = pathlib.Path("services/reconstruction/assets/fixtures")
MANIFEST = json.loads((FIXTURES / "manifest.json").read_text())
ITEM_IDS = [entry["id"] for entry in MANIFEST]


def test_manifest_holds_two_distinct_furniture_items() -> None:
    items = [FurnitureItem.model_validate(entry) for entry in MANIFEST]
    assert len(items) == 2
    assert len({item.id for item in items}) == 2


@pytest.mark.parametrize("entry", MANIFEST, ids=ITEM_IDS)
def test_mesh_is_normalised_to_metric_bounds(entry: dict) -> None:
    """CLAUDE.md rule 2: bbox bottom-centre at origin, front +Z, bbox_m exact."""
    item = FurnitureItem.model_validate(entry)
    mesh = trimesh.load(item.glb_url, force="mesh")
    lo, hi = mesh.bounds

    assert lo[1] == pytest.approx(0.0, abs=1e-6), "floor must sit at Y=0"
    assert (lo[0] + hi[0]) == pytest.approx(0.0, abs=1e-6), "X must be centred"
    assert (lo[2] + hi[2]) == pytest.approx(0.0, abs=1e-6), "Z must be centred"

    assert (hi[0] - lo[0]) == pytest.approx(item.bbox_m.width, abs=1e-6)
    assert (hi[1] - lo[1]) == pytest.approx(item.bbox_m.height, abs=1e-6)
    assert (hi[2] - lo[2]) == pytest.approx(item.bbox_m.depth, abs=1e-6)

    assert item.pose.yaw_deg == 0.0, "fixture front already faces +Z"


@pytest.mark.parametrize("entry", MANIFEST, ids=ITEM_IDS)
def test_every_item_has_evidence_and_dimension_provenance(entry: dict) -> None:
    """Proposed sidecar (issue #13 §2, §5): provenance must never be silently absent."""
    evidence = json.loads((FIXTURES / "evidence.json").read_text())
    record = evidence[entry["id"]]
    assert record["dimension_provenance"] in {"measured", "estimated", "catalog", "unknown"}
    assert record["frames"], "an asset must cite at least one source frame"
