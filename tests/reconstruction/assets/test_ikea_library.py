"""The bundled retailer library must satisfy the same delivery checks as live imports."""

import json
from pathlib import Path

from services.reconstruction.assets.delivery import inspect_asset
from services.reconstruction.assets.models import AssetEvidence, EvidenceFrame, FurnitureAsset

ROOT = Path(__file__).resolve().parents[3]


def test_bundled_ikea_meshes_pass_delivery_checks() -> None:
    items = json.loads((ROOT / "frontend/src/data/ikeaCatalog.json").read_text())
    assert len(items) == 100
    for item in items:
        asset = FurnitureAsset(
            **item["asset"],
            evidence=AssetEvidence(
                frames=[EvidenceFrame(frame_index=0, timestamp_s=0)], primary_frame_index=0
            ),
        )
        check = inspect_asset(
            asset,
            data_dir=ROOT / "frontend/public/catalog/ikea",
            url_base="/catalog/ikea/assets",
        )
        assert not check.problems, (item["sku"], check.problems)
        assert not asset.is_proxy
