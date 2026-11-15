# Graph Report - AI_HACKATHON_PROJECT_1  (2026-11-15)

## Corpus Check
- 172 files · ~275,182 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2505 nodes · 6936 edges · 113 communities (99 shown, 14 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 811 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `93975cff`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- layout_tools.py
- detect_blocked_doors
- test_room_shell.py
- test_segmentation.py
- test_room_align_vision.py
- test_room_align.py
- footprint.py
- Registry
- useStore
- calculate_free_floor_ratio
- FurnitureAsset
- test_reconstruction.py
- Pose2D
- RoomScene
- test_room_parse.py
- test_api.py
- _Room
- regions.py
- parse.py
- detect_collisions
- test_normalisation.py
- Box
- Frame
- scenes.py
- SpatialInputError
- schema.ts
- RoomView.tsx
- SpaceShift 3D representation and asset handoff — design
- models.py
- RequestBudget
- scene
- annotate.py
- detect_front_clearance
- geometry.py
- walk.ts
- spatial_engine/main.py
- compilerOptions
- calculate_brightness_approximation
- routes.py
- generate_mock_glbs.py
- BBoxM
- FloorPlanScreen.tsx
- test_contract_occupancy.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- _by_index
- test_room_routes.py
- compilerOptions
- propose_layout
- mesh_providers.py
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
- store.ts
- _door_frame
- test_agent.py
- Implementation plan: issue #14
- Architecture
- editorControls.test.ts
- scripts
- openings.py
- test_demo_assets.py
- SpaceShift — System Architecture & 4-Developer Execution DAG
- Spatial findings: Dev 3 / Dev 4 handoff
- furniture_model
- mockScene.ts
- Spatial engine
- store_asset
- Asset Handoff Agreement Implementation Plan
- Review Focus
- Review Focus
- Furniture masks and placement evidence — issue #15
- invalid_request
- plugins
- generate-landscapes.ts
- _Budget
- Floor-plan parser (Dev 1)
- Individual furniture meshes with proxy fallback — issue #16
- scripts
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- Furniture mesh normalisation — issue #17
- .to_item
- model_validator
- audit_scene
- test_report.py
- _plan_parts
- frontend/package.json
- ._check_winding
- health
- LayoutProposal
- .__init__
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
1. `RoomScene` - 131 edges
2. `FurnitureAsset` - 68 edges
3. `Registry` - 61 edges
4. `BBoxM` - 53 edges
5. `FurnitureItem` - 51 edges
6. `align_assets()` - 51 edges
7. `Pose2D` - 49 edges
8. `Frame` - 46 edges
9. `SpatialInputError` - 46 edges
10. `reconstruct_furniture()` - 44 edges

## Surprising Connections (you probably didn't know these)
- `test_field_docstrings_reach_openapi()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_scene_rules_are_validated()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_all_home_furniture_urls_have_canonical_models()` --uses--> `RoomScene`  [INFERRED]
  tests/test_demo_assets.py → contracts/schema.py
- `test_dev1_consumes_fixtures_through_the_asset_interface()` --uses--> `FurnitureAsset`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `conform_openings()` --uses--> `Vec2`  [INFERRED]
  services/reconstruction/room/openings.py → contracts/schema.py

## Import Cycles
- None detected.

## Communities (113 total, 14 thin omitted)

### Community 0 - "layout_tools.py"
Cohesion: 0.05
Nodes (76): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+68 more)

### Community 1 - "detect_blocked_doors"
Cohesion: 0.06
Nodes (85): BlockedDoorIssue, ContractModel, BaseModel, BlockedDoorIssue, ClearanceIssue, CollisionIssue, CollisionPart, FengShuiReport (+77 more)

### Community 2 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 3 - "test_segmentation.py"
Cohesion: 0.10
Nodes (69): Rect, _fetch(), MaskError, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, main(), Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the… (+61 more)

### Community 4 - "test_room_align_vision.py"
Cohesion: 0.06
Nodes (57): EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., AlignmentRecord, AlignmentResult, _Capture, main(), pose_error(), FurnitureItem (+49 more)

### Community 5 - "test_room_align.py"
Cohesion: 0.11
Nodes (63): DoorOpening, FurnitureItem, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver (+55 more)

### Community 6 - "footprint.py"
Cohesion: 0.07
Nodes (56): any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach() (+48 more)

### Community 7 - "Registry"
Cohesion: 0.11
Nodes (46): Connection, FalVisionProvider, Reviewed detections keyed by full source frame keys, never by batch position., RecordedProvider, Any, Path, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle. (+38 more)

### Community 8 - "useStore"
Cohesion: 0.07
Nodes (38): App(), ORDER, screenVariants, EditorScreen(), ChatTab(), LibraryTab(), Sidebar(), StatsTab() (+30 more)

### Community 9 - "calculate_free_floor_ratio"
Cohesion: 0.10
Nodes (52): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, item(), FurnitureItem, parametrize (+44 more)

### Community 10 - "FurnitureAsset"
Cohesion: 0.07
Nodes (40): Image, MaskSource, FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., FrameSource, RoomScene, Drop hints that name an unknown asset or wall; keep the most confident per…, _usable_hints() (+32 more)

### Community 11 - "test_reconstruction.py"
Cohesion: 0.10
Nodes (48): inspect_mesh(), MeshError, Exception, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, (triangles, extents) of a usable glTF 2.0 binary; MeshError("invalid_mesh")…, RawMesh, main(), Path (+40 more)

### Community 12 - "Pose2D"
Cohesion: 0.15
Nodes (42): Pose2D, WindowOpening, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., compare_layouts(), Compare to baseline (default original); movement always references original.…, item(), FurnitureItem, parametrize (+34 more)

### Community 13 - "RoomScene"
Cohesion: 0.12
Nodes (40): RoomScene, assemble_scene(), NoFurniture, RoomScene, What a furniture source supplies for one room., The room alone: what parsed rooms get until #16 produces furniture assets., The room with its furniture placed. Never drops the room: a source that fails…, SceneFurniture (+32 more)

### Community 14 - "test_room_parse.py"
Cohesion: 0.13
Nodes (40): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), PlanAnnotations, clear_cache(), Forget assembled scenes (tests, or after the furniture source changes)., skipif (+32 more)

### Community 15 - "test_api.py"
Cohesion: 0.09
Nodes (37): AuditReport, payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422() (+29 more)

### Community 16 - "_Room"
Cohesion: 0.08
Nodes (34): Correction, Facing, _access(), _Choice, _extents(), _front(), _nearby(), _place_default() (+26 more)

### Community 17 - "regions.py"
Cohesion: 0.12
Nodes (36): int32, ImageFloor, Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges() (+28 more)

### Community 18 - "parse.py"
Cohesion: 0.11
Nodes (38): FloorCaption, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance(), _consensus() (+30 more)

### Community 19 - "detect_collisions"
Cohesion: 0.12
Nodes (37): CollisionIssue, detect_collisions(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, item(), part(), CollisionPart (+29 more)

### Community 20 - "test_normalisation.py"
Cohesion: 0.17
Nodes (38): Front, NormalisationError, normalise_mesh(), BBoxM, ValueError, Fit a raw glTF 2.0 binary to the furniture profile, store it and return its…, The raw mesh cannot meet the furniture profile. The message is safe to report;…, assert_fits() (+30 more)

### Community 21 - "Box"
Cohesion: 0.10
Nodes (31): box_pixels(), fal_media_url(), FalSamProvider, GrabCutProvider, MaskProvider, Any, NDArray, Protocol (+23 more)

### Community 22 - "Frame"
Cohesion: 0.14
Nodes (33): DiscoveryProvider, OfflineProvider, Protocol, fal vision proposes instances across full images; reviewed recordings run…, Local SQLite transactions for scene identities and recoverable provider…, Local #14 CLI. Defaults to offline sampling; --live explicitly permits provider…, _diagnostic(), DiscoveredObject (+25 more)

### Community 23 - "scenes.py"
Cohesion: 0.08
Nodes (33): demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), RoomScene, Serve shared demo meshes and generate room shells without frontend asset copies., The shared three-floor fixtures, one whole-floor scene per floor name., Split the shared floor fixtures by wall prefix, in the original floor… (+25 more)

### Community 24 - "SpatialInputError"
Cohesion: 0.10
Nodes (30): BrightnessApproximation, A window-openness proxy for layout comparison, not a lighting simulation., Ratios describe geometric openness, never percentage brightness or lux., WindowOpenness, prepare_scene(), RoomScene, ValueError, A validated domain-input failure whose message is safe to show to the caller. (+22 more)

### Community 25 - "schema.ts"
Cohesion: 0.07
Nodes (34): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_PART_DIMENSION_M (+26 more)

### Community 26 - "RoomView.tsx"
Cohesion: 0.12
Nodes (22): DoorSwings(), floorPlane, Furniture, Mesh(), MeshBoundary, categoryWash, disposeInk(), inkify() (+14 more)

### Community 27 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 28 - "models.py"
Cohesion: 0.08
Nodes (22): BBoxM, CollisionPart, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).…, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), AssetEvidence, NormalisedMesh, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence… (+14 more)

### Community 29 - "RequestBudget"
Cohesion: 0.11
Nodes (22): DiscoveryError, parse_discovery(), Exception, Path, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, Per-run inference submission attempts; cache reads and handle recovery are free., RequestBudget, evidence_for() (+14 more)

### Community 30 - "scene"
Cohesion: 0.17
Nodes (27): OptimiseRequest, ModelReply, Step, interpret(), item(), move(), Any, parametrize (+19 more)

### Community 31 - "annotate.py"
Cohesion: 0.10
Nodes (21): ParsedFloor, AnnotationResult, Compass, FalVisionAnnotator, FixedAnnotator, NullAnnotator, BaseModel, Path (+13 more)

### Community 32 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 33 - "geometry.py"
Cohesion: 0.15
Nodes (25): Polygon, Spatial checks independent of HTTP, mesh loading and provider services., CollisionVolume, front_clearance_zone(), furniture_collision_volumes(), furniture_footprint(), FurnitureGeometry, prepare_furniture() (+17 more)

### Community 34 - "walk.ts"
Cohesion: 0.18
Nodes (21): captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera(), restoreEditorView(), Human() (+13 more)

### Community 35 - "spatial_engine/main.py"
Cohesion: 0.10
Nodes (25): AnthropicLayoutModel, LayoutModel, Protocol, Claude through the official SDK. The loop above owns retries, so the SDK makes…, audit(), _cached_model(), get_interpreter_model(), get_layout_model() (+17 more)

### Community 36 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 37 - "calculate_brightness_approximation"
Cohesion: 0.22
Nodes (25): calculate_brightness_approximation(), RoomScene, Project nearby occupied parts onto each window and union their shadows. The…, item(), FurnitureItem, parametrize, RoomScene, Analytic window-area cases for a declared geometric brightness proxy. (+17 more)

### Community 38 - "routes.py"
Cohesion: 0.11
Nodes (24): description, File, PlanAnnotator, Protocol, plan_id_for(), find_parsed_scene(), get_annotator(), get_plan() (+16 more)

### Community 39 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 40 - "BBoxM"
Cohesion: 0.15
Nodes (21): Category, BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, KnownDimensions, proxy_asset(), proxy_glb(), BBoxM, model_validator (+13 more)

### Community 41 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (20): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+12 more)

### Community 42 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 43 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 44 - "_by_index"
Cohesion: 0.15
Nodes (20): _by_index(), _decode(), _fractions(), _jpeg(), Exception, MonkeyPatch, ndarray, parametrize (+12 more)

### Community 45 - "test_room_routes.py"
Cohesion: 0.16
Nodes (21): bay_room(), _canvas(), l_room(), _png(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),…, L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed., 4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m… (+13 more)

### Community 46 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 47 - "propose_layout"
Cohesion: 0.15
Nodes (19): Outcome, AgentLimits, _explain_result(), _explore(), _interpret(), _Interpretation, _percent(), propose_layout() (+11 more)

### Community 48 - "mesh_providers.py"
Cohesion: 0.13
Nodes (16): ArtifactTooLarge, fetch_bounded(), Exception, A provider artifact exceeded its size cap; nothing was kept., Stream a provider artifact without redirects, enforcing `limit` while reading., FalSam3dProvider, _fetch(), MeshProvider (+8 more)

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
Cohesion: 0.27
Nodes (15): MIN_HEIGHT_OVERLAP_M, MIN_PLAN_OVERLAP_M2, byId(), collisionVolumes(), convexOverlapArea(), covered(), detectBlockedDoors(), detectCollisions() (+7 more)

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
Cohesion: 0.14
Nodes (14): 3D representation and asset handoff, Agent-driven layout recommendations, Backend-owned mock meshes, Bootstrap, Decisions, Frame selection and identity (#14), Furniture alignment (#8), Furniture masks (#15) (+6 more)

### Community 59 - "store.ts"
Cohesion: 0.19
Nodes (13): CatalogItem, bounds(), fitYaw(), Pt, Volume, humanPoseAt(), bump(), ChatMessage (+5 more)

### Community 60 - "_door_frame"
Cohesion: 0.21
Nodes (14): LineString, door_entry_segment(), _door_frame(), _DoorFrame, DoorOpening, WallSegment, WindowOpening, Validate and resolve a door's closed leaf and room side once for all checks. (+6 more)

### Community 61 - "test_agent.py"
Cohesion: 0.23
Nodes (13): ProviderError, Exception, A failed model call. `kind` is safe to log; no key or payload is kept., ToolCall, Request, Response, The agent loop with scripted model replies, and the SDK adapter over a mock…, sdk_model() (+5 more)

### Community 62 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 63 - "Architecture"
Cohesion: 0.17
Nodes (12): Architecture, Backend-provided demo models, Editor play mode, Furniture evidence selection (#14), Furniture masks and placement evidence (#15), Furniture normalisation (#17, PR #54 review), Home screen and intake presentation, Individual furniture meshes and proxies (#16) (+4 more)

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

### Community 70 - "furniture_model"
Cohesion: 0.24
Nodes (11): FileResponse, furniture_model(), legacy_model(), _model_file(), get, Path, Response, Build once per room/process, using the reconstruction service's shell generator. (+3 more)

### Community 71 - "mockScene.ts"
Cohesion: 0.20
Nodes (8): AuditStats(), fixture, freshMockScene(), mockScene, report, scene, item(), room()

### Community 72 - "Spatial engine"
Cohesion: 0.18
Nodes (11): Audit endpoint, Brightness approximation for layout comparison, Free floor area, Front clearance, Internal layout comparison (issue #33), Layout drafts for proposed moves (issue #33), Layout exploration tools (issue #33), Layout suggestions: `POST /solve` (issues #33, #34) (+3 more)

### Community 73 - "store_asset"
Cohesion: 0.27
Nodes (9): APIRouter, asset_router(), Path, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset() (+1 more)

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

### Community 89 - "audit_scene"
Cohesion: 0.33
Nodes (6): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, test_no_configured_model_is_reported_as_unavailable_not_as_a_clean_result(), test_non_brightness_goals_accept_audit_valid_windows()

### Community 90 - "test_report.py"
Cohesion: 0.47
Nodes (5): RoomScene, Regression checks for report composition and request-local geometry reuse., scene(), test_prepared_geometry_cannot_be_passed_to_different_scene(), test_volumes_built_once_per_item_and_not_retained_across_requests()

### Community 91 - "_plan_parts"
Cohesion: 0.33
Nodes (6): _plan_parts(), Any, FurnitureItem, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_fixture_scene_has_no_collisions()

### Community 92 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 94 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 95 - "LayoutProposal"
Cohesion: 0.67
Nodes (3): LayoutProposal, Proposed furniture poses. Only poses change: shell, openings, item IDs and…, test_solve_endpoint_returns_the_contract_and_honest_outcomes()

## Knowledge Gaps
- **347 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+342 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `layout_tools.py`, `detect_blocked_doors`, `test_room_shell.py`, `test_room_align_vision.py`, `test_room_align.py`, `calculate_free_floor_ratio`, `FurnitureAsset`, `Pose2D`, `test_room_parse.py`, `test_api.py`, `_Room`, `parse.py`, `detect_collisions`, `scenes.py`, `SpatialInputError`, `scene`, `detect_front_clearance`, `spatial_engine/main.py`, `calculate_brightness_approximation`, `routes.py`, `generate_mock_glbs.py`, `_by_index`, `test_room_routes.py`, `test_demo_assets.py`, `audit_scene`, `test_report.py`, `._check_winding`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `detect_blocked_doors`, `test_room_align_vision.py`, `test_room_align.py`, `BBoxM`, `test_contract_occupancy.py`, `test_reconstruction.py`, `Pose2D`, `RoomScene`, `_by_index`, `_Room`, `test_normalisation.py`, `scenes.py`, `Frame`, `.to_item`, `models.py`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `detect_front_clearance`, `detect_blocked_doors`, `layout_tools.py`, `geometry.py`, `calculate_brightness_approximation`, `footprint.py`, `calculate_free_floor_ratio`, `FurnitureAsset`, `test_reconstruction.py`, `Pose2D`, `_Room`, `detect_collisions`, `test_normalisation.py`, `models.py`, `scene`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 128 inferred relationships involving `RoomScene` (e.g. with `main()` and `demo_floors()`) actually correct?**
  _`RoomScene` has 128 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `FurnitureAsset` (e.g. with `BBoxM` and `CollisionPart`) actually correct?**
  _`FurnitureAsset` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `Registry` (e.g. with `FalSamProvider` and `GrabCutProvider`) actually correct?**
  _`Registry` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `BBoxM` (e.g. with `template_parts()` and `FurnitureAsset`) actually correct?**
  _`BBoxM` has 50 INFERRED edges - model-reasoned connections that need verification._