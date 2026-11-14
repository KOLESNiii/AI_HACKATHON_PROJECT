# Dev 2.1 fixture furniture

Two independently movable fixture assets so Dev 1, Dev 3 and Dev 4 can integrate before
real video extraction works. Regenerate the meshes with:

```
.venv/bin/python -I services/reconstruction/assets/fixtures/make_fixtures.py
```

| file | what it is |
|---|---|
| `vid-desk-01.glb` / `vid-chair-01.glb` | normalised proxy boxes — bottom-centre at origin, front `+Z`, metres |
| `manifest.json` | two `contracts.schema.FurnitureItem` records, validated in `tests/` |
| `evidence.json` | **proposed** evidence/provenance sidecar (see `../README.md` §2, §5) |

## Present

- Exact metric `bbox_m` matching the mesh bounds.
- Stable IDs following the agreed-pending format.
- Normalisation guarantee verified by assertion in the generator and by test.

## Deliberately not present

- Real geometry. These are labelled proxy boxes, the documented failure fallback — not
  reconstructed meshes.
- Real mask/frame evidence. `mask_url` and `bbox_px` are `null`; there is no source video
  for a fixture. Dev 1's alignment must tolerate null evidence on fixtures.
- Hosted `glb_url`s. Paths are repo-relative; swap for served URLs once reconstruction
  routes exist.
