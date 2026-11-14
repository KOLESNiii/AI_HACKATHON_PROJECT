# Graph Report - hackathon-project  (2026-11-14)

## Corpus Check
- 123 files · ~131,537 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1518 nodes · 3540 edges · 91 communities (76 shown, 15 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 338 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `abd16707`
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
- mask_providers.py
- detect_out_of_bounds
- .prettierrc.json
- tsconfig.json
- test_contract_occupancy.py
- spaceshift
- fixtures/README.md
- ContractModel
- test_segmentation.py
- SpaceShift 3D representation and asset handoff — design
- scripts
- Asset Handoff Agreement Implementation Plan
- detect_blocked_doors
- FurnitureItem
- test_room_parse.py
- regions.py
- Video frame selection and furniture identity — issue #14
- RoomScene
- generate_mock_glbs.py
- Dev 4 implementation and integration plan
- polygon.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- Agent Instructions
- Implementation plan: issue #14
- parse_floor_plan
- Vec2
- ui.tsx
- detect_front_clearance
- PlanAnnotations
- useStore
- Floor-plan parser (Dev 1)
- audit_scene
- test_contracts.py
- spatialPreview.ts
- Furniture.tsx
- frontend/package.json
- furniture_footprint
- Sidebar.tsx
- raster.py
- Review Focus
- Furniture masks and placement evidence — issue #15
- editorControls.test.ts
- openings.py
- invalid_request
- test_api.py
- FurnitureAsset
- test_service_health_and_cors
- @react-three/drei
- vite
- CollisionPart
- test_room_routes.py
- segment_furniture
- MaskRecord
- Box
- Frame
- Mask
- sam_scene
- test_handoff_cases.py
- test_collision_parts.py
- segment_items.py
- _build_scene
- Decisions
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- Architecture
- Spatial findings: Dev 3 / Dev 4 handoff
- decode
- Spatial engine
- Registry
- RequestBudget

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 61 edges
2. `detect_collisions()` - 38 edges
3. `detect_blocked_doors()` - 38 edges
4. `ContractModel` - 32 edges
5. `Discovery` - 32 edges
6. `calculate_free_floor_ratio()` - 32 edges
7. `segment_furniture()` - 31 edges
8. `calculate_reachable_floor_ratio()` - 31 edges
9. `detect_front_clearance()` - 31 edges
10. `useStore` - 31 edges

## Surprising Connections (you probably didn't know these)
- `test_field_docstrings_reach_openapi()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_scene_rules_are_validated()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_audit_report_must_echo_scene()` --uses--> `AuditReport`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_unassessed_audit_fields_round_trip_as_null()` --uses--> `AuditReport`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `main()` --uses--> `RoomScene`  [INFERRED]
  scripts/generate_mock_glbs.py → contracts/schema.py

## Import Cycles
- None detected.

## Communities (91 total, 15 thin omitted)

### Community 0 - "calculate_free_floor_ratio"
Cohesion: 0.10
Nodes (52): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, item(), FurnitureItem, parametrize (+44 more)

### Community 1 - "schema.ts"
Cohesion: 0.07
Nodes (34): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M, MIN_PLAN_OVERLAP_M2 (+26 more)

### Community 2 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.14
Nodes (14): 10. Room inputs (#5), 1. IDs, 2. What Dev 2 returns, 3. Evidence, 4. Mesh references, 5. Normalisation guarantee, 6. Occupied volume, 7. Dimension provenance (+6 more)

### Community 3 - "parse.py"
Cohesion: 0.15
Nodes (30): FloorCaption, BaseModel, RoomLabel, _assign_labels(), _bridge_sides(), _caption_distance(), _consensus(), _fallback_scale() (+22 more)

### Community 4 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 6 - "test_selection.py"
Cohesion: 0.06
Nodes (83): BaseModel, DiscoveryProvider, model_validator, DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery() (+75 more)

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
Cohesion: 0.19
Nodes (21): CollisionIssue, detect_collisions(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, item(), FurnitureItem, parametrize (+13 more)

### Community 13 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 14 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 15 - "mask_providers.py"
Cohesion: 0.14
Nodes (17): Any, Exception, box_pixels(), FalSamProvider, GrabCutProvider, MaskError, NDArray, Registry (+9 more)

### Community 16 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 19 - "test_contract_occupancy.py"
Cohesion: 0.15
Nodes (22): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+14 more)

### Community 27 - "ContractModel"
Cohesion: 0.10
Nodes (33): ContractModel, BaseModel, AuditReport, BlockedDoorIssue, ClearanceIssue, CollisionIssue, FengShuiReport, FengShuiSightline (+25 more)

### Community 28 - "test_segmentation.py"
Cohesion: 0.19
Nodes (28): MonkeyPatch, Registry, FakeProvider, loose_box(), make_scene(), make_scene_frame_dict(), MaskRecord, Path (+20 more)

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
Cohesion: 0.20
Nodes (30): BlockedDoorIssue, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize, RoomScene, Door sweep checks using the shared stored hinge and opening conventions. (+22 more)

### Community 33 - "FurnitureItem"
Cohesion: 0.15
Nodes (25): FurnitureItem, Polygon, Spatial checks independent of HTTP, mesh loading and provider services., CollisionVolume, front_clearance_zone(), furniture_collision_volumes(), FurnitureGeometry, prepare_furniture() (+17 more)

### Community 34 - "test_room_parse.py"
Cohesion: 0.19
Nodes (29): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, skipif, _close(), _example(), _has_vertex(), _label() (+21 more)

### Community 35 - "regions.py"
Cohesion: 0.12
Nodes (32): int32, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point() (+24 more)

### Community 36 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 37 - "RoomScene"
Cohesion: 0.05
Nodes (88): RoomScene, model_validator, floor_polygon is clockwise in plan view and every wall has the room on its…, int64, build_shell(), _clean(), _clip(), _cross() (+80 more)

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

### Community 44 - "parse_floor_plan"
Cohesion: 0.10
Nodes (26): Depends, description, File, Response, health(), get, Process liveness only; does not probe external providers., parse_floor_plan() (+18 more)

### Community 45 - "Vec2"
Cohesion: 0.23
Nodes (16): DoorOpening, Vec2, WallSegment, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, A point on the floor plan (Y omitted)., DoorOpening, LineString, door_entry_segment() (+8 more)

### Community 46 - "ui.tsx"
Cohesion: 0.12
Nodes (19): App(), FloorPlanScreen(), ProgressScreen(), UploadScreen(), Button(), ButtonProps, Chip(), dotColor (+11 more)

### Community 47 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 48 - "PlanAnnotations"
Cohesion: 0.09
Nodes (28): ParsedFloor, Protocol, AnnotationResult, Compass, _extract_json(), FalVisionAnnotator, FixedAnnotator, NullAnnotator (+20 more)

### Community 49 - "useStore"
Cohesion: 0.17
Nodes (22): EditorScreen(), Furniture, RoomView(), SelectionTools(), LibraryTab(), Sidebar(), CatalogItem, freshMockScene() (+14 more)

### Community 50 - "Floor-plan parser (Dev 1)"
Cohesion: 0.40
Nodes (4): Floor-plan parser (Dev 1), How it works, Status and limits, Use

### Community 51 - "audit_scene"
Cohesion: 0.11
Nodes (19): Path, audit(), health(), AuditReport, get, post, RoomScene, Process liveness only; does not probe external providers. (+11 more)

### Community 52 - "test_contracts.py"
Cohesion: 0.16
Nodes (17): load_generator(), load_mock(), RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must…, solid_at(), test_audit_report_must_echo_scene() (+9 more)

### Community 53 - "spatialPreview.ts"
Cohesion: 0.20
Nodes (19): DoorSwings(), doorSwing(), footprint(), Pt, toWorld(), byId(), collisionVolumes(), convexOverlapArea() (+11 more)

### Community 54 - "Furniture.tsx"
Cohesion: 0.16
Nodes (13): floorPlane, Mesh(), MeshBoundary, categoryWash, disposeInk(), inkify(), inkLine, RotationRing() (+5 more)

### Community 55 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 57 - "furniture_footprint"
Cohesion: 0.32
Nodes (13): furniture_footprint(), Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, make_item(), FurnitureItem, parametrize, Footprint examples independent of meshes, providers and HTTP routes., test_45_degree_corners_follow_threejs_yaw(), test_does_not_mutate_item() (+5 more)

### Community 58 - "Sidebar.tsx"
Cohesion: 0.15
Nodes (11): AuditStats(), ChatTab(), StatsTab(), tabs, catalog, catalogCategories, AgentReply, sendAgentMessage() (+3 more)

### Community 59 - "raster.py"
Cohesion: 0.25
Nodes (10): Gray, estimate_wall_px(), flatten_illumination(), Mask, rasterise(), Image → binary masks: all ink, and the structural strokes that are walls.…, Divide by a smooth estimate of the paper so a photographed printout thresholds…, Thickness of the main walls: the dominant stroke width, weighted towards thick… (+2 more)

### Community 60 - "Review Focus"
Cohesion: 0.20
Nodes (9): Execution record, Furniture Segmentation Implementation Plan, Global Constraints, Review Focus, Task 1: Mask records, Task 2: Pipeline with the offline provider, Task 3: Evidence handoff, Task 4: Live SAM 3 provider (+1 more)

### Community 61 - "Furniture masks and placement evidence — issue #15"
Cohesion: 0.22
Nodes (8): Approaches, Design, Furniture masks and placement evidence — issue #15, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 20 requests), Live result (2026-11-14), Needs coordination

### Community 62 - "editorControls.test.ts"
Cohesion: 0.32
Nodes (7): editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, initial

### Community 63 - "openings.py"
Cohesion: 0.24
Nodes (11): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+3 more)

### Community 64 - "invalid_request"
Cohesion: 0.28
Nodes (9): exception_handler, JSONResponse, Request, RequestValidationError, invalid_request(), Exception, Keep standard actionable error keys without echoing input or non-JSON values., Programming errors remain 500s; return structured output without leaking… (+1 more)

### Community 65 - "test_api.py"
Cohesion: 0.20
Nodes (16): payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422() (+8 more)

### Community 66 - "FurnitureAsset"
Cohesion: 0.09
Nodes (19): Pose2D, AssetEvidence, EvidenceFrame, FurnitureAsset, FurnitureItem, model_validator, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence…, One video frame an asset was seen in. Optional fields are null for fixtures. (+11 more)

### Community 70 - "CollisionPart"
Cohesion: 0.33
Nodes (6): BBoxM, CollisionPart, Canonical metric bounds in the item's local frame: width along X, height along…, One box of an item's occupied volume, in the item's local frame (the .glb…, NormalisedMesh, Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`.

### Community 71 - "test_room_routes.py"
Cohesion: 0.14
Nodes (23): bay_room(), _canvas(), l_room(), _png(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),…, L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed., 4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m… (+15 more)

### Community 72 - "segment_furniture"
Cohesion: 0.17
Nodes (19): MaskProvider, RegistryState, SegmentationResult, _bounds(), _check(), _overlaps(), Box, Frame (+11 more)

### Community 77 - "sam_scene"
Cohesion: 0.14
Nodes (24): FalSamProvider, parametrize, Rect, RequestBudget, box_mask(), iou(), png(), Box (+16 more)

### Community 79 - "test_collision_parts.py"
Cohesion: 0.28
Nodes (15): CollisionPart, item(), part(), FurnitureItem, parametrize, Occupied-volume integration with the merged Dev 2 contract and fixture., test_disjoint_intersections_are_summed(), test_fallback_solid_box_and_fixed_item_are_checked() (+7 more)

### Community 80 - "segment_items.py"
Cohesion: 0.19
Nodes (14): AssetEvidence, MaskProvider, main(), Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the…, write_report(), Mask (+6 more)

### Community 81 - "_build_scene"
Cohesion: 0.31
Nodes (9): _bearing(), _build_scene(), ndarray, Point, RoomScene, Plan bearing (clockwise from -Z) of direction (nx, nz)., _rect_sides_px(), _room_scale() (+1 more)

### Community 82 - "Decisions"
Cohesion: 0.25
Nodes (8): 3D representation and asset handoff, Bootstrap, Decisions, Frame selection and identity (#14), Furniture masks (#15), PR #44 review follow-up, Revised execution plan, Spatial audit without speculative scores

### Community 83 - "SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin"
Cohesion: 0.25
Nodes (8): 1. The Core Differentiator (Why We Beat Existing Tools), 2. What We Stole (And Improved) From Competitors, 3. Full Tech Stack, 4. Quickstart (Local Development), **AI & Generative Media (`services/reconstruction` & `services/media_gen`)**, **Design & Frontend (`frontend/`)**, SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin, **Spatial Audit & Solver Engine (`services/spatial_engine`)**

### Community 84 - "Architecture"
Cohesion: 0.33
Nodes (5): Architecture, Furniture evidence selection (#14), Furniture masks and placement evidence (#15), Spatial audit API, Workstream ownership

### Community 85 - "Spatial findings: Dev 3 / Dev 4 handoff"
Cohesion: 0.33
Nodes (5): Completion and follow-up, Consuming the findings, HTTP handoff contract, Load the same examples in the editor and backend, Spatial findings: Dev 3 / Dev 4 handoff

### Community 86 - "decode"
Cohesion: 0.40
Nodes (6): decode(), NDArray, ValueError, UnreadableImage, test_empty_or_corrupt_image_is_unreadable(), uint8

### Community 87 - "Spatial engine"
Cohesion: 0.33
Nodes (6): Audit endpoint, Free floor area, Front clearance, Reachable walking space, Shared geometry and regression cases, Spatial engine

## Knowledge Gaps
- **283 isolated node(s):** `1. The Core Differentiator (Why We Beat Existing Tools)`, `2. What We Stole (And Improved) From Competitors`, `**Design & Frontend (`frontend/`)**`, `**AI & Generative Media (`services/reconstruction` & `services/media_gen`)**`, `**Spatial Audit & Solver Engine (`services/spatial_engine`)**` (+278 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `calculate_free_floor_ratio`, `detect_blocked_doors`, `FurnitureItem`, `test_api.py`, `test_room_parse.py`, `generate_mock_glbs.py`, `test_room_routes.py`, `parse_floor_plan`, `detect_front_clearance`, `detect_out_of_bounds`, `_build_scene`, `audit_scene`, `test_contracts.py`, `ContractModel`?**
  _High betweenness centrality (0.151) - this node is a cross-community bridge._
- **Why does `ContractModel` connect `ContractModel` to `FurnitureItem`, `test_room_parse.py`, `FurnitureAsset`, `RoomScene`, `CollisionPart`, `Vec2`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `segment_furniture()` connect `segment_furniture` to `test_selection.py`, `sam_scene`, `mask_providers.py`, `segment_items.py`, `test_segmentation.py`, `openings.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 58 inferred relationships involving `RoomScene` (e.g. with `main()` and `_build_scene()`) actually correct?**
  _`RoomScene` has 58 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `detect_collisions()` (e.g. with `CollisionIssue` and `FurnitureItem`) actually correct?**
  _`detect_collisions()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `detect_blocked_doors()` (e.g. with `BlockedDoorIssue` and `RoomScene`) actually correct?**
  _`detect_blocked_doors()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `Discovery` (e.g. with `DiscoveryProvider` and `FalVisionProvider`) actually correct?**
  _`Discovery` has 9 INFERRED edges - model-reasoned connections that need verification._