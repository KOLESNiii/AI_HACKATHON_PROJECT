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
  semantics are documented for reviewer/consumer acknowledgement, not represented
  as already reviewed approval of this subsequent patch.
- Conservatively exclude any door with a reported swing obstruction from walking
  entry. We do not infer whether a partly blocked leaf can open enough to pass.
- Preserve the shared chair-as-blocker exemption and the operator's chair-target
  exemption. They are front-access product rules, not walking-space exemptions.
- Preserve full-width front clearance and interior-floor wall semantics. A notch
  obstructing any part of the required strip is a finding even if its centre line
  is clear; wall thickness already extends outward from the usable floor.
