"""Only canonical movable mesh assets may be copied by the chat harness."""

import json
import shutil

import pytest
from pydantic import ValidationError

from services.spatial_engine import library
from services.spatial_engine.chat import ChatRequest, add_item, chat
from services.spatial_engine.geometry import SpatialInputError
from tests.spatial_engine.test_agent import scene
from tests.spatial_engine.test_chat import Scripted, arguments

ASSET_ID = "ikea-50263838"


@pytest.fixture
def isolated_library(tmp_path, monkeypatch):
    asset = library.library_assets()[ASSET_ID]
    manifest = tmp_path / "catalog.json"
    item = asset.model_dump(exclude={"pose"})
    manifest.write_text(json.dumps([{"sku": ASSET_ID, "asset": item}]))
    (tmp_path / "assets").mkdir()
    model = tmp_path / "assets" / asset.glb_url.rsplit("/", 1)[1]
    shutil.copyfile(library.ASSET_ROOT / "assets" / model.name, model)
    monkeypatch.setattr(library, "CATALOG_PATH", manifest)
    monkeypatch.setattr(library, "ASSET_ROOT", tmp_path)
    return tmp_path, model


def test_library_uses_real_meshes_and_preserves_asset_evidence():
    assets = library.library_assets()
    assert assets
    assert len(assets) == 100
    for asset in assets.values():
        assert not asset.is_proxy and not asset.is_fixed
        assert asset.glb_url.startswith("/catalog/ikea/assets/")
    source = assets[ASSET_ID]
    before = source.model_dump()
    result = add_item(scene(), arguments(asset_id=source.id, x=4.5, z=2.0))
    copy = result.additions[0]
    assert copy.id != source.id
    assert copy.model_dump(exclude={"id", "pose"}) == source.model_dump(exclude={"id", "pose"})
    assert source.model_dump() == before
    assert "from Library" in result.text and "as a proxy" not in result.text


def test_missing_or_broken_files_are_excluded_without_a_proxy_fallback(isolated_library):
    _, model = isolated_library
    assert set(library.library_assets()) == {ASSET_ID}
    model.write_bytes(b"not a mesh")
    assert not library.library_assets()
    with pytest.raises(SpatialInputError, match="unavailable"):
        add_item(scene(), arguments())
    model.unlink()
    assert not library.library_assets()


@pytest.mark.parametrize("flags", [{"is_proxy": True}, {"is_fixed": True}])
def test_proxy_and_fixed_assets_are_not_available_even_with_a_glb_file(isolated_library, flags):
    root, _ = isolated_library
    manifest = root / "catalog.json"
    data = json.loads(manifest.read_text())
    item = data[0]["asset"]
    item.update(flags)
    manifest.write_text(json.dumps(data))
    assert not library.library_assets()
    with pytest.raises(SpatialInputError, match="unavailable"):
        add_item(scene(), arguments())


def test_outside_asset_symlinks_are_excluded(isolated_library, tmp_path):
    _, model = isolated_library
    outside = tmp_path.parent / f"{tmp_path.name}-outside.glb"
    outside.write_bytes(model.read_bytes())
    model.unlink()
    try:
        model.symlink_to(outside)
        assert not library.library_assets()
    finally:
        outside.unlink()


@pytest.mark.parametrize(
    "changes",
    [
        {"asset_id": "not-in-library"},
        {"asset_id": "/api/spatial_engine/proxies/1/1/1.glb"},
    ],
)
def test_unlisted_ids_and_proxy_urls_cannot_be_added(changes):
    with pytest.raises(SpatialInputError, match="Library asset_id"):
        add_item(scene(), arguments(**changes))


@pytest.mark.parametrize(
    "changes",
    [
        {"name": "Invented desk"},
        {"width_m": 0.1},
        {"glb_url": "/invented.glb"},
        {"is_proxy": False},
        {"bbox_m": {"width": 0.1, "height": 0.1, "depth": 0.1}},
    ],
)
def test_model_cannot_override_canonical_asset_metadata(changes):
    with pytest.raises(ValidationError):
        add_item(scene(), arguments(**changes))


def test_model_only_receives_the_canonical_library_and_allowed_ids():
    model = Scripted(arguments())
    chat(ChatRequest(scene=scene(), instruction="Add bedside drawers"), model)
    request = model.requests[0]
    payload = json.loads(request["messages"][0]["content"])
    assets = library.library_assets()
    assert {entry["asset_id"] for entry in payload["library"]} == set(assets)
    tool = next(tool for tool in request["tools"] if tool["name"] == "add_item")
    fields = tool["input_schema"]["properties"]
    assert set(fields["asset_id"]["enum"]) == set(assets)
    assert not {"name", "category", "width_m", "height_m", "depth_m", "glb_url"} & fields.keys()


def test_empty_library_does_not_offer_an_addition_tool(isolated_library):
    _, model_file = isolated_library
    model_file.unlink()
    model = Scripted("There are no available Library meshes to add.")
    result = chat(ChatRequest(scene=scene(), instruction="Add a desk"), model)
    assert not result.additions
    assert {tool["name"] for tool in model.requests[0]["tools"]} == {"rearrange_room"}
