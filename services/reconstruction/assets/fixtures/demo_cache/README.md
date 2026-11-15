# Committed demo cache (#20)

Published furniture that loads with no provider, key or network. One folder per scene, written
by `python -m services.reconstruction.assets.demo_cache publish`: `CURRENT` names the published
generation, `g-<hex>/`, which holds `manifest.json` and the files. Do not edit the files by
hand: `manifest.json` lists each file's SHA-256, and a changed file makes the cache refuse to
load. After regenerating, run `prune` (with no service reading the cache), then commit the
new generation and `CURRENT`, and delete the replaced generation from git.

| Folder | Scene | Contents |
|---|---|---|
| `reviewed-opening-room-a68c301f/` | `reviewed-opening-room`, the opening room (0-6 s) of `examples/three_floor_3.mp4`, bound to the real-input room in `room/fixtures/real_rooms.json` | 4 normalised SAM 3D meshes (`vid-000001` table, `vid-000002` rear sofa, `vid-000003` right sofa, `vid-000004` office chair, 9,804-17,978 triangles each) and 15 SAM 3 masks, 4.97 MB |

Provenance: delivered on 2026-11-15 by `deliver_furniture` from registry revision 13 of a pipeline
run on the committed video (reviewed recording `tests/reconstruction/assets/fixtures/
opening_room.reviewed.json`, live SAM 3 and SAM 3D, see the #15-#17 sections of
`../../README.md`). Sizes are `estimated` and every item asks for a `"dimensions"` correction.
The item labelled office chair reconstructs as an armchair.

Regenerate after the pipeline changes the scene, then commit the folder:

```bash
uv run --extra reconstruction python -m services.reconstruction.assets.demo_cache publish \
  --scene-id reviewed-opening-room --data-dir artifacts/furniture
uv run --extra reconstruction python -m services.reconstruction.assets.demo_cache verify \
  --scene-id reviewed-opening-room
uv run --extra reconstruction python -m services.reconstruction.assets.demo_cache prune \
  --scene-id reviewed-opening-room
```

Retailer models are not committed here. They are third-party files: publish catalog scenes
(`--catalog`) into a local `FURNITURE_DEMO_CACHE_DIR` instead.
