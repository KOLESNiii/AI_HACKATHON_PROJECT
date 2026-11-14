# SpaceShift — System Architecture & 4-Developer Execution DAG

## 1. Ownership and implementation boundaries

Split the difficult reconstruction work between room geometry and individual
furniture assets. Service folders describe runtime boundaries; they do not imply
one developer per service. Keep the existing folders, ports, and shared room models.

| Owner | Responsibility | Deliverable |
| --- | --- | --- |
| Dev 1 — Room geometry and scene assembly | Parse the floor plan, establish metric scale, extrude walls/openings, align video observations with the plan, place furniture | Room shell and assembled `RoomScene` |
| Dev 2 — Furniture and asset pipeline | Select video frames, segment and deduplicate furniture, reconstruct individual meshes, normalise assets; later import retailer assets through the same pipeline | Separately movable furniture meshes, dimensions, stable IDs, and source metadata |
| Dev 3 — Editor and rendering | Scene loading, furniture manipulation, camera/state, UI, audit overlays, aligned RGB/depth/object-mask export | Interactive editor and render-map bundle |
| Dev 4 — Spatial audit and optimisation | Clearance, collisions, door access, layout scoring, proposed rearrangements, editor feedback integration | `AuditReport` and improved furniture poses |

```text
spaceshift/
├── contracts/                     # Shared room models and mock fixture; coordinate edits
├── services/
│   ├── reconstruction/            # Port 8001: Dev 1 owns app/routes and room assembly
│   │   ├── room/                  # Planned: Dev 1 owns floor plan, shell, placement
│   │   └── assets/                # Planned: Dev 2 owns extraction and mesh normalisation
│   ├── spatial_engine/            # Port 8002: Dev 4 owns audit and solver
│   └── media_gen/                 # Port 8003: Dev 2 owns catalog adapter/app;
│                                  # later photoreal integration is assigned at M2
└── frontend/                      # Dev 3 owns editor, UI, and render-map export
```

`room/` and `assets/` are proposed file ownership boundaries, not implemented
modules. Dev 2 supplies asset functions; Dev 1 wires them into reconstruction
routes. Catalog adapters reuse that asset pipeline rather than implementing a
second mesh generator or normaliser. Dev 2 coordinates any required Python extra
changes with the root manifest owner before importing reconstruction dependencies
from `media_gen`.

Coordinate edits to service entry points, root manifests/lockfiles, and contracts
before implementation. Existing coordinate invariants in `CLAUDE.md` apply:
metres, Y-up, mesh bottom-centre at the origin, logical front facing +Z.
This split reduces overlapping edits; folder ownership cannot guarantee zero conflicts.

## 2. Handoffs to agree at kickoff

These are interface requirements to settle using the existing models where
possible. They do not introduce new API routes or schema fields by themselves.

| Handoff | Producer → consumer | Required agreement |
| --- | --- | --- |
| Room geometry | Dev 1 → Devs 3 and 4 | Metric shell, walls/openings, optional compass, coordinate frame and known scale reference |
| Furniture assets | Dev 2 → Dev 1 → Dev 3 | Stable object ID, mesh location, metric bounds, orientation, source-frame identity and dimension provenance |
| Placement evidence | Dev 2 → Dev 1 | Object IDs tied to source frames/masks; Dev 1 owns alignment and final room poses |
| Assembled scene | Dev 1 → Devs 3 and 4 | Existing `RoomScene`, asset references and initial furniture poses |
| Audit and proposed layout | Dev 4 → Dev 3 | Existing `AuditReport`, proposed poses tied to the same object IDs; preserve shell and asset identity |
| Render maps | Dev 3 → later photoreal adapter | RGB, depth and object masks from one scene revision, camera and resolution; depth encoding/range and mask-ID mapping |

Dev 2 normalises furniture meshes once, regardless of video or catalog source.
Dev 3 applies the resulting scene transforms and exports all render maps from the
same renderer. Dev 4 computes spatial findings; Dev 3 visualises them.

Unknown scale or uncertain placement needs explicit user correction, not an
invented exact measurement. Use dimensioned proxy boxes when mesh extraction
fails, and label them as proxies. Missing compass follows the existing contract
fallback and must remain distinguishable from grounded orientation.

## 3. Execution DAG

Times are target checkpoints, not estimates that guarantee reconstruction quality.
Each owner starts against the shared fixture so development can proceed in parallel.

```mermaid
flowchart TD
    M0["T+0–1h · ALL: agree handoffs and fixture<br/>One floor plan, matching video, scale reference, stable object IDs"]

    M0 --> R1["DEV 1 · T+1–5h<br/>Floor-plan geometry, metric shell, openings<br/>Initial placement against fixture"]
    M0 --> A1["DEV 2 · T+1–5h<br/>Video frames, object masks, deduplication<br/>Two separate assets; dimensioned proxies if needed"]
    M0 --> E1["DEV 3 · T+1–5h<br/>Load fixture, camera, select/move/rotate objects"]
    M0 --> S1["DEV 4 · T+1–5h<br/>Collision, clearance and door checks against fixture"]

    R1 --> R2["DEV 1 + DEV 2 · T+5–8h<br/>Align object evidence to plan<br/>Dev 1 assembles scene; Dev 2 supplies normalised assets"]
    A1 --> R2
    R2 --> M1["M1 · T+8h · ALL: first editable room<br/>One floor plan + video → shell + two independently movable items<br/>Live audit responds to a furniture move"]
    E1 --> M1
    S1 --> M1

    M1 --> R3["DEV 1 · T+8–14h<br/>Improve alignment and placement correction<br/>Validate dimensions and openings"]
    M1 --> A3["DEV 2 · T+8–14h<br/>Improve segmentation and mesh quality<br/>Then catalog lookup/import through the same asset pipeline"]
    M1 --> E3["DEV 3 · T+8–14h<br/>Audit overlays and proposed-layout controls<br/>Aligned RGB/depth/object-mask capture"]
    M1 --> S3["DEV 4 · T+8–14h<br/>Layout scoring and bounded optimisation<br/>Validate proposed poses against the same audit"]

    R3 --> M2["M2 · T+14–17h · ALL: validated layout<br/>Accept improved poses, re-audit, capture consistent render maps<br/>Cache a reproducible demo scene"]
    A3 --> M2
    E3 --> M2
    S3 --> M2

    M2 --> CORE["T+17–22h · ALL: core integration<br/>Failure handling, scale/placement correction, demo fallback"]
    M2 -.-> PHOTO["Optional · assign available owner at M2<br/>Photoreal adapter consumes render maps<br/>Dev 3 supports capture; no duplicate scene reconstruction"]
    CORE --> DEMO["T+22–28h · ALL: bug fixes, UX polish, 90-second demo"]
    PHOTO -.-> DEMO
    PHOTO -.-> VIDEO["Stretch only · generated walkthrough<br/>After core acceptance and photoreal still work"]
    DEMO -.-> VIDEO

    classDef milestone fill:#f1f5f9,stroke:#475569,color:#0f172a
    classDef room fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef assets fill:#ffedd5,stroke:#ea580c,color:#7c2d12
    classDef editor fill:#f3e8ff,stroke:#9333ea,color:#581c87
    classDef spatial fill:#dcfce7,stroke:#16a34a,color:#14532d
    class M0,M1,M2,CORE,DEMO milestone
    class R1,R2,R3 room
    class A1,A3 assets
    class E1,E3 editor
    class S1,S3 spatial
```

## 4. Acceptance and scope priorities

**M1:** A matching floor plan and video produce a metric room shell and at least two
separate furniture items. Each item can be moved independently; moving one updates
the spatial audit. Proxy geometry is acceptable if visibly identified. The fixture
unblocks development but does not replace this real-input integration check.

**M2:** The editor can apply a proposed layout and re-run the audit. Mesh bounds,
poses and spatial checks agree in metres. RGB, depth and object masks describe the
same scene/camera. Provider failure still permits editing and auditing the cached
scene. A layout with unresolved violations must be reported as such.

Prioritise room/furniture separation, metric placement, editing and basic spatial
checks. Improve mesh quality next; add catalog imports once video assets work.
Glare/Feng Shui checks and specialised shaders follow the basic audit. Photoreal
stills are optional after M2, with a named owner assigned then. Generated video is
stretch scope and does not gate the working demo.
