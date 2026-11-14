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
existing Pydantic models from `contracts.schema`; no domain routes are implemented
by the bootstrap. Operational `GET /health` returns
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
Masks/meshes remain #15–#17, and Dev 1 still owns video-to-plan alignment and final placement.
