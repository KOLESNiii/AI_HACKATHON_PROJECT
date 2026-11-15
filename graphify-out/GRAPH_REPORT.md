# Graph Report - AI_HACKATHON_PROJECT_1  (2026-11-15)

## Corpus Check
- 175 files · ~276,704 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2529 nodes · 7014 edges · 110 communities (99 shown, 11 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 820 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `815eef36`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- LayoutToolbox
- detect_blocked_doors
- test_room_shell.py
- test_segmentation.py
- FurnitureAsset
- test_room_align.py
- footprint.py
- test_selection.py
- Sidebar.tsx
- calculate_free_floor_ratio
- observe_vision.py
- test_reconstruction.py
- test_objective.py
- RoomScene
- test_room_parse.py
- ContractModel
- Pose2D
- regions.py
- parse.py
- detect_collisions
- BBoxM
- Box
- App.tsx
- demo_assets.py
- layout_tools.py
- schema.ts
- useStore
- SpaceShift 3D representation and asset handoff — design
- test_fixture_scene.py
- reconstruction.py
- test_agent.py
- parse_floor_plan
- detect_front_clearance
- SpatialInputError
- walk.ts
- spatial_engine/main.py
- compilerOptions
- calculate_brightness_approximation
- EvidenceFrame
- generate_mock_glbs.py
- render_room
- FloorPlanScreen.tsx
- test_contract_occupancy.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_room_align_vision.py
- test_room_routes.py
- compilerOptions
- agent.py
- Furniture.tsx
- Video frame selection and furniture identity — issue #14
- dependencies
- devDependencies
- raster.py
- polygon.py
- spatialPreview.ts
- Dev 4 implementation and integration plan
- Dev 2 → Dev 1 asset handoff
- Agent Instructions
- Decisions
- furniture_footprint
- Registry
- ProviderError
- Implementation plan: issue #14
- Architecture
- editorControls.test.ts
- scripts
- openings.py
- test_demo_assets.py
- SpaceShift — System Architecture & 4-Developer Execution DAG
- Spatial findings: Dev 3 / Dev 4 handoff
- hints_from_reply
- .observe
- Spatial engine
- test_cli_places_the_reception_assets_from_recorded_hints
- Asset Handoff Agreement Implementation Plan
- Review Focus
- Review Focus
- Furniture masks and placement evidence — issue #15
- invalid_request
- plugins
- generate-landscapes.ts
- ModelReply
- Floor-plan parser (Dev 1)
- Individual furniture meshes with proxy fallback — issue #16
- scripts
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- Furniture mesh normalisation — issue #17
- .to_item
- health
- test_report.py
- frontend/package.json
- ._check_winding
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- vite
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- spaceshift

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 132 edges
2. `FurnitureAsset` - 68 edges
3. `Registry` - 61 edges
4. `BBoxM` - 53 edges
5. `FurnitureItem` - 51 edges
6. `align_assets()` - 51 edges
7. `SpatialInputError` - 50 edges
8. `Pose2D` - 49 edges
9. `Frame` - 46 edges
10. `reconstruct_furniture()` - 44 edges

## Surprising Connections (you probably didn't know these)
- `test_field_docstrings_reach_openapi()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_scene_rules_are_validated()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_all_home_furniture_urls_have_canonical_models()` --uses--> `RoomScene`  [INFERRED]
  tests/test_demo_assets.py → contracts/schema.py
- `test_evidence_matches_the_agreed_shape()` --uses--> `AssetEvidence`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `test_dev1_consumes_fixtures_through_the_asset_interface()` --uses--> `FurnitureAsset`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py

## Import Cycles
- None detected.

## Communities (110 total, 11 thin omitted)

### Community 0 - "LayoutToolbox"
Cohesion: 0.06
Nodes (70): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+62 more)

### Community 1 - "detect_blocked_doors"
Cohesion: 0.09
Nodes (59): BlockedDoorIssue, BlockedDoorIssue, detect_blocked_doors(), detect_out_of_bounds(), RoomScene, Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item() (+51 more)

### Community 2 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 3 - "test_segmentation.py"
Cohesion: 0.10
Nodes (71): Rect, _fetch(), MaskError, Exception, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, main(), Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads… (+63 more)

### Community 4 - "FurnitureAsset"
Cohesion: 0.06
Nodes (52): FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., AlignmentRecord, AlignmentResult, _Capture, main(), pose_error(), FrameSource (+44 more)

### Community 5 - "test_room_align.py"
Cohesion: 0.11
Nodes (60): FurnitureItem, align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, item_occupied(), FurnitureItem, FixedObserver, NullObserver (+52 more)

### Community 6 - "footprint.py"
Cohesion: 0.06
Nodes (59): DoorOpening, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by() (+51 more)

### Community 7 - "test_selection.py"
Cohesion: 0.09
Nodes (71): DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery(), Exception, Path, Protocol (+63 more)

### Community 8 - "Sidebar.tsx"
Cohesion: 0.09
Nodes (24): EditorScreen(), AuditStats(), ChatTab(), Sidebar(), StatsTab(), tabs, PlayControllerHandle, PlayOverlay() (+16 more)

### Community 9 - "calculate_free_floor_ratio"
Cohesion: 0.09
Nodes (58): CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, audit_scene() (+50 more)

### Community 10 - "observe_vision.py"
Cohesion: 0.23
Nodes (13): Image, _draw_marks(), _encode(), _Mark, _mark_box(), BaseModel, Placement hints from a vision model on fal.ai (`FAL_KEY`). The model is shown a…, The evidence frames worth sending: every asset shown at least once, widest… (+5 more)

### Community 11 - "test_reconstruction.py"
Cohesion: 0.09
Nodes (37): FailureKind, ArtifactTooLarge, fal_media_url(), fetch_bounded(), Instance masks from item boxes (#15): local GrabCut offline, fal SAM 3 when…, A provider artifact exceeded its size cap; nothing was kept., Provider artifacts are fetched over HTTPS from fal's media hosts only., Stream a provider artifact without redirects, enforcing `limit` while reading. (+29 more)

### Community 12 - "test_objective.py"
Cohesion: 0.15
Nodes (43): WindowOpening, compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, item(), FurnitureItem, parametrize (+35 more)

### Community 13 - "RoomScene"
Cohesion: 0.13
Nodes (38): RoomScene, Vec2, A point on the floor plan (Y omitted)., NoFurniture, The room alone: what parsed rooms get until #16 produces furniture assets., build_prompt(), conform_openings(), RoomScene (+30 more)

### Community 14 - "test_room_parse.py"
Cohesion: 0.12
Nodes (42): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), NullAnnotator, PlanAnnotations, No labels: the parser falls back to estimated scale and generic names., clear_cache() (+34 more)

### Community 15 - "ContractModel"
Cohesion: 0.06
Nodes (54): ContractModel, BaseModel, AuditReport, ClearanceIssue, CollisionIssue, FengShuiReport, FengShuiSightline, GlareAlert (+46 more)

### Community 16 - "Pose2D"
Cohesion: 0.09
Nodes (39): Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., Correction, Facing, _access(), _Choice, _extents(), _front() (+31 more)

### Community 17 - "regions.py"
Cohesion: 0.12
Nodes (32): int32, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point() (+24 more)

### Community 18 - "parse.py"
Cohesion: 0.12
Nodes (39): FloorCaption, BaseModel, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance() (+31 more)

### Community 19 - "detect_collisions"
Cohesion: 0.12
Nodes (37): CollisionIssue, detect_collisions(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, item(), part(), CollisionPart (+29 more)

### Community 20 - "BBoxM"
Cohesion: 0.05
Nodes (102): APIRouter, Category, BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, asset_router(), Path, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file… (+94 more)

### Community 21 - "Box"
Cohesion: 0.10
Nodes (30): box_pixels(), FalSamProvider, GrabCutProvider, MaskProvider, Any, NDArray, Protocol, uint8 (+22 more)

### Community 22 - "App.tsx"
Cohesion: 0.13
Nodes (14): App(), ORDER, screenVariants, HomeScreen(), rise, Landscape(), LANDSCAPES, startAt() (+6 more)

### Community 23 - "demo_assets.py"
Cohesion: 0.10
Nodes (29): FileResponse, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file() (+21 more)

### Community 24 - "layout_tools.py"
Cohesion: 0.10
Nodes (21): _Arguments, _CompareArguments, _EvaluateArguments, _InspectArguments, _Move, _point(), BaseModel, Validated layout-exploration tools for an agent. The agent only proposes poses.… (+13 more)

### Community 25 - "schema.ts"
Cohesion: 0.07
Nodes (33): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_PART_DIMENSION_M (+25 more)

### Community 26 - "useStore"
Cohesion: 0.13
Nodes (27): floorPlane, Furniture, Navigation(), RoomView(), RotationRing(), SelectionTools(), LibraryTab(), Human() (+19 more)

### Community 27 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 28 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 29 - "reconstruction.py"
Cohesion: 0.07
Nodes (37): MeshProvider, Protocol, AssetEvidence, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence…, Reconstruct registered furniture. Offline proxies by default; --live uploads to…, choose_view(), _clipped(), _Job (+29 more)

### Community 30 - "test_agent.py"
Cohesion: 0.19
Nodes (35): OptimiseRequest, propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, Step, interpret(), item(), move() (+27 more)

### Community 31 - "parse_floor_plan"
Cohesion: 0.06
Nodes (44): description, File, ParsedFloor, AnnotationResult, Compass, FalVisionAnnotator, FixedAnnotator, PlanAnnotator (+36 more)

### Community 32 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 33 - "SpatialInputError"
Cohesion: 0.11
Nodes (39): WallSegment, LineString, Polygon, Spatial checks independent of HTTP, mesh loading and provider services., CollisionVolume, door_entry_segment(), _door_frame(), door_swing_sector() (+31 more)

### Community 34 - "walk.ts"
Cohesion: 0.14
Nodes (24): WALK_HEADROOM_M, captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera(), restoreEditorView() (+16 more)

### Community 35 - "spatial_engine/main.py"
Cohesion: 0.10
Nodes (36): LayoutProposal, Proposed furniture poses. Only poses change: shell, openings, item IDs and…, LayoutModel, Protocol, ActivityAnchor, assess_feng_shui(), Assessment, DetailModel (+28 more)

### Community 36 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 37 - "calculate_brightness_approximation"
Cohesion: 0.17
Nodes (29): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, A window-openness proxy for layout comparison, not a lighting simulation., Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item() (+21 more)

### Community 38 - "EvidenceFrame"
Cohesion: 0.16
Nodes (19): EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., directory_frames(), FrameSource, Path, Frames of one video stored as `<frame_index>.jpg` or `.png` (upright, as…, The upright frames Dev 2's pipeline stored, for evidence made by…, The #15 instance masks named by `EvidenceFrame.mask_url`, relative to the asset… (+11 more)

### Community 39 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 40 - "render_room"
Cohesion: 0.17
Nodes (12): PlanView, FurnitureItem, Point, RoomScene, Plan view of one room: the picture of the contract geometry that people and the…, Short labels for a room's walls (A, B, ...), in wall order: wall ID -> letter., Room (x, z) of a point given as fractions of the image's width and height., Walls (lettered), windows, door swings and furniture, +X right and +Z down the… (+4 more)

### Community 41 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (20): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+12 more)

### Community 42 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 43 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 44 - "test_room_align_vision.py"
Cohesion: 0.18
Nodes (22): _by_index(), _decode(), _fractions(), _jpeg(), Exception, MonkeyPatch, ndarray, parametrize (+14 more)

### Community 45 - "test_room_routes.py"
Cohesion: 0.14
Nodes (23): ParsedRoom, One room parsed from a floor plan. `scene` uses its floor's shared frame (see…, bay_room(), _canvas(), l_room(), _png(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),… (+15 more)

### Community 46 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 47 - "agent.py"
Cohesion: 0.13
Nodes (14): Outcome, AgentLimits, _Budget, _explain_result(), _explore(), _interpret(), _Interpretation, _percent() (+6 more)

### Community 48 - "Furniture.tsx"
Cohesion: 0.24
Nodes (8): Mesh(), MeshBoundary, categoryWash, disposeInk(), inkify(), inkLine, Shell, inwardNormal()

### Community 49 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 50 - "dependencies"
Cohesion: 0.12
Nodes (17): framer-motion, dependencies, framer-motion, react, react-dom, @react-three/fiber, tailwindcss, @tailwindcss/vite (+9 more)

### Community 51 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, oxlint, prettier, @types/node, @types/react, @types/react-dom, @types/three, typescript (+9 more)

### Community 52 - "raster.py"
Cohesion: 0.17
Nodes (16): Gray, decode(), estimate_wall_px(), flatten_illumination(), Mask, NDArray, uint8, ValueError (+8 more)

### Community 53 - "polygon.py"
Cohesion: 0.22
Nodes (16): area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), float64, Mask, NDArray (+8 more)

### Community 54 - "spatialPreview.ts"
Cohesion: 0.17
Nodes (21): MIN_HEIGHT_OVERLAP_M, MIN_PLAN_OVERLAP_M2, DoorSwings(), doorSwing(), footprint(), Pt, toWorld(), byId() (+13 more)

### Community 55 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 56 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.12
Nodes (16): 10. Room inputs (#5), 1. IDs, 2. What Dev 2 returns, 3. Evidence, 4. Mesh references, 5. Normalisation guarantee, 6. Occupied volume, 7. Dimension provenance (+8 more)

### Community 57 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 58 - "Decisions"
Cohesion: 0.13
Nodes (15): 3D representation and asset handoff, Agent-driven layout recommendations, Backend-owned mock meshes, Bootstrap, Decisions, Feng shui evaluation agent, Frame selection and identity (#14), Furniture alignment (#8) (+7 more)

### Community 59 - "furniture_footprint"
Cohesion: 0.32
Nodes (13): furniture_footprint(), Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, make_item(), FurnitureItem, parametrize, Footprint examples independent of meshes, providers and HTTP routes., test_45_degree_corners_follow_threejs_yaw(), test_does_not_mutate_item() (+5 more)

### Community 60 - "Registry"
Cohesion: 0.24
Nodes (6): Connection, Any, Path, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle., Registry

### Community 61 - "ProviderError"
Cohesion: 0.18
Nodes (11): AnthropicLayoutModel, ProviderError, Exception, A failed model call. `kind` is safe to log; no key or payload is kept., Claude through the official SDK. The loop above owns retries, so the SDK makes…, Request, Response, sdk_model() (+3 more)

### Community 62 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 63 - "Architecture"
Cohesion: 0.15
Nodes (13): Architecture, Backend-provided demo models, Editor play mode, Furniture evidence selection (#14), Furniture masks and placement evidence (#15), Furniture normalisation (#17, PR #54 review), Home screen and intake presentation, Individual furniture meshes and proxies (#16) (+5 more)

### Community 64 - "editorControls.test.ts"
Cohesion: 0.32
Nodes (7): editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, initial

### Community 65 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 66 - "openings.py"
Cohesion: 0.24
Nodes (11): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+3 more)

### Community 67 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 68 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 69 - "Spatial findings: Dev 3 / Dev 4 handoff"
Cohesion: 0.18
Nodes (6): Completion and follow-up, Consuming the findings, HTTP handoff contract, Layout suggestions (`POST /solve`), Load the same examples in the editor and backend, Spatial findings: Dev 3 / Dev 4 handoff

### Community 70 - "hints_from_reply"
Cohesion: 0.25
Nodes (9): _distance_to_wall(), _facing(), hints_from_reply(), Point, RoomScene, WallFrame, Front points away from wall `back`; express that in quarter turns of wall…, Convert the model's plan points and wall letters into wall-relative hints.… (+1 more)

### Community 71 - ".observe"
Cohesion: 0.36
Nodes (4): MaskSource, FalVisionObserver, Asks a vision LLM on fal.ai where each asset stands (`FAL_KEY`). Endpoint and…, One request: the plan (PNG) first, then the frames (JPEG). None when…

### Community 72 - "Spatial engine"
Cohesion: 0.17
Nodes (12): Audit endpoint, Brightness approximation for layout comparison, Feng shui assessment, Free floor area, Front clearance, Internal layout comparison (issue #33), Layout drafts for proposed moves (issue #33), Layout exploration tools (issue #33) (+4 more)

### Community 73 - "test_cli_places_the_reception_assets_from_recorded_hints"
Cohesion: 0.50
Nodes (4): CaptureFixture, Status of a browser URL from the reconstruction app (the proxy strips the…, _served(), test_cli_places_the_reception_assets_from_recorded_hints()

### Community 74 - "Asset Handoff Agreement Implementation Plan"
Cohesion: 0.20
Nodes (9): Asset Handoff Agreement Implementation Plan, Deferred, each under its own issue, Execution notes (2026-11-14), File Structure, Global Constraints, Review Focus, Task 1: Contract additions, Task 2: One fixture scene (+1 more)

### Community 75 - "Review Focus"
Cohesion: 0.20
Nodes (9): Completed verification, Furniture Mesh Reconstruction Implementation Plan, Global Constraints, Review Focus, Task 1: Mesh records, Task 2: Proxy assets and the asset store, Task 3: Pipeline with a test provider, Task 4: Live SAM 3D provider (+1 more)

### Community 76 - "Review Focus"
Cohesion: 0.20
Nodes (9): Execution record, Furniture Segmentation Implementation Plan, Global Constraints, Review Focus, Task 1: Mask records, Task 2: Pipeline with the offline provider, Task 3: Evidence handoff, Task 4: Live SAM 3 provider (+1 more)

### Community 77 - "Furniture masks and placement evidence — issue #15"
Cohesion: 0.22
Nodes (8): Approaches, Design, Furniture masks and placement evidence — issue #15, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 20 requests), Live result (2026-11-14), Needs coordination

### Community 78 - "invalid_request"
Cohesion: 0.28
Nodes (9): exception_handler, JSONResponse, RequestValidationError, invalid_request(), Exception, Request, Programming errors remain 500s; return structured output without leaking…, Keep standard actionable error keys without echoing input or non-JSON values. (+1 more)

### Community 79 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 80 - "generate-landscapes.ts"
Cohesion: 0.22
Nodes (7): file, outDir, page, root, SEEDS, tmp, vendor

### Community 81 - "ModelReply"
Cohesion: 0.24
Nodes (6): ModelReply, Any, ToolCall, Any, RecordedModel, test_route()

### Community 82 - "Floor-plan parser (Dev 1)"
Cohesion: 0.25
Nodes (6): Floor-plan parser (Dev 1), Furniture alignment (#8), How it works, Scene assembly (#9), Status and limits, Use

### Community 83 - "Individual furniture meshes with proxy fallback — issue #16"
Cohesion: 0.25
Nodes (7): Approaches, Design, Individual furniture meshes with proxy fallback — issue #16, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 15 requests for this issue), Needs coordination

### Community 84 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, format, format:check, lint, preview, typecheck

### Community 85 - "SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin"
Cohesion: 0.25
Nodes (8): 1. The Core Differentiator (Why We Beat Existing Tools), 2. What We Stole (And Improved) From Competitors, 3. Full Tech Stack, 4. Quickstart (Local Development), **AI & Generative Media (`services/reconstruction` & `services/media_gen`)**, **Design & Frontend (`frontend/`)**, SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin, **Spatial Audit & Solver Engine (`services/spatial_engine`)**

### Community 86 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

### Community 87 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 88 - "health"
Cohesion: 0.67
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 90 - "test_report.py"
Cohesion: 0.47
Nodes (5): RoomScene, Regression checks for report composition and request-local geometry reuse., scene(), test_prepared_geometry_cannot_be_passed_to_different_scene(), test_volumes_built_once_per_item_and_not_retained_across_requests()

### Community 92 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 94 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

## Knowledge Gaps
- **350 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+345 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `LayoutToolbox`, `detect_blocked_doors`, `test_room_shell.py`, `FurnitureAsset`, `test_room_align.py`, `calculate_free_floor_ratio`, `test_objective.py`, `test_room_parse.py`, `ContractModel`, `Pose2D`, `parse.py`, `detect_collisions`, `demo_assets.py`, `layout_tools.py`, `test_agent.py`, `parse_floor_plan`, `detect_front_clearance`, `SpatialInputError`, `spatial_engine/main.py`, `calculate_brightness_approximation`, `EvidenceFrame`, `generate_mock_glbs.py`, `render_room`, `test_room_align_vision.py`, `test_room_routes.py`, `test_demo_assets.py`, `hints_from_reply`, `.observe`, `test_cli_places_the_reception_assets_from_recorded_hints`, `test_report.py`, `._check_winding`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `test_room_align.py`, `hints_from_reply`, `.observe`, `calculate_free_floor_ratio`, `observe_vision.py`, `test_reconstruction.py`, `test_contract_occupancy.py`, `RoomScene`, `test_room_align_vision.py`, `ContractModel`, `Pose2D`, `BBoxM`, `demo_assets.py`, `.to_item`, `test_fixture_scene.py`, `reconstruction.py`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `detect_front_clearance`, `detect_blocked_doors`, `LayoutToolbox`, `FurnitureAsset`, `calculate_brightness_approximation`, `footprint.py`, `calculate_free_floor_ratio`, `test_reconstruction.py`, `test_objective.py`, `ContractModel`, `Pose2D`, `detect_collisions`, `furniture_footprint`, `test_agent.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 129 inferred relationships involving `RoomScene` (e.g. with `main()` and `demo_floors()`) actually correct?**
  _`RoomScene` has 129 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `FurnitureAsset` (e.g. with `BBoxM` and `CollisionPart`) actually correct?**
  _`FurnitureAsset` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `Registry` (e.g. with `FalSamProvider` and `GrabCutProvider`) actually correct?**
  _`Registry` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `BBoxM` (e.g. with `template_parts()` and `FurnitureAsset`) actually correct?**
  _`BBoxM` has 50 INFERRED edges - model-reasoned connections that need verification._