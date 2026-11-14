# Implementation plan: issue #14

Status: #14 vertical slice implemented; original planning checklist retained below.
The execution record identifies implemented scope and deferred design options. Design:
`docs/superpowers/specs/2026-11-14-video-frame-selection-design.md`.

## Execution record

Implemented `selection_models.py`, `video.py`, `registry.py`, `providers.py`, `selection.py`
and `select_frames.py`, with regression tests and a manually reviewed real-input recording.
SQLite snapshots are transactionally validated; JSON is the inspection/recording format.
`select_furniture_frames` and the CLI produce timestamped upright originals, object views,
source identity and permanent IDs. `object_evidence` adapts one source to the fixed handoff.
No contracts, existing asset models, dependencies, service routes or other owners' code changed.

Implementation decisions following live evaluation:

- Separate-image fal vision input replaced contact-sheet inference after a missed sofa.
  Gemini Flash and Sonnet proposals still merged/split instances. Live output is explicitly
  review-required (exit 2); reviewed `Discovery` recordings provide the accepted inventory.
- The first six seconds of clip 3 have a reviewed recording for four target items and six
  source frames. Replay and reversed-detection reruns retain the same four identities.
- Conservative evidence/reference matching was sufficient for this reviewed slice. SciPy
  was not imported and dependency manifests were not changed. There is no custom assignment
  solver, automatic track merge/retirement, or claim of autonomous whole-house identification.
- Sampling chooses the sharper of two timestamped neighbours per interval and ranks object
  crops for appearance. It retains chronological geometry candidates; automatic room cuts,
  angle estimation, dense camera recovery and plan fitting are deferred to follow-on work.
- The camera feasibility probe is documented, but a production VGGT downloader/adapter is
  deferred until the #15/#8 integration needs it. No arbitrary provider fields were added to
  `provider_pose`, and `extract_furniture` was not replaced by a partial implementation.
- Full checks use `UV_CACHE_DIR=/tmp/spaceshift-uv-cache` in this environment. FastAPI's existing
  TestClient tests require running outside this sandbox; the restricted run stalls there.

The unchecked items below are original design options/test ideas, not claims of delivered
features. Current usage, limitations and acceptance replay are in `assets/README.md`.

## Scope and constraints

Implement usable keyframes, furniture discovery, conservative deduplication and persistent
IDs. Keep the existing `contracts/`, `assets/models.py`, `extract_furniture(Path, scene_id)`
signature, service routes, dependency manifests and other contributors' modules unchanged.
No meshes, proxy URLs, production masks, final poses, or new HTTP contracts in this issue.

Intended production files all live in `services/reconstruction/assets/`. Tests are isolated
under `tests/reconstruction/assets/`; runtime outputs live in an ignored/configured data
directory. Confirm any deeper `AGENTS.md`, branch and working tree before starting. Do not
commit, push or open a PR unless requested. If central interfaces or manifests need changes,
stop that part and coordinate rather than expanding scope.

## Library-first implementation

Reuse FFmpeg/FFprobe, OpenCV, NumPy, Pydantic, fal-client, HTTPX, trimesh and pytest already
available to the project. Use standard-library SQLite for the local registry, replacing the
earlier proposed custom JSON locking/atomic-write scheme. Keep JSON as the inspection format.
Use library image scores, feature matching and RANSAC; keep custom code to source mappings,
furniture association rules and pipeline wiring. Reuse fal-client request handles and SDK
retry behaviour; application code supplies stage deadlines, budget and result recovery.

Prefer SciPy's `linear_sum_assignment` for association after coordinating its declaration in
the reconstruction extra: it is currently declared only for spatial and cannot be assumed
in a reconstruction-only install. Do not implement a matching solver, database locking system,
video decoder or GLB parser from scratch. A new dependency needs a specific gap and central
manifest coordination; libraries must still pass the identity/material acceptance checks.

## Task 1: Internal selection records and durable registry

Files: new `selection_models.py`, `registry.py`; tests `test_registry.py`.

- [ ] Define finite, bounded typed internal records for source videos, frame keys,
  upright pixel boxes, observations, selected views, objects and selection completeness.
  Use source hash + stream + original ordinal/PTS; keep geometry-group identity explicit.
- [ ] Define `SelectionResult`: registry revision, discovered objects with stable IDs,
  appearance/geometry frame references, unresolved matches, warnings and completion status.
  It is not `FurnitureAsset`; importing it must not create provider clients.
- [ ] Implement a versioned local SQLite registry through `sqlite3`, with transactions,
  parameterised queries, safe runtime paths and unique scene/object/source-frame constraints.
  Read/reconcile inside the write transaction, bound lock waits, and keep provider calls
  outside it. No custom file-lock implementation, ORM or separate database service.
- [ ] Allocate valid opaque IDs once; preserve them across category fixes, input reorder,
  cached retries and mesh-stage updates. Store aliases/tombstones for confirmed merges.
- [ ] Test two sources with frame 0, detector-order shuffle, concurrent updates, rollback
  before commit, corrupt/unknown registry version, and an object missing on one rerun. Verify no
  silent ID reset and no overwritten update.

## Task 2: Timestamped upright extraction and quality selection

Files: new `video.py`, `frames.py`; tests `test_video.py`, `test_frames.py`.

- [ ] Wrap FFprobe/FFmpeg with argument arrays, bounded subprocess timeouts, explicit tool
  availability checks and local-path inputs. Read display rotation, time base and decoded PTS.
  Preserve actual source frame ordinals; select before applying FPS conversion when mapping
  evidence. Handle duplicate PTS and undecodable segments explicitly.
- [ ] Produce upright low-resolution candidates and retain full-resolution selected frames.
  Record all encoded/upright/provider pixel transforms. Rotation must not be applied twice.
- [ ] Use OpenCV/NumPy for exposure, Laplacian blur and histogram/feature similarity scores;
  reuse SIFT/ORB matchers and RANSAC for overlap checks. Segment discontinuities and retain
  temporal neighbours. Discovery sampling starts near 1 Hz; geometry uses denser overlap.
- [ ] After detections, score object crops and choose coverage first, then primary appearance
  and up to three alternate views. Keep the only poor observation with a quality warning.
- [ ] Test rotated variable-frame-rate fixtures, duplicate ordinals across sources, fast pan,
  rare poorly lit object, clipped boxes, and appearance/geometry view sets differing on purpose.
  Generate tiny test clips locally with FFmpeg; do not add the private walkthroughs to tests.

## Task 3: Bounded fal discovery with offline substitution

Files: new `discovery.py`, `providers.py`; tests `test_discovery.py` and small sanitised
JSON response fixtures under `tests/reconstruction/assets/fixtures/`.

- [ ] Define a narrow injected discovery-provider protocol plus recorded/no-key adapters.
  Use existing `fal-client`; no new SDK or root manifest edit.
- [ ] Add a fal vision adapter using the existing default endpoint/model values and validated
  structured observations. Do not couple to Dev 1's `room/annotate.py` implementation.
- [ ] Implement bounded attempts, request count, concurrency, deadline, result caching and
  request recovery. Preserve candidates on malformed/empty/provider-failed responses and
  mark discovery incomplete. Do not silently interpret failure as no furniture.
- [ ] Store prompt/model/version/configuration with cached detections; distinguish an explicit
  re-detect from a retry. Sanitize diagnostics and avoid raw provider URLs in fixtures.
- [ ] Test invalid JSON, out-of-bounds/nonfinite boxes, unknown categories, timeout, missing
  credentials, partial success and no repeat billing for cached completed requests.

## Task 4: Identity association and selected-object evidence

Files: new `identity.py`, `selection.py`; tests `test_identity.py`, `test_selection.py`.

- [ ] Implement domain gates and association costs using category, appearance and continuity.
  After dependency coordination, pass the costs to SciPy `linear_sum_assignment` with
  explicit unmatched alternatives; never force a low-confidence match to fill an assignment.
  Do not implement the optimiser itself. Keep provider track IDs scoped to a request; map
  them to persistent object IDs. If SciPy cannot be adopted in this extra, defer global
  assignment and accept only conservative unambiguous matches, documenting the limitation.
- [ ] Record cannot-link pairs for confirmed distinct co-visible objects. Validate reflections
  before either merging or creating cannot-link evidence. Avoid transitive merges that
  violate an existing cannot-link relation.
- [ ] Add cross-clip matching only when corroborating room/appearance/verified geometry is
  present. Unregistered coordinate groups must never share a distance comparison.
- [ ] Keep ambiguous candidates separate with a review record. Reconcile new observations
  against the registry in a transaction; test reordered input and changed detection order.
- [ ] Assemble selected original images/boxes and geometry-frame references per stable ID.
  No production segmentation (#15) or final asset construction (#16) in this module.
- [ ] Test both sofas together and revisited, identical chairs at distinct locations, a mirror,
  re-entry after occlusion, two similar rooms with unknown floor, verified different floors,
  disconnected captures, and category correction without ID changes.

## Task 5: Optional camera probe and evidence adapter

Files: new `camera_evidence.py` only after verifying the live output; tests
`test_camera_evidence.py`. Probe artifacts initially remain local.

- [x] With explicit upload approval, run one VGGT request on eight overlapping frames and
  one SAM video-RLE request on the 16-frame clip-3 excerpt. Record request IDs and durations.
  Cancel after the agreed bounded deadline; do not resubmit blindly if a result is recoverable.
- [x] Inspect actual camera-array dimensions, prediction/depth encoding and image padding.
  Decode a downloaded depth/confidence sample and check source-pixel reprojection. Record
  actual SAM frame/object indexing, RLE encoding and visibility behaviour; do not assume an
  undocumented stable cross-clip ID. If output is insufficient, retain optional/unavailable
  status rather than building around a guessed payload.
  Probe outcome: VGGT returned usable camera/depth arrays in 44.24 s; 37 first-pair feature
  matches reprojected with 1.13 px median error. Use raw float32 depth because exported PNGs
  clip some valid values; use the actual 294 × 518 valid image region inside the 518-square
  model frame. Eight prediction JSON files total 60.1 MB, so trim/cache outputs deliberately.
  SAM returned one combined mask per frame in 7.17 s, merging both sofas and including the
  chair in some frames; metadata has no object IDs. Masks decode as 1-based start/length RLE
  in row-major order and agree with every returned box. Do not use this text-only response
  as separate-object tracking. Instance-specific masking remains to validate in #15.
  Full results and limitations are in the design's provider-probe section; raw artifacts and
  analysis assertions are local in `/tmp/spaceshift-issue14/`. No metric placement or material
  generation was tested and no further inference calls were made.
- [ ] For validated payloads, store typed local cameras/depth references with coordinate-group
  identity and input order. Test camera-from-world inversion, resize/pad/rotation round-trip,
  depth mapping and multiple unregistered groups using synthetic known geometry.
- [ ] Keep `provider_pose` untouched for its documented SAM 3D purpose. No plan fitting or
  `Pose2D` generation. Camera probe success alone does not gate basic #14 selection.
- [ ] Agree the additive sidecar reader and source-manifest use with Dev 1 before integrating
  multiple videos into the existing extraction façade. Do not implement an alternative
  public signature or reinterpret `primary_frame_index` to avoid this coordination.

## Task 6: Inspectable real-input evaluation and documentation

Files: new `select_frames.py` CLI module; update `assets/README.md` only after design approval
to document implemented behaviour, configuration and failure reporting. Keep its agreed
function/evidence examples intact. Add tests `test_selection_cli.py`.

- [ ] Provide an offline/report mode with contact sheets, labelled boxes, stable IDs,
  source video/PTS, selected primary/alternate views, unresolved identities and geometry
  status. Reports stay local and contain no credentials. Live calls require explicit opt-in.
- [ ] Create a small human-reviewed sighting inventory for clip 3's opening room. Confirm
  exact source times/ordinals from decoded frames rather than rounded contact-sheet times.
- [ ] Evaluate discovery coverage and same-object/different-object associations against that
  inventory. Require both sofas to remain separate; require all repeated sightings to retain
  IDs. Resolve ambiguities or report that #14's real-input acceptance is still incomplete.
- [ ] Repeat with an overlapping second clip when one is identified; record unresolved room
  membership for disconnected clips. Do not infer room/storey from the filename suffix.
- [ ] Demonstrate rerun stability and recovery after an interrupted provider job. Save small
  sanitised response fixtures; do not commit original room media or raw provider artifacts.
- [ ] Run the checks below and inspect the diff. Record measured results and limitations in
  the eventual review handoff. No claimed passing checks without actual execution.

## Validation commands for implementation

Use the existing environment, with no dependency/lockfile edits unless coordinated:

```bash
.venv/bin/ruff check services/reconstruction/assets tests/reconstruction/assets
.venv/bin/ruff format --check services/reconstruction/assets tests/reconstruction/assets
.venv/bin/mypy services/reconstruction/assets
.venv/bin/pytest -q tests/reconstruction/assets tests/test_fixture_scene.py tests/test_contracts.py
git diff --check
git diff --stat
git status --short --branch
```

Run the repository's full `bun run check` before a requested PR when dependencies/tools are
available; report unrelated baseline failures separately. #14 does not add TSX, modify the
frontend, or start a development server.

## Follow-on issue gates (planned here, implemented separately)

| Issue/owner | Required evidence |
| --- | --- |
| #15 / Dev 2 | Decoded per-object masks/crops map to original source coordinates and permanent IDs; primary plus alternate appearance views retained |
| #16 / Dev 2 | Evaluate textured SAM/TRELLIS, optionally Meshy PBR; one live output inspected; separate assets; timeout/failure returns labelled proxies for known objects |
| #17 / Dev 2 | Material-preserving GLB round-trip and visual comparison; UV/material maps/factors survive; dimensions, axes, normals/tangents, budgets and 1 mm bounds pass |
| #8 / Dev 1 | Room/floor match and scale/rotation/translation verified with landmarks; camera and furniture positions agree; ambiguous position/front/dimensions request correction |
| #18 / Devs 1–3 | Two independent items load, move, retain materials/IDs/bounds and re-audit correctly; cached scene remains usable on provider failure |

At #16/#17, check `export_textured_glb`, embedded textures and any external PBR maps before
choosing a provider. Original shader recovery from video is not an acceptance claim. Material
fidelity requires comparing renders with source observations; nonempty `materials` JSON alone
is insufficient. Any simplification/export path must preserve or rebake UV/material data.
