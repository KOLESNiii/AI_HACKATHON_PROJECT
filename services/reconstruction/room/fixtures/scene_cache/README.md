# Committed scene cache (#12)

Published floor plans that the reconstruction service knows from startup, with no upload,
provider, key or network. One file per plan, `<plan_id>.json`, written by
`python -m services.reconstruction.room.scene_cache publish`: the plan as parsed (`plan`) and
the assembled scene of each room bound to furniture (`scenes`). Do not edit a file by hand:
`verify` and `tests/test_scene_cache.py` assemble the room again and fail on any difference.

| File | Plan | Contents |
|---|---|---|
| `plan-83a12322e933.json` | `examples/three_floor.png`, 3 floors, 23 rooms | The parsed plan, and the assembled real-input room `plan-83a12322e933-floor-0-room-3` ("Reception Room / Kitchen (1)", 18 walls) with the four meshes of Dev 2's furniture cache (`vid-000001` table, `vid-000002` rear sofa, `vid-000003` right sofa, `vid-000004` office chair), 147 kB |

Provenance: published on 2026-11-15 from the committed image, the recorded room labels
`../three_floor.annotations.json` (a recording of the live fal vision answer), the hints in
`../real_rooms.json` and the furniture cache generation `g-5eb02891c8cd00a9` of
`reviewed-opening-room` (`../../../assets/fixtures/demo_cache/`). No provider request.

Regenerate after the parser, the aligner, the hints or the furniture cache change the room,
then commit the file:

```bash
uv run --extra reconstruction python -m services.reconstruction.room.scene_cache publish \
  examples/three_floor.png \
  --annotations services/reconstruction/room/fixtures/three_floor.annotations.json
uv run --extra reconstruction python -m services.reconstruction.room.scene_cache verify \
  --plan-id plan-83a12322e933 --images examples/three_floor.png \
  --annotations services/reconstruction/room/fixtures/three_floor.annotations.json
```

See `../../README.md`, "Demo scene cache (#12)".
