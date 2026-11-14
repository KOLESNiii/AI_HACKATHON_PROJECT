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
- Keep the first version inside one level room with the current lighting. Doorway
  exits, character animation, jumping and time-of-day controls remain separate work.

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
  explicit paid refresh. Do not resubmit automatically.
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
