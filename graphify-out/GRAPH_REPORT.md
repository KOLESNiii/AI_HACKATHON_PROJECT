# Graph Report - hackathon-project  (2026-11-14)

## Corpus Check
- 79 files · ~88,254 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1074 nodes · 2495 edges · 70 communities (61 shown, 9 thin omitted)
- Extraction: 73% EXTRACTED · 27% INFERRED · 0% AMBIGUOUS · INFERRED: 668 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `42077f55`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ContractModel
- schema.ts
- Dev 2 → Dev 1 asset handoff
- SpaceShift — Figma Design System & Spatial UI Spec
- SpaceShift — System Architecture & 4-Developer Execution DAG
- CLAUDE.md
- compilerOptions
- compilerOptions
- dependencies
- devDependencies
- plugins
- Video frame selection and furniture identity — issue #14
- scripts
- health
- Implementation plan: issue #14
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
- RoomScene
- test_room_parse.py
- Mask
- SpaceShift 3D representation and asset handoff — design
- FurnitureAsset
- generate_mock_glbs.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- raster.py
- .graphify_detect.json
- Agent Instructions
- models.py
- Asset Handoff Agreement Implementation Plan
- test_selection.py
- SpaceShift — System Architecture & 4-Developer Execution DAG
- evidence.json
- Path
- scripts
- mock_scene.json
- Pose2D
- frontend/package.json
- App.tsx
- Floor-plan parser (Dev 1)
- .graphify_ast.json
- three_floor.annotations.json
- SpaceShift — Figma Design System & Spatial UI Spec
- .graphify_cached.json
- one_floor.annotations.json
- health
- health
- health
- SpaceShift — AI Coding Agent Rules & Invariants
- Dev 2 fixture furniture

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 57 edges
2. `ContractModel` - 57 edges
3. `PlanAnnotations` - 52 edges
4. `ParsedFloorPlan` - 46 edges
5. `Bridge` - 42 edges
6. `FloorCaption` - 39 edges
7. `PlanAnnotator` - 39 edges
8. `RoomLabel` - 39 edges
9. `Raster` - 39 edges
10. `ParsedRoom` - 38 edges

## Surprising Connections (you probably didn't know these)
- `Scene` --uses--> `RoomScene`  [INFERRED]
  scripts/generate_mock_glbs.py → contracts/schema.py
- `int` --uses--> `RoomScene`  [INFERRED]
  scripts/generate_mock_glbs.py → contracts/schema.py
- `float` --uses--> `FurnitureAsset`  [INFERRED]
  tests/test_contract_occupancy.py → services/reconstruction/assets/models.py
- `float` --uses--> `FurnitureItem`  [INFERRED]
  tests/test_contract_occupancy.py → contracts/schema.py
- `float` --uses--> `RoomCaptureInputs`  [INFERRED]
  tests/test_contract_occupancy.py → contracts/schema.py

## Import Cycles
- None detected.

## Communities (70 total, 9 thin omitted)

### Community 0 - "ContractModel"
Cohesion: 0.11
Nodes (29): BaseModel, BlockedDoorIssue, ClearanceIssue, CollisionIssue, ContractModel, DoorOpening, FengShuiSightline, GlareAlert (+21 more)

### Community 1 - "schema.ts"
Cohesion: 0.09
Nodes (32): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M, MIN_PLAN_OVERLAP_M2, AuditReport, BBoxM (+24 more)

### Community 2 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.06
Nodes (29): Architecture, Furniture evidence selection (#14), Workstream ownership, 3D representation and asset handoff, Bootstrap, Decisions, Frame selection and identity (#14), Revised execution plan (+21 more)

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
Cohesion: 0.12
Nodes (17): framer-motion, dependencies, framer-motion, react-dom, @react-three/drei, @react-three/fiber, tailwindcss, @tailwindcss/vite (+9 more)

### Community 10 - "devDependencies"
Cohesion: 0.10
Nodes (19): devDependencies, oxlint, prettier, @types/node, @types/react, @types/react-dom, @types/three, typescript (+11 more)

### Community 11 - "plugins"
Cohesion: 0.17
Nodes (11): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, App(), services, oxc (+3 more)

### Community 12 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 13 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 14 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 15 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 16 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 19 - "test_contract_occupancy.py"
Cohesion: 0.17
Nodes (24): FurnitureItem, parametrize, inputs(), item(), part(), float, str, Box collision parts, fixed items and item IDs on the shared contract. (+16 more)

### Community 27 - "test_contracts.py"
Cohesion: 0.17
Nodes (22): AuditReport, FengShuiReport, LayoutProposal, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., Proposed furniture poses. Only poses change: shell, openings, item IDs and…, RoomScene, RoomScene (+14 more)

### Community 28 - "test_fixture_scene.py"
Cohesion: 0.24
Nodes (8): The one fixture scene: Dev 2's fixture assets placed in the mock room (issues #5, The module-doc collision rule: touching is allowed, overlapping is not., test_chair_seat_clears_the_desktop(), test_evidence_matches_the_agreed_shape(), test_fixture_items_carry_the_agreed_fields(), test_fixture_scene_has_no_collisions(), test_generated_meshes_match_bbox(), test_scene_holds_the_fixture_items_and_the_two_originals()

### Community 29 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 30 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, format, format:check, lint, preview, typecheck

### Community 31 - "Asset Handoff Agreement Implementation Plan"
Cohesion: 0.20
Nodes (9): Asset Handoff Agreement Implementation Plan, Deferred, each under its own issue, Execution notes (2026-11-14), File Structure, Global Constraints, Review Focus, Task 1: Contract additions, Task 2: One fixture scene (+1 more)

### Community 33 - "RoomScene"
Cohesion: 0.10
Nodes (104): DoorOpening, ParsedFloor, ParsedFloorPlan, ParsedRoom, RoomScene, Vec2, WallSegment, WindowOpening (+96 more)

### Community 34 - "test_room_parse.py"
Cohesion: 0.07
Nodes (59): AnnotationResult, Compass, _extract_json(), FixedAnnotator, NullAnnotator, What computer vision cannot read off a floor plan: room labels with their printe, Plans print labels in capitals ("BEDROOM (4)"); show them in title case., No labels: the parser falls back to estimated scale and generic names. (+51 more)

### Community 35 - "Mask"
Cohesion: 0.09
Nodes (51): int32, attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Bridges → doors and windows on specific room walls.  A bridge is attached to eve (+43 more)

### Community 36 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.05
Nodes (36): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+28 more)

### Community 37 - "FurnitureAsset"
Cohesion: 0.17
Nodes (25): AssetEvidence, FurnitureAsset, NormalisedMesh, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., Dev 1 places the asset: add the pose it aligned from the floor plan., Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`., BBoxM, CollisionPart (+17 more)

### Community 38 - "generate_mock_glbs.py"
Cohesion: 0.12
Nodes (28): floor_polygon is clockwise in plan view and every wall has the room on its…, floor_polygon is clockwise in plan view and every wall has the room on its (-dz,, Scene, coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main() (+20 more)

### Community 39 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.10
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 40 - "raster.py"
Cohesion: 0.11
Nodes (31): float64, Gray, area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), Room region (pixels) → simple, clean polygon of the interior wall faces.  The fr (+23 more)

### Community 41 - ".graphify_detect.json"
Cohesion: 0.11
Nodes (17): files, code, document, image, paper, video, graphifyignore_patterns, ignored (+9 more)

### Community 42 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 43 - "models.py"
Cohesion: 0.25
Nodes (7): EvidenceFrame, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder).  Evidence sta, One video frame an asset was seen in. Optional fields are null for fixtures., BBoxM, CollisionPart, Canonical metric bounds in the item's local frame: width along X, height along…, One box of an item's occupied volume, in the item's local frame (the .glb…

### Community 44 - "Asset Handoff Agreement Implementation Plan"
Cohesion: 0.13
Nodes (14): Asset Handoff Agreement Implementation Plan, code:bash (git fetch origin), code:python (LEGACY_DESK = {  # the pre-change shape: none of the new fie), code:text (Occupied volume and collision (the editor preview and the au), code:python (ROOT = Path(__file__).resolve().parent.parent), code:bash (git rm services/reconstruction/assets/fixtures/vid-desk-01.g), Deferred, each under its own issue, Execution notes (2026-11-14) (+6 more)

### Community 45 - "test_selection.py"
Cohesion: 0.06
Nodes (84): Any, AssetEvidence, Connection, Discovery, Exception, fixture, Frame, model_validator (+76 more)

### Community 46 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.15
Nodes (12): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, code:text (spaceshift/), code:mermaid (flowchart TD), Dev 1: Room geometry and scene assembly (+4 more)

### Community 47 - "evidence.json"
Cohesion: 0.15
Nodes (12): fix-radiator-01, frames, primary_frame_index, vid-chair-01, frames, primary_frame_index, vid-desk-01, frames (+4 more)

### Community 49 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 51 - "mock_scene.json"
Cohesion: 0.18
Nodes (10): doors, floor_polygon, furniture, north_compass_deg, revision, scene_id, shell_glb_url, sun_hour (+2 more)

### Community 52 - "Pose2D"
Cohesion: 0.31
Nodes (11): AuditReport, FengShuiReport, LayoutProposal, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., Proposed furniture poses. Only poses change: shell, openings, item IDs and glb_u, bool, float (+3 more)

### Community 55 - "frontend/package.json"
Cohesion: 0.53
Nodes (4): name, private, type, version

### Community 56 - "App.tsx"
Cohesion: 0.40
Nodes (3): react, react, services

### Community 57 - "Floor-plan parser (Dev 1)"
Cohesion: 0.33
Nodes (5): code:bash (# API (port 8001): POST images, then fetch the plan or one r), Floor-plan parser (Dev 1), How it works, Status and limits, Use

### Community 58 - ".graphify_ast.json"
Cohesion: 0.40
Nodes (4): edges, input_tokens, nodes, output_tokens

### Community 59 - "three_floor.annotations.json"
Cohesion: 0.40
Nodes (4): compass, north_bearing_deg, floors, rooms

### Community 60 - "SpaceShift — Figma Design System & Spatial UI Spec"
Cohesion: 0.50
Nodes (3): 1. Aesthetic Direction: "Architectural CAD meets Spatial Glass", 2. Screen Choreography (Zero Clutter), SpaceShift — Figma Design System & Spatial UI Spec

### Community 61 - ".graphify_cached.json"
Cohesion: 0.50
Nodes (3): edges, hyperedges, nodes

### Community 62 - "one_floor.annotations.json"
Cohesion: 0.50
Nodes (3): compass, floors, rooms

### Community 63 - "health"
Cohesion: 0.50
Nodes (3): health(), Process liveness only; does not probe external providers., str

### Community 64 - "health"
Cohesion: 0.50
Nodes (3): health(), Process liveness only; does not probe external providers., str

### Community 65 - "health"
Cohesion: 0.50
Nodes (3): str, health(), Process liveness only; does not probe external providers.

## Knowledge Gaps
- **319 isolated node(s):** `Goal and scope`, `Provider probe — executed after explicit upload approval`, `Library reuse requirement`, `End-to-end flow and ownership`, `1. Source identity and local frame processing` (+314 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ContractModel` connect `ContractModel` to `RoomScene`, `FurnitureAsset`, `models.py`, `test_contract_occupancy.py`, `Pose2D`, `test_contracts.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `Bridge` connect `RoomScene` to `Mask`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `RoomScene` connect `RoomScene` to `ContractModel`, `test_room_parse.py`, `FurnitureAsset`, `generate_mock_glbs.py`, `Pose2D`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 54 inferred relationships involving `RoomScene` (e.g. with `Depends` and `description`) actually correct?**
  _`RoomScene` has 54 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `ContractModel` (e.g. with `AssetEvidence` and `EvidenceFrame`) actually correct?**
  _`ContractModel` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `PlanAnnotations` (e.g. with `EdgeHit` and `FloorCaption`) actually correct?**
  _`PlanAnnotations` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `ParsedFloorPlan` (e.g. with `Depends` and `description`) actually correct?**
  _`ParsedFloorPlan` has 43 INFERRED edges - model-reasoned connections that need verification._