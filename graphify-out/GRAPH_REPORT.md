# Graph Report - hackathon-project  (2026-11-14)

## Corpus Check
- 34 files · ~7,990 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 210 nodes · 202 edges · 26 communities (21 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `38e45672`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BaseModel
- schema.ts
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- SpaceShift — Figma Design System & Spatial UI Spec
- SpaceShift — System Architecture & 4-Developer Execution DAG
- CLAUDE.md
- compilerOptions
- compilerOptions
- dependencies
- devDependencies
- plugins
- scripts
- scripts
- health
- health
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- spaceshift

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 19 edges
2. `compilerOptions` - 15 edges
3. `scripts` - 8 edges
4. `scripts` - 8 edges
5. `SpaceShift — System Architecture & 4-Developer Execution DAG` - 6 edges
6. `5. Developer focus and ordered task lists` - 5 edges
7. `SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin` - 5 edges
8. `plugins` - 4 edges
9. `3. Full Tech Stack` - 4 edges
10. `health()` - 3 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (26 total, 5 thin omitted)

### Community 0 - "BaseModel"
Cohesion: 0.22
Nodes (16): BaseModel, BBoxM, BlockedDoorIssue, CollisionIssue, FengShuiReport, FengShuiSightline, GlareAlert, Pose2D (+8 more)

### Community 1 - "schema.ts"
Cohesion: 0.22
Nodes (8): AuditReport, DoorOpening, FurnitureItem, RoomScene, Vec2, Vec3, WallSegment, WindowOpening

### Community 2 - "SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin"
Cohesion: 0.12
Nodes (13): Architecture, Workstream ownership, Bootstrap, Decisions, Revised execution plan, 1. The Core Differentiator (Why We Beat Existing Tools), 2. What We Stole (And Improved) From Competitors, 3. Full Tech Stack (+5 more)

### Community 3 - "SpaceShift — Figma Design System & Spatial UI Spec"
Cohesion: 0.50
Nodes (3): 1. Aesthetic Direction: "Architectural CAD meets Spatial Glass", 2. Screen Choreography (Zero Clutter), SpaceShift — Figma Design System & Spatial UI Spec

### Community 4 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 7 - "compilerOptions"
Cohesion: 0.08
Nodes (24): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+16 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 9 - "dependencies"
Cohesion: 0.11
Nodes (19): framer-motion, dependencies, framer-motion, react, react-dom, @react-three/drei, @react-three/fiber, tailwindcss (+11 more)

### Community 10 - "devDependencies"
Cohesion: 0.11
Nodes (19): devDependencies, oxlint, prettier, @types/node, @types/react, @types/react-dom, @types/three, typescript (+11 more)

### Community 11 - "plugins"
Cohesion: 0.16
Nodes (11): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, App(), services, oxc (+3 more)

### Community 12 - "scripts"
Cohesion: 0.15
Nodes (12): name, private, scripts, build, dev, format, format:check, lint (+4 more)

### Community 13 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 14 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 15 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 16 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

## Knowledge Gaps
- **113 isolated node(s):** `1. Ownership and implementation boundaries`, `2. Handoffs to agree at kickoff`, `3. Execution DAG`, `4. Acceptance and scope priorities`, `Dev 1: Room geometry and scene assembly` (+108 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `devDependencies` connect `devDependencies` to `scripts`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `dependencies` connect `dependencies` to `scripts`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **What connects `1. Ownership and implementation boundaries`, `2. Handoffs to agree at kickoff`, `3. Execution DAG` to the rest of the system?**
  _113 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._