# Architecture

## Bundled retailer library

`scripts/cache_ikea_library.py` reads IKEA UK search and product pages through the
existing retailer parser, then uses the shared mesh normalizer and delivery checks.
Only products with published dimensions, a usable retailer mesh and a thumbnail
enter the balanced 100-product snapshot. Unsupported candidates are skipped; an
unfilled category fails the refresh. No paid provider or runtime service is needed.

Metadata and source evidence live in `frontend/src/data/ikeaCatalog.json`; bundled
content-addressed GLBs and thumbnails live in `frontend/public/catalog/ikea/`.
The Library displays local images and passes each complete asset through the existing
catalog addition path, preserving dimensions, collision templates and model URLs.
The spatial service reads the same snapshot for canonical agent additions.
Browsing and adding work offline. Prices and availability are snapshots, with links
to IKEA for current details. Refresh setup and ownership are in the asset notice.

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


## Frontend audio

`frontend/src/audio/` owns a native Web Audio mixer with music, effects and master
gain buses. One `SoundControls` instance lives outside screen transitions and
subscribes to typed semantic cues. Store actions emit cues after successful edits;
drag handlers emit once on completion, and unchanged/cancelled gestures are silent.
Effects are synthesized from original resonant tones and filtered noise, cached as
short buffers, capped at six voices, with rotation ticks throttled to 100 ms.

Two streamed HTML audio elements repeat the bundled `public/audio/reverie.mp3`
with a five-second equal-power crossfade. Navigation preserves playback; Play
reduces music by 25%. Music loading never gates the room UI. Failed music stops
retrying for that app session while effects remain available; unsupported audio
leaves the UI functional. Blocked autoplay retries on user gestures. Hidden tabs
pause media and suspend the context, and late playback results respect mute and
disposal. React Strict Mode cleanup removes subscriptions, timers and audio nodes.

A separate Zustand store saves validated audio preferences under
`spaceshift.audio.v1` in localStorage, tolerating disabled/corrupt storage. Defaults
are music 20%, effects 55%, both enabled. Audio preferences never enter `RoomScene`
or bump its revision. No service, API key, runtime dependency or backend contract
is added. Credits, source and reproducible asset preparation are in
`frontend/public/audio/NOTICE.md`.

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

Scoring and glare remain unimplemented; Feng Shui is a small rule-based placement metric.
`overall_score`, `glare_alerts` and `feng_shui` are nullable in both shared schemas.
Consumers must display null as unassessed, not zero/no issues. The richer rule-based
Feng Shui score is separately available at `/feng-shui/score`. `glare_orientation_grounded` is also nullable:
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

The editor calls this route on room load and after committed edits. Persistence
remains separate work. See the spatial README and Dev 3 handoff for examples.

## Layout suggestion API

`POST /solve` on port 8002 accepts `OptimiseRequest` and returns `LayoutProposal`.
It is the only spatial route that calls a provider: Claude Sonnet through the
official `anthropic` SDK (spatial extra), using `ANTHROPIC_API_KEY` and optional
`SPACESHIFT_LAYOUT_MODEL` from root `.env`. The model proposes furniture poses
through three validated tools; the service audits each draft, enforces fixed and
locked items and per-request limits, re-audits the best draft and returns it only
if it is valid and better. Assistant failures and limits are reported in the
response's `outcome` with HTTP 200, never as a clean or successful proposal;
invalid input is HTTP 422. Nothing is persisted and the editor's scene is not
changed. Details and limits are in the spatial README.

## Editor layout review and live Stats

`frontend/src/lib/agent.ts` sends the current `RoomScene` and the latest instruction
to the existing `/solve` route; tool execution and objective ranking stay on the
backend. The client bounds waiting to 120 seconds and never retries a solve
automatically. There is no conversation-history API, new dependency or shared
schema change. The server-side `ANTHROPIC_API_KEY` remains outside browser code.

The store retains a full proposal, its immutable base-scene snapshot and an optional
matching baseline audit. Chat renders a floor-plan diff and per-item translation,
rotation and measured before/after findings. Proposed scenes never replace the
current scene or Stats while awaiting a decision. Acceptance validates the complete
proposal again, requires the original room session and scene snapshot with no
active gesture, applies only known movable item poses, and increments the revision
once. Mesh URLs, sizes, IDs, fixed items and room geometry are preserved. Rejecting
only changes the proposal's review state. Editing invalidates earlier proposals.

`frontend/src/lib/editorServices.ts` owns one editor lifetime, across tabs and Play.
It fetches the canonical assembled room first (15-second timeout), preserving
warnings and falling back visibly to the local fixture on failure. Editing is
blocked while this initial load is pending. Live audit requests wait 250 ms after
committed edits, skip active gestures, and time out after 10 seconds. Room session,
scene identity and revision checks reject late results, including live drag poses
that have not yet changed the revision. Superseded requests and editor cleanup
abort browser fetches; abort does not guarantee server/provider cancellation.
Stats exposes loading/error/retry states and retains null as unassessed. Returned
Feng Shui assessments display directly when backend work populates them.

The left-hand version tree stores complete layout snapshots in local Zustand
state. The canonical room is the root. Manual commits update the working scene,
its audit revision and an unsaved-changes flag, without creating history nodes.
Ctrl+S/Cmd+S or Save version checkpoints all manual changes together; an accepted
agent proposal still saves immediately, including the reviewed working draft.
Each save appends to `currentVersionId` and selects its new child, so successive
saves are a linear chain. A fork appears only after selecting an ancestor with an
existing successor and saving a changed layout. Unchanged saves create no nodes.
The tree keeps single-successor paths aligned and indents only at forks.

Unsaved manual changes block version navigation until Save or Discard. Discard
restores the selected snapshot without creating a node. Selection restores furniture (including additions/deletions),
poses and metadata from the snapshot using a fresh monotonically increasing audit
revision. It creates no node, cancels pending agent/audit fetches, invalidates older
proposals and triggers a new audit. Every agent request captures the selected
version and current scene; acceptance checks both before creating its child.
Saving manual changes preserves scene identity/revision and the current audit,
but advances the selected version, cancelling an in-flight suggestion and making
older proposals stale. The shortcut also works while the chat input is focused;
active gestures and room loading cannot save a partial layout.
Version navigation is blocked during gestures, room loading and Play. History is
local to the open room and resets on a new room or page reload; there is no server
persistence or shared contract change.

## Library mesh collection

The frontend catalog derives its entries from the demo floor fixtures, excluding
fixed fixtures and proxies. Each entry retains the source model's dimensions,
collision parts, access rules and uncertainty metadata, and uses the existing
`/api/reconstruction/mock-room/assets/` route. No model files are copied and no new
backend route, provider call or dependency is needed. Unsupported mock retail
names/prices are replaced by the available room models, labelled estimated.

Adding an entry clones its asset metadata onto a fresh item ID and the chosen
room pose, marks the working layout unsaved and refreshes the audit. Ctrl+S saves
it with any other manual changes as a single version.
`FurnitureMesh` is shared by placed items and the Library's selected-model preview:
it fits GLBs to `bbox_m`, clones appearance materials and leaves loader-cached
geometry/textures intact. Library uses one on-demand preview canvas, with orbit
controls, loading and failure states, instead of one WebGL context per card.
Failed mesh loads retain the editor's labelled proxy fallback.

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

The editor now loads these scenes through `frontend/src/lib/spatial.ts`, keeping
the local fixture from `frontend/src/data/demoHome.ts` as a visibly warned fallback.

The response matches `roomScene(roomId)` (same IDs, shell and model URLs, fixture poses) except
that doors sit exactly on their walls. The editor still owns `revision` after load.

## Read-only feng shui evaluation

The spatial service exposes `POST /feng-shui`; service-local request/result models
in `feng_shui.py` wrap the unchanged `RoomScene` with optional mirror surfaces,
activity anchors and observations. The complete scene and deterministic audit feed
one bounded model call using the repository skill at
`services/spatial_engine/skills/feng-shui/SKILL.md` as the system instruction.
Existing Anthropic configuration is reused. Output is schema-validated and finding
IDs are checked against the input; failure remains explicitly unassessed. It does
not feed layout ranking or populate the deterministic audit's feng shui field.
See the spatial service README for input semantics and failure behaviour.

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
| Demo cache (#20) | When the data directory has no data for the video, Dev 2's committed cache (`$FURNITURE_DEMO_CACHE_DIR`, default `services/reconstruction/assets/fixtures/demo_cache`): the four normalised meshes, hash-verified and installed into the asset store, with a warning naming the cache. No provider request |

Until the pipeline has run for the video, and when no demo cache is published for it, the room
comes back alone with the warning "No furniture extracted for this room yet". While frame selection is still storing items, it comes
back with the items so far and "furniture still being extracted: no ... yet". Neither is kept:
the next request looks again. Once every hinted item is there, the scene is kept in memory
until restart (re-running the pipeline needs a restart; a persistent cache is #12).

The scene ID only names the plan image. Parsed without its labels (no `FAL_KEY`, or the label
call fails), the same image gives a different room under the same ID ("Unlabelled space 4",
11 walls). The source checks the room's walls against the binding (same IDs; same shape:
lengths within 5 % or 5 cm after fitting one scale, so a scale correction (#11) keeps the
furniture) and otherwise places no furniture, with a warning saying the geometry does not
match and naming the difference.

The first audit of the room reports two things the user can fix by moving furniture: the chair
stands in the swing of the entrance door (`blocked_doors`: `door0` by `vid-000004`), and the
table is 0.19 m in front of the rear sofa (a `clearance_issue`). Moving the chair against the
east wall clears the door; dragging the table onto the sofa adds a collision. With the demo
cache's meshes (#20), whose estimated sizes are larger, the first audit also has the right sofa
in `door0`'s swing, the table 0.12 m from the rear sofa and the right sofa 0.37 m from it; still
no collisions.

**Handoff to Dev 3 (#25).** Load the room with the fetch above
(`/api/reconstruction/scenes/plan-83a12322e933-floor-0-room-3`, after the plan is uploaded),
draw `is_proxy` items as labelled boxes (name plus "proxy"), and after each move POST the
edited scene with `revision + 1` to `/api/spatial_engine/audit`, ignoring reports for older
revisions. Show the `X-Reconstruction-Warnings` list. **Dev 4 (#32):** the audit accepts this
room as is; the findings above are the expected baseline. **Dev 2 (#18):** item IDs and the
`glb_url`s pass through unchanged; an item's normalised mesh (`ItemReconstruction.asset`)
replaces its proxy as soon as the pipeline stores one.

## Corrections (#11)

The user corrects what the reconstruction flags: a floor's scale (`"dimensions"` on
`ParsedRoom`) and where furniture stands (`placement`, `orientation` on `FurnitureItem`). The
service keeps both, in memory, for as long as it keeps the scene (persistence is #12). No
contract model changed: the pose route takes a `RoomScene`, the scale route takes query
parameters. Code: `services/reconstruction/room/correct.py`, routes in `scenes.py`.

| Route | Does |
|---|---|
| `PUT /scenes/{scene_id}` (body `RoomScene`) | Keeps the edited scene's poses (and `sun_hour`). Returns the kept scene; the next `GET` returns the same |
| `POST /scenes/{scene_id}/scale?wall_id=w16&length_m=4.81&revision=N` | Rescales the room's whole floor so that wall is that long. Returns the corrected scene |

Pose correction rules:

- **409** when the scene is not kept yet (its furniture is still being extracted), when
  `revision` is not newer than the kept one, or when the geometry (polygon, walls, openings,
  shell URL, north) differs from the kept scene, i.e. it was edited before a scale correction.
- **422** for an unknown item, an item changed in anything but `pose`, or an added correction
  flag. Asset identity (ID, mesh URL, size, proxy state) cannot change through an edit.
- **422** for a non-finite pose (`NaN`, `Infinity`), before anything is kept.
- Moving an item clears its `placement` flag and turning it clears `orientation`; the editor
  may also clear a flag the user confirmed. Items left out keep their pose. Poses are not
  checked against the room: the audit reports problems.

Scale correction:

- One drawing has one scale and one frame, so every room on the floor is rescaled about the
  floor's origin, from the original parse: the factor is `length_m` over the wall's parsed
  length, so corrections never compound and correcting back restores the parse.
- Plan lengths scale exactly (no rounding, so the room is similar to the parse and every
  opening that fitted its wall still does): polygon, walls (and their traced thickness), window
  offsets and widths, door hinges and widths, then clamped to their walls against float error.
  Heights, bearings and IDs do not; doors are conformed to their walls again. The rooms become `dimension_source: "user_corrected"` without `"dimensions"`, and the
  plan carries one note per corrected floor.
- The shell is immutable per URL, so a corrected room gets `shells/<scene_id>.<digest>.glb`;
  the superseded URL is 404.
- Every kept scene of the floor carries its furniture over and goes up one revision. Each
  item keeps its fraction along the wall it stands in front of, its distance from that wall
  and its yaw; sizes do not change (they come from the video, not the plan). An item the
  rescale pushes out of a smaller room moves to the nearest spot where it fits with the same
  yaw (`align.nearest_fit`), flagged `placement` if that is more than 0.3 m away; one that fits
  nowhere stays where it was carried, flagged.
- **422** for a demo room (fixture geometry), an unknown wall, a factor outside 0.25-4, or a
  factor at which some room of the floor would not be a valid room (narrow features shrink
  below the contract's checks); nothing changes. **409** when the scene is not kept, or
  `revision` is not the kept one (save edits first). The corrected floor and every carried
  scene are computed before anything is published.

Concurrency: sync routes run in a thread pool, so every check-then-write of the plan store and
the kept scenes holds one lock (`routes.STATE_LOCK`): a PUT's revision check and write, a whole
scale correction, and a GET's cache write. Assembly itself runs outside it. A GET never
replaces a kept scene (a slow assembly that finishes after a save returns the saved scene), and
an assembly overtaken by a scale correction is done again from the corrected room (409 after
3 attempts), so a scene's shell URL is always served.

**Handoff to Dev 3 (#25, #26).** PUT the scene when a drag or rotation ends (the revision the
editor already bumps). To correct scale, PUT first, then POST with the current revision and
replace the scene with the response; reload the shell when `shell_glb_url` changes. Prompt for
the flags that remain. On 409, reload the scene. **Dev 4:** nothing changes; the audit receives
the corrected scene, and the tests check it accepts it with openings on their walls.

## Chat additions and application

`POST /chat` on the spatial service accepts `{scene: RoomScene, instruction: string}`
(up to 500 characters, 60 existing items) and returns `{text, poses, additions, report}`.
These service-local models leave `/solve` and the shared scene contract unchanged.
Chat offers `add_item` and `rearrange_room`; the latter delegates to the existing
solver, including its custom goals. Both use the configured layout model. Chat and
any delegated solve share a 90-second, six-call, 200k-token allowance.

`add_item` selects exactly one real Library mesh by asset ID, plus up to 32 moves of existing
movable furniture. Mesh dimensions, collision parts, provenance and uncertainty flags
are copied from that Library entry; the model cannot change them. The new item and every moved item must pass collision,
floor containment and door-swing checks, and a room that could be entered must stay
enterable. Findings among untouched items do not reject the addition; they remain in
the report and are counted in the reply. Rejections name the offending items to the
model for a bounded retry. Existing fixed items cannot move. Front-clearance warnings
are returned for review. A turn that ends without a proposal returns the model's own
words with no changes attached. The server never changes the submitted scene or persists a draft.
The legacy `/proxies/{width}/{height}/{depth}.glb` route remains available for older
scene references; it is not offered to the bot. New bot additions retain the Library
mesh URL and render through the existing mesh renderer.

The Chat tab calls `/api/spatial_engine/chat`. Apply appends additions and applies
poses atomically with one revision bump; stale replies, duplicate IDs, repeated
application, dismissed proposals and application during a gesture or Play are rejected. Room-session
cancellation still discards responses from rooms that have been closed. The audited
report provides a preview before Apply and follows the accepted revision into Stats;
the live audit then checks the new revision. Chat reuses the spatial client's timeout,
cancellation and readable error handling. Provider failure or no key returns
an explanation with no changes. Both manual and bot Library additions preserve their
real model URLs and original geometry metadata.
No new configuration or dependencies are introduced;
`ANTHROPIC_API_KEY` and `SPACESHIFT_LAYOUT_MODEL` are reused. Tests use scripted models.

## Streaming layout progress

`POST /solve/stream` accepts the existing `OptimiseRequest` and runs the same harness
as `/solve`, which remains available as JSON. Shared contracts define SSE payloads:
`progress` carries a stage and factual message, `result` carries a `LayoutProposal`,
and `error` carries an actionable message. Input/geometry validation happens before
stream headers, preserving HTTP 422. Provider unavailability and search limits keep
the existing proposal outcomes; unexpected execution failures produce an error event.

The synchronous harness runs in a request-local worker, forwarding interpretation,
model exploration, tool checks, retries and final validation through a queue. Ten-second
SSE comment heartbeats keep idle connections active. The endpoint disables caching and
proxy buffering; deployment proxies must pass streaming responses without buffering.
No provider token streaming, new dependency or ranking-policy change is involved.
Disconnect signals cooperative cancellation: no later model calls or tool executions
are scheduled, although an active provider call can finish within its existing timeout.

The editor reads the POST response incrementally with fetch, retaining its 120-second
total timeout and stale-request guards. Current status appears beside Cancel, with a
bounded expandable activity log retained on the final, failed or cancelled reply.
Only a complete validated result creates a proposal card. An interrupted stream is
an error and is never retried automatically; progress events never mutate the room.


## Editor Feng Shui score integration

The editor calls `POST /feng-shui/score` with `{scene}` independently of `/audit`
and the opt-in AI advice at `/feng-shui`. A shared 250 ms debounce refreshes audit
and score after canonical room load and committed edits; active gestures suppress
requests. Independent loading/error/retry state prevents a scoring failure from
hiding a valid audit. Room-session, scene-snapshot and revision validation rejects
late results from an older committed revision or that land mid-drag; uncommitted
drag frames keep the last committed revision's results on screen. Room/version changes and
editor cleanup abort outstanding scoring requests.

Stats shows the server's score, weighted-rule coverage, audit cap, rule breakdown,
sightlines and unassessed assumptions. Null means not assessable, and zero remains
a scored result. Mirror inventories and occupant anchors are not supplied by this
UI; the backend's corresponding assumptions remain visible. The audit's nullable
`feng_shui` field is not rewritten to conceal these separate response shapes.

Each actionable proposal scores its immutable before and pose-applied snapshots
without changing the live scene. The comparison shows score and coverage, with
its own retry on failure. Component cleanup cancels these requests and snapshot
identity guards reject late responses. Scoring never changes proposal ranking,
acceptance, history or live Stats; acceptance triggers the normal live refresh.

## Main integration: chat additions and streaming

The active editor chat uses `POST /chat/stream`. It runs main's `/chat` additions
and rearrangement flow with the same factual progress transport as `/solve/stream`.
The existing JSON `/chat` and `/solve` routes and direct `/solve/stream` remain
available. Chat preserves the nested layout goal/outcome when it delegates to solve.
Its terminal SSE event is `reply` (a `ChatReply`, `ChatStreamEvent` in contracts), so
it is never confused with `LayoutStreamEvent`'s `result`.

The editor validates additions and existing-item moves atomically, previews new
footprints, and saves accepted additions as part of the same room-history version.
Existing untouched findings do not veto an addition; the new and moved items must
pass main's placement rules. Library additions retain their actual model URLs.
The single `useLiveAudit` lifetime delegates to the canonical-room/audit/score
coordinator, avoiding duplicate audit effects.

The `feng_shui` solver goal now ranks the full `/feng-shui/score` result shown in
Stats. Its runtime skill and rule feedback guide exploration; the audit's smaller
door-placement metric remains a separate diagnostic and is not used for this goal.


## Skill-guided Feng Shui optimisation

Chat routes an “optimise the feng shui” instruction to layout exploration, retaining
the instruction and interpreted locks. For the `feng_shui` goal only, the harness
loads the repository-owned skill in `layout_optimisation` mode. Inspection and
candidate-evaluation tool results include the exact full score, weighted rules,
coverage, cap and unassessed notes from the Stats scorer. The same full score ranks
candidates and is recomputed during the independent final check. Other goals do
not incur full scoring or skill-loading work.

`feng_shui_inputs.py` holds shared request models and validation, keeping the pure
scorer independent of model orchestration. Existing imports from `feng_shui.py`
remain compatible. The advisory endpoint uses the same skill in read-only
`assessment` mode with its original structured-response tool. Missing or malformed
skill content is a server configuration error (HTTP 503, or a stream `error` event),
never `assistant_unavailable`, and exploration never runs without the guidance.
During optimisation the scorer reuses each candidate's audit and geometry, so it adds
no repeated audits and accepts every scene `/audit` accepts. No additional provider call or new dependency is
introduced. Score weights, inventory and fixed/locked-item constraints are unchanged.


## Library-only chat additions

`services/spatial_engine/library.py` reads the same `ikeaCatalog.json` snapshot
as the frontend Library, validating the bundled files in `frontend/public/catalog/ikea`. It excludes fixed/proxy entries and missing or
invalid GLB files, confines files to the canonical assets directory, and keeps
local `/catalog/ikea/assets/` browser URLs. No new service call, provider or configuration is needed.

Chat supplies this inventory to the model and enumerates its IDs in the addition
tool schema. `add_item` accepts only `asset_id`, pose, optional existing-item moves
and unhandled notes. It rechecks availability and clones the server-owned asset
with a fresh ID and pose, preserving dimensions, collision parts and provenance.
Unknown IDs and invented metadata are rejected; an empty inventory removes the
addition tool. There is no proxy fallback. The editor independently checks each
addition against its own Library before preview/application, including JSON-client
responses. Existing room items and saved versions are not rewritten.


## Library URL imports

`POST /catalog/import` on reconstruction accepts `{url, scene_id}` and returns the
existing `CatalogImport` model (asset, provenance, checks and warnings). The editor
uses `/api/reconstruction/catalog/import`, previews the result and adds it only on
**Add**. The existing retailer pipeline fetches public HTTP(S) addresses only,
including redirects, and bounds downloads. Imports are serialized within the
service process to protect registry updates. With `FAL_KEY`, masks use fal SAM 3 (`fal-ai/sam-3/image`) and missing or
unusable retailer models fall back to SAM 3D (`fal-ai/sam-3/3d-objects`).
Without a key, segmentation stays local and geometry falls back to a proxy.
Failed live segmentation falls back to stored masks or GrabCut with warnings; failed
generation returns a labelled proxy. Existing GrabCut masks are upgraded on reimport;
successful SAM masks and meshes reuse the registry cache to avoid duplicate charges.
Published dimensions remain authoritative. Each stage permits at most two requests,
with existing provider timeouts (120 seconds for masks, 420 seconds for meshes).
Unusable pages return 422; storage/processing failures return 502. Dimension
correction flags and provenance survive addition to the room. Imported assets use
the same configured furniture data directory and asset-serving route as video assets.
