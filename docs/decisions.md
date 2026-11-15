# Decisions

## Calm editor audio

- Enable music and effects by default, as chosen by the operator, with immediate
  master mute, independent channel controls and remembered preferences. Respect
  browser autoplay gating and pause hidden tabs; do not queue delayed effects.
- Match the ink editor with short wooden/paper-like synthesized cues and a quiet
  piano-led recording. Use semantic action completion instead of generic button or
  hover sounds; keep camera movement, typing and continuous drags silent.
- Use native Web Audio and streamed music rather than adding an audio framework
  or decoding a full song into memory. Keep audio outside the room model and
  shared interfaces. First-person footsteps and environmental ambience are deferred.
- Bundle Scott Buckley's “Reverie” under CC BY 4.0 with visible attribution and an
  asset notice. Serve music locally, normalize it, and crossfade repeat boundaries;
  no live streaming service or paid provider is required.

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

## Agent-driven layout recommendations

- Sonnet proposes furniture poses through validated tools; our geometry code
  audits every proposal. No mathematical solver or exhaustive position search is
  used. Issue #33's "bounded search" means bounded agent exploration.
- User customisation is a fixed choice of four goals (`balanced`, `brighter`,
  `roomier`, `minimal_changes`) that reorder soft priorities only. Collisions,
  room containment, blocked doors, fixed items and locked items are never traded.
  There is no weight editor and the model cannot define scoring.
- Operator decision (2026-11-14): a requested goal ranks above front clearance,
  so "make it brighter" may reduce access in front of furniture. The alternative
  (access always first) was rejected because a request could then be reported as
  improved without delivering what was asked.
- Operator decision (2026-11-14): support one measured placement request,
  "item near a window" (footprint within 0.5 m of a window opening). Other
  placement wording is acknowledged as unsupported rather than guessed.
- Operator decision (2026-11-14): the user types free text; optional explicit
  goal and locked-item choices from the UI override the model's reading.
- Drafts are request-local and immutable, with one evaluation budget per request.
  The server keeps the best fully valid draft; an invalid draft is never returned
  as a recommendation, even if it improves on an invalid starting layout.
- `POST /solve` uses the official `anthropic` SDK (added to the spatial extra and
  `uv.lock`) with `claude-sonnet-5-5`, configurable through `SPACESHIFT_LAYOUT_MODEL`.
  Sonnet 5.5 rejects forced tool calls, so the instruction is interpreted with an
  ordinary tool call and falls back to the explicit or default goal if the model
  does not make it. The server-side refusal fallback beta is enabled for the
  default model so a declined request is re-run instead of failing.
- Assistant failures and limits are an `outcome` in an HTTP 200 `LayoutProposal`
  so the editor handles one response shape; only invalid input is an HTTP error.
- The preview explanation is generated by the server from measured results, so it
  cannot claim something the audit did not show.

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

## Feng shui evaluation agent

- Keep traditional Form School assessment separate from deterministic audit scores
  and layout ranking. Recommendations require a spatial re-audit before application.
- Reuse full RoomScene geometry; add mirrors and occupant/headboard directions as
  service-local supplemental inputs rather than changing the shared room contract.
- Unknown mirror inventories and missing activity anchors remain explicit unknowns.
  Furniture front orientation alone cannot establish an occupant's gaze or headboard.
- Use a repository-owned skill as the runtime system instruction, one provider call,
  validated structured findings and explicit unavailable outcomes; no new dependencies.

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
  refused (its tolerance was 1e-8 m then; 1 mm since main's `POSITION_TOLERANCE_M`). Openings are also clamped to their walls.
- Second PR #59 review: a factor at which a room of the floor breaks the contract is a 422 that
  changes nothing (the floor is corrected whole or not at all), never a 500.
- Second PR #59 review: a GET overtaken by a scale correction assembles the corrected room
  again rather than returning a retired shell URL; 409 after 3 attempts.

## Tolerance for reconstructed coordinates

- The shared three-floor demo fixtures round wall coordinates to six decimals, so
  door hinges sit about 3e-7 m off their wall. The audit required agreement within
  1e-8 m and rejected 23 of the 25 demo rooms with HTTP 422; the door-entry test
  had the same margin and reported empty rooms as 0% reachable.
- Doors, windows and door entries now share `POSITION_TOLERANCE_M` (1 mm). An
  opening more than 1 mm off its wall is still rejected as invalid input.

## Acceptable layout proposals

- Operator decision (2026-11-14): a proposal may keep a door-swing problem that
  already existed, but never overlapping furniture or items outside the room, and
  it may not block a door that was clear. This replaced the all-or-nothing rule,
  under which a room with a fixed item in a door swing could never get a suggestion.
- Operator decision (2026-11-14): no cached demo answers. Requests are always live.

## Custom requests

- A request that none of the four measurable goals fits becomes the `custom` goal: Sonnet
  receives the user's words and the server enforces the hard rules and that access does not
  get worse. The wish itself is unverified and the explanation says so; the user judges it in
  the preview. Hard rules (no overlap, nothing outside the room, no newly blocked door, locks)
  are never relaxed. Further measurable goals (Feng Shui) are added as a metric plus one entry
  in the priority table.
- An instruction that could not be read is dropped with a note and the result is reported as
  `stopped_early`, so it is never presented as honouring what the user wrote.

## Retailer import review (#60)

- Classify the product's head phrase before `with`, `and` or a comma, using the last
  furniture/accessory noun and preserving compound names such as bedside table. This
  keeps classification offline, deterministic and free; no Anthropic key is required.
- Retailer GLBs use their metre-scale extents when published/user dimensions are absent.
  Their dimensions remain estimated and request correction; generated meshes still use
  category height. Both paths retain the normaliser's size and geometry checks.
- Product IDs discard query strings, fragments and trailing slashes. Read image dimensions
  with Pillow before OpenCV decode and refuse images over 25 million pixels. Downloads
  share a monotonic deadline across redirects and body chunks, with each network operation
  also limited by the remaining budget at the start of its request.
- Keep the CLI's normalisation preflight and delivery check: the duplicate work is accepted
  for now to preserve the single delivery validation path.

## Demo asset cache (#20)

- The M2 demo's furniture is a published cache, not the pipeline's data directory: a manifest
  of the delivered assets with every referenced file's SHA-256, installed into the asset store
  under the same paths. URLs and evidence stay valid. Nothing is regenerated, and a changed file
  refuses to load.
- The real-input room uses the cache only when the pipeline has no data for its video, so
  running the pipeline still takes effect. A broken cache gives the old empty-room answer plus
  the reason, never a partial room.
- A publish never takes the cache away: it writes an immutable generation folder, then switches
  a `CURRENT` pointer file with one atomic replace (no symlink, so it works from git on any OS).
  A reader resolves the pointer once; the replaced generation is kept for readers still on it.
- Commit the opening room's four meshes and masks (4.97 MB, derived from the committed example
  video). Do not commit retailer models (third-party files); catalog scenes are cached locally.
- Bounds agreement includes the glTF's declared `POSITION` min/max. three.js fits the mesh from
  them, so `inspect_asset` checks them against `bbox_m` alongside the vertex bounds.
- The cache does not remove the need for `FAL_KEY` to read plan labels; recorded labels are #12.
  Layout answers (`/solve`) are not cached (the operator decision above).
