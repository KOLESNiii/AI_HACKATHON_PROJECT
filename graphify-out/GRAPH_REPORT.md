# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 158 files · ~169,877 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1779 nodes · 4473 edges · 100 communities (89 shown, 11 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 439 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9ae381c1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- calculate_reachable_floor_ratio
- schema.ts
- Dev 2 → Dev 1 asset handoff
- parse.py
- SpaceShift — System Architecture & 4-Developer Execution DAG
- CLAUDE.md
- RequestBudget
- compilerOptions
- compilerOptions
- dependencies
- devDependencies
- plugins
- detect_collisions
- scripts
- health
- routes.py
- detect_out_of_bounds
- .prettierrc.json
- tsconfig.json
- ValueError
- spaceshift
- fixtures/README.md
- ContractModel
- test_segmentation.py
- SpaceShift 3D representation and asset handoff — design
- scripts
- Asset Handoff Agreement Implementation Plan
- detect_blocked_doors
- FurnitureItem
- _rooms
- regions.py
- Video frame selection and furniture identity — issue #14
- RoomScene
- generate_mock_glbs.py
- Dev 4 implementation and integration plan
- polygon.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- Agent Instructions
- Implementation plan: issue #14
- parse_plan
- test_room_routes.py
- ui.tsx
- detect_front_clearance
- test_reconstruction.py
- useStore
- Floor-plan parser (Dev 1)
- walk.ts
- test_contract_occupancy.py
- RoomView.tsx
- geometry.ts
- frontend/package.json
- furniture_footprint
- Sidebar.tsx
- raster.py
- Review Focus
- Furniture masks and placement evidence — issue #15
- demo_assets.py
- reconstruct_furniture
- FloorPlanScreen.tsx
- Vec2
- shell.py
- test_service_health_and_cors
- @react-three/drei
- vite
- test_selection.py
- Registry
- selection.py
- Bridge
- test_normalisation.py
- calculate_free_floor_ratio
- normalise_mesh
- test_shared_handoff_case
- mock_room/README.md
- selection_models.py
- BBoxM
- Individual furniture meshes with proxy fallback — issue #16
- Decisions
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- Architecture
- Spatial findings: Dev 3 / Dev 4 handoff
- test_room_parse.py
- Spatial engine
- FixedAnnotator
- test_demo_assets.py
- single_room
- PlanAnnotations
- Review Focus
- invalid_request
- KnownDimensions
- Furniture mesh normalisation — issue #17
- ._check_winding
- _inside
- BaseModel

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 62 edges
2. `Registry` - 54 edges
3. `segment_furniture()` - 43 edges
4. `useStore` - 41 edges
5. `Frame` - 40 edges
6. `detect_collisions()` - 38 edges
7. `detect_blocked_doors()` - 38 edges
8. `reconstruct_furniture()` - 37 edges
9. `RequestBudget` - 36 edges
10. `Box` - 34 edges

## Surprising Connections (you probably didn't know these)
- `test_field_docstrings_reach_openapi()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_scene_rules_are_validated()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_all_home_furniture_urls_have_canonical_models()` --uses--> `RoomScene`  [INFERRED]
  tests/test_demo_assets.py → contracts/schema.py
- `test_evidence_matches_the_agreed_shape()` --uses--> `AssetEvidence`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `test_unusable_or_over_budget_meshes_are_refused_and_nothing_is_stored()` --uses--> `NormalisationError`  [INFERRED]
  tests/reconstruction/assets/test_normalisation.py → services/reconstruction/assets/normalisation.py

## Import Cycles
- None detected.

## Communities (100 total, 11 thin omitted)

### Community 0 - "calculate_reachable_floor_ratio"
Cohesion: 0.17
Nodes (29): calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, divided_room(), obstacle(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 1 - "schema.ts"
Cohesion: 0.07
Nodes (34): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M, MIN_PLAN_OVERLAP_M2 (+26 more)

### Community 2 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.12
Nodes (16): 10. Room inputs (#5), 1. IDs, 2. What Dev 2 returns, 3. Evidence, 4. Mesh references, 5. Normalisation guarantee, 6. Occupied volume, 7. Dimension provenance (+8 more)

### Community 3 - "parse.py"
Cohesion: 0.14
Nodes (32): RoomLabel, _assign_labels(), _bridge_sides(), _caption_distance(), _consensus(), _fallback_scale(), _floor_order(), _floor_scales() (+24 more)

### Community 4 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 6 - "RequestBudget"
Cohesion: 0.08
Nodes (48): box_pixels(), FalSamProvider, _fetch(), GrabCutProvider, MaskError, MaskProvider, Any, Exception (+40 more)

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
Cohesion: 0.12
Nodes (37): CollisionIssue, CollisionPart, detect_collisions(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, item(), part() (+29 more)

### Community 13 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 14 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 15 - "routes.py"
Cohesion: 0.14
Nodes (18): ParsedFloor, FalVisionAnnotator, PlanAnnotator, Protocol, What computer vision cannot read off a floor plan: room labels with their…, Reads labels with a vision LLM on fal.ai (`FAL_KEY`). The endpoint and model…, Plans print labels in capitals ("BEDROOM (4)"); show them in title case., _tidy_name() (+10 more)

### Community 16 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 19 - "ValueError"
Cohesion: 0.27
Nodes (3): model_validator, model_validator, ValueError

### Community 27 - "ContractModel"
Cohesion: 0.05
Nodes (62): ContractModel, BaseModel, AuditReport, ClearanceIssue, CollisionIssue, FengShuiReport, FengShuiSightline, GlareAlert (+54 more)

### Community 28 - "test_segmentation.py"
Cohesion: 0.12
Nodes (59): Rect, Store a mask and cut-out for every selected view of the scene's (or the named)…, segment_furniture(), Sighting, test_mesh_record_belongs_to_a_sighting_and_goes_stale_with_its_mask(), box_mask(), FakeProvider, iou() (+51 more)

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
Cohesion: 0.19
Nodes (31): BlockedDoorIssue, BlockedDoorIssue, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize, RoomScene (+23 more)

### Community 33 - "FurnitureItem"
Cohesion: 0.08
Nodes (42): FurnitureItem, Polygon, Spatial checks independent of HTTP, mesh loading and provider services., CollisionVolume, front_clearance_zone(), furniture_collision_volumes(), FurnitureGeometry, prepare_furniture() (+34 more)

### Community 34 - "_rooms"
Cohesion: 0.23
Nodes (17): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, skipif, _close(), _example(), _has_vertex(), ParsedFloorPlan (+9 more)

### Community 35 - "regions.py"
Cohesion: 0.13
Nodes (33): int32, Raster, _accept(), _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point() (+25 more)

### Community 36 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 37 - "RoomScene"
Cohesion: 0.12
Nodes (43): RoomScene, build_shell(), Scene, The room shell as a trimesh Scene with nodes `floor`, `ceiling`, `wall_<id>`., shell_glb(), corner_probes(), invalid_footprints(), _l_door() (+35 more)

### Community 38 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 39 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 40 - "polygon.py"
Cohesion: 0.24
Nodes (15): area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), Mask, NDArray, Point (+7 more)

### Community 41 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 42 - "Agent Instructions"
Cohesion: 0.14
Nodes (13): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+5 more)

### Community 43 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 44 - "parse_plan"
Cohesion: 0.13
Nodes (17): Depends, description, File, _find_scene(), get_plan(), get_room(), get_shell(), parse_plan() (+9 more)

### Community 45 - "test_room_routes.py"
Cohesion: 0.18
Nodes (13): health(), get, Process liveness only; does not probe external providers., _png(), client(), TestClient, Floor-plan routes on the reconstruction service, and the ParsedFloorPlan…, test_errors() (+5 more)

### Community 46 - "ui.tsx"
Cohesion: 0.16
Nodes (16): App(), EditorScreen(), Sidebar(), ProgressScreen(), UploadScreen(), Button(), ButtonProps, Chip() (+8 more)

### Community 47 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 48 - "test_reconstruction.py"
Cohesion: 0.14
Nodes (22): FalSam3dProvider, _fetch(), inspect_mesh(), MeshError, MeshProvider, One raw mesh per furniture item (#16), from a source frame and the item's #15…, fal SAM 3D Objects: one frame and one item mask per request (verified live…, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP… (+14 more)

### Community 49 - "useStore"
Cohesion: 0.15
Nodes (20): editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, CatalogItem, bounds() (+12 more)

### Community 50 - "Floor-plan parser (Dev 1)"
Cohesion: 0.40
Nodes (4): Floor-plan parser (Dev 1), How it works, Status and limits, Use

### Community 51 - "walk.ts"
Cohesion: 0.16
Nodes (23): captureEditorView(), EditorOrbit, EditorView, floor, PlayControllerHandle, pointOnFloor(), resizePlayCamera(), restoreEditorView() (+15 more)

### Community 52 - "test_contract_occupancy.py"
Cohesion: 0.06
Nodes (37): Pose2D, RoomCaptureInputs, FurnitureAsset, FurnitureItem, model_validator, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., Dev 1 places the asset: add the pose it aligned from the floor plan., inputs() (+29 more)

### Community 53 - "RoomView.tsx"
Cohesion: 0.14
Nodes (21): DoorSwings(), MeshBoundary, Navigation(), RoomView(), doorSwing(), Pt, byId(), collisionVolumes() (+13 more)

### Community 54 - "geometry.ts"
Cohesion: 0.18
Nodes (16): floorPlane, Furniture, Mesh(), categoryWash, disposeInk(), inkify(), inkLine, RotationRing() (+8 more)

### Community 55 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 57 - "furniture_footprint"
Cohesion: 0.32
Nodes (13): furniture_footprint(), Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, make_item(), FurnitureItem, parametrize, Footprint examples independent of meshes, providers and HTTP routes., test_45_degree_corners_follow_threejs_yaw(), test_does_not_mutate_item() (+5 more)

### Community 58 - "Sidebar.tsx"
Cohesion: 0.10
Nodes (18): AuditStats(), ChatTab(), LibraryTab(), StatsTab(), tabs, catalog, catalogCategories, fixture (+10 more)

### Community 59 - "raster.py"
Cohesion: 0.25
Nodes (10): Gray, estimate_wall_px(), flatten_illumination(), Mask, rasterise(), Image → binary masks: all ink, and the structural strokes that are walls.…, Divide by a smooth estimate of the paper so a photographed printout thresholds…, Thickness of the main walls: the dominant stroke width, weighted towards thick… (+2 more)

### Community 60 - "Review Focus"
Cohesion: 0.20
Nodes (9): Execution record, Furniture Segmentation Implementation Plan, Global Constraints, Review Focus, Task 1: Mask records, Task 2: Pipeline with the offline provider, Task 3: Evidence handoff, Task 4: Live SAM 3 provider (+1 more)

### Community 61 - "Furniture masks and placement evidence — issue #15"
Cohesion: 0.22
Nodes (8): Approaches, Design, Furniture masks and placement evidence — issue #15, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 20 requests), Live result (2026-11-14), Needs coordination

### Community 62 - "demo_assets.py"
Cohesion: 0.18
Nodes (16): FileResponse, demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file(), get, Path (+8 more)

### Community 63 - "reconstruct_furniture"
Cohesion: 0.22
Nodes (19): MeshProvider, choose_view(), _clipped(), Path, The one masked view to reconstruct from: confident, then whole, then large., Give every (or each named) item of the scene its own raw mesh, and always a…, reconstruct_furniture(), test_a_mesh_that_cannot_be_normalised_keeps_its_proxy_and_says_so() (+11 more)

### Community 64 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (20): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+12 more)

### Community 65 - "Vec2"
Cohesion: 0.23
Nodes (16): DoorOpening, Vec2, WallSegment, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, A point on the floor plan (Y omitted)., DoorOpening, LineString, door_entry_segment() (+8 more)

### Community 66 - "shell.py"
Cohesion: 0.10
Nodes (38): int64, _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key(), _miter() (+30 more)

### Community 70 - "test_selection.py"
Cohesion: 0.16
Nodes (34): DiscoveryError, Exception, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, _diagnostic(), DiscoveredObject, RegistryState, Conservative exact-evidence/reference matching; deliberately no custom…, reconcile() (+26 more)

### Community 71 - "Registry"
Cohesion: 0.20
Nodes (7): Connection, Any, Path, Local SQLite transactions for scene identities and recoverable provider…, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle., Registry

### Community 72 - "selection.py"
Cohesion: 0.12
Nodes (43): DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery(), Path, Protocol, fal vision proposes instances across full images; reviewed recordings run…, Reviewed detections keyed by full source frame keys, never by batch position. (+35 more)

### Community 73 - "Bridge"
Cohesion: 0.14
Nodes (19): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+11 more)

### Community 74 - "test_normalisation.py"
Cohesion: 0.19
Nodes (28): Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., parametrize, Scene, assert_fits(), chair_like(), gltf_json(), BBoxM (+20 more)

### Community 75 - "calculate_free_floor_ratio"
Cohesion: 0.22
Nodes (25): CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, item(), FurnitureItem, parametrize, RoomScene (+17 more)

### Community 76 - "normalise_mesh"
Cohesion: 0.12
Nodes (22): float64, Front, NDArray, NormalisedMesh, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, BBoxM, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).…, The category's parts inside `bbox`, or `[]` (one solid box) for solid… (+14 more)

### Community 77 - "test_shared_handoff_case"
Cohesion: 0.33
Nodes (4): Any, parametrize, Reusable scene variants and expected findings for Dev 3/4 integration., test_shared_handoff_case()

### Community 79 - "selection_models.py"
Cohesion: 0.13
Nodes (18): BaseModel, EvidenceFrame, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence…, One video frame an asset was seen in. Optional fields are null for fixtures., _Job, Masked views -> one stored raw mesh per item, or an explicit failure, and…, ItemReconstruction, MaskRecord (+10 more)

### Community 80 - "BBoxM"
Cohesion: 0.11
Nodes (22): AssetEvidence, Category, BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, FurnitureAsset, asset_router(), Readers never see a partial file., Store a finished, profile-conforming `.glb` and return its `glb_url`. (+14 more)

### Community 81 - "Individual furniture meshes with proxy fallback — issue #16"
Cohesion: 0.25
Nodes (7): Approaches, Design, Individual furniture meshes with proxy fallback — issue #16, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 15 requests for this issue), Needs coordination

### Community 82 - "Decisions"
Cohesion: 0.20
Nodes (10): 3D representation and asset handoff, Backend-owned mock meshes, Bootstrap, Decisions, Frame selection and identity (#14), Furniture masks (#15), Human-scale room preview, PR #44 review follow-up (+2 more)

### Community 83 - "SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin"
Cohesion: 0.25
Nodes (8): 1. The Core Differentiator (Why We Beat Existing Tools), 2. What We Stole (And Improved) From Competitors, 3. Full Tech Stack, 4. Quickstart (Local Development), **AI & Generative Media (`services/reconstruction` & `services/media_gen`)**, **Design & Frontend (`frontend/`)**, SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin, **Spatial Audit & Solver Engine (`services/spatial_engine`)**

### Community 84 - "Architecture"
Cohesion: 0.29
Nodes (7): Architecture, Backend-provided demo models, Editor play mode, Furniture evidence selection (#14), Furniture masks and placement evidence (#15), Spatial audit API, Workstream ownership

### Community 85 - "Spatial findings: Dev 3 / Dev 4 handoff"
Cohesion: 0.33
Nodes (5): Completion and follow-up, Consuming the findings, HTTP handoff contract, Load the same examples in the editor and backend, Spatial findings: Dev 3 / Dev 4 handoff

### Community 86 - "test_room_parse.py"
Cohesion: 0.18
Nodes (13): _extract_json(), FloorCaption, decode(), NDArray, uint8, ValueError, UnreadableImage, MonkeyPatch (+5 more)

### Community 87 - "Spatial engine"
Cohesion: 0.29
Nodes (6): Audit endpoint, Free floor area, Front clearance, Reachable walking space, Shared geometry and regression cases, Spatial engine

### Community 89 - "FixedAnnotator"
Cohesion: 0.15
Nodes (8): AnnotationResult, Compass, FixedAnnotator, NullAnnotator, BaseModel, Path, No labels: the parser falls back to estimated scale and generic names., Returns pre-recorded annotations (tests, the debug CLI, cached demo plans).

### Community 90 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 91 - "single_room"
Cohesion: 0.29
Nodes (12): bay_room(), _canvas(), l_room(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),…, L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed., 4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m…, Interior 4.0 x 3.0 m at px (200..600, 200..500). Walls 0.2 m outside it. - Door… (+4 more)

### Community 92 - "PlanAnnotations"
Cohesion: 0.40
Nodes (11): PlanAnnotations, _label(), _parse(), Two identical rooms printed as 3 x 3 m and 6 x 6 m: no scale satisfies both, so…, single_plan(), test_bay_window_on_a_diagonal_wall(), test_compass_sets_north_and_window_azimuth(), test_conflicting_labels_are_not_trusted_as_measured() (+3 more)

### Community 93 - "Review Focus"
Cohesion: 0.20
Nodes (9): Completed verification, Furniture Mesh Reconstruction Implementation Plan, Global Constraints, Review Focus, Task 1: Mesh records, Task 2: Proxy assets and the asset store, Task 3: Pipeline with a test provider, Task 4: Live SAM 3D provider (+1 more)

### Community 94 - "invalid_request"
Cohesion: 0.28
Nodes (9): exception_handler, JSONResponse, Request, RequestValidationError, invalid_request(), Exception, Keep standard actionable error keys without echoing input or non-JSON values., Programming errors remain 500s; return structured output without leaking… (+1 more)

### Community 95 - "KnownDimensions"
Cohesion: 0.33
Nodes (8): KnownDimensions, A size someone can vouch for, with where it came from., main(), Path, Reconstruct registered furniture. Offline proxies by default; --live uploads to…, write_report(), ReconstructionResult, test_cli_accepts_known_dimensions()

### Community 96 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

### Community 98 - "_inside"
Cohesion: 0.50
Nodes (4): _inside(), ndarray, Trimesh, Ray parity in plain numpy (Moller-Trumbore), so the probes need no SciPy or…

## Knowledge Gaps
- **315 isolated node(s):** `Intent`, `What the stored meshes showed (2026-11-15, no provider requests)`, `Approaches`, `Design`, `Calls made by the author, open to correction` (+310 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `calculate_reachable_floor_ratio`, `detect_collisions`, `detect_out_of_bounds`, `ContractModel`, `detect_blocked_doors`, `FurnitureItem`, `_rooms`, `generate_mock_glbs.py`, `parse_plan`, `test_room_routes.py`, `detect_front_clearance`, `demo_assets.py`, `shell.py`, `Bridge`, `calculate_free_floor_ratio`, `test_shared_handoff_case`, `test_demo_assets.py`, `single_room`, `._check_winding`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `ContractModel` connect `ContractModel` to `detect_blocked_doors`, `Vec2`, `FurnitureItem`, `_rooms`, `RoomScene`, `RequestBudget`, `test_normalisation.py`, `calculate_free_floor_ratio`, `selection_models.py`, `BBoxM`, `test_contract_occupancy.py`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `attach()` connect `Bridge` to `parse.py`, `test_segmentation.py`, `reconstruct_furniture`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 59 inferred relationships involving `RoomScene` (e.g. with `main()` and `demo_rooms()`) actually correct?**
  _`RoomScene` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `Registry` (e.g. with `FalSamProvider` and `GrabCutProvider`) actually correct?**
  _`Registry` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `segment_furniture()` (e.g. with `MaskProvider` and `Box`) actually correct?**
  _`segment_furniture()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `Frame` (e.g. with `FalSamProvider` and `GrabCutProvider`) actually correct?**
  _`Frame` has 19 INFERRED edges - model-reasoned connections that need verification._