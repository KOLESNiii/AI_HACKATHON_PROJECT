# Graph Report - hackathon-project  (2026-11-14)

## Corpus Check
- 107 files · ~108,022 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1085 nodes · 2540 edges · 72 communities (63 shown, 9 thin omitted)
- Extraction: 71% EXTRACTED · 29% INFERRED · 0% AMBIGUOUS · INFERRED: 746 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4fbef628`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ContractModel
- schema.ts
- Decisions
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
- test_room_shell.py
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
- PlanAnnotations
- Mask
- SpaceShift 3D representation and asset handoff — design
- FurnitureAsset
- generate_mock_glbs.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- region_polygon
- .graphify_detect.json
- Agent Instructions
- Dev 2 → Dev 1 asset handoff
- Asset Handoff Agreement Implementation Plan
- routes.py
- SpaceShift — System Architecture & 4-Developer Execution DAG
- evidence.json
- test_service_health_and_cors
- scripts
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- mock_scene.json
- schema.py
- ._check_winding
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
1. `RoomScene` - 85 edges
2. `PlanAnnotations` - 65 edges
3. `ParsedFloorPlan` - 58 edges
4. `ContractModel` - 57 edges
5. `Bridge` - 43 edges
6. `FixedAnnotator` - 42 edges
7. `PlanAnnotator` - 41 edges
8. `RoomLabel` - 40 edges
9. `FloorCaption` - 40 edges
10. `Raster` - 40 edges

## Surprising Connections (you probably didn't know these)
- `int` --uses--> `RoomScene`  [INFERRED]
  scripts/generate_mock_glbs.py → contracts/schema.py
- `Scene` --uses--> `RoomScene`  [INFERRED]
  scripts/generate_mock_glbs.py → contracts/schema.py
- `Scene` --uses--> `RoomScene`  [INFERRED]
  scripts/generate_mock_glbs.py → contracts/schema.py
- `EvidenceFrame` --uses--> `ContractModel`  [INFERRED]
  services/reconstruction/assets/models.py → contracts/schema.py
- `EvidenceFrame` --uses--> `Pose2D`  [INFERRED]
  services/reconstruction/assets/models.py → contracts/schema.py

## Import Cycles
- None detected.

## Communities (72 total, 9 thin omitted)

### Community 0 - "ContractModel"
Cohesion: 0.13
Nodes (26): Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder).  Evidence sta, BaseModel, AuditReport, BBoxM, BlockedDoorIssue, ClearanceIssue, CollisionIssue, CollisionPart (+18 more)

### Community 1 - "schema.ts"
Cohesion: 0.09
Nodes (32): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M, MIN_PLAN_OVERLAP_M2, AuditReport, BBoxM (+24 more)

### Community 2 - "Decisions"
Cohesion: 0.11
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
Cohesion: 0.12
Nodes (17): framer-motion, dependencies, framer-motion, react-dom, @react-three/drei, @react-three/fiber, tailwindcss, @tailwindcss/vite (+9 more)

### Community 10 - "devDependencies"
Cohesion: 0.10
Nodes (19): devDependencies, oxlint, prettier, @types/node, @types/react, @types/react-dom, @types/three, typescript (+11 more)

### Community 11 - "plugins"
Cohesion: 0.17
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

### Community 15 - "test_room_shell.py"
Cohesion: 0.06
Nodes (78): object, build_shell(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key(), _miter() (+70 more)

### Community 16 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 19 - "test_contract_occupancy.py"
Cohesion: 0.14
Nodes (31): Any, FurnitureItem, RoomCaptureInputs, What the user uploads for one room. Scale is read from the dimension labels on t, parametrize, Compass, RoomCaptureInputs, inputs() (+23 more)

### Community 27 - "test_contracts.py"
Cohesion: 0.19
Nodes (18): RoomScene, Path, RoomScene, load_generator(), load_mock(), True when the point lies inside one of the mesh's boxes (all mock parts are boxe, schema.ts treats every non-nullable field as present, so the fixture must includ, plan_normal_deg is derived from the wall's outward normal (dz, -dx). (+10 more)

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
Cohesion: 0.11
Nodes (96): DoorOpening, DoorOpening, ParsedFloor, ParsedFloorPlan, ParsedRoom, RoomScene, Vec2, WallSegment (+88 more)

### Community 34 - "PlanAnnotations"
Cohesion: 0.06
Nodes (90): MonkeyPatch, ParsedFloor, ParsedRoom, AnnotationResult, _extract_json(), FalVisionAnnotator, FixedAnnotator, NullAnnotator (+82 more)

### Community 35 - "Mask"
Cohesion: 0.09
Nodes (51): int32, attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Bridges → doors and windows on specific room walls.  A bridge is attached to eve (+43 more)

### Community 36 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.05
Nodes (36): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+28 more)

### Community 37 - "FurnitureAsset"
Cohesion: 0.20
Nodes (20): AssetEvidence, EvidenceFrame, FurnitureAsset, NormalisedMesh, One video frame an asset was seen in. Optional fields are null for fixtures., What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., Dev 1 places the asset: add the pose it aligned from the floor plan., Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`. (+12 more)

### Community 38 - "generate_mock_glbs.py"
Cohesion: 0.15
Nodes (27): Scene, coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), float (+19 more)

### Community 39 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.10
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 40 - "region_polygon"
Cohesion: 0.22
Nodes (18): float64, area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), Room region (pixels) → simple, clean polygon of the interior wall faces.  The fr, Outer contour of a room region as a simplified polygon in pixels, wound for the (+10 more)

### Community 41 - ".graphify_detect.json"
Cohesion: 0.11
Nodes (17): files, code, document, image, paper, video, graphifyignore_patterns, ignored (+9 more)

### Community 42 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 43 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.13
Nodes (14): 10. Room inputs (#5), 1. IDs, 2. What Dev 2 returns, 3. Evidence, 4. Mesh references, 5. Normalisation guarantee, 6. Occupied volume, 7. Dimension provenance (+6 more)

### Community 44 - "Asset Handoff Agreement Implementation Plan"
Cohesion: 0.13
Nodes (14): Asset Handoff Agreement Implementation Plan, code:bash (git fetch origin), code:python (LEGACY_DESK = {  # the pre-change shape: none of the new fie), code:text (Occupied volume and collision (the editor preview and the au), code:python (ROOT = Path(__file__).resolve().parent.parent), code:bash (git rm services/reconstruction/assets/fixtures/vid-desk-01.g), Deferred, each under its own issue, Execution notes (2026-11-14) (+6 more)

### Community 45 - "routes.py"
Cohesion: 0.08
Nodes (31): Gray, decode(), estimate_wall_px(), flatten_illumination(), rasterise(), Image → binary masks: all ink, and the structural strokes that are walls.  Every, Divide by a smooth estimate of the paper so a photographed printout thresholds e, Divide by a smooth estimate of the paper so a photographed printout thresholds e (+23 more)

### Community 46 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.15
Nodes (12): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, code:text (spaceshift/), code:mermaid (flowchart TD), Dev 1: Room geometry and scene assembly (+4 more)

### Community 47 - "evidence.json"
Cohesion: 0.15
Nodes (12): fix-radiator-01, frames, primary_frame_index, vid-chair-01, frames, primary_frame_index, vid-desk-01, frames (+4 more)

### Community 49 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 50 - "SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin"
Cohesion: 0.17
Nodes (11): 1. The Core Differentiator (Why We Beat Existing Tools), 2. What We Stole (And Improved) From Competitors, 3. Full Tech Stack, 4. Quickstart (Local Development), **AI & Generative Media (`services/reconstruction` & `services/media_gen`)**, code:bash (bun run setup), code:bash (bun run dev:reconstruction # http://localhost:8001/docs), code:bash (bun run build             # TypeScript check + production fr) (+3 more)

### Community 51 - "mock_scene.json"
Cohesion: 0.18
Nodes (10): doors, floor_polygon, furniture, north_compass_deg, revision, scene_id, shell_glb_url, sun_hour (+2 more)

### Community 52 - "schema.py"
Cohesion: 0.13
Nodes (21): AuditReport, BlockedDoorIssue, ClearanceIssue, CollisionIssue, FengShuiReport, FengShuiSightline, GlareAlert, LayoutProposal (+13 more)

### Community 54 - "._check_winding"
Cohesion: 0.40
Nodes (3): floor_polygon is clockwise in plan view and every wall has the room on its…, floor_polygon is clockwise in plan view and every wall has the room on its (-dz,, model_validator

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
Cohesion: 0.40
Nodes (4): health(), Process liveness only; does not probe external providers., Process liveness only; does not probe external providers., str

### Community 65 - "health"
Cohesion: 0.50
Nodes (3): str, health(), Process liveness only; does not probe external providers.

## Knowledge Gaps
- **309 isolated node(s):** `code`, `document`, `paper`, `image`, `video` (+304 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `ContractModel`, `PlanAnnotations`, `FurnitureAsset`, `generate_mock_glbs.py`, `routes.py`, `test_room_shell.py`, `schema.py`, `._check_winding`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `ContractModel` connect `ContractModel` to `RoomScene`, `FurnitureAsset`, `test_contract_occupancy.py`, `schema.py`, `test_contracts.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `Bridge` connect `RoomScene` to `Mask`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 82 inferred relationships involving `RoomScene` (e.g. with `Depends` and `description`) actually correct?**
  _`RoomScene` has 82 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `PlanAnnotations` (e.g. with `EdgeHit` and `FloorCaption`) actually correct?**
  _`PlanAnnotations` has 49 INFERRED edges - model-reasoned connections that need verification._
- **Are the 55 inferred relationships involving `ParsedFloorPlan` (e.g. with `Depends` and `description`) actually correct?**
  _`ParsedFloorPlan` has 55 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `ContractModel` (e.g. with `AssetEvidence` and `EvidenceFrame`) actually correct?**
  _`ContractModel` has 6 INFERRED edges - model-reasoned connections that need verification._