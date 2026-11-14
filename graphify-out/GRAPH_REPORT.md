# Graph Report - hackathon-project  (2026-11-14)

## Corpus Check
- 12 files · ~3,655 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 46 nodes · 53 edges · 7 communities (5 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d687071c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BaseModel
- schema.ts
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- SpaceShift — Figma Design System & Spatial UI Spec
- SpaceShift — System Architecture & 4-Developer Execution DAG
- CLAUDE.md

## God Nodes (most connected - your core abstractions)
1. `SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin` - 5 edges
2. `3. Full Tech Stack` - 4 edges
3. `SpaceShift — Figma Design System & Spatial UI Spec` - 3 edges
4. `SpaceShift — System Architecture & 4-Developer Execution DAG` - 2 edges
5. `Vec2` - 2 edges
6. `Vec3` - 2 edges
7. `WallSegment` - 2 edges
8. `WindowOpening` - 2 edges
9. `DoorOpening` - 2 edges
10. `BBoxM` - 2 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (7 total, 2 thin omitted)

### Community 0 - "BaseModel"
Cohesion: 0.22
Nodes (16): BaseModel, BBoxM, BlockedDoorIssue, CollisionIssue, FengShuiReport, FengShuiSightline, GlareAlert, Pose2D (+8 more)

### Community 1 - "schema.ts"
Cohesion: 0.22
Nodes (8): AuditReport, DoorOpening, FurnitureItem, RoomScene, Vec2, Vec3, WallSegment, WindowOpening

### Community 2 - "SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin"
Cohesion: 0.22
Nodes (8): 1. The Core Differentiator (Why We Beat Existing Tools), 2. What We Stole (And Improved) From Competitors, 3. Full Tech Stack, 4. Quickstart (Local Development), **AI & Generative Media (`services/reconstruction` & `services/media_gen`)**, **Design & Frontend (`frontend/`)**, SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin, **Spatial Audit & Solver Engine (`services/spatial_engine`)**

### Community 3 - "SpaceShift — Figma Design System & Spatial UI Spec"
Cohesion: 0.50
Nodes (3): 1. Aesthetic Direction: "Architectural CAD meets Spatial Glass", 2. Screen Choreography (Zero Clutter), SpaceShift — Figma Design System & Spatial UI Spec

## Knowledge Gaps
- **18 isolated node(s):** `1. Monorepo Isolation Rules`, `SpaceShift — AI Coding Agent Rules & Invariants`, `1. Aesthetic Direction: "Architectural CAD meets Spatial Glass"`, `2. Screen Choreography (Zero Clutter)`, `1. The Core Differentiator (Why We Beat Existing Tools)` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `1. Monorepo Isolation Rules`, `SpaceShift — AI Coding Agent Rules & Invariants`, `1. Aesthetic Direction: "Architectural CAD meets Spatial Glass"` to the rest of the system?**
  _18 weakly-connected nodes found - possible documentation gaps or missing edges._