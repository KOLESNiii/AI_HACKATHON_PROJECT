# Architecture

The ownership and geometry rules in `ARCHITECTURE_DAG.md`, `CLAUDE.md`, and
`contracts/` remain the source of truth. Bootstrap preserves those contracts.

- `frontend/`: React 19, TypeScript, Vite running with Bun. Three.js, R3F, Drei,
  Zustand, Tailwind CSS and Framer Motion support the planned editor.
- `services/reconstruction/` (8001): floor-plan/video parsing and mesh reconstruction.
- `services/spatial_engine/` (8002): geometry audit and layout solver.
- `services/media_gen/` (8003): product search and generated imagery/video.
- `contracts/`: existing Python and TypeScript room models and mock fixture;
  coordinate changes with the team before editing.
- `tests/`: API smoke tests. Each service can add tests in its own directory later.

Each service owns its FastAPI app and routes. Domain endpoints must import the
existing Pydantic models from `contracts.schema`. Reconstruction and media expose
health only; the spatial service implements `POST /audit` as described below.
Operational `GET /health` returns
`{"status":"ok","service":"<service folder>"}` and checks process liveness only.
All services expose OpenAPI at `/openapi.json` and Swagger UI at `/docs`.

The development frontend sends `/api/<service folder>/health`; Vite strips that
prefix and proxies to the service port. Failed requests appear as unavailable in
the UI. No authentication or persistence is implemented. Production hosting must
supply equivalent reverse-proxy routing for `/api/`; Vite's proxy is development only.
CORS allows all origins per the existing hackathon rules, without credentials.

Python uses a root uv project, a reproducible lockfile, and optional service extras.
Provider keys belong in root `.env`, loaded by the service launch commands.
`FAL_KEY`, `LINKUP_API_KEY`, and `TAVILY_API_KEY` are reserved for later integrations;
no provider calls are made yet. Never place secrets in frontend `VITE_` variables.

Frontend and service directories can be developed independently. Coordinate
changes to root manifests, lockfiles, proxy routing, and shared contracts.


## Workstream ownership

`ARCHITECTURE_DAG.md` defines the revised four-person execution plan: Dev 1 owns
room geometry and scene assembly, Dev 2 owns furniture extraction and catalog
assets, Dev 3 owns the editor and render maps, and Dev 4 owns audit/optimisation.
Dev 1 and Dev 2 share the reconstruction service through planned `room/` and
`assets/` module boundaries; Dev 1 owns its entry point. Catalog imports reuse
Dev 2's asset normalisation pipeline. Existing directories, ports and contracts
are unchanged. Photoreal integration is assigned after the validated-layout
milestone; generated video is stretch scope.

## Furniture evidence selection (#14)

`services/reconstruction/assets/selection.py` selects upright frames with decoded source
ordinals/PTS and uses an injected live or recorded discovery provider. `registry.py` uses
local SQLite transactions to retain IDs and cache recoverable provider requests; original
frames and local reports live in a configured runtime directory. No new HTTP route or
shared schema is introduced. The CLI defaults to offline sampling; live vision proposals
are explicitly review-required. A reviewed real-room recording provides reproducible replay.

`SelectionResult` retains multiple source identities; `object_evidence` adapts one source to
the fixed `AssetEvidence` without changing ordinal semantics or overloading `provider_pose`.
Meshes remain #16–#17, and Dev 1 still owns video-to-plan alignment and final placement.

## Furniture masks and placement evidence (#15)

`services/reconstruction/assets/segmentation.py` turns each registered item's selected views
into stored instance masks and cut-outs, recorded on the item in the same SQLite registry.

- Purpose: say which pixels of which source frame belong to each furniture ID, for Dev 1's
  alignment (#8) and mesh reconstruction (#16).
- Input: a scene ID whose registry holds #14 sightings, and the retained source frames.
  Output: a `SegmentationResult`; mask and cut-out PNGs under the runtime data directory;
  `object_evidence` fills `EvidenceFrame.mask_url` (data-directory relative) and `bbox_px`.
- Configuration: none offline (local GrabCut). The live provider is fal.ai
  `fal-ai/sam-3/image` with `FAL_KEY`, one request per frame, opt-in through the CLI's `--live`.
- Failure: a failed, rejected or budget-deferred mask is reported per item and view; items,
  IDs and stored masks are kept, and nothing raises past the pipeline. Saved requests are
  re-read on retry without a new charge.

No HTTP route, contract or dependency changes.

## Spatial audit API

`POST /audit` on port 8002 accepts `RoomScene` directly and returns `AuditReport`.
The editor uses `/api/spatial_engine/audit` through Vite. The request is read-only,
has no provider calls, and echoes the submitted scene ID/revision. Results combine
collisions, room containment, door obstruction, front clearance and a reachable
floor ratio using a 50 cm person and entry through any physically passable door.
Door swing obstruction is reported separately: clipping the swing arc does not
exclude an entry unless obstacles actually prevent passage through the doorway.

Scoring, glare and Feng Shui remain unimplemented. `overall_score`, `glare_alerts`
and `feng_shui` are nullable in both shared schemas. Consumers must display null
as unassessed, not zero/no issues. `glare_orientation_grounded` is also nullable:
null means glare was not assessed, true means assessed with grounded orientation,
and false means an assessment used the plan-normal/-Z fallback.
Scene input and geometry failures return HTTP 422 with a `detail` list containing
`loc`, `msg`, and `type`; raw input/context is omitted. Unexpected failures remain
server errors with generic structured details. Missing doors return a successful
partial report: `walkable_floor_ratio` is null and independent findings remain
available. Known but unusable/blocked entries produce a ratio of zero.

Audit requests build a request-local geometry context once, reusing item volumes,
walking projections, broad-phase bounds and free-floor geometry across checks.
It is rebuilt after each request and is never retained across scene revisions.

Scoring/optimisation, persistence and live editor wiring are separate work. No
`POST /solve` route exists yet. See the spatial README and Dev 3 handoff for examples.

## Editor play mode

`frontend/src/components/play/` owns human placement, the mannequin, first-person
camera and pointer-lock lifecycle. The editor supplies a ref with floor projection
and Play actions; DOM pointer capture supports dragging from the launcher into the
canvas. A valid drop places or relocates one human. Invalid/cancelled drops retain
the previous pose. The local Zustand mode, human pose and placement preview are
separate from `RoomScene`, never sent to services, and never bump scene revisions.

`frontend/src/lib/walk.ts` checks a 0.25 m-radius body against the usable floor
polygon and the existing collision-part projections below `WALK_HEADROOM_M`.
Movement uses short steps and axis sliding, with no physics dependency or backend
requests. The room perimeter remains closed, including at doorways. Placement and
Play entry share these checks; furniture edits can invalidate an existing placement.

Play switches to a separate camera at 1.6 m eye height and hides editing controls.
The complete room shell is visible. Escape, unexpected pointer-lock loss or window
focus loss saves the last human position/heading and restores the editor camera and orbit
target. Pointer-lock denial leaves the editor active with a retry message. Opening
a room resets the actor; component cleanup releases capture and held keys.

### Play lighting

`frontend/src/lib/lighting.ts` derives an illustrative sun, wall-aligned window
sources and up to four ceiling sources from the existing room geometry.
`PlayLighting` renders a shadow-casting directional sun and one shadow-casting
ceiling spotlight, with additional ceiling sources and window area lights as
unshadowed fill. The full room shell and furniture cast and receive shadows;
shadow-only door infills prevent sunlight from entering through missing adjacent
rooms. Window apertures are treated as exposed to the exterior. No surrounding
buildings, glazing transmission or astronomical location/date are modelled.

Inputs are local `PlayLightingSettings` (artificial percentage and time in hours)
plus `RoomScene`; outputs are renderer lights, a procedural reflection environment
and play-only material clones. GLTF geometry, textures and cached source materials
are left untouched. The shell receives neutral PBR materials; furniture keeps
its source PBR textures when available. Lighting and the walking/lighting-panel
substate remain outside `RoomScene`, revisions and audit requests. Opening another
room resets lighting to 50% and 14:00; exiting play retains it for that room.

L opens the lighting panel in place, clears movement and deliberately releases
pointer lock. `PlaySession` distinguishes this release from an unexpected loss.
Resume requests capture in a user gesture and preserves the camera. Denial leaves
the panel open with a retry message; Esc, blur, hidden document and room changes
clean up the session. Pending capture requests are guarded by room session and
request identity. No backend endpoints, credentials or new packages are needed.

Exposure stays fixed; natural sources are off at night and without valid windows.
The local 128-pixel environment updates at most five times per second while direct
lights follow slider input immediately. Reflection shapes and indirect fill are
approximations, including some fill leakage in concave rooms. There are no exact
furniture/mirror reflections or multi-bounce light transport. Daylight is a visual
preview and does not populate the unassessed glare fields in the spatial audit.
Shadow maps are cached while walking and invalidated when lighting or loaded
geometry changes. Play caps pixel ratio at 1.5; real GPU frame rate still depends
on source furniture complexity and the user's hardware.

## Backend-provided demo models

`services/reconstruction/demo_assets.py` owns demo binary routes on port 8001:

- `GET /mock-room/assets/<filename>.glb` reads the canonical furniture model directly
  from `contracts/mock_room/assets/`.
- `GET /mock-room/shells/<room_id>.glb` extracts the matching wall-prefix room from
  the shared three-floor JSON fixtures and uses the existing shell generator. Results
  are cached in memory per process; no shell files are written into the frontend.
- `GET /mock_room/<filename>.glb` serves the older single-room fixture meshes from
  `services/reconstruction/fixtures/mock_room/`.

`demo_room_scene(room_id)` (not a route) returns one demo room as the editor's `roomScene`
builds it: its walls and openings, the furniture standing inside it, and browser URLs for
the shell and models. Furniture alignment (#8) runs on these rooms so its output carries the
room IDs the editor uses.

Frontend scene adapters prepend `/api/reconstruction` to these URLs, using the
existing Vite proxy. Shared fixture JSON and geometry stay unchanged. Production
hosting must forward this prefix to the reconstruction service, as for its other APIs.
No provider keys or new configuration are required. Unknown models/rooms and paths
outside the fixture roots return 404; model-loader failures use the editor's existing
proxy-box/shell-error fallback. These named demo URLs use `Cache-Control: no-cache`.
Restart the reconstruction service after changing source fixture geometry to clear
the in-memory room/shell cache. The frontend's former copy/build script is removed.

## Home screen and intake presentation

The frontend starts at the local `home` screen, branded Refresh, before upload,
processing, room selection and editing. Framer Motion coordinates screen and
room-panel transitions using the existing dependency; processing still advances
on demo timers rather than reconstruction-job progress.

`Landscape` stays mounted for the app session and scrolls four pre-rendered WebP
panoramas on home/processing screens. Each panorama has two adjacent copies for a
seamless CSS transform loop; hidden panoramas pause, and reduced-motion preferences
pause the landscape animation. Home and floor-plan processing have distinct images;
room builds alternate between the other two. No landscape engine runs in the browser.

`frontend/scripts/generate-landscapes.ts` optionally regenerates the checked-in
images from the locally vendored MIT-licensed Shan Shui Inf engine, using fixed
seeds and headless Chromium. Set `CHROME_BIN` if Chromium is not in Playwright's
local cache. Image regeneration needs no provider keys and is not part of normal
setup or builds. Attribution/licenses accompany the vendored source and the public
landscapes; the vendored HTML is retained only for regeneration, not bundled at runtime.

## Individual furniture meshes and proxies (#16)

`assets/reconstruction.py` consumes the #14 registry and #15 masks, calling an injected
`MeshProvider` concurrently per item. It validates raw GLBs, writes them under the runtime
`meshes/` directory and attaches `MeshRecord`s transactionally while their mask is current.
Each result retains a labelled, dimensioned proxy and explicit typed failures; failed
replacements preserve a current stored mesh. The offline default never submits inference.

`FalSam3dProvider` uses `fal-ai/sam-3/3d-objects` with `FAL_KEY`, uploading one frame and mask
per item. It retains request handles in the existing namespaced SQLite request cache;
timeouts remain recoverable and submission uncertainty blocks duplicate charges. Downloads
are bounded to 20 MB over HTTPS from fal media hosts. A shared thread-safe request budget
caps new submissions. Provider pose metadata is attached to the corresponding evidence
frame. Raw meshes retain provider scale/orientation; canonical normalisation remains #17.

`assets/proxies.py` uses caller-supplied known dimensions or category estimates marked for
correction. `assets/asset_store.py` stores their GLBs by SHA-256 and supplies `asset_router`
for Dev 1 to mount at `/assets`; browser URLs include `/api/reconstruction`. This PR does
not mount the route or change shared schemas/manifests. `reconstruct_items` provides local
JSON/Markdown reports; see the asset README for configuration and retry commands.

## Furniture normalisation (#17, PR #54 review)

`assets/normalisation.py` fits raw meshes to metric bounds before serving them. Known
dimensions are matched exactly; unknown dimensions use the category height and require
correction. Retailer GLBs instead keep their metre-scale extents, still marked estimated
and requiring dimension correction. If any estimated side exceeds 3 times its category size, normalisation refuses
the mesh and reconstruction retains its proxy with a warning. Supplying dimensions allows
the stored raw mesh to be retried offline. Unused vertices are removed before fitting;
providers without a known front convention request an orientation correction.

**Handoff to Dev 4:** desk, table and chair proxies now use the same category-template
collision parts as normalised assets, rather than a solid bounding box. The audit should
consume these parts to preserve nesting and walking space. Other categories retain the
solid-box fallback. Shared collision contracts are unchanged. Pillow in the reconstruction
extra preserves textures; it was approved in the #17 design and changes the root manifest
and lockfile in PR #54. This review follow-up adds no dependencies.

## Scene assembly route (#9)

`GET /scenes/{scene_id}` on port 8001 (`services/reconstruction/scenes.py`) returns one room as a
contract `RoomScene`, ready for the editor and `POST /audit`:

- Input: a scene ID. Either a room of an uploaded floor plan (`<plan_id>-<room_id>`, the
  `ParsedRoom.scene.scene_id` from `POST /floor-plans`) or a demo-home room (`g-reception`).
- Output: the room's walls, openings and shell URL, and its furniture, one item per asset with
  its own pose and correction flags (`room/assemble.py` → `room/align.py`). Doors are put
  exactly on their walls first, so the audit accepts every room. `revision` is 0.
- Furniture: demo rooms place the fixture furniture through the same path as video furniture.
  An uploaded room bound to a video gets that video's furniture (#10, below); other uploaded
  rooms have none, with a warning. `get_furniture_source` is the seam.
- Warnings, such as why a room has no furniture, are in the `X-Reconstruction-Warnings`
  response header (a JSON list, exposed to CORS); the body stays a contract model. How each
  pose was decided is not exposed.
- Failure: unknown scene IDs return 404; a failing furniture source gives the room without
  furniture and a warning, and a failing placement observer gives the default layout and a
  warning. Such a scene is not kept: the next request retries. Complete scenes are assembled
  once and kept in memory with their plan (`Cache-Control: no-cache`, because furniture
  changes as meshes arrive). No keys needed.

**Handoff to Dev 3.** The editor can load rooms from the backend instead of assembling them in
`frontend/src/data/demoHome.ts`. A sketch of the swap, keeping the local fixture as a fallback:

```ts
export async function fetchRoomScene(roomId: string): Promise<RoomScene> {
  try {
    const res = await fetch(`/api/reconstruction/scenes/${encodeURIComponent(roomId)}`)
    if (res.ok) return (await res.json()) as RoomScene
  } catch {
    /* backend down: fall through */
  }
  return roomScene(roomId)
}
```

The response matches `roomScene(roomId)` (same IDs, shell and model URLs, fixture poses) except
that doors sit exactly on their walls. The editor still owns `revision` after load.

## Real-input room (#10)

The M1 room is real input end to end: the plan parser's own room for `examples/three_floor.png`
and the furniture Dev 2's pipeline extracts from the opening room (0-6 s) of
`examples/three_floor_3.mp4`.

| | |
|---|---|
| Scene ID | `plan-83a12322e933-floor-0-room-3`, "Reception Room / Kitchen (1)" (an open archway merges the two; the plan warns) |
| Binding | `services/reconstruction/room/fixtures/real_rooms.json`: scene ID, plan, video, Dev 2's furniture scene `reviewed-opening-room`, the room's 18 wall lengths, and a reviewed hint per item |
| Source | `room/video_furniture.RealRoomFurniture`, the default `get_furniture_source`. Calls Dev 2's `reconstruct_furniture` **offline** (stored results only, never a provider request) |
| Items | `vid-000001` table, `vid-000002` rear sofa, `vid-000003` right sofa, `vid-000004` office chair: the IDs frame selection allocates on the real video. Dev 2's IDs, names and evidence (masks included) |
| Meshes | The item's normalised mesh (#17) when the pipeline has one; otherwise Dev 2's labelled proxy: a box of the item's size with a dark front strip, `is_proxy: true`, `dimension_source: "estimated"`, `"dimensions"` in `correction_needed`. The offline runbook below makes no meshes, so all four are proxies |
| Placement | From the binding's hints (confidence 0.6-0.7), so every item also has `placement` in `correction_needed` |
| Files | `GET /assets/<sha256>.glb` (browser `/api/reconstruction/assets/...`), Dev 2's content-addressed store, cached as immutable. Other names are 404 |
| Data | `$FURNITURE_DATA_DIR`, default `artifacts/furniture` in the repository (Dev 2's CLI default) |

Until the pipeline has run for the video, the room comes back alone with the warning "No
furniture extracted for this room yet". While frame selection is still storing items, it comes
back with the items so far and "furniture still being extracted: no ... yet". Neither is kept:
the next request looks again. Once every hinted item is there, the scene is kept in memory
until restart (re-running the pipeline needs a restart; a persistent cache is #12).

The scene ID only names the plan image. Parsed without its labels (no `FAL_KEY`, or the label
call fails), the same image gives a different room under the same ID ("Unlabelled space 4",
11 walls). The source checks the room's walls against the binding (same IDs, lengths within
5 % or 5 cm) and otherwise places no furniture, with a warning saying the geometry does not
match and naming the difference.

The first audit of the room reports two things the user can fix by moving furniture: the chair
stands in the swing of the entrance door (`blocked_doors`: `door0` by `vid-000004`), and the
table is 0.19 m in front of the rear sofa (a `clearance_issue`). Moving the chair against the
east wall clears the door; dragging the table onto the sofa adds a collision.

**Handoff to Dev 3 (#25).** Load the room with the fetch above
(`/api/reconstruction/scenes/plan-83a12322e933-floor-0-room-3`, after the plan is uploaded),
draw `is_proxy` items as labelled boxes (name plus "proxy"), and after each move POST the
edited scene with `revision + 1` to `/api/spatial_engine/audit`, ignoring reports for older
revisions. Show the `X-Reconstruction-Warnings` list. **Dev 4 (#32):** the audit accepts this
room as is; the findings above are the expected baseline. **Dev 2 (#18):** item IDs and the
`glb_url`s pass through unchanged; an item's normalised mesh (`ItemReconstruction.asset`)
replaces its proxy as soon as the pipeline stores one.
