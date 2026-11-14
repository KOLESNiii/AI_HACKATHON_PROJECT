# SpaceShift — System Architecture & 4-Developer Execution DAG

## 1. Monorepo Isolation Rules
To allow 4 developers and their AI coding agents (Claude Code / Cursor) to work simultaneously with **zero merge conflicts**, each developer owns one top-level folder. `contracts/` is locked at **T+0h**.

```text
spaceshift/
├── CLAUDE.md                   # Global agent rules & coordinate system invariants
├── contracts/                  # [LOCKED AT T+0h] Shared schemas + Mock Room Fixture
│   ├── schema.py               # Pydantic v2 models
│   ├── schema.ts               # Exact TypeScript mirror
│   └── mock_room/              # mock_scene.json + shell.glb + bed.glb + desk.glb + wardrobe.glb
├── services/
│   ├── reconstruction/         # [DEV 1] Floor plan parser + video -> fal.ai .glb extractor (Port 8001)
│   ├── spatial_engine/         # [DEV 2] Audit metrics + simulated annealing solver (Port 8002)
│   └── media_gen/              # [DEV 4] fal.ai Photoreal/Video + Linkup/Tavily search (Port 8003)
└── frontend/                   # [DEV 3] Figma HUD + R3F 3D viewport + GLSL shaders (Port 5173)
```

```mermaid
flowchart TD
    M0["`**[T+0h] ALL DEVS: Lock Contracts & Mock Fixture**
    Commit contracts/schema.ts, schema.py & contracts/mock_room/*`"]

    %% DEV 1: RECONSTRUCTION
    M0 --> D1_1["`**[DEV 1 | T+1–5h] Floor Plan VLM + OpenCV Parser**
    Extract walls, doors, windows & optional north_compass_deg`"]
    D1_1 --> D1_2["`**[DEV 1 | T+5–11h] Video to fal.ai 3D Extractor**
    Crop keyframes → sam-3d-objects / trellis-2 → .glb`"]
    D1_2 --> D1_3["`**[DEV 1 | T+11–17h] Base Shell Mesh & Scale Normalizer**
    Extrude shell.glb in trimesh + center/scale furniture .glbs`"]

    %% DEV 2: SPATIAL ENGINE
    M0 --> D2_1["`**[DEV 2 | T+1–5h] Shapely Clearance & Door-Arc Auditor**
    Collisions, door swings, connected walkable % (under 30ms)`"]
    D2_1 --> D2_2["`**[DEV 2 | T+5–11h] Optional-Compass Solar Glare & Feng Shui**
    Fallback south-facing assumption + command-position rays`"]
    D2_2 --> D2_3["`**[DEV 2 | T+11–17h] Simulated Annealing Auto-Solver**
    Wall-snapping + 90° rotations → optimal RoomScene`"]

    %% DEV 3: FRONTEND, SHADERS & FIGMA
    M0 --> D3_1["`**[DEV 3 | T+1–5h] Figma Tokens & R3F Interactive Canvas**
    Load mock_scene.json, 60fps drag/rotate/snap gizmos`"]
    D3_1 --> D3_2["`**[DEV 3 | T+5–11h] Custom GLSL Audit Shaders**
    Sunbeam glare cone, floor walkable hatch & door-swing arcs`"]
    D3_2 --> D3_3["`**[DEV 3 | T+11–17h] Glassmorphic HUD & Depth Exporter**
    Floating toolbar, sun/compass dial & Three.js depth PNG capture`"]

    %% DEV 4: GENERATIVE MEDIA & GROUNDED SHOPPING
    M0 --> D4_1["`**[DEV 4 | T+1–5h] Grounded Product Search & URL Parser**
    Linkup/Tavily dims extractor + trellis-2 proxy .glb`"]
    D4_1 --> D4_2["`**[DEV 4 | T+5–11h] Photoreal Depth-to-Image Pipeline**
    flux-control-lora-depth from viewport depth + RGB`"]
    D4_2 --> D4_3["`**[DEV 4 | T+11–17h] Generative Video Walkthrough**
    kling-video / veo3 5s clip from start/end renders`"]

    %% INTEGRATION
    D1_3 --> INT["`**[T+17–22h] Integration Gate**
    Wire live services + pre-cache 2 real rooms for instant demo fallback`"]
    D2_3 --> INT
    D3_3 --> INT
    D4_3 --> INT

    INT --> POLISH["`**[T+22–28h] Figma Micro-Interactions, Bug Bash & 90s Pitch**`"]

    %% STYLING
    classDef milestone fill:#f1f5f9,stroke:#475569,color:#0f172a,stroke-width:2px
    classDef reconstruction fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef spatial fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef frontend fill:#f3e8ff,stroke:#9333ea,color:#581c87
    classDef media fill:#ffedd5,stroke:#ea580c,color:#7c2d12

    class M0,INT,POLISH milestone
    class D1_1,D1_2,D1_3 reconstruction
    class D2_1,D2_2,D2_3 spatial
    class D3_1,D3_2,D3_3 frontend
    class D4_1,D4_2,D4_3 media
```