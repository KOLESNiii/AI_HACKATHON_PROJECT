# Graph Report - hackathon-project  (2026-11-14)

## Corpus Check
- 117 files · ~123,247 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1387 nodes · 3214 edges · 72 communities (62 shown, 10 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 321 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `72989a46`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- calculate_free_floor_ratio
- schema.ts
- Dev 2 → Dev 1 asset handoff
- parse.py
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
- RoomScene
- health
- .prettierrc.json
- tsconfig.json
- test_contract_occupancy.py
- spaceshift
- fixtures/README.md
- test_api.py
- FurnitureAsset
- SpaceShift 3D representation and asset handoff — design
- scripts
- Asset Handoff Agreement Implementation Plan
- detect_blocked_doors
- detect_out_of_bounds
- test_room_parse.py
- regions.py
- Video frame selection and furniture identity — issue #14
- _plan_parts
- generate_mock_glbs.py
- Dev 4 implementation and integration plan
- polygon.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- Agent Instructions
- Implementation plan: issue #14
- test_room_routes.py
- .to_item
- ui.tsx
- detect_front_clearance
- parse_floor_plan
- useStore
- Floor-plan parser (Dev 1)
- FurnitureItem
- ContractModel
- spatialPreview.ts
- Furniture.tsx
- frontend/package.json
- audit.py
- Sidebar.tsx
- raster.py
- audit_scene
- Vec2
- editorControls.test.ts
- openings.py
- invalid_request
- render_shell_section
- _wire_schema
- test_service_health_and_cors
- @react-three/drei
- vite
- Protocol
- ValueError

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 61 edges
2. `detect_blocked_doors()` - 38 edges
3. `detect_collisions()` - 38 edges
4. `ContractModel` - 32 edges
5. `Discovery` - 32 edges
6. `calculate_free_floor_ratio()` - 32 edges
7. `useStore` - 31 edges
8. `detect_front_clearance()` - 31 edges
9. `calculate_reachable_floor_ratio()` - 31 edges
10. `Registry` - 29 edges

## Surprising Connections (you probably didn't know these)
- `test_field_docstrings_reach_openapi()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_scene_rules_are_validated()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `_build_scene()` --uses--> `Vec2`  [INFERRED]
  services/reconstruction/room/parse.py → contracts/schema.py
- `room_floor_polygon()` --uses--> `Vec2`  [INFERRED]
  services/spatial_engine/geometry.py → contracts/schema.py
- `room()` --uses--> `Vec2`  [INFERRED]
  tests/spatial_engine/test_clearance.py → contracts/schema.py

## Import Cycles
- None detected.

## Communities (72 total, 10 thin omitted)

### Community 0 - "calculate_free_floor_ratio"
Cohesion: 0.10
Nodes (56): CollisionPart, DoorOpening, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, One box of an item's occupied volume, in the item's local frame (the .glb…, calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene (+48 more)

### Community 1 - "schema.ts"
Cohesion: 0.07
Nodes (34): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M, MIN_PLAN_OVERLAP_M2 (+26 more)

### Community 2 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.04
Nodes (43): Architecture, Furniture evidence selection (#14), Spatial audit API, Workstream ownership, 3D representation and asset handoff, Bootstrap, Decisions, Frame selection and identity (#14) (+35 more)

### Community 3 - "parse.py"
Cohesion: 0.12
Nodes (37): FloorCaption, BaseModel, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance() (+29 more)

### Community 4 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 6 - "test_selection.py"
Cohesion: 0.06
Nodes (96): CaptureFixture, Connection, DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery(), Exception (+88 more)

### Community 7 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

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
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 12 - "detect_collisions"
Cohesion: 0.11
Nodes (39): CollisionIssue, CollisionPart, BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, detect_collisions(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding… (+31 more)

### Community 13 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 14 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 15 - "RoomScene"
Cohesion: 0.05
Nodes (88): RoomScene, model_validator, floor_polygon is clockwise in plan view and every wall has the room on its…, int64, build_shell(), _clean(), _clip(), _cross() (+80 more)

### Community 16 - "health"
Cohesion: 0.67
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 19 - "test_contract_occupancy.py"
Cohesion: 0.20
Nodes (17): RoomCaptureInputs, inputs(), item(), part(), FurnitureItem, parametrize, Box collision parts, fixed items and item IDs on the shared contract., test_fixture_category_must_be_fixed() (+9 more)

### Community 27 - "test_api.py"
Cohesion: 0.09
Nodes (36): AuditReport, payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422() (+28 more)

### Community 28 - "FurnitureAsset"
Cohesion: 0.14
Nodes (11): AssetEvidence, EvidenceFrame, FurnitureAsset, NormalisedMesh, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence…, One video frame an asset was seen in. Optional fields are null for fixtures., What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`. (+3 more)

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
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 34 - "test_room_parse.py"
Cohesion: 0.12
Nodes (46): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), PlanAnnotations, skipif, bay_room(), _canvas() (+38 more)

### Community 35 - "regions.py"
Cohesion: 0.12
Nodes (34): int32, Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction() (+26 more)

### Community 36 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 37 - "_plan_parts"
Cohesion: 0.33
Nodes (6): _plan_parts(), Any, FurnitureItem, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_fixture_scene_has_no_collisions()

### Community 38 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 39 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 40 - "polygon.py"
Cohesion: 0.22
Nodes (16): float64, area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), Mask, NDArray (+8 more)

### Community 41 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 42 - "Agent Instructions"
Cohesion: 0.14
Nodes (13): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+5 more)

### Community 43 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 44 - "test_room_routes.py"
Cohesion: 0.22
Nodes (11): health(), get, Process liveness only; does not probe external providers., _png(), client(), fixture, TestClient, Floor-plan routes on the reconstruction service, and the ParsedFloorPlan… (+3 more)

### Community 45 - ".to_item"
Cohesion: 0.33
Nodes (4): Pose2D, FurnitureItem, model_validator, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 46 - "ui.tsx"
Cohesion: 0.13
Nodes (20): App(), FloorPlanScreen(), ProgressScreen(), UploadScreen(), Button(), ButtonProps, Chip(), dotColor (+12 more)

### Community 47 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 48 - "parse_floor_plan"
Cohesion: 0.06
Nodes (43): Depends, description, File, Response, AnnotationResult, Compass, FalVisionAnnotator, FixedAnnotator (+35 more)

### Community 49 - "useStore"
Cohesion: 0.17
Nodes (20): EditorScreen(), Furniture, RoomView(), SelectionTools(), Sidebar(), CatalogItem, freshMockScene(), bounds() (+12 more)

### Community 50 - "Floor-plan parser (Dev 1)"
Cohesion: 0.40
Nodes (4): Floor-plan parser (Dev 1), How it works, Status and limits, Use

### Community 51 - "FurnitureItem"
Cohesion: 0.18
Nodes (22): FurnitureItem, Polygon, CollisionVolume, front_clearance_zone(), furniture_collision_volumes(), furniture_footprint(), FurnitureItem, An item's occupied box transformed into a vertical prism in room space. (+14 more)

### Community 52 - "ContractModel"
Cohesion: 0.12
Nodes (27): ContractModel, BaseModel, ClearanceIssue, CollisionIssue, FengShuiReport, FengShuiSightline, GlareAlert, LayoutProposal (+19 more)

### Community 53 - "spatialPreview.ts"
Cohesion: 0.20
Nodes (19): DoorSwings(), doorSwing(), footprint(), Pt, toWorld(), byId(), collisionVolumes(), convexOverlapArea() (+11 more)

### Community 54 - "Furniture.tsx"
Cohesion: 0.17
Nodes (12): floorPlane, Mesh(), MeshBoundary, categoryWash, disposeInk(), inkify(), inkLine, RotationRing() (+4 more)

### Community 55 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 57 - "audit.py"
Cohesion: 0.21
Nodes (16): Spatial checks independent of HTTP, mesh loading and provider services., FurnitureGeometry, prepare_furniture(), prepare_scene(), RoomScene, ValueError, Metric floor geometry using the coordinate conventions in contracts.schema., A validated domain-input failure whose message is safe to show to the caller. (+8 more)

### Community 58 - "Sidebar.tsx"
Cohesion: 0.14
Nodes (13): AuditStats(), ChatTab(), LibraryTab(), StatsTab(), tabs, catalog, catalogCategories, AgentReply (+5 more)

### Community 59 - "raster.py"
Cohesion: 0.17
Nodes (16): Gray, decode(), estimate_wall_px(), flatten_illumination(), Mask, NDArray, uint8, ValueError (+8 more)

### Community 60 - "audit_scene"
Cohesion: 0.16
Nodes (14): audit(), AuditReport, post, RoomScene, Return current spatial findings; scoring, glare and Feng Shui are not assessed., audit_scene(), AuditReport, RoomScene (+6 more)

### Community 61 - "Vec2"
Cohesion: 0.26
Nodes (14): Vec2, WallSegment, A point on the floor plan (Y omitted)., DoorOpening, LineString, door_entry_segment(), _door_frame(), door_swing_sector() (+6 more)

### Community 62 - "editorControls.test.ts"
Cohesion: 0.32
Nodes (7): editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, initial

### Community 63 - "openings.py"
Cohesion: 0.24
Nodes (11): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+3 more)

### Community 64 - "invalid_request"
Cohesion: 0.28
Nodes (9): exception_handler, JSONResponse, Request, RequestValidationError, invalid_request(), Exception, Keep standard actionable error keys without echoing input or non-JSON values., Programming errors remain 500s; return structured output without leaking… (+1 more)

### Community 65 - "render_shell_section"
Cohesion: 0.40
Nodes (6): ParsedFloor, ndarray, Draw the contract geometry exactly as returned (metres), not the source image:…, Cut every room's shell horizontally at height y and draw the cut, like an…, render_floor(), render_shell_section()

### Community 66 - "_wire_schema"
Cohesion: 0.40
Nodes (5): Any, BaseModel, Field name -> JSON schema with descriptions removed, so docstrings may differ., test_furniture_asset_mirrors_item_without_pose(), _wire_schema()

## Knowledge Gaps
- **266 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `WALK_HEADROOM_M` (+261 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `calculate_free_floor_ratio`, `detect_blocked_doors`, `detect_out_of_bounds`, `parse.py`, `test_room_parse.py`, `generate_mock_glbs.py`, `detect_collisions`, `test_room_routes.py`, `detect_front_clearance`, `parse_floor_plan`, `ContractModel`, `audit.py`, `test_api.py`, `audit_scene`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `ContractModel` connect `ContractModel` to `detect_blocked_doors`, `calculate_free_floor_ratio`, `test_room_parse.py`, `detect_collisions`, `RoomScene`, `FurnitureItem`, `test_api.py`, `FurnitureAsset`, `Vec2`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Why does `_build_scene()` connect `parse.py` to `calculate_free_floor_ratio`, `regions.py`, `RoomScene`, `parse_floor_plan`, `ContractModel`, `Vec2`, `openings.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 58 inferred relationships involving `RoomScene` (e.g. with `main()` and `_build_scene()`) actually correct?**
  _`RoomScene` has 58 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `detect_blocked_doors()` (e.g. with `BlockedDoorIssue` and `RoomScene`) actually correct?**
  _`detect_blocked_doors()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `detect_collisions()` (e.g. with `CollisionIssue` and `FurnitureItem`) actually correct?**
  _`detect_collisions()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `Discovery` (e.g. with `DiscoveryProvider` and `FalVisionProvider`) actually correct?**
  _`Discovery` has 9 INFERRED edges - model-reasoned connections that need verification._