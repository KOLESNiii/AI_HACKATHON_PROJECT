# Decisions

## Bootstrap

- Preserve the three FastAPI service boundaries and ports already agreed in the
  README and execution DAG, allowing separate contributor ownership.
- Use Bun for frontend package management and Vite execution; use uv for Python
  environments and dependency locking. Avoid an extra monorepo framework.
- Keep one Python manifest initially, with extras for geometry, reconstruction,
  and media libraries. Service launch commands select their extra automatically.
- Install the frontend stack specified in the README. Defer provider-specific
  vision/search SDKs until a provider is selected; HTTPX supports HTTP integrations.
- Provide health endpoints and a connection screen as a working bootstrap check.
  Health responses are operational metadata, separate from locked domain models.
- Keep provider calls, databases, deployment, and product behaviour out of the
  bootstrap. No credentials or paid services are needed to run the scaffold.


## Revised execution plan

- Split reconstruction into room geometry/assembly and furniture/asset extraction
  so two contributors tackle its uncertainty in parallel.
- Keep runtime service boundaries stable while assigning explicit module ownership
  within reconstruction. Reuse one furniture normalisation pipeline for video and
  catalog inputs.
- Assign render-map production to the editor owner and spatial findings to the
  audit owner. Integrate a real editable room and live audit at the first milestone.
- Defer photoreal integration ownership until the validated-layout milestone;
  generated walkthroughs are stretch scope rather than a dedicated core workstream.


## 3D representation and asset handoff

- The scene JSON is the only geometric truth. `.glb` files are derived visuals fitted to
  `bbox_m`; the audit and solver never read a mesh.
- Furniture that nests is described by box collision parts on each item, so a chair under a
  desk or a table over a radiator audits correctly. An empty list means one solid box.
- Item IDs are permanent and opaque; mesh URLs are immutable, so upgrading a proxy to a real
  mesh changes the URL and never the ID.
- Source evidence stays inside the reconstruction service and out of `RoomScene`.
- Full reasoning: `docs/superpowers/specs/2026-11-14-3d-representation-design.md`. The agreed
  Dev 2 → Dev 1 handoff: `services/reconstruction/assets/README.md`.

## Frame selection and identity (#14)

- Reuse FFmpeg/FFprobe, OpenCV/NumPy, Pydantic and fal-client; use Python's built-in SQLite
  transactions for local identity/request persistence. No dependency manifests change.
- Keep additional source identity and selected-image references in internal selection records.
  Adapt a single source into the existing handoff; keep the locked contracts unchanged.
- Live vision is a proposal source: tests exposed merged furniture and split chair parts.
  Mark it review-required rather than certify a false inventory. Support corrected offline
  recordings and verify ID stability on manually reviewed real-room sightings.
- Use conservative evidence/reference matching; do not add a custom assignment solver or
  silently depend on SciPy's spatial extra. Uncertain associations remain visible.
- Preserve full upright source pixels for later appearance reconstruction. Camera estimation
  was probed, but plan fitting, instance masks, material generation and normalisation remain
  the subsequent owners/issues. There is no claim of recovering original shaders from video.

## Furniture masks (#15)

- Prompt SAM 3 with each item's reviewed box, all boxes of a frame in one request. A live
  probe showed the masks map back to their boxes through `metadata.index`; the text-prompted
  video endpoint probed in #14 merged items and is not used.
- Keep local GrabCut as the offline default so the stage runs without keys or spend. It is
  labelled approximate and is never a silent substitute for a failed live call.
- Store masks on the item in the existing registry and keep `mask_url` relative to the data
  directory. Evidence stays inside the reconstruction service; serving it is a route decision.
- Report coverage and quality separately: `complete` means every selected view has a mask;
  overlaps and low SAM scores are warnings. Masks are not edited or merged automatically.
  
## Spatial audit without speculative scores

- Expose implemented checks through `POST /audit`, with existing scene/revision
  echoes and no mutation, provider calls or persistence.
- Use the reachable-floor calculation (50 cm person, union across suitable doors)
  for `walkable_floor_ratio`. Keep raw free-floor area as a separate internal
  metric; it must not be described as reachability.
- Return `null` for unimplemented overall scoring, glare alerts and Feng Shui.
  Mirror nullable types in Python and TypeScript instead of publishing fabricated
  scores or treating unperformed checks as clean. Existing numeric/assessed
  responses still validate; consumers must now handle null.
- Keep malformed input/geometry as HTTP 422 and unexpected failures as server
  errors. Omit raw request data and validation context from error responses.

## PR #44 review follow-up

- Reviewer `bananadado` explicitly approved the original nullable score/glare/
  Feng Shui contract change in [review 5906650105](https://github.com/KOLESNiii/AI_HACKATHON_PROJECT/pull/44#pullrequestreview-5906650105),
  requesting documentation. Tests and handoff docs cover null and legacy assessed
  values. Shared schema, documentation and test edits are intentional parts of
  this API integration, as requested by the Dev 4 operator.
- In response to review items 1 and 3, extend the same null convention to unknown
  walking entry (`walkable_floor_ratio`) and unassessed glare orientation
  (`glare_orientation_grounded`), mirrored in Python/TypeScript. These follow-up
  semantics were subsequently approved by the teammates, as confirmed by the
  Dev 4 operator in this session. Keep all five fields nullable, display null as
  unknown/unassessed, and align the compass rule in `CLAUDE.md` with these meanings.
  This records the operator's confirmation; it does not claim an approval comment
  has been posted to GitHub.
- The initial review fix excluded any swing-obstructed door from walking entry.
  This was superseded after the second review's plant example: swing obstruction
  and physical doorway passage are now separate checks. Entry segments and
  obstacle-eroded free space determine whether a person can enter; a small object
  clipping only the swing arc does not zero the room's reachability. This remains
  an access approximation, not a simulation of partially opened door leaves.
- Preserve the shared chair-as-blocker exemption and the operator's chair-target
  exemption. They are front-access product rules, not walking-space exemptions.
- Preserve full-width front clearance and interior-floor wall semantics. A notch
  obstructing any part of the required strip is a finding even if its centre line
  is clear; wall thickness already extends outward from the usable floor.

## Human-scale room preview

- Keep one local mannequin and its pose outside the shared room model: walking is
  a camera preview and must not change spatial findings, proposals or revisions.
- Use the existing collision parts and 2 m headroom rule with a 50 cm circular
  body, matching the audit's walking dimensions. A 1.6 m eye height provides a
  standing view; small collision steps avoid adding a physics framework.
- Require explicit placement and Play activation. Invalid drops preserve the last
  placement; pointer-lock denial preserves the editor. Escape and lost capture
  return to the saved orbit view with the human at its last walking pose.
- Keep the first version inside one level room. Doorway exits, character animation
  and jumping remain separate work. Time-of-day lighting is added as described below.

## Interactive play lighting

- Use the existing Three.js/R3F/Drei renderer for an interactive preview. Avoid
  path tracing, paid services and backend contract changes. A fixed illustrative
  06:00–18:00 day follows plan north, assuming -Z when compass data is missing;
  it does not predict real-world solar exposure or change glare audit results.
- Keep the ink editor and use cloned PBR materials in Play, preserving source
  furniture textures. Do not modify/dispose loader-cached geometry or textures.
- Separate warm artificial lighting from sun/sky illumination. The artificial
  dimmer controls virtual ceiling sources and their approximate bounce; changing
  time affects only natural sources. Fix exposure so the dimmer remains meaningful.
- Spend shadow rendering on one sun and one ceiling source. Use window area lights
  and a throttled procedural environment for approximate fill and reflections;
  accept that these do not model occluded multi-bounce light or exact reflections.
- Use shadow-only doorway infills because adjacent-room geometry is absent. Keep
  physical window apertures open; glazing, exterior obstructions and fixture-level
  lamp placement are outside this preview.
- L pauses first-person control and intentionally releases mouse capture for the
  sliders; Resume explicitly recaptures it. Preserve unexpected-loss/Esc/focus-loss
  exits and guard late capture results. Settings are local to the opened room.

## Individual furniture reconstruction (#16)

- Use the operator-selected fal SAM 3D Objects endpoint with one #15 frame/mask pair per
  item. Keep failures isolated and run items concurrently; the live probe took 170 seconds.
- Persist raw meshes separately from servable assets. SAM 3D shapes are approximately
  unit-scaled; interpreting metadata and producing the metric mesh profile belong to #17.
- Always supply an honest proxy: known dimensions keep their provenance, category guesses
  are estimates requiring correction. Failed replacements keep a current previous mesh and
  report the failed attempt alongside it. Never silently treat a proxy as a reconstruction.
- Reuse the existing request registry and make its shared budget thread-safe. Recover saved
  handles for free after a timeout; uncertain submissions require investigation or an
  explicit paid refresh. Do not resubmit automatically. Terminal remote errors, disallowed
  artifact URLs and invalid meshes mark the request failed and require a new `--refresh`
  namespace; transient network failures retain the recoverable handle.
- Add an opt-in content-addressed asset router for Dev 1 to mount, preserving entry-point
  ownership and the existing frontend proxy and shared contracts.

## Backend-owned mock meshes

- Serve existing furniture fixtures directly from the reconstruction backend; keep
  their canonical files under `contracts/mock_room/assets/` without frontend copies.
- Generate per-room demo shells on demand with the existing backend geometry code
  and cache them in memory. Remove the frontend asset-copy/build step and generated
  shell files. Stable demo room names are not immutable content hashes, so these URLs
  require cache revalidation.
- Move the original single-room GLBs into backend fixtures and adapt their browser
  URLs through `/api/reconstruction`. Preserve the shared JSON's original geometry
  and paths for the audit, asset handoff and existing fixture consumers.

## Furniture alignment (#8)

- Place furniture from coarse wall-relative hints plus deterministic geometry, the same split
  as the floor-plan parser. `provider_pose` registration waits until Dev 2 produces it.
- Keep plan geometry in plain Python inside `room/`; no manifest change. Tests cross-check it
  against the spatial audit.
- A hinted item is moved only when its spot is impossible (outside the room or inside another
  item). An item in a door swing stays where it was seen and is flagged; the audit reports it.
- Vision placement is a proposal: its confidence is capped below the level that clears the
  `placement` and `orientation` flags. Live runs misplaced both reception sofas.
- Alignment records and hints stay inside the reconstruction service, out of `RoomScene`.
- Align per room, using the editor's room convention for the demo home
  (`demo_assets.demo_room_scene`: rooms by wall prefix, furniture by position) rather than a
  second geometric splitter with its own room IDs. Both gave identical rooms; only the IDs
  and shell URLs differed, and the editor's IDs are the ones a scene route (#9) must return.
- Use #15 masks where they exist: the vision observer traces each item's mask instead of its
  box, so overlapping items in one frame stay distinguishable. Masks do not change geometry;
  without a camera solution they carry no metric position.

## Scene assembly route (#9)

- One read-only route, `GET /scenes/{scene_id}`, over rooms the service already knows (uploaded
  plans and the demo home), returning a contract `RoomScene`. Warnings travel in a response
  header so the body stays a contract model; alignment records stay internal.
- Uploaded rooms come back without furniture, with a warning, until Dev 2's extraction (#16)
  produces assets. Dev 1 does not build its own proxy furniture from #14/#15 output.
- Demo rooms go through the same assembly path as video furniture: pose-less assets plus hints
  read off the fixture poses, which reproduces those poses.
- Conform doors to their walls during parsing and assembly. Millimetre rounding left hinges up
  to 0.9 mm off their walls and leaves up to 1 mm past them; the audit's 1e-8 m tolerance then
  rejected 23 of 25 demo rooms and 13 of 30 parsed example rooms. Errors over 5 mm are left as
  they are and reported, since they are real geometry errors, not rounding.
- Backend only: the editor still assembles rooms locally; switching it is Dev 3's change.
- Keep only complete assemblies. A furniture source or placement observer that fails (a provider
  timeout) yields the room with a warning, but caching that would make the failure permanent for
  the process, so the next request retries. Retrying is safe for paid providers: Dev 2's registry
  re-reads saved requests instead of resubmitting them.

## Real-input room (#10)

- The M1 room is the parser's own room for `three_floor.png`, not the hand-made demo
  `g-reception`, so the shell, openings and scale come from real input. It includes the kitchen
  (an archway the parser does not split); that limit stays visible as a plan warning.
- Furniture is each item's normalised mesh (#17) when the pipeline has one, otherwise Dev 2's
  labelled proxy, never a raw mesh (provider scale and orientation). The issue allows proxies
  when extraction is incomplete, and each one says so (`is_proxy`, estimated size, a warning
  naming them).
- The source runs Dev 2's reconstruction offline only. A scene request never pays for or waits
  on a provider; meshes are made by the pipeline's CLI.
- Placement uses reviewed hints, not the vision observer, which put this room's sofas on the
  wrong walls (#8). They are the #8 reviewed hints moved onto the parsed room's walls with the
  north-west corners aligned: a conversion, not a new judgement, still flagged for correction.
- A bound room whose furniture is not extracted yet, or only partly (a hinted item is missing:
  frame selection stores items batch by batch), is not cached (`SceneFurniture.complete =
  False`), so running the pipeline while the server is up takes effect on the next request
  (PR #55 review).
- A binding is checked against the room's walls, not just its scene ID: the ID hashes the plan
  image, and the same image parsed without labels is a different room. A mismatch places no
  furniture and says so, rather than putting the reception's furniture in another room (PR #55
  review). Tolerance 5 % or 5 cm per wall, after fitting one scale (#11: a corrected scale is
  the same room). Making the plan deterministic without labels (recorded labels) is left to
  #12.
- The asset store is mounted with the same data directory the source reads (#52), so a proxy
  URL in a scene is always servable by the same process.

## Corrections (#11)

- No contract change: `PUT /scenes/{scene_id}` takes and returns a `RoomScene`, and the scale
  correction takes `wall_id`, `length_m` and `revision` as query parameters.
- A scale correction rescales the whole floor (one drawing, one scale, one shared frame), from
  the original parse, so corrections never compound. Furniture sizes are not rescaled.
- Furniture is carried over by wall, keeping its yaw; the aligner only places again an item
  the rescale pushes out of the room. Hinted items still stand in door swings (#8).
- A pose edit may change poses and clear flags, nothing else; moving clears `placement`,
  turning clears `orientation`. Stale edits are 409, invalid ones 422.
- Both corrections need the scene the service keeps (409 while furniture is still being
  extracted), and the scale correction needs the kept revision, so unsaved edits are never
  dropped. Corrected shells get a new URL, keeping shell files immutable.
- Kept in memory with the plan and scene; persistence across restarts is #12.
- PR #59 review: one lock (`routes.STATE_LOCK`) serialises every check-then-write of plans and
  kept scenes, so an older in-flight save can no longer replace a newer revision; a GET only
  fills an empty slot and does not keep an assembly whose room was rescaled meanwhile.
- PR #59 review: an item pushed out by a rescale keeps the user's yaw; only its position gives
  way (`align.nearest_fit`), and no orientation flag is added.
- PR #59 review: non-finite poses are refused (422); `Pose2D` itself accepts them, and they
  would come back as `null`, an invalid scene.
- Second PR #59 review: rescaled lengths are no longer rounded to the millimetre; rounding
  endpoints and widths separately made a door wider than its diagonal wall, which the audit
  (tolerance 1e-8 m) refused. Openings are also clamped to their walls.
- Second PR #59 review: a factor at which a room of the floor breaks the contract is a 422 that
  changes nothing (the floor is corrected whole or not at all), never a 500.
- Second PR #59 review: a GET overtaken by a scale correction assembles the corrected room
  again rather than returning a retired shell URL; 409 after 3 attempts.
