# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 158 files · ~170,469 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1793 nodes · 4500 edges · 98 communities (88 shown, 10 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 434 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7930ffef`
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
- parse_floor_plan
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
- audit_scene
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
- routes.py
- FixedAnnotator
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
- test_contracts.py
- Sidebar.tsx
- raster.py
- Review Focus
- Furniture masks and placement evidence — issue #15
- demo_assets.py
- reconstruct_furniture
- FloorPlanScreen.tsx
- audit.py
- models.py
- test_service_health_and_cors
- @react-three/drei
- vite
- test_selection.py
- Registry
- selection.py
- Bridge
- test_normalisation.py
- calculate_free_floor_ratio
- reconstruction.py
- test_api.py
- mock_room/README.md
- selection_models.py
- proxy_asset
- Individual furniture meshes with proxy fallback — issue #16
- Decisions
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- Architecture
- Spatial findings: Dev 3 / Dev 4 handoff
- decode
- Spatial engine
- PlanAnnotations
- _build_scene
- ndarray
- _plan_parts
- Review Focus
- invalid_request
- reconstruct_items.py
- Furniture mesh normalisation — issue #17
- BaseModel

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 62 edges
2. `Registry` - 54 edges
3. `segment_furniture()` - 43 edges
4. `useStore` - 41 edges
5. `detect_collisions()` - 38 edges
6. `detect_blocked_doors()` - 38 edges
7. `reconstruct_furniture()` - 37 edges
8. `RequestBudget` - 36 edges
9. `Frame` - 36 edges
10. `Box` - 34 edges

## Surprising Connections (you probably didn't know these)
- `test_field_docstrings_reach_openapi()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_scene_rules_are_validated()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_all_home_furniture_urls_have_canonical_models()` --uses--> `RoomScene`  [INFERRED]
  tests/test_demo_assets.py → contracts/schema.py
- `test_implausible_estimates_are_refused_without_storing_an_asset()` --uses--> `NormalisationError`  [INFERRED]
  tests/reconstruction/assets/test_normalisation.py → services/reconstruction/assets/normalisation.py
- `test_unusable_or_over_budget_meshes_are_refused_and_nothing_is_stored()` --uses--> `NormalisationError`  [INFERRED]
  tests/reconstruction/assets/test_normalisation.py → services/reconstruction/assets/normalisation.py

## Import Cycles
- None detected.

## Communities (98 total, 10 thin omitted)

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
Cohesion: 0.13
Nodes (31): Compass, FloorCaption, BaseModel, RoomLabel, _assign_labels(), _bridge_sides(), _caption_distance(), _consensus() (+23 more)

### Community 4 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 6 - "RequestBudget"
Cohesion: 0.08
Nodes (38): box_pixels(), FalSamProvider, GrabCutProvider, MaskProvider, Any, NDArray, Protocol, uint8 (+30 more)

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
Cohesion: 0.07
Nodes (62): CollisionIssue, CollisionPart, BBoxM, FurnitureItem, model_validator, Canonical metric bounds in the item's local frame: width along X, height along…, floor_polygon is clockwise in plan view and every wall has the room on its…, detect_collisions() (+54 more)

### Community 13 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 14 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 15 - "parse_floor_plan"
Cohesion: 0.11
Nodes (24): Depends, description, File, ParsedFloor, PlanAnnotator, Protocol, main(), ndarray (+16 more)

### Community 16 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 19 - "ValueError"
Cohesion: 0.27
Nodes (3): model_validator, model_validator, ValueError

### Community 27 - "ContractModel"
Cohesion: 0.13
Nodes (24): ContractModel, BaseModel, ClearanceIssue, CollisionIssue, FengShuiSightline, GlareAlert, LayoutProposal, OptimiseRequest (+16 more)

### Community 28 - "test_segmentation.py"
Cohesion: 0.11
Nodes (62): Rect, _fetch(), MaskError, Exception, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, Store a mask and cut-out for every selected view of the scene's (or the named)…, Resolve an `EvidenceFrame.mask_url` (relative to the asset data directory)., read_mask() (+54 more)

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
Cohesion: 0.14
Nodes (37): BlockedDoorIssue, BlockedDoorIssue, CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem (+29 more)

### Community 33 - "audit_scene"
Cohesion: 0.12
Nodes (18): audit(), health(), AuditReport, get, post, RoomScene, Process liveness only; does not probe external providers., Return current spatial findings; scoring, glare and Feng Shui are not assessed. (+10 more)

### Community 34 - "test_room_parse.py"
Cohesion: 0.20
Nodes (28): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, skipif, _close(), _example(), _has_vertex(), _label() (+20 more)

### Community 35 - "regions.py"
Cohesion: 0.14
Nodes (31): int32, Raster, _accept(), _cast(), draw_bridges(), _end_direction(), _exit_point(), find_bridges() (+23 more)

### Community 36 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 37 - "RoomScene"
Cohesion: 0.05
Nodes (85): RoomScene, int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad() (+77 more)

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

### Community 44 - "routes.py"
Cohesion: 0.18
Nodes (13): health(), get, Process liveness only; does not probe external providers., _find_scene(), get_plan(), get_room(), get_shell(), get (+5 more)

### Community 45 - "FixedAnnotator"
Cohesion: 0.16
Nodes (16): FixedAnnotator, Path, Returns pre-recorded annotations (tests, the debug CLI, cached demo plans)., _png(), Interior 4.0 x 3.0 m at px (200..600, 200..500). Walls 0.2 m outside it. - Door…, single_room(), client(), TestClient (+8 more)

### Community 46 - "ui.tsx"
Cohesion: 0.16
Nodes (16): App(), EditorScreen(), Sidebar(), ProgressScreen(), UploadScreen(), Button(), ButtonProps, Chip() (+8 more)

### Community 47 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 48 - "test_reconstruction.py"
Cohesion: 0.12
Nodes (26): FalSam3dProvider, _fetch(), inspect_mesh(), MeshError, MeshProvider, One raw mesh per furniture item (#16), from a source frame and the item's #15…, fal SAM 3D Objects: one frame and one item mask per request (verified live…, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP… (+18 more)

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
Cohesion: 0.15
Nodes (22): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+14 more)

### Community 53 - "RoomView.tsx"
Cohesion: 0.14
Nodes (21): DoorSwings(), MeshBoundary, Navigation(), RoomView(), doorSwing(), Pt, byId(), collisionVolumes() (+13 more)

### Community 54 - "geometry.ts"
Cohesion: 0.18
Nodes (16): floorPlane, Furniture, Mesh(), categoryWash, disposeInk(), inkify(), inkLine, RotationRing() (+8 more)

### Community 55 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 57 - "test_contracts.py"
Cohesion: 0.14
Nodes (22): AuditReport, FengShuiReport, load_generator(), load_mock(), parametrize, RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are… (+14 more)

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
Cohesion: 0.10
Nodes (26): FileResponse, demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file(), get, Path (+18 more)

### Community 63 - "reconstruct_furniture"
Cohesion: 0.16
Nodes (24): Frame, KnownDimensions, MaskRecord, MeshProvider, ReconstructionResult, SelectedObject, choose_view(), _clipped() (+16 more)

### Community 64 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (20): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+12 more)

### Community 65 - "audit.py"
Cohesion: 0.13
Nodes (32): DoorOpening, Vec2, WallSegment, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, A point on the floor plan (Y omitted)., DoorOpening, LineString, Polygon (+24 more)

### Community 66 - "models.py"
Cohesion: 0.11
Nodes (13): Pose2D, AssetEvidence, FurnitureAsset, NormalisedMesh, FurnitureItem, model_validator, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence…, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence. (+5 more)

### Community 70 - "test_selection.py"
Cohesion: 0.14
Nodes (43): FalVisionProvider, Reviewed detections keyed by full source frame keys, never by batch position., RecordedProvider, main(), Path, Full-resolution source artifacts stay separate; the report shows boxes and IDs., write_report(), _diagnostic() (+35 more)

### Community 71 - "Registry"
Cohesion: 0.24
Nodes (6): Connection, Any, Path, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle., Registry

### Community 72 - "selection.py"
Cohesion: 0.13
Nodes (36): EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., DiscoveryError, DiscoveryProvider, OfflineProvider, parse_discovery(), Exception, Path (+28 more)

### Community 73 - "Bridge"
Cohesion: 0.17
Nodes (15): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+7 more)

### Community 74 - "test_normalisation.py"
Cohesion: 0.18
Nodes (36): Front, NormalisedMesh, parametrize, Scene, normalise_mesh(), BBoxM, Fit a raw glTF 2.0 binary to the furniture profile, store it and return its…, assert_fits() (+28 more)

### Community 75 - "calculate_free_floor_ratio"
Cohesion: 0.24
Nodes (23): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, item(), FurnitureItem, parametrize, RoomScene, Free floor area is distinct from reachable walking space., room() (+15 more)

### Community 76 - "reconstruction.py"
Cohesion: 0.11
Nodes (22): float64, NDArray, asset_router(), Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset() (+14 more)

### Community 77 - "test_api.py"
Cohesion: 0.20
Nodes (16): payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422() (+8 more)

### Community 79 - "selection_models.py"
Cohesion: 0.13
Nodes (20): BaseModel, DiscoveredObject, ItemReconstruction, MaskRecord, MeshFailure, MeshRecord, MissingMask, Internal #14-#16 records. Source evidence is deliberately separate from… (+12 more)

### Community 80 - "proxy_asset"
Cohesion: 0.15
Nodes (16): AssetEvidence, Category, FurnitureAsset, BBoxM, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), KnownDimensions, proxy_asset() (+8 more)

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
Cohesion: 0.20
Nodes (10): Architecture, Backend-provided demo models, Editor play mode, Furniture evidence selection (#14), Furniture masks and placement evidence (#15), Furniture normalisation (#17, PR #54 review), Individual furniture meshes and proxies (#16), Scene assembly route (#9) (+2 more)

### Community 85 - "Spatial findings: Dev 3 / Dev 4 handoff"
Cohesion: 0.33
Nodes (5): Completion and follow-up, Consuming the findings, HTTP handoff contract, Load the same examples in the editor and backend, Spatial findings: Dev 3 / Dev 4 handoff

### Community 86 - "decode"
Cohesion: 0.40
Nodes (6): decode(), NDArray, uint8, ValueError, UnreadableImage, test_empty_or_corrupt_image_is_unreadable()

### Community 87 - "Spatial engine"
Cohesion: 0.29
Nodes (6): Audit endpoint, Free floor area, Front clearance, Reachable walking space, Shared geometry and regression cases, Spatial engine

### Community 89 - "PlanAnnotations"
Cohesion: 0.15
Nodes (13): AnnotationResult, _extract_json(), FalVisionAnnotator, NullAnnotator, PlanAnnotations, What computer vision cannot read off a floor plan: room labels with their…, Reads labels with a vision LLM on fal.ai (`FAL_KEY`). The endpoint and model…, Plans print labels in capitals ("BEDROOM (4)"); show them in title case. (+5 more)

### Community 90 - "_build_scene"
Cohesion: 0.33
Nodes (7): _bearing(), _build_scene(), Point, RoomScene, Plan bearing (clockwise from -Z) of direction (nx, nz)., RoomGeometry, _wall_thickness_px()

### Community 91 - "ndarray"
Cohesion: 0.39
Nodes (9): bay_room(), _canvas(), l_room(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),…, L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed., 4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m…, two_rooms() (+1 more)

### Community 92 - "_plan_parts"
Cohesion: 0.33
Nodes (6): _plan_parts(), Any, FurnitureItem, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_fixture_scene_has_no_collisions()

### Community 93 - "Review Focus"
Cohesion: 0.20
Nodes (9): Completed verification, Furniture Mesh Reconstruction Implementation Plan, Global Constraints, Review Focus, Task 1: Mesh records, Task 2: Proxy assets and the asset store, Task 3: Pipeline with a test provider, Task 4: Live SAM 3D provider (+1 more)

### Community 94 - "invalid_request"
Cohesion: 0.28
Nodes (9): exception_handler, JSONResponse, Request, RequestValidationError, invalid_request(), Exception, Keep standard actionable error keys without echoing input or non-JSON values., Programming errors remain 500s; return structured output without leaking… (+1 more)

### Community 95 - "reconstruct_items.py"
Cohesion: 0.43
Nodes (6): main(), Path, Reconstruct registered furniture. Offline proxies by default; --live uploads to…, write_report(), ReconstructionResult, test_cli_accepts_known_dimensions()

### Community 96 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

## Knowledge Gaps
- **318 isolated node(s):** `Workstream ownership`, `Furniture evidence selection (#14)`, `Furniture masks and placement evidence (#15)`, `Spatial audit API`, `Editor play mode` (+313 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `detect_blocked_doors`, `audit.py`, `audit_scene`, `calculate_reachable_floor_ratio`, `test_room_parse.py`, `generate_mock_glbs.py`, `calculate_free_floor_ratio`, `detect_collisions`, `routes.py`, `test_api.py`, `detect_front_clearance`, `detect_out_of_bounds`, `FixedAnnotator`, `test_contracts.py`, `_build_scene`, `ContractModel`, `demo_assets.py`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **Why does `ContractModel` connect `ContractModel` to `detect_blocked_doors`, `audit.py`, `test_room_parse.py`, `models.py`, `RoomScene`, `selection.py`, `detect_collisions`, `test_contracts.py`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `attach()` connect `Bridge` to `parse.py`, `test_segmentation.py`, `reconstruct_furniture`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 59 inferred relationships involving `RoomScene` (e.g. with `main()` and `demo_rooms()`) actually correct?**
  _`RoomScene` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `Registry` (e.g. with `FalSamProvider` and `GrabCutProvider`) actually correct?**
  _`Registry` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `segment_furniture()` (e.g. with `MaskProvider` and `Box`) actually correct?**
  _`segment_furniture()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `detect_collisions()` (e.g. with `CollisionIssue` and `FurnitureItem`) actually correct?**
  _`detect_collisions()` has 3 INFERRED edges - model-reasoned connections that need verification._