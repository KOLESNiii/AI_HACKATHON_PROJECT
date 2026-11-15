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

Plans are cached in memory by `plan_id`, which is a hash of the image bytes. Plans published
in the scene cache (#12, below) are in that cache from startup.

Walkthrough videos are optional: up to `MAX_ROOM_VIDEOS` may be posted with the plan
(`curl -F files=@plan.png -F videos=@a.mp4 -F videos=@b.mov ...`). They are saved as
`<upload dir>/<plan_id>/videos/<sha256[:16]>.<ext>` (`$RECONSTRUCTION_UPLOAD_DIR`, default
`artifacts/uploads`), at most 500 MB each, and their furniture is **extracted live with fal.ai
in the background** (`video_jobs.py`; needs `FAL_KEY` and FFmpeg). The videos are cut up by room
so most of the work runs in parallel:

1. every video is sampled at once (32 frames each);
2. every frame is matched to a numbered plan room by fal vision, all 8-frame chunks at once,
   then smoothed per video by walkthrough continuity (rooms change through shared doors;
   `room_frames.py`). Whole-home walkthroughs are fine;
3. each room's frames (at most 16, spread over every video) are searched for furniture and
   its items cut out (SAM 3), all rooms at once (6 at a time), each in its own registry
   namespace. Batches within a room stay in order, so a sofa seen twice is one item; rooms
   cannot duplicate each other. Answers are read leniently (a mistaken answer is repaired,
   not discarded; batches that still fail are counted in the room's warnings);
4. SAM 3D meshes of a room's items when that room is first opened, as soon as that room has
   finished step 3, even while other rooms are still being searched.

Until a room's furniture is ready, `GET /scenes/<room>` returns the room without furniture, a
warning, `X-Furniture-Pending: true` and `X-Furniture-Progress`, and the editor polls. Then the
items are placed by the vision observer (`observe_vision.py`), flagged where it cannot tell.
Requests are capped per room, and every paid result is cached in the furniture data
directory, so re-uploading the same videos costs nothing. VGGT cameras/depth (probed in #14)
are not used: they are unscaled and not integrated.

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

## Real-input room (#10)

`fixtures/real_rooms.json` binds the parsed reception room of `examples/three_floor.png`
(`plan-83a12322e933-floor-0-room-3`) to the furniture Dev 2's pipeline extracts from
`examples/three_floor_3.mp4` (`reviewed-opening-room`), with a reviewed hint per item.
`video_furniture.RealRoomFurniture` reads that furniture offline from `$FURNITURE_DATA_DIR`
(default `artifacts/furniture`) and places it from the hints. Each item is its normalised mesh
(#17) when the pipeline has made one, otherwise a labelled proxy (the runbook below makes
none). When the data directory has nothing for the video, the furniture comes from Dev 2's
committed demo cache instead (#20): the four normalised meshes, with no pipeline run, so step 1
is optional (see `assets/README.md`, "validation and demo cache"). Runbook (needs FFmpeg; no
provider requests, no charges):

```bash
# 1. Furniture of the video: reviewed recording (#14) and GrabCut masks (#15), offline
uv run --extra reconstruction python -m services.reconstruction.assets.select_frames \
  examples/three_floor_3.mp4 --scene-id reviewed-opening-room --start 0 --end 6 --max-frames 8 \
  --data-dir artifacts/furniture --out /tmp/reviewed-furniture \
  --recorded tests/reconstruction/assets/fixtures/opening_room.reviewed.json
uv run --extra reconstruction python -m services.reconstruction.assets.segment_items \
  --scene-id reviewed-opening-room --data-dir artifacts/furniture --out /tmp/furniture-masks

# 2. Services (from the repository root)
uv run --extra reconstruction uvicorn services.reconstruction.main:app --port 8001
uv run --extra spatial uvicorn services.spatial_engine.main:app --port 8002

# 3. Load the room, audit it; edit a pose and audit again. The upload is optional for this
#    plan: the scene cache (#12) already holds it, and answers the upload without a provider.
curl -F files=@examples/three_floor.png localhost:8001/floor-plans > /dev/null
curl -D headers.txt -o scene.json localhost:8001/scenes/plan-83a12322e933-floor-0-room-3
curl -H 'Content-Type: application/json' -d @scene.json localhost:8002/audit

# 4. Corrections (#11): keep an edited scene (revision + 1), then correct the floor's scale
curl -X PUT -H 'Content-Type: application/json' -d @edited.json \
  localhost:8001/scenes/plan-83a12322e933-floor-0-room-3
curl -X POST 'localhost:8001/scenes/plan-83a12322e933-floor-0-room-3/scale?wall_id=w16&length_m=4.81&revision=1'
```

Tests parse the plan with the recorded labels (`fixtures/three_floor.annotations.json`). Live
labels (`FAL_KEY`) are expected to give the same room. Without labels the image parses into a
different room under the same scene ID: the binding's wall lengths (`walls_m`) catch that, and
the room comes back without furniture and a warning saying its geometry does not match. The
service itself no longer parses this plan: its scene cache (#12, below) holds the labelled
parse, so the paragraph applies when that cache is disabled or to another plan. A
partial inventory (selection still running) is shown but not kept. The wall check is on
shape, so the room keeps its furniture after a scale correction. The hints are the #8 reviewed `g-reception` hints moved onto
this room's walls (north-west corners aligned); `tests/test_real_room.py` fails if the parser's
wall IDs drift from them. The chair's hint lands in the entrance door's swing, which alignment
flags and the audit reports until the chair is moved.

## Demo scene cache (#12)

`scene_cache.py`. The real-input room loads on a fresh checkout with no upload, no `FAL_KEY`
and no network. `fixtures/scene_cache/plan-83a12322e933.json` holds the plan as parsed with its
recorded labels, and the room as assembled. When the service starts it restores every published
plan into the plan store (`routes.restore_plan`), as if the plan had been uploaded. From there
the room is an ordinary uploaded room:

- `GET /scenes/plan-83a12322e933-floor-0-room-3` assembles it through the usual path: pipeline
  furniture if `$FURNITURE_DATA_DIR` has any, else Dev 2's committed furniture cache (#20).
- The shell, `PUT /scenes/...` and `POST /scenes/.../scale` work as for any uploaded plan. The
  scale correction has the whole floor's original parse, because the whole plan is restored.
- Uploading `examples/three_floor.png` returns the restored plan without calling the label
  provider (a plan ID is the hash of the image bytes). The plan's `warnings` end with "from the
  published scene cache: recorded room labels, no provider used".
- A plan the service already has is never replaced by the cache.

The stored assembled scene is the published result; the service does not serve it directly.
`verify` and `tests/test_scene_cache.py` assemble the room again and compare (1 mm, 0.001°), so
a checkout that verifies serves exactly that scene.

```bash
# Fresh checkout, no keys: start both services, then
ID=plan-83a12322e933-floor-0-room-3
curl -D headers.txt -o scene.json localhost:8001/scenes/$ID        # 4 meshes, 18 walls
curl -o shell.glb localhost:8001/shells/$ID.glb
curl -H 'Content-Type: application/json' -d @scene.json localhost:8002/audit
# edit a pose in scene.json, set "revision": 1, then keep it and audit again
curl -X PUT -H 'Content-Type: application/json' -d @edited.json localhost:8001/scenes/$ID
curl -X POST "localhost:8001/scenes/$ID/scale?wall_id=w16&length_m=4.81&revision=1"

# Is the committed cache what this checkout reproduces? Offline, about 10 s.
uv run --extra reconstruction python -m services.reconstruction.room.scene_cache verify \
  --plan-id plan-83a12322e933 --images examples/three_floor.png \
  --annotations services/reconstruction/room/fixtures/three_floor.annotations.json
```

Checks. `publish` refuses, and `verify` reports, when:

| Check | Meaning |
|---|---|
| The cached scene is a room of the cached plan | Same scene ID; every field but `furniture` equals the plan room with its doors conformed; revision 0 |
| The assembly is complete | The furniture source and observer did not fail, and every hinted item is placed |
| Every item fits | No `AlignmentRecord` has `fits == False` |
| Delivered assets are unchanged | `delivery.check_placed`: ID, mesh URL, bounds and flags as Dev 2 published them |
| The shell builds | `shell.shell_glb` accepts the room |
| Reproduced (`verify` only) | The assembly, and with `--images` the parse, equal the published ones |

First audit of the published scene (estimates, flagged for correction): `door0` is blocked by
`vid-000003` and `vid-000004`; the table is 0.12 m in front of the rear sofa and the right sofa
0.37 m from it; no collisions, nothing out of bounds. Moving the chair to (3.9, 8.6) leaves
`door0` blocked by the right sofa only.

Limits:

- A cache file that is unreadable, misnamed or inconsistent is skipped with a logged reason
  (`scene cache skipped: ...`); its rooms are then unknown until the plan is uploaded. A repaired
  file takes effect at the next start.
- Corrections are not persisted. Kept poses and scale corrections live in memory, so a restart
  returns to the published scene.
- For this plan the label provider is never asked, even with `FAL_KEY` set. To parse it live,
  point `SCENE_DEMO_CACHE_DIR` at an empty directory, or use the debug CLI above, which never
  reads the cache.
- `SCENE_DEMO_CACHE_DIR` replaces the default directory (`fixtures/scene_cache`).
  `tests/conftest.py` points it at an empty one, so other tests parse for themselves.

## Corrections (#11)

`correct.py`, served by `PUT /scenes/{scene_id}` and `POST /scenes/{scene_id}/scale`
(`services/reconstruction/scenes.py`):

- `apply_pose_edit(kept, edit)`: the kept scene with the edit's poses. Only poses change (and
  flags the user cleared); moving clears `placement`, turning clears `orientation`.
  `StaleEdit` (409) for an old revision or other geometry, `InvalidEdit` (422) otherwise.
- `rescale_floor` / `rescale_room`: a floor at `factor` times its parsed size about its
  origin, at full precision. Plan lengths scale, heights do not; openings are clamped to their
  walls and doors conformed again; a changed room gets a new shell URL
  (`<scene_id>.<digest>.glb`). A room that would break the contract raises `InvalidScale`.
  `routes.prepare_floor_scale` takes the factor against the original parse
  (`routes._originals`), so corrections never compound; `routes.publish` serves the result.
- `carry_furniture(old, room)`: furniture keeps its fraction along its wall, its distance
  from it and its yaw. An item pushed out of a smaller room moves to the nearest spot where it
  fits with the same yaw (`align.nearest_fit`).

See [architecture](../../../docs/architecture.md#corrections-11) for the rules and handoffs.

## Scene assembly (#9)

`assemble.assemble_scene(room, source)` returns one room with its furniture placed, for
`GET /scenes/{scene_id}` (`services/reconstruction/scenes.py`). It conforms the doors to their
walls (`openings.conform_openings`, also applied by the parser), asks a `FurnitureSource` for
pose-less assets and an observer, places them with `align_assets`, and keeps the room's scene
ID, shell URL and openings. A failing source still gives the room, with a warning and
`Assembly.complete = False` (also set when the placement observer fails); the route does not
keep incomplete assemblies, so the next request retries.
Uploaded rooms bound to a video get its furniture (`video_furniture.RealRoomFurniture`, below);
others get `NoFurniture`. The demo home's source reuses its fixture furniture. See
[architecture](../../../docs/architecture.md#scene-assembly-route-9).

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
- The vision observer is not wired into a route (#9), and its answers are not persisted: the
  scene cache (#12) holds the room placed from the reviewed hints.
