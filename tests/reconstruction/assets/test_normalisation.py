from __future__ import annotations

import io
import json
import struct
from pathlib import Path

import numpy as np
import pytest
import trimesh
from PIL import Image
from test_reconstruction import EVIDENCE, MeshDouble, masked_scene

from contracts.schema import GLB_BBOX_TOLERANCE_M, BBoxM, FurnitureItem, Pose2D
from services.reconstruction.assets.collision_templates import template_parts
from services.reconstruction.assets.models import FurnitureAsset
from services.reconstruction.assets.normalisation import (
    MAX_TEXTURE_PX,
    NormalisationError,
    normalise_mesh,
)
from services.reconstruction.assets.proxies import CATEGORY_SIZE_M, KnownDimensions, proxy_asset
from services.reconstruction.assets.reconstruct_items import main
from services.reconstruction.assets.reconstruction import reconstruct_furniture

MOCK_SCENE = Path(__file__).parents[3] / "contracts" / "mock_room" / "mock_scene.json"


def raw_box(tmp_path: Path, extents=(1.0, 0.5, 0.6), offset=(3.0, -2.0, 5.0), name="raw.glb"):
    """A provider-like mesh: unit-scaled, nowhere near the origin."""
    box = trimesh.creation.box(extents=extents)
    box.apply_translation(offset)
    path = tmp_path / name
    path.write_bytes(box.export(file_type="glb"))
    return path


def stored(tmp_path: Path, glb_url: str) -> bytes:
    assert glb_url.startswith("/api/reconstruction/assets/")
    return (tmp_path / "assets" / glb_url.rsplit("/", 1)[1]).read_bytes()


def scene_of(glb: bytes) -> trimesh.Scene:
    return trimesh.load_scene(io.BytesIO(glb), file_type="glb")


def gltf_json(glb: bytes) -> dict:
    return json.loads(glb[20 : 20 + struct.unpack("<I", glb[12:16])[0]])


def assert_fits(glb: bytes, bbox: BBoxM) -> None:
    """The profile: bounds equal `bbox`, bottom-centre at the origin."""
    expected = [
        [-bbox.width / 2, 0, -bbox.depth / 2],
        [bbox.width / 2, bbox.height, bbox.depth / 2],
    ]
    assert np.abs(np.asarray(scene_of(glb).bounds) - expected).max() < GLB_BBOX_TOLERANCE_M


def test_unknown_size_scales_uniformly_from_the_category_height_and_asks(tmp_path: Path) -> None:
    result = normalise_mesh(
        raw_box(tmp_path), category="sofa", target_bbox=None, data_dir=tmp_path, front="+z"
    )
    height = CATEGORY_SIZE_M["sofa"][1]
    # 1.0 x 0.5 x 0.6 keeps its proportions: a guess, never a measurement.
    assert result.bbox_m == BBoxM(width=2 * height, height=height, depth=1.2 * height)
    assert result.correction_needed == ["dimensions"]
    assert_fits(stored(tmp_path, result.glb_url), result.bbox_m)


def test_known_dimensions_are_matched_exactly_without_a_correction(tmp_path: Path) -> None:
    target = BBoxM(width=2.0, height=1.0, depth=1.2)
    result = normalise_mesh(
        raw_box(tmp_path), category="sofa", target_bbox=target, data_dir=tmp_path, front="+z"
    )
    assert result.bbox_m == target and result.correction_needed == []
    assert_fits(stored(tmp_path, result.glb_url), target)
    again = normalise_mesh(
        raw_box(tmp_path), category="sofa", target_bbox=target, data_dir=tmp_path, front="+z"
    )
    assert again.glb_url == result.glb_url, "same input, same bytes: the URL is a content hash"


def test_a_shape_that_disagrees_with_stated_dimensions_asks_for_them(tmp_path: Path) -> None:
    target = BBoxM(width=2.0, height=1.0, depth=2.0)  # depth stretched 67% against the others
    result = normalise_mesh(
        raw_box(tmp_path), category="sofa", target_bbox=target, data_dir=tmp_path, front="+z"
    )
    assert result.bbox_m == target and result.correction_needed == ["dimensions"]
    assert_fits(stored(tmp_path, result.glb_url), target)
    near = BBoxM(width=2.0, height=1.0, depth=1.3)  # 8%: inside the 15% allowance
    assert not normalise_mesh(
        raw_box(tmp_path), category="sofa", target_bbox=near, data_dir=tmp_path, front="+z"
    ).correction_needed


def chair_like(tmp_path: Path, back_towards: tuple[float, float, float]) -> Path:
    """A seat with a tall back on one side; the front is the opposite side."""
    seat = trimesh.creation.box(extents=[0.6, 0.4, 0.6])
    back = trimesh.creation.box(extents=[0.1, 0.5, 0.1])
    back.apply_translation(np.array([0, 0.45, 0]) + 0.25 * np.array(back_towards))
    path = tmp_path / "chair.glb"
    path.write_bytes(trimesh.util.concatenate([seat, back]).export(file_type="glb"))
    return path


@pytest.mark.parametrize(
    ("front", "back_towards"),
    [("+z", (0, 0, -1)), ("-z", (0, 0, 1)), ("+x", (-1, 0, 0)), ("-x", (1, 0, 0))],
)
def test_the_stated_front_is_turned_to_plus_z(tmp_path: Path, front, back_towards) -> None:
    result = normalise_mesh(
        chair_like(tmp_path, back_towards),
        category="chair",
        target_bbox=None,
        data_dir=tmp_path,
        front=front,
    )
    assert "orientation" not in result.correction_needed
    mesh = scene_of(stored(tmp_path, result.glb_url)).to_geometry()
    top = mesh.vertices[mesh.vertices[:, 1] > 0.9 * result.bbox_m.height]
    assert top[:, 2].max() < 0, "the back is behind the centre, so the front faces +Z"
    assert abs(top[:, 0].mean()) < 1e-6
    assert mesh.is_winding_consistent and mesh.volume > 0, "turned, not mirrored"


def test_an_unknown_front_keeps_the_mesh_as_given_and_asks_for_orientation(tmp_path: Path) -> None:
    result = normalise_mesh(
        chair_like(tmp_path, (1, 0, 0)), category="chair", target_bbox=None, data_dir=tmp_path
    )
    assert set(result.correction_needed) == {"dimensions", "orientation"}
    mesh = scene_of(stored(tmp_path, result.glb_url)).to_geometry()
    top = mesh.vertices[mesh.vertices[:, 1] > 0.9 * result.bbox_m.height]
    assert top[:, 0].min() > 0


def test_node_transforms_are_baked_into_the_vertices(tmp_path: Path) -> None:
    scene = trimesh.Scene()
    transform = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])  # lying on its back
    transform[:3, 3] = [4, 5, 6]
    scene.add_geometry(trimesh.creation.box(extents=[1.0, 0.6, 0.5]), transform=transform)
    scene.add_geometry(
        trimesh.creation.box(extents=[0.2, 0.2, 0.2]),
        transform=trimesh.transformations.translation_matrix([4, 5, 6]),
    )
    path = tmp_path / "nested.glb"
    path.write_bytes(scene.export(file_type="glb"))
    target = BBoxM(width=2.0, height=1.0, depth=1.2)  # the rotated box is 1.0 x 0.5 x 0.6
    result = normalise_mesh(
        path, category="other", target_bbox=target, data_dir=tmp_path, front="+z"
    )
    glb = stored(tmp_path, result.glb_url)
    assert_fits(glb, target)
    assert not result.correction_needed
    document = gltf_json(glb)
    for node in document["nodes"]:
        assert not {"matrix", "translation", "rotation", "scale"} & node.keys()
    assert not {"skins", "animations", "cameras"} & document.keys()


def textured(tmp_path: Path, size: int) -> Path:
    box = trimesh.creation.box(extents=[1.0, 0.5, 0.6])
    pixels = np.zeros((size, size, 3), np.uint8)
    pixels[: size // 2] = (200, 30, 30)
    box.visual = trimesh.visual.TextureVisuals(
        uv=np.random.default_rng(0).random((len(box.vertices), 2)),
        material=trimesh.visual.material.PBRMaterial(baseColorTexture=Image.fromarray(pixels)),
    )
    path = tmp_path / f"textured-{size}.glb"
    path.write_bytes(box.export(file_type="glb"))
    return path


@pytest.mark.parametrize("size", [256, 2048])
def test_textures_survive_and_are_capped(tmp_path: Path, size: int) -> None:
    result = normalise_mesh(
        textured(tmp_path, size), category="other", target_bbox=None, data_dir=tmp_path, front="+z"
    )
    mesh = scene_of(stored(tmp_path, result.glb_url)).to_geometry()
    texture = mesh.visual.material.baseColorTexture
    assert texture.size == (min(size, MAX_TEXTURE_PX),) * 2
    assert mesh.visual.uv is not None and len(mesh.visual.uv) == len(mesh.vertices)
    assert texture.convert("RGB").getpixel((2, 2)) == (200, 30, 30)


def test_unusable_or_over_budget_meshes_are_refused_and_nothing_is_stored(tmp_path: Path) -> None:
    garbage = tmp_path / "bad.glb"
    garbage.write_bytes(b"not a mesh")
    empty = tmp_path / "empty.glb"
    empty.write_bytes(trimesh.exchange.gltf.export_glb(trimesh.Scene()))
    dense = tmp_path / "dense.glb"
    dense.write_bytes(trimesh.creation.icosphere(subdivisions=6).export(file_type="glb"))  # 81,920
    flat = raw_box(tmp_path, extents=(1.0, 1.0, 0.001), name="flat.glb")
    for path in (garbage, empty, dense, flat, tmp_path / "missing.glb"):
        with pytest.raises(NormalisationError):
            normalise_mesh(path, category="other", target_bbox=None, data_dir=tmp_path, front="+z")
    assert not (tmp_path / "assets").exists()
    with pytest.raises(ValueError, match="category"):
        normalise_mesh(raw_box(tmp_path), category="spaceship", target_bbox=None, data_dir=tmp_path)


def test_templates_follow_the_shared_fixture_and_always_fit(tmp_path: Path) -> None:
    fixture = json.loads(MOCK_SCENE.read_text())
    checked = 0
    for item in fixture["furniture"]:
        if item["collision_source"] == "template" and item["collision_parts"]:
            parts = template_parts(item["category"], BBoxM(**item["bbox_m"]))
            got = [[round(v, 6) for v in p.model_dump().values()] for p in parts]
            want = [[round(v, 6) for v in p.values()] for p in item["collision_parts"]]
            assert sorted(got) == sorted(want), item["id"]
            checked += 1
    assert checked >= 2
    assert template_parts("sofa", BBoxM(width=2, height=0.8, depth=0.9)) == []
    # Too small for its template: one solid box, never an invalid part.
    assert template_parts("table", BBoxM(width=0.1, height=0.04, depth=0.1)) == []
    for category in ("desk", "table", "chair"):
        for bbox in (
            BBoxM(width=1.2, height=0.75, depth=0.6),
            BBoxM(width=0.3, height=0.2, depth=0.3),
        ):
            asset = proxy_asset(
                "vid-000001",
                "x",
                category,
                EVIDENCE,
                data_dir=tmp_path,
                known=KnownDimensions(bbox_m=bbox, source="measured"),
            )
            assert asset.collision_parts == template_parts(category, bbox) != []
            asset.to_item(Pose2D(x=0, z=0, yaw_deg=0))


def test_normalised_meshes_carry_template_parts(tmp_path: Path) -> None:
    result = normalise_mesh(
        raw_box(tmp_path), category="desk", target_bbox=None, data_dir=tmp_path, front="+z"
    )
    assert result.collision_source == "template"
    assert result.collision_parts == template_parts("desk", result.bbox_m) != []


def test_pipeline_serves_normalised_meshes_and_keeps_estimates_distinct(tmp_path: Path) -> None:
    masked_scene(tmp_path)
    known = KnownDimensions(bbox_m=BBoxM(width=2.0, height=1.0, depth=1.2), source="measured")
    result = reconstruct_furniture(
        "scene", data_dir=tmp_path, provider=MeshDouble(), dimensions={"vid-000001": known}
    )
    assert result.complete
    measured, guessed = (item.asset for item in result.items)
    assert measured.id == "vid-000001" and not measured.is_proxy
    assert measured.bbox_m == known.bbox_m and measured.dimension_source == "measured"
    assert measured.correction_needed == []
    assert not guessed.is_proxy and guessed.dimension_source == "estimated"
    assert "dimensions" in guessed.correction_needed
    for item in result.items:
        assert item.proxy.is_proxy and item.asset.glb_url != item.proxy.glb_url
        assert item.asset.evidence == item.proxy.evidence
        assert_fits(stored(tmp_path, item.asset.glb_url), item.asset.bbox_m)
        FurnitureItem.model_validate(item.asset.to_item(Pose2D(x=1, z=1, yaw_deg=90)))
    # Offline rerun: same stored raw meshes, same immutable URLs.
    again = reconstruct_furniture("scene", data_dir=tmp_path, dimensions={"vid-000001": known})
    assert [i.asset.glb_url for i in again.items] == [i.asset.glb_url for i in result.items]


def test_a_mesh_that_cannot_be_normalised_keeps_its_proxy_and_says_so(tmp_path: Path) -> None:
    masked_scene(tmp_path, two=False)
    dense = trimesh.creation.icosphere(subdivisions=6).export(file_type="glb")
    result = reconstruct_furniture("scene", data_dir=tmp_path, provider=MeshDouble(glb=dense))
    item = result.items[0]
    assert item.mesh is not None and item.asset is None and item.proxy.is_proxy
    assert not result.complete
    assert any("vid-000001" in w and "normalis" in w for w in result.warnings)
    # No mesh at all: nothing to normalise.
    masked_scene(tmp_path / "other", two=False)
    assert reconstruct_furniture("scene", data_dir=tmp_path / "other").items[0].asset is None


def test_cli_writes_the_normalised_asset_when_there_is_one(tmp_path: Path) -> None:
    masked_scene(tmp_path, two=False)
    reconstruct_furniture("scene", data_dir=tmp_path, provider=MeshDouble())
    out = tmp_path / "report"
    assert main(["--scene-id", "scene", "--data-dir", str(tmp_path), "--out", str(out)]) == 0
    assets = json.loads((out / "assets.json").read_text())
    asset = FurnitureAsset.model_validate(assets[0])
    assert not asset.is_proxy
    assert_fits(stored(tmp_path, asset.glb_url), asset.bbox_m)
    assert "Normalised mesh" in (out / "report.md").read_text()
