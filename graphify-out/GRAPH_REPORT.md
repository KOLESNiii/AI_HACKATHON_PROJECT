# Graph Report - hackathon-project  (2026-11-14)

## Corpus Check
- 79 files · ~89,813 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 997 nodes · 2095 edges · 57 communities (48 shown, 9 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 244 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `35fe5c2f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ContractModel
- schema.ts
- Dev 2 → Dev 1 asset handoff
- SpaceShift — Figma Design System & Spatial UI Spec
- SpaceShift — System Architecture & 4-Developer Execution DAG
- CLAUDE.md
- test_selection.py
- compilerOptions
- compilerOptions
- dependencies
- devDependencies
- plugins
- detect_collisions
- scripts
- health
- routes.py
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
- detect_blocked_doors
- detect_out_of_bounds
- test_room_parse.py
- parse.py
- Video frame selection and furniture identity — issue #14
- _plan_parts
- generate_mock_glbs.py
- Dev 4 implementation and integration plan
- raster.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- Agent Instructions
- Implementation plan: issue #14
- test_room_routes.py
- FurnitureItem
- single_room
- BBoxM
- PlanAnnotations
- Spatial findings: Dev 3 / Dev 4 handoff
- Floor-plan parser (Dev 1)
- @react-three/drei
- vite
- Protocol
- ._check_winding
- frontend/package.json

## God Nodes (most connected - your core abstractions)
1. `detect_blocked_doors()` - 34 edges
2. `detect_collisions()` - 34 edges
3. `ContractModel` - 32 edges
4. `Discovery` - 32 edges
5. `Registry` - 29 edges
6. `select_furniture_frames()` - 26 edges
7. `scene()` - 26 edges
8. `RoomScene` - 25 edges
9. `parse_floor_plan()` - 23 edges
10. `detect_out_of_bounds()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `test_field_docstrings_reach_openapi()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_scene_rules_are_validated()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_dev1_consumes_fixtures_through_the_asset_interface()` --uses--> `FurnitureAsset`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `_build_scene()` --uses--> `Vec2`  [INFERRED]
  services/reconstruction/room/parse.py → contracts/schema.py
- `scene()` --uses--> `Vec2`  [INFERRED]
  tests/spatial_engine/test_doors.py → contracts/schema.py

## Import Cycles
- None detected.

## Communities (57 total, 9 thin omitted)

### Community 0 - "ContractModel"
Cohesion: 0.11
Nodes (30): ContractModel, BaseModel, AuditReport, ClearanceIssue, CollisionIssue, DoorOpening, FengShuiReport, FengShuiSightline (+22 more)

### Community 1 - "schema.ts"
Cohesion: 0.06
Nodes (34): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M, MIN_PLAN_OVERLAP_M2 (+26 more)

### Community 2 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.06
Nodes (29): Architecture, Furniture evidence selection (#14), Workstream ownership, 3D representation and asset handoff, Bootstrap, Decisions, Frame selection and identity (#14), Revised execution plan (+21 more)

### Community 3 - "SpaceShift — Figma Design System & Spatial UI Spec"
Cohesion: 0.50
Nodes (3): 1. Aesthetic Direction: "Architectural CAD meets Spatial Glass", 2. Screen Choreography (Zero Clutter), SpaceShift — Figma Design System & Spatial UI Spec

### Community 4 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 6 - "test_selection.py"
Cohesion: 0.06
Nodes (97): CaptureFixture, Connection, Exception, DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery() (+89 more)

### Community 7 - "compilerOptions"
Cohesion: 0.08
Nodes (24): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+16 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 9 - "dependencies"
Cohesion: 0.12
Nodes (17): framer-motion, dependencies, framer-motion, react, react-dom, @react-three/fiber, tailwindcss, @tailwindcss/vite (+9 more)

### Community 10 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, oxlint, prettier, @types/node, @types/react, @types/react-dom, @types/three, typescript (+9 more)

### Community 11 - "plugins"
Cohesion: 0.16
Nodes (11): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, App(), services, oxc (+3 more)

### Community 12 - "detect_collisions"
Cohesion: 0.11
Nodes (41): CollisionIssue, CollisionPart, detect_collisions(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, CollisionVolume, furniture_collision_volumes() (+33 more)

### Community 13 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 14 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 15 - "routes.py"
Cohesion: 0.11
Nodes (19): Depends, description, File, post, health(), get, Process liveness only; does not probe external providers., get_annotator() (+11 more)

### Community 16 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 19 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 27 - "test_contracts.py"
Cohesion: 0.18
Nodes (16): load_generator(), load_mock(), RoomScene, True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must…, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., solid_at(), test_audit_report_must_echo_scene() (+8 more)

### Community 28 - "test_fixture_scene.py"
Cohesion: 0.16
Nodes (7): AssetEvidence, EvidenceFrame, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence…, One video frame an asset was seen in. Optional fields are null for fixtures., The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape()

### Community 29 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 30 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, format, format:check, lint, preview, typecheck

### Community 31 - "Asset Handoff Agreement Implementation Plan"
Cohesion: 0.20
Nodes (9): Asset Handoff Agreement Implementation Plan, Deferred, each under its own issue, Execution notes (2026-11-14), File Structure, Global Constraints, Review Focus, Task 1: Contract additions, Task 2: One fixture scene (+1 more)

### Community 32 - "detect_blocked_doors"
Cohesion: 0.15
Nodes (35): BlockedDoorIssue, BlockedDoorIssue, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize, RoomScene (+27 more)

### Community 33 - "detect_out_of_bounds"
Cohesion: 0.09
Nodes (49): Vec2, A point on the floor plan (Y omitted)., DoorOpening, detect_out_of_bounds(), RoomScene, Spatial checks independent of HTTP, mesh loading and provider services., Return sorted item IDs whose rectangular footprint leaves the interior floor.…, door_swing_sector() (+41 more)

### Community 34 - "test_room_parse.py"
Cohesion: 0.19
Nodes (30): ParsedFloorPlan, RoomScene, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, skipif, _close(), _example(), _has_vertex() (+22 more)

### Community 35 - "parse.py"
Cohesion: 0.05
Nodes (87): int32, FloorCaption, BaseModel, RoomLabel, attach(), door_leaf(), EdgeHit, _ink_along() (+79 more)

### Community 36 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 37 - "_plan_parts"
Cohesion: 0.29
Nodes (7): Polygon, _plan_parts(), Any, FurnitureItem, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_fixture_scene_has_no_collisions()

### Community 38 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): Scene, coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray (+15 more)

### Community 39 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 40 - "raster.py"
Cohesion: 0.10
Nodes (31): float64, Gray, area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), Mask (+23 more)

### Community 41 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.13
Nodes (14): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+6 more)

### Community 42 - "Agent Instructions"
Cohesion: 0.14
Nodes (13): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+5 more)

### Community 43 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 44 - "test_room_routes.py"
Cohesion: 0.22
Nodes (11): TestClient, parametrize, test_service_health_and_cors(), _png(), client(), fixture, Floor-plan routes on the reconstruction service, and the ParsedFloorPlan…, test_errors() (+3 more)

### Community 45 - "FurnitureItem"
Cohesion: 0.24
Nodes (8): FurnitureItem, Pose2D, FurnitureAsset, FurnitureItem, model_validator, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., Dev 1 places the asset: add the pose it aligned from the floor plan., test_furniture_asset_mirrors_item_without_pose()

### Community 46 - "single_room"
Cohesion: 0.33
Nodes (11): bay_room(), _canvas(), l_room(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),…, L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed., 4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m…, Interior 4.0 x 3.0 m at px (200..600, 200..500). Walls 0.2 m outside it. - Door… (+3 more)

### Community 47 - "BBoxM"
Cohesion: 0.33
Nodes (6): BBoxM, CollisionPart, Canonical metric bounds in the item's local frame: width along X, height along…, One box of an item's occupied volume, in the item's local frame (the .glb…, NormalisedMesh, Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`.

### Community 48 - "PlanAnnotations"
Cohesion: 0.09
Nodes (25): ParsedFloor, AnnotationResult, Compass, _extract_json(), FalVisionAnnotator, FixedAnnotator, NullAnnotator, PlanAnnotations (+17 more)

### Community 49 - "Spatial findings: Dev 3 / Dev 4 handoff"
Cohesion: 0.33
Nodes (5): Completion and follow-up, Consuming the findings, HTTP handoff contract, Load the same examples in the editor and backend, Spatial findings: Dev 3 / Dev 4 handoff

### Community 50 - "Floor-plan parser (Dev 1)"
Cohesion: 0.40
Nodes (4): Floor-plan parser (Dev 1), How it works, Status and limits, Use

### Community 55 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

## Knowledge Gaps
- **254 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MIN_PLAN_OVERLAP_M2` (+249 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `test_room_parse.py` to `ContractModel`, `detect_blocked_doors`, `detect_out_of_bounds`, `parse.py`, `generate_mock_glbs.py`, `detect_collisions`, `test_room_routes.py`, `routes.py`, `._check_winding`, `test_contracts.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `UnreadableImage` connect `raster.py` to `test_room_parse.py`, `test_selection.py`, `routes.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `ContractModel` connect `ContractModel` to `detect_blocked_doors`, `detect_out_of_bounds`, `test_room_parse.py`, `FurnitureItem`, `BBoxM`, `test_fixture_scene.py`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `detect_blocked_doors()` (e.g. with `BlockedDoorIssue` and `RoomScene`) actually correct?**
  _`detect_blocked_doors()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `detect_collisions()` (e.g. with `CollisionIssue` and `FurnitureItem`) actually correct?**
  _`detect_collisions()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `Discovery` (e.g. with `DiscoveryProvider` and `FalVisionProvider`) actually correct?**
  _`Discovery` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `ValueError` (e.g. with `._check_collision_parts()` and `._check_winding()`) actually correct?**
  _`ValueError` has 29 INFERRED edges - model-reasoned connections that need verification._