# Floor-plan parser (Dev 1)

Turns floor-plan images into contract geometry: every floor and every room, each room as a
`RoomScene` (`furniture == []`) inside a `ParsedFloorPlan` (`contracts/schema.py`).

## How it works

Hybrid: OpenCV does all the geometry; a vision LLM only reads text.

| Step | Module | What it does |
|---|---|---|
| 1 | `raster.py` | Resample to 2000 px, flatten lighting (photographed printouts), threshold. Keep strokes of wall thickness; drop text, hatching, door leaves, glazing and furniture symbols. |
| 2 | `annotate.py` | Vision LLM on fal.ai reads room labels with printed metric dimensions, floor captions and the compass. Returns JSON only; never geometry. |
| 3 | `regions.py` | Doors and windows are gaps in the walls. Wall ends cast rays along their wall (or pair up across bay corners) to bridge each gap. Long bridges count only if glazing lines run along them. Rooms = enclosed free space; floors = connected wall masses. |
| 4 | `parse.py` | Scale per floor from labelled rooms whose two printed dimensions agree (median); second gap pass with metric door/window limits; merge slivers (stair treads, wardrobes, partitions); assign captions to floors. |
| 5 | `polygon.py` | Room contour → straightened polygon (snapped to 45° multiples), contract winding. |
| 6 | `openings.py` | Bridges → walls. Glazed exterior gap = window; anything else = door. Hinge and swing side come from the drawn leaf. |
| 7 | `shell.py` | `RoomScene` → shell `.glb`: floor slab (top at Y=0), ceiling, one `wall_<id>` node per wall with door/window openings cut. Walls stand on the interior face and extend outward; corners are mitred so 45° bays, reflex corners and mixed thicknesses close cleanly. |

Each floor has its own frame: metres, origin at the floor's top-left wall bound, +X right,
+Z down the image. All rooms on a floor share it.

## Use

```bash
# API (port 8001): POST images, then fetch the plan or one room
curl -F files=@examples/one_floor.jpg localhost:8001/floor-plans
curl localhost:8001/floor-plans/<plan_id>
curl localhost:8001/floor-plans/<plan_id>/rooms/<room_id>     # -> RoomScene
curl -o room.glb localhost:8001/shells/<scene_id>.glb         # the scene's shell_glb_url

# Debug CLI: plan.json plus a render of the returned geometry per floor
uv run python -m services.reconstruction.room examples/three_floor.png --out /tmp/plan \
    --annotations services/reconstruction/room/fixtures/three_floor.annotations.json [--shells]
```

`--shells` also writes each room's `.glb` and a per-floor section of the shells cut at 1 m
(walls as outlines, openings as gaps).

Plans are cached in memory by `plan_id`, which is a hash of the image bytes.

Configuration: `FAL_KEY` (required for labels). Optional: `FAL_VISION_ENDPOINT` (default
`fal-ai/any-llm/vision`) and `FAL_VISION_MODEL` (default `google/gemini-2.5-flash`). Without
a key, or if the call fails, rooms are still traced. Scale is then estimated from door widths
and every room carries `dimension_source = "estimated"` and `"dimensions"` in
`correction_needed`.

## Status and limits

- The fal call was verified live (`google/gemini-2.5-flash` via `fal-ai/any-llm/vision`,
  about 5-9 s per image). `fixtures/*.annotations.json` are its recorded output for the two
  example plans, so tests stay offline. Label positions are approximate (within the right
  room); geometry never depends on them beyond picking the room.
- Shells are built on first request and cached in memory with the plans (immutable: the
  scene ID comes from the image bytes). The ceiling sits at the tallest wall's height.
- Open archways wider than a door, with no glazing, are not split, so both rooms come out as
  one region (named `A / B`, with a warning). Stairs and landings can fragment.
- Photographed printouts are not perspective-corrected; mild keystone costs a few percent.
- Door hinge and swing are inferred from the drawn leaf. When no leaf is found, the room gets
  `"openings"` in `correction_needed`.

## Scene assembly (#9)

`assemble.assemble_scene(room, source)` returns one room with its furniture placed, for
`GET /scenes/{scene_id}` (`services/reconstruction/scenes.py`). It conforms the doors to their
walls (`openings.conform_openings`, also applied by the parser), asks a `FurnitureSource` for
pose-less assets and an observer, places them with `align_assets`, and keeps the room's scene
ID, shell URL and openings. A failing source still gives the room, with a warning.
`NoFurniture` is the default for uploaded rooms until #16; the demo home's source reuses its
fixture furniture. See [architecture](../../../docs/architecture.md#scene-assembly-route-9).

## Furniture alignment (#8)

`align.align_assets(scene, assets, observer, frames=None)` places Dev 2's pose-less
`FurnitureAsset`s in one room and returns `FurnitureItem`s plus an `AlignmentRecord` per asset ID.

| Module | What it does |
|---|---|
| `footprint.py` | Plan geometry in plain Python: collision by parts, room containment, door sweeps. Agrees with the spatial audit on every demo room. |
| `observe.py` | `PlacementHint`: where an asset was seen, relative to a wall (`along_frac`, `offset_m`, `facing`, `seated_at`). `NullObserver`, `FixedObserver`. |
| `observe_vision.py` | `FalVisionObserver`: shows a vision model the lettered plan and the evidence frames with each asset numbered, its #15 mask traced when available and its box otherwise. `selection_frames` / `directory_frames` supply frame pixels; `selection_masks` reads `EvidenceFrame.mask_url`. |
| `align.py` | Hints to poses. Impossible spots (outside the room, inside another item) move to the nearest possible one. Assets without a hint get a default spot: back to a wall, clear of doors, windows and front access. |
| `plan_view.py`, `align_debug.py` | Plan rendering and the debug CLI. |

Rules:

- Takes a single-room `RoomScene`: one the parser returns, or a demo room from
  `demo_assets.demo_room_scene(room_id)`, which builds the room exactly as the editor opens
  it (`g-reception`: walls with that prefix, the furniture inside, served shell and models).
- Furniture already in the scene is never moved, and an asset whose ID is already placed
  keeps its pose, so a re-run changes nothing the user touched.
- Nothing is dropped. An asset that fits nowhere is returned in the middle with `fits = False`.
- Uncertainty goes into `correction_needed`: `placement` and `orientation` for a default spot or
  a hint below 0.75 confidence; `orientation` when the front is unknown; `placement` when the
  item was moved more than 0.3 m to fit or stands in a door swing.
- A vision answer is capped at 0.7 confidence, so it is always flagged. Only reviewed hints
  can settle a pose.
- Records stay inside the service and link each pose to its `primary_frame_index`, which #15
  now points at a view with a usable mask when there is one.

```bash
# Default layout for the demo home's own furniture, compared with its poses
uv run python -m services.reconstruction.room align --demo all --out /tmp/align
#   or a floor (--demo ground) or rooms (--demo g-master f-bed4)

# The reception room of examples/three_floor_3.mp4 from reviewed hints
uv run python -m services.reconstruction.room align --demo g-reception --out /tmp/align \
    --assets services/reconstruction/room/fixtures/reception.assets.json \
    --hints services/reconstruction/room/fixtures/reception.hints.json

# Live (FAL_KEY): replace --hints with  --live --frames DIR [--masks DATA_DIR] [--save-hints FILE]
# Any single-room scene instead of a demo room:  --scene ROOM.json
```

Writes `<scene_id>.json` (the aligned room) and `<scene_id>.png` per room, and `records.json`.

Fixtures: `reception.assets.json` is the four demo reception items with Dev 2's reviewed boxes
(frames 0-150 of `three_floor_3.mp4`) as evidence, without masks, and the served demo model
URLs (`/api/reconstruction/mock-room/assets/...`). `reception.hints.json` was
reviewed by the coding agent against those frames, not measured and not human-verified.

Limits found in the live check (`fal-ai/any-llm/vision`, 10-20 s with `gemini-2.5-flash`,
about 95 s with `gemini-2.5-pro`):

- With boxes, both models misread the reception room: they put the camera at the wrong door,
  so the sofas land on the wrong walls, at a self-reported 0.9. Hence the confidence cap.
- With traced masks (offline GrabCut from the reviewed boxes), one flash run put the rear sofa
  on the reviewed wall and the other sofa still on the wrong one. One run, not a measurement.
- The reviewed hints follow the video and disagree with the demo poses for both sofas.
- `EvidenceFrame` has a mask reference but no image reference, so frame pixels come through a
  `FrameSource`.
- Not wired into a route (#9) and not persisted (#12).
