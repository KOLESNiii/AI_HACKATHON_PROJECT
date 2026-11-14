# Graph Report - hackathon-project  (2026-11-14)

## Corpus Check
- 42 files · ~21,912 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 347 nodes · 365 edges · 33 communities (26 shown, 7 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `138d49ff`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schema.py
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
- Dev 2 → Dev 1 asset handoff
- scripts
- health
- health
- health
- .prettierrc.json
- tsconfig.json
- test_contract_occupancy.py
- spaceshift
- fixtures/README.md
- test_contracts.py
- test_fixture_scene.py
- SpaceShift 3D representation and asset handoff — design
- scripts
- Asset Handoff Agreement Implementation Plan
- FurnitureItem

## God Nodes (most connected - your core abstractions)
1. `ContractModel` - 23 edges
2. `compilerOptions` - 19 edges
3. `compilerOptions` - 15 edges
4. `SpaceShift 3D representation and asset handoff — design` - 14 edges
5. `Dev 2 → Dev 1 asset handoff` - 11 edges
6. `item()` - 10 edges
7. `load_mock()` - 8 edges
8. `scripts` - 8 edges
9. `scripts` - 8 edges
10. `Asset Handoff Agreement Implementation Plan` - 6 edges

## Surprising Connections (you probably didn't know these)
- `item()` --uses--> `FurnitureItem`  [INFERRED]
  tests/test_contract_occupancy.py → contracts/schema.py

## Import Cycles
- None detected.

## Communities (33 total, 7 thin omitted)

### Community 0 - "schema.py"
Cohesion: 0.10
Nodes (31): BaseModel, AuditReport, BBoxM, BlockedDoorIssue, ClearanceIssue, CollisionIssue, CollisionPart, ContractModel (+23 more)

### Community 1 - "schema.ts"
Cohesion: 0.07
Nodes (28): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M, MIN_PLAN_OVERLAP_M2, AuditReport, BBoxM (+20 more)

### Community 2 - "SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin"
Cohesion: 0.12
Nodes (14): Architecture, Workstream ownership, 3D representation and asset handoff, Bootstrap, Decisions, Revised execution plan, 1. The Core Differentiator (Why We Beat Existing Tools), 2. What We Stole (And Improved) From Competitors (+6 more)

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

### Community 12 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.17
Nodes (11): 1. IDs, 2. What Dev 2 returns, 3. Evidence, 4. Mesh references, 5. Normalisation guarantee, 6. Occupied volume, 7. Dimension provenance, 8. Functions and failure contract (+3 more)

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

### Community 19 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (16): Any, FurnitureItem, floor_polygon is clockwise in plan view and every wall has the room on its…, model_validator, parametrize, item(), part(), Box collision parts, fixed items and item IDs on the shared contract. (+8 more)

### Community 27 - "test_contracts.py"
Cohesion: 0.17
Nodes (14): RoomScene, load_generator(), load_mock(), True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must…, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., solid_at(), test_layout_proposal_round_trips() (+6 more)

### Community 29 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 30 - "scripts"
Cohesion: 0.15
Nodes (12): name, private, scripts, build, dev, format, format:check, lint (+4 more)

### Community 31 - "Asset Handoff Agreement Implementation Plan"
Cohesion: 0.20
Nodes (9): Asset Handoff Agreement Implementation Plan, Deferred, each under its own issue, Execution notes (2026-11-14), File Structure, Global Constraints, Review Focus, Task 1: Contract additions, Task 2: One fixture scene (+1 more)

## Knowledge Gaps
- **178 isolated node(s):** `Execution notes (2026-11-14)`, `Global Constraints`, `Review Focus`, `Deferred, each under its own issue`, `Task 1: Contract additions` (+173 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `devDependencies` connect `devDependencies` to `scripts`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `dependencies` connect `dependencies` to `scripts`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **What connects `Execution notes (2026-11-14)`, `Global Constraints`, `Review Focus` to the rest of the system?**
  _178 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `schema.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1028225806451613 - nodes in this community are weakly interconnected._
- **Should `schema.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.06896551724137931 - nodes in this community are weakly interconnected._
- **Should `SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._