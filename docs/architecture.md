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
The complete room shell is visible. Escape, pointer-lock loss or window focus loss
saves the last human position/heading and restores the editor camera and orbit
target. Pointer-lock denial leaves the editor active with a retry message. Opening
a room resets the actor; component cleanup releases capture and held keys.

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

`Landscape` stays mounted for the app session and is shown on home/processing
screens. It lazy-loads the locally vendored MIT-licensed Shan Shui Inf engine as
text into an iframe with `sandbox="allow-scripts"`. The adapter hides the original
controls, fits the viewport and pauses/resumes drift through source-checked
`postMessage` events. A procedural canvas fallback paints while the engine starts
or if loading/adaptation fails. No provider requests or extra configuration are
required. Attribution and the original license live beside the vendored source.

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

## Scene assembly route (#9)

`GET /scenes/{scene_id}` on port 8001 (`services/reconstruction/scenes.py`) returns one room as a
contract `RoomScene`, ready for the editor and `POST /audit`:

- Input: a scene ID. Either a room of an uploaded floor plan (`<plan_id>-<room_id>`, the
  `ParsedRoom.scene.scene_id` from `POST /floor-plans`) or a demo-home room (`g-reception`).
- Output: the room's walls, openings and shell URL, and its furniture, one item per asset with
  its own pose and correction flags (`room/assemble.py` → `room/align.py`). Doors are put
  exactly on their walls first, so the audit accepts every room. `revision` is 0.
- Furniture: demo rooms place the fixture furniture through the same path as video furniture.
  Uploaded rooms have none until Dev 2's extraction (#16) exists; `get_furniture_source` is the
  seam it plugs into.
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
