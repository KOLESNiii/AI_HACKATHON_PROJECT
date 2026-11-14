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
