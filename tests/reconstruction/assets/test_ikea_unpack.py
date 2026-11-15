"""Build-only codec checks; application/runtime installs do not need DracoPy."""

import io
import json
import struct

import numpy as np
import pytest
import trimesh


def test_unpack_preserves_draco_geometry_and_uvs() -> None:
    draco = pytest.importorskip("DracoPy")
    from scripts.cache_ikea_library import unpack_model

    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    uv = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    compressed = draco.encode(points, np.array([[0, 1, 2]], dtype=np.uint32), tex_coord=uv)
    attributes = draco.decode(compressed).attributes
    ids = {a["attribute_type"]: a["unique_id"] for a in attributes}
    document = {
        "asset": {"version": "2.0"},
        "buffers": [{"byteLength": len(compressed)}],
        "bufferViews": [{"buffer": 0, "byteLength": len(compressed)}],
        "accessors": [
            {"type": "SCALAR", "componentType": 5125, "count": 3},
            {"type": "VEC3", "componentType": 5126, "count": 3},
            {"type": "VEC2", "componentType": 5126, "count": 3},
        ],
        "meshes": [
            {
                "primitives": [
                    {
                        "attributes": {"POSITION": 1, "TEXCOORD_0": 2},
                        "indices": 0,
                        "extensions": {
                            "KHR_draco_mesh_compression": {
                                "bufferView": 0,
                                "attributes": {"POSITION": ids[0], "TEXCOORD_0": ids[3]},
                            }
                        },
                    }
                ]
            }
        ],
        "nodes": [{"mesh": 0}],
        "scenes": [{"nodes": [0]}],
        "scene": 0,
        "extensionsRequired": ["KHR_draco_mesh_compression"],
        "textures": [{"extensions": {"EXT_texture_webp": {"source": 0}}}],
    }
    header = json.dumps(document).encode()
    header += b" " * (-len(header) % 4)
    binary = compressed + b"\0" * (-len(compressed) % 4)
    raw = (
        struct.pack("<III", 0x46546C67, 2, 28 + len(header) + len(binary))
        + struct.pack("<II", len(header), 0x4E4F534A)
        + header
        + struct.pack("<II", len(binary), 0x004E4942)
        + binary
    )
    expanded = unpack_model(raw)
    size = struct.unpack_from("<I", expanded, 12)[0]
    result = json.loads(expanded[20 : 20 + size])
    assert result["textures"][0]["source"] == 0
    assert result["extensionsRequired"] == []
    assert "KHR_draco_mesh_compression" not in result["meshes"][0]["primitives"][0]["extensions"]
    # No image needed to verify geometry and UV accessors.
    result.pop("textures")
    mesh = next(iter(trimesh.load_scene(io.BytesIO(expanded), file_type="glb").geometry.values()))
    assert len(mesh.faces) == 1
    assert np.allclose(mesh.bounds, [[0, 0, 0], [1, 1, 0]], atol=0.001)
    accessor = result["accessors"][2]
    view = result["bufferViews"][accessor["bufferView"]]
    start = 20 + size + 8 + view["byteOffset"]
    restored_uv = np.frombuffer(expanded[start : start + view["byteLength"]], dtype="<f4").reshape(
        -1, 2
    )
    assert np.allclose(np.sort(restored_uv, axis=0), np.sort(uv, axis=0), atol=0.001)
