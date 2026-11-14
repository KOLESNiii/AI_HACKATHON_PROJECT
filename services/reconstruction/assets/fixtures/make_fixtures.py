"""Generate the two Dev 2.1 fixture proxy meshes, normalised per CLAUDE.md rule 2."""
import pathlib

import trimesh

OUT = pathlib.Path("services/reconstruction/assets/fixtures")

FIXTURES = [
    ("vid-desk-01", dict(width=1.40, height=0.75, depth=0.70)),
    ("vid-chair-01", dict(width=0.52, height=0.95, depth=0.55)),
]

for obj_id, bbox in FIXTURES:
    mesh = trimesh.creation.box(extents=(bbox["width"], bbox["height"], bbox["depth"]))
    # Normalise: bbox bottom-centre -> (0, 0, 0). Front is +Z; a symmetric box needs no yaw.
    lo, hi = mesh.bounds
    mesh.apply_translation([-(lo[0] + hi[0]) / 2.0, -lo[1], -(lo[2] + hi[2]) / 2.0])
    lo, hi = mesh.bounds
    assert abs(lo[1]) < 1e-9, lo
    assert abs(lo[0] + hi[0]) < 1e-9 and abs(lo[2] + hi[2]) < 1e-9, (lo, hi)
    assert [round(v, 6) for v in (hi - lo)] == [bbox["width"], bbox["height"], bbox["depth"]]
    path = OUT / f"{obj_id}.glb"
    mesh.export(path)
    print(f"{path}  bounds_lo={lo.round(4).tolist()} bounds_hi={hi.round(4).tolist()}")
