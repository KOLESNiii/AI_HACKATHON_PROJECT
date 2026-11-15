"""Small dimensioned GLB box, without a reconstruction dependency."""

import json
import struct


def proxy_glb(width: float, height: float, depth: float) -> bytes:
    vertices = [
        (x, y, z)
        for y in (0, height)
        for z in (-depth / 2, depth / 2)
        for x in (-width / 2, width / 2)
    ]
    indices = [
        0,
        2,
        1,
        1,
        2,
        3,
        4,
        5,
        6,
        5,
        7,
        6,
        0,
        1,
        4,
        1,
        5,
        4,
        2,
        6,
        3,
        3,
        6,
        7,
        0,
        4,
        2,
        2,
        4,
        6,
        1,
        3,
        5,
        3,
        7,
        5,
    ]
    positions = struct.pack("<24f", *(v for point in vertices for v in point))
    binary = positions + struct.pack("<36H", *indices)
    document = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(positions)},
            {"buffer": 0, "byteOffset": len(positions), "byteLength": len(binary) - len(positions)},
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": 8,
                "type": "VEC3",
                "min": [-width / 2, 0, -depth / 2],
                "max": [width / 2, height, depth / 2],
            },
            {"bufferView": 1, "componentType": 5123, "count": 36, "type": "SCALAR"},
        ],
    }
    encoded = json.dumps(document, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 4)
    return (
        struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(encoded) + 8 + len(binary))
        + struct.pack("<II", len(encoded), 0x4E4F534A)
        + encoded
        + struct.pack("<II", len(binary), 0x004E4942)
        + binary
    )
