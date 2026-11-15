# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 278 files · ~422,088 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4187 nodes · 12432 edges · 154 communities (129 shown, 25 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1392 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4d7614d6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- test_scene_cache.py
- test_video_jobs.py
- test_real_room.py
- RoomScene
- audio.test.ts
- catalog.py
- footprint.py
- test_segmentation.py
- test_room_shell.py
- test_room_align.py
- calculate_free_floor_ratio
- Sidebar.tsx
- test_layout_tools.py
- test_delivery.py
- test_selection.py
- App.tsx
- propose_layout
- BBoxM
- test_objective.py
- DraftSession
- regions.py
- test_chat.py
- test_room_correct.py
- test_room_parse.py
- agent.ts
- test_contracts.py
- chat.py
- contracts.ts
- parse.py
- calculate_brightness_approximation
- RoomView.tsx
- walk.ts
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- demo_assets.py
- detect_blocked_doors
- test_feng_shui_optimisation.py
- test_reconstruction.py
- detect_out_of_bounds
- ContractModel
- scenes.py
- score_feng_shui
- compilerOptions
- test_demo_cache.py
- FixedAnnotator
- layoutProgress.test.tsx
- scene_cache.py
- Registry
- generate_mock_glbs.py
- divided_access_room
- test_contract_occupancy.py
- FurnitureAsset
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_room_align_vision.py
- Decisions
- LayoutToolbox
- room
- routes.py
- compilerOptions
- Video frame selection and furniture identity — issue #14
- KnownDimensions
- Dev 2 → Dev 1 asset handoff
- dependencies
- devDependencies
- raster.py
- polygon.py
- Architecture
- Dev 4 implementation and integration plan
- Furniture.tsx
- Agent Instructions
- reconstruct_furniture
- models.py
- test_furniture_search.py
- Implementation plan: issue #14
- Spatial engine
- SpatialInputError
- store.ts
- scripts
- scene_cache/README.md
- SpaceShift — System Architecture & 4-Developer Execution DAG
- Asset Handoff Agreement Implementation Plan
- Review Focus
- Review Focus
- Floor-plan parser (Dev 1)
- Furniture masks and placement evidence — issue #15
- furniture_search.py
- detect_collisions
- generate-landscapes.ts
- Individual furniture meshes with proxy fallback — issue #16
- Furniture asset delivery and checks (#18, Dev 2.6)
- Retailer asset import (#19, Dev 2.7)
- scripts
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- Spatial findings: Dev 3 / Dev 4 handoff
- Furniture mesh normalisation — issue #17
- parse_floor_plan
- align_debug.py
- test_room_routes.py
- README.md
- frontend/package.json
- catalog_router
- _Budget
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- CatalogError
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift
- SKILL.md
- manifest.json
- retailer.py
- fetch_product
- test_demo_assets.py
- vite
- import_product
- openings.py
- Validated, cached demo assets (#20, Dev 2.8)
- .reconstruct
- check_delivery.py
- _store
- Trimesh
- template_parts
- plugins
- test_shared_handoff_case
- _declared_bounds
- demo_cache/README.md
- ArtifactTooLarge
- computed_field
- furniture_proxy
- APIRouter
- Exception
- Protocol
- float64
- Trimesh
- model_validator
- CaptureFixture
- MonkeyPatch
- FloorPlanScreen.tsx
- geometry.ts
- furniture_footprint
- model_validator

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 247 edges
2. `useStore` - 96 edges
3. `FurnitureAsset` - 83 edges
4. `Pose2D` - 80 edges
5. `FurnitureItem` - 79 edges
6. `SpatialInputError` - 75 edges
7. `audit_scene()` - 66 edges
8. `propose_layout()` - 64 edges
9. `BBoxM` - 60 edges
10. `Registry` - 57 edges

## Surprising Connections (you probably didn't know these)
- `test_field_docstrings_reach_openapi()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_scene_rules_are_validated()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_all_home_furniture_urls_have_canonical_models()` --uses--> `RoomScene`  [INFERRED]
  tests/test_demo_assets.py → contracts/schema.py
- `test_audit_report_must_echo_scene()` --uses--> `AuditReport`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_unassessed_audit_fields_round_trip_as_null()` --uses--> `AuditReport`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py

## Import Cycles
- None detected.

## Communities (154 total, 25 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.11
Nodes (48): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., bounds() (+40 more)

### Community 1 - "test_scene_cache.py"
Cohesion: 0.08
Nodes (45): furniture_data_dir(), Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, health(), get, Process liveness only; does not probe external providers., Serve every plan published in `cache_dir` (`routes.restore_plan`); a plan…, restore_published() (+37 more)

### Community 2 - "test_video_jobs.py"
Cohesion: 0.06
Nodes (53): Runner, FurnitureSource, NoFurniture, Protocol, The room alone: what parsed rooms get until #16 produces furniture assets., extracting(), extraction_failed(), ExtractionError (+45 more)

### Community 3 - "test_real_room.py"
Cohesion: 0.08
Nodes (76): Collection, proxy_warning(), clear_cache(), Forget assembled scenes (tests, or after the furniture source changes)., _audit(), auditor(), _clear(), client() (+68 more)

### Community 4 - "RoomScene"
Cohesion: 0.09
Nodes (48): RoomScene, _Capture, Passes hints through and keeps them, so a live run can be recorded., assemble_scene(), assets_of(), RoomScene, One room + its furniture -> the `RoomScene` the editor and the audit load (#9).…, A scene's furniture as pose-less assets with placeholder evidence (no source… (+40 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (23): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+15 more)

### Community 6 - "catalog.py"
Cohesion: 0.06
Nodes (60): Protocol, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, card_like(), ImageProvenance, Retailer products through the shared asset pipeline (#19). A product is…, Download the product image and store it as the item's one source frame., Whether the item's generated mesh is a flat card instead of a piece of…, The product image the item's view was made from. (+52 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (60): DoorOpening, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by() (+52 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.09
Nodes (76): Rect, _fetch(), GrabCutProvider, MaskError, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, No network or cost. Approximate: it can keep floor or an occluder inside the…, main(), Path (+68 more)

### Community 9 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (57): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+49 more)

### Community 11 - "calculate_free_floor_ratio"
Cohesion: 0.07
Nodes (68): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, payload(), Any, Exception (+60 more)

### Community 12 - "Sidebar.tsx"
Cohesion: 0.08
Nodes (29): CatalogPreview(), FengShuiScoreCard(), AuditStats(), ChatTab(), FengShuiSection(), LibraryTab(), Sidebar(), StatsTab() (+21 more)

### Community 13 - "test_layout_tools.py"
Cohesion: 0.21
Nodes (23): evaluate(), item(), move(), Any, FurnitureItem, parametrize, RoomScene, Scripted tool calls: validation, shared budget, duplicates and best-draft… (+15 more)

### Community 14 - "test_delivery.py"
Cohesion: 0.15
Nodes (40): Store a finished, profile-conforming `.glb` and return its `glb_url`., store_asset(), check_placed(), deliver_furniture(), Path, RoomScene, A scene's furniture for Dev 1 to place: per item, its checked mesh or its…, Faults in how a scene carries delivered assets; empty when every asset appears… (+32 more)

### Community 15 - "test_selection.py"
Cohesion: 0.09
Nodes (74): DiscoveryError, DiscoveryProvider, FalVisionProvider, parse_discovery(), Exception, Protocol, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, Reviewed detections keyed by full source frame keys, never by batch position. (+66 more)

### Community 16 - "App.tsx"
Cohesion: 0.08
Nodes (24): App(), ORDER, screenVariants, HomeScreen(), rise, Landscape(), LANDSCAPES, startAt() (+16 more)

### Community 17 - "propose_layout"
Cohesion: 0.08
Nodes (80): OptimiseRequest, AgentLimits, _interpret(), prepare_layout(), propose_layout(), ProviderError, LayoutProposal, OptimiseRequest (+72 more)

### Community 18 - "BBoxM"
Cohesion: 0.17
Nodes (40): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, NormalisedMesh, NormalisationError, normalise_mesh(), BBoxM, ValueError (+32 more)

### Community 19 - "test_objective.py"
Cohesion: 0.12
Nodes (49): WindowOpening, compare_layouts(), evaluate_layout(), LayoutMetrics, Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, No known collisions, boundary violations or blocked doors; not a safety…, item() (+41 more)

### Community 20 - "DraftSession"
Cohesion: 0.10
Nodes (37): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+29 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (32): int32, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point() (+24 more)

### Community 22 - "test_chat.py"
Cohesion: 0.08
Nodes (77): ChatRequest, POST /chat and /chat/stream., add_item(), chat(), ChatRequest, FurnitureItem, ProgressCallback, Validated tool handler. A rejected addition never mutates the caller's scene.… (+69 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.08
Nodes (53): model_validator, floor_polygon is clockwise in plan view and every wall has the room on its…, apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, InvalidScale (+45 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.10
Nodes (51): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), PlanAnnotations, bay_room(), _canvas(), _close() (+43 more)

### Community 25 - "agent.ts"
Cohesion: 0.06
Nodes (60): AuditDiff(), LayoutProposalCard(), PlanDiff(), poseText(), ScoreComparison, useProposalScores(), useLiveAudit(), isLibraryAsset() (+52 more)

### Community 26 - "test_contracts.py"
Cohesion: 0.14
Nodes (20): load_generator(), load_mock(), parametrize, RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must…, solid_at() (+12 more)

### Community 27 - "chat.py"
Cohesion: 0.09
Nodes (36): ChatReply, POST /chat response, and the data of /chat/stream's terminal `reply` event., AddItemArguments, _apply(), _combine(), _error_text(), _percent(), place() (+28 more)

### Community 28 - "contracts.ts"
Cohesion: 0.06
Nodes (46): ChatStreamEvent, GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, LayoutProgressStage, LayoutStreamEvent, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES (+38 more)

### Community 29 - "parse.py"
Cohesion: 0.17
Nodes (27): RoomLabel, _assign_labels(), _bridge_sides(), _caption_distance(), _consensus(), _fallback_scale(), _floor_order(), _floor_scales() (+19 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.18
Nodes (28): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item(), FurnitureItem (+20 more)

### Community 31 - "RoomView.tsx"
Cohesion: 0.12
Nodes (23): EditorScreen(), clock(), ExtractionProgress(), floorPlane, flaggedFor(), RoomView(), SelectionTools(), VersionTree() (+15 more)

### Community 32 - "walk.ts"
Cohesion: 0.08
Nodes (28): WALK_HEADROOM_M, RotationRing(), captureEditorView(), EditorOrbit, EditorView, restoreEditorView(), PlaySession, SessionOptions (+20 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.04
Nodes (91): exception_handler, FengShuiResult, JSONResponse, Outcome, RequestValidationError, profile(), Any, RoomScene (+83 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "demo_assets.py"
Cohesion: 0.10
Nodes (30): FileResponse, demo_room_scenes(), Each demo room with the furniture standing in it, as the editor builds them., demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model() (+22 more)

### Community 36 - "detect_blocked_doors"
Cohesion: 0.20
Nodes (30): BlockedDoorIssue, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize, RoomScene, Door sweep checks using the shared stored hinge and opening conventions. (+22 more)

### Community 37 - "test_feng_shui_optimisation.py"
Cohesion: 0.13
Nodes (26): ModelReply, Any, ToolCall, assess_feng_shui(), FengShuiRequest, LayoutPreferences, What the user asked for, already validated by the server., Any (+18 more)

### Community 38 - "test_reconstruction.py"
Cohesion: 0.07
Nodes (44): Exception, FailureKind, fal_media_url(), Provider artifacts are fetched over HTTPS from fal's media hosts only., _encode_png(), _FalMeshProvider, FalSam3dProvider, FalTrellis2Provider (+36 more)

### Community 39 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 40 - "ContractModel"
Cohesion: 0.08
Nodes (39): ChatErrorEvent, ChatProgressEvent, ChatReplyEvent, ContractModel, _FengShuiModel, LayoutErrorEvent, LayoutProgressEvent, LayoutResultEvent (+31 more)

### Community 41 - "scenes.py"
Cohesion: 0.08
Nodes (39): ge, HTTPException, Query, Assembly, find_parsed_scene(), get_plan(), get_room(), get_shell() (+31 more)

### Community 42 - "score_feng_shui"
Cohesion: 0.10
Nodes (61): FengShuiRequest, POST /feng-shui and /feng-shui/score., FengShuiSightline, RuleScore, _add(), _angle_deg(), _backing(), _balance() (+53 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.05
Nodes (112): Readers never see a partial file., write_atomic(), _gltf_problems(), inspect_asset(), Re-read an asset's stored file and check it against the furniture profile and…, Scene-graph rules of the furniture profile, read from the file's JSON chunk., cache_folder(), CachedFile (+104 more)

### Community 45 - "FixedAnnotator"
Cohesion: 0.09
Nodes (24): AnnotationResult, Compass, FalVisionAnnotator, FixedAnnotator, FloorCaption, NullAnnotator, BaseModel, Path (+16 more)

### Community 46 - "layoutProgress.test.tsx"
Cohesion: 0.11
Nodes (20): HarnessProgress(), HarnessStatus(), VersionTreeView(), DEFAULT_ROOM_ID, proposalSummary(), initial, proposal(), propose() (+12 more)

### Community 47 - "scene_cache.py"
Cohesion: 0.06
Nodes (62): demo_cache_dir(), Path, Where published demo furniture is read from when the pipeline has none (#20).…, Where published scene caches are read from when the service starts (#12).…, scene_cache_dir(), PlanAnnotator, Protocol, _annotator() (+54 more)

### Community 48 - "Registry"
Cohesion: 0.12
Nodes (15): Connection, box_pixels(), FalSamProvider, Any, NDArray, uint8, fal SAM 3 image: every item box of one frame in one request (verified live…, (x0, y0, x1, y1) with at least one pixel, matching `video.crop`. (+7 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "divided_access_room"
Cohesion: 0.40
Nodes (4): divided_access_room(), RoomScene, Shared regression geometry for custom layout access checks., Clearing a wardrobe by moving its blocker behind the divider cuts circulation.

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 52 - "FurnitureAsset"
Cohesion: 0.08
Nodes (49): FurnitureItem, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., Correction, Facing, FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., _access() (+41 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_room_align_vision.py"
Cohesion: 0.05
Nodes (76): Image, MaskSource, EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., main(), Path, build_prompt(), directory_frames() (+68 more)

### Community 55 - "Decisions"
Cohesion: 0.06
Nodes (35): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+27 more)

### Community 56 - "LayoutToolbox"
Cohesion: 0.13
Nodes (26): _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, LayoutToolbox, _metrics(), _Move (+18 more)

### Community 57 - "room"
Cohesion: 0.26
Nodes (19): piece(), FurnitureItem, parametrize, RoomScene, The placement metric: each tradition on hand-built geometry, and honest 'not…, A 6 m square room; the door is on the north (z=0) wall, centred at x=2.5., room(), test_a_bed_whose_foot_points_straight_at_the_door_is_in_coffin_position() (+11 more)

### Community 58 - "routes.py"
Cohesion: 0.08
Nodes (39): BinaryIO, File, Where walkthrough videos uploaded with a floor plan are kept…, upload_dir(), clear_corrections(), get_annotator(), get_extractions(), get_upload_dir() (+31 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "KnownDimensions"
Cohesion: 0.11
Nodes (21): asset_router(), APIRouter, Path, `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., KnownDimensions, proxy_asset(), proxy_glb(), BBoxM (+13 more)

### Community 62 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.10
Nodes (20): 10. Room inputs (#5), 1. IDs, 2. What Dev 2 returns, 3. Evidence, 4. Mesh references, 5. Normalisation guarantee, 6. Occupied volume, 7. Dimension provenance (+12 more)

### Community 63 - "dependencies"
Cohesion: 0.12
Nodes (17): framer-motion, dependencies, framer-motion, react, react-dom, @react-three/fiber, tailwindcss, @tailwindcss/vite (+9 more)

### Community 64 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, oxlint, prettier, @types/node, @types/react, @types/react-dom, @types/three, typescript (+9 more)

### Community 65 - "raster.py"
Cohesion: 0.17
Nodes (16): Gray, decode(), estimate_wall_px(), flatten_illumination(), Mask, NDArray, uint8, ValueError (+8 more)

### Community 66 - "polygon.py"
Cohesion: 0.22
Nodes (16): area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), float64, Mask, NDArray (+8 more)

### Community 67 - "Architecture"
Cohesion: 0.07
Nodes (28): Architecture, Backend-provided demo models, Bundled retailer library, Chat additions and application, Corrections (#11), Demo scene cache (#12), Editor Feng Shui score integration, Editor layout review and live Stats (+20 more)

### Community 68 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "Furniture.tsx"
Cohesion: 0.14
Nodes (24): MeshBoundary, ProxyBox(), FurnitureMesh(), categoryWash, disposeInk(), inkify(), inkLine, Shell (+16 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "reconstruct_furniture"
Cohesion: 0.20
Nodes (23): main(), Path, write_report(), Path, Give every (or each named) item of the scene its own raw mesh, and always a…, reconstruct_furniture(), test_a_mesh_that_cannot_be_normalised_is_delivered_as_its_proxy(), test_a_provider_failure_keeps_both_items_as_proxies() (+15 more)

### Community 72 - "models.py"
Cohesion: 0.06
Nodes (29): fetch(), main(), prepare(), Fetch a balanced, offline IKEA library using only published retailer meshes.…, Reuse bounded, public-only downloads; keep raw evidence outside the project., Expand retailer Draco geometry and expose WebP sources to the shared reader.…, unpack_model(), _along_mesh() (+21 more)

### Community 73 - "test_furniture_search.py"
Cohesion: 0.23
Nodes (17): Exception, No search could run (no key, provider down). The message is safe to show., SearchUnavailable, ikea(), Linkup, product(), Any, Exception (+9 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.11
Nodes (19): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Feng shui score, Free floor area, Front clearance (+11 more)

### Community 76 - "SpatialInputError"
Cohesion: 0.05
Nodes (99): AuditReport, Vec2, WallSegment, A point on the floor plan (Y omitted)., FengShuiReport, height_overlaps(), Spatial checks independent of HTTP, mesh loading and provider services., A window-openness proxy for layout comparison, not a lighting simulation. (+91 more)

### Community 77 - "store.ts"
Cohesion: 0.07
Nodes (56): playCue(), useAudioPreferences, Furniture, editorKey(), handleItemKey(), handleSaveKey(), panCamera(), rotationDegrees (+48 more)

### Community 78 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 80 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 81 - "Asset Handoff Agreement Implementation Plan"
Cohesion: 0.20
Nodes (9): Asset Handoff Agreement Implementation Plan, Deferred, each under its own issue, Execution notes (2026-11-14), File Structure, Global Constraints, Review Focus, Task 1: Contract additions, Task 2: One fixture scene (+1 more)

### Community 82 - "Review Focus"
Cohesion: 0.20
Nodes (9): Completed verification, Furniture Mesh Reconstruction Implementation Plan, Global Constraints, Review Focus, Task 1: Mesh records, Task 2: Proxy assets and the asset store, Task 3: Pipeline with a test provider, Task 4: Live SAM 3D provider (+1 more)

### Community 83 - "Review Focus"
Cohesion: 0.20
Nodes (9): Execution record, Furniture Segmentation Implementation Plan, Global Constraints, Review Focus, Task 1: Mask records, Task 2: Pipeline with the offline provider, Task 3: Evidence handoff, Task 4: Live SAM 3 provider (+1 more)

### Community 84 - "Floor-plan parser (Dev 1)"
Cohesion: 0.18
Nodes (9): Corrections (#11), Demo scene cache (#12), Floor-plan parser (Dev 1), Furniture alignment (#8), How it works, Real-input room (#10), Scene assembly (#9), Status and limits (+1 more)

### Community 85 - "Furniture masks and placement evidence — issue #15"
Cohesion: 0.22
Nodes (8): Approaches, Design, Furniture masks and placement evidence — issue #15, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 20 requests), Live result (2026-11-14), Needs coordination

### Community 86 - "furniture_search.py"
Cohesion: 0.18
Nodes (24): ProductOption, A real retailer product the chat agent found; the editor offers it to add to…, IkeaSearch, PageReader, ProductOption, _host(), _ikea_options(), _linkup_urls() (+16 more)

### Community 87 - "detect_collisions"
Cohesion: 0.09
Nodes (63): ClearanceIssue, CollisionIssue, detect_collisions(), detect_front_clearance(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, Check full-width front access strips, returning one issue per blocker. actual_m…, item() (+55 more)

### Community 88 - "generate-landscapes.ts"
Cohesion: 0.22
Nodes (7): file, outDir, page, root, SEEDS, tmp, vendor

### Community 89 - "Individual furniture meshes with proxy fallback — issue #16"
Cohesion: 0.25
Nodes (7): Approaches, Design, Individual furniture meshes with proxy fallback — issue #16, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 15 requests for this issue), Needs coordination

### Community 90 - "Furniture asset delivery and checks (#18, Dev 2.6)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Furniture asset delivery and checks (#18, Dev 2.6), Goals, Intent, Non-goals, Tests

### Community 91 - "Retailer asset import (#19, Dev 2.7)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Left open, Non-goals, Retailer asset import (#19, Dev 2.7)

### Community 92 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, format, format:check, lint, preview, typecheck

### Community 93 - "SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin"
Cohesion: 0.25
Nodes (8): 1. The Core Differentiator (Why We Beat Existing Tools), 2. What We Stole (And Improved) From Competitors, 3. Full Tech Stack, 4. Quickstart (Local Development), **AI & Generative Media (`services/reconstruction` & `services/media_gen`)**, **Design & Frontend (`frontend/`)**, SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin, **Spatial Audit & Solver Engine (`services/spatial_engine`)**

### Community 94 - "Spatial findings: Dev 3 / Dev 4 handoff"
Cohesion: 0.17
Nodes (12): Bot additions restricted to mesh Library assets, Completion and follow-up, Consuming the findings, Deterministic Feng Shui score in the editor, Editor integration status (issues #32 and #35), HTTP handoff contract, Layout suggestions (`POST /solve`), Live execution updates (+4 more)

### Community 95 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

### Community 96 - "parse_floor_plan"
Cohesion: 0.17
Nodes (16): _bearing(), _build_scene(), parse_floor_plan(), plan_id_for(), ndarray, ParsedFloorPlan, Point, RoomScene (+8 more)

### Community 97 - "align_debug.py"
Cohesion: 0.10
Nodes (24): AlignmentRecord, AlignmentResult, pose_error(), FurnitureItem, Debug CLI for furniture alignment: place assets in a room and draw the result.…, (distance in metres, absolute yaw difference in degrees) between two poses., _report(), BaseModel (+16 more)

### Community 98 - "test_room_routes.py"
Cohesion: 0.23
Nodes (15): _png(), client(), _plan_file(), TestClient, Floor-plan routes on the reconstruction service, and the ParsedFloorPlan…, Uploads in tmp_path; extraction jobs recorded, never run against fal., test_errors(), test_oversized_video_is_rejected() (+7 more)

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "catalog_router"
Cohesion: 0.18
Nodes (13): APIRouter, catalog_router(), Fetch, Path, `fetch` replaces the public downloader (tests)., client(), MonkeyPatch, parametrize (+5 more)

### Community 102 - "_Budget"
Cohesion: 0.21
Nodes (6): LayoutProgress, A factual harness update, never a proposed edit or model reasoning., _Budget, _Counted, Any, Charges the chat budget for the model calls a delegated harness makes.

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "CatalogError"
Cohesion: 0.11
Nodes (20): post, CatalogError, _check_public(), fetch_public(), ValueError, The product cannot be imported at all. The message is safe to show., Refuse anything but http(s) to a public address: an imported URL is untrusted…, Download a public URL with a size cap, re-checking every redirect hop. (+12 more)

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "retailer.py"
Cohesion: 0.09
Nodes (30): HTMLParser, _binary_models(), _dimensions(), _first_url(), _is_type(), _item_text(), _metres(), _model_urls() (+22 more)

### Community 124 - "fetch_product"
Cohesion: 0.20
Nodes (12): fetch_product(), guess_category(), Category, Fetch, Classify the head phrase, using its last furniture or accessory noun.…, Download and read one retailer product page. Raises CatalogError. `source`…, parametrize, test_categories_come_from_the_products_own_words() (+4 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "import_product"
Cohesion: 0.09
Nodes (33): CaptureFixture, computed_field, FurnitureAsset, KnownDimensions, MaskProvider, MonkeyPatch, CatalogImport, import_product() (+25 more)

### Community 128 - "openings.py"
Cohesion: 0.24
Nodes (11): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+3 more)

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 130 - ".reconstruct"
Cohesion: 0.22
Nodes (10): _decode(), item_box(), Mask, NDArray, Registry, RequestBudget, uint8, The next published model that is usable and within the triangle budget. Each… (+2 more)

### Community 131 - "check_delivery.py"
Cohesion: 0.25
Nodes (9): main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), Delivery, computed_field, Every delivered asset passed its checks. Proxies are allowed; they are listed., load_dimensions() (+1 more)

### Community 132 - "_store"
Cohesion: 0.31
Nodes (9): _bounds(), _overlaps(), Mask, NDArray, Path, uint8, Masks of different items should not claim the same pixels; flag it, do not edit…, _store() (+1 more)

### Community 133 - "Trimesh"
Cohesion: 0.25
Nodes (8): float64, _bounds(), _cap_textures(), _load(), NDArray, Path, Every triangle mesh of the file in the file's world frame: node transforms…, Trimesh

### Community 134 - "template_parts"
Cohesion: 0.33
Nodes (5): BBoxM, CollisionPart, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).…, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts()

### Community 135 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 136 - "test_shared_handoff_case"
Cohesion: 0.33
Nodes (4): Any, parametrize, Reusable scene variants and expected findings for Dev 3/4 integration., test_shared_handoff_case()

### Community 137 - "_declared_bounds"
Cohesion: 0.67
Nodes (4): _declared_bounds(), _declared_bounds_problems(), ndarray, The bounds the file declares: the union of its `POSITION` accessors' min/max.…

### Community 139 - "ArtifactTooLarge"
Cohesion: 0.67
Nodes (3): ArtifactTooLarge, Exception, A provider artifact exceeded its size cap; nothing was kept.

### Community 141 - "furniture_proxy"
Cohesion: 0.25
Nodes (8): le, furniture_proxy(), health(), get, gt, Path, Response, Process liveness only; does not probe external providers.

### Community 150 - "FloorPlanScreen.tsx"
Cohesion: 0.14
Nodes (27): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DemoFloor (+19 more)

### Community 152 - "geometry.ts"
Cohesion: 0.16
Nodes (23): MIN_HEIGHT_OVERLAP_M, MIN_PLAN_OVERLAP_M2, DoorSwings(), doorSwing(), fitsRoom(), fitYaw(), footprint(), Pt (+15 more)

### Community 157 - "furniture_footprint"
Cohesion: 0.17
Nodes (25): furniture_footprint(), Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, make_item(), FurnitureItem, parametrize, Footprint examples independent of meshes, providers and HTTP routes., test_45_degree_corners_follow_threejs_yaw(), test_does_not_mutate_item() (+17 more)

## Knowledge Gaps
- **469 isolated node(s):** `imports`, `PlaceReply`, `1. IDs`, `2. What Dev 2 returns`, `3. Evidence` (+464 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `test_scene_cache.py`, `test_video_jobs.py`, `test_real_room.py`, `test_shared_handoff_case`, `test_room_shell.py`, `test_room_align.py`, `calculate_free_floor_ratio`, `test_layout_tools.py`, `test_delivery.py`, `propose_layout`, `test_objective.py`, `DraftSession`, `test_chat.py`, `test_room_correct.py`, `test_room_parse.py`, `test_contracts.py`, `chat.py`, `furniture_footprint`, `calculate_brightness_approximation`, `spatial_engine/main.py`, `demo_assets.py`, `detect_blocked_doors`, `detect_out_of_bounds`, `ContractModel`, `scenes.py`, `score_feng_shui`, `test_demo_cache.py`, `scene_cache.py`, `generate_mock_glbs.py`, `divided_access_room`, `FurnitureAsset`, `test_room_align_vision.py`, `LayoutToolbox`, `room`, `SpatialInputError`, `detect_collisions`, `parse_floor_plan`, `align_debug.py`, `test_room_routes.py`, `test_demo_assets.py`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `align_debug.py`, `check_delivery.py`, `RoomScene`, `demo_assets.py`, `catalog.py`, `reconstruct_furniture`, `models.py`, `ContractModel`, `test_room_align.py`, `test_demo_cache.py`, `test_delivery.py`, `scene_cache.py`, `BBoxM`, `test_contract_occupancy.py`, `test_room_align_vision.py`, `KnownDimensions`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `FurnitureItem` connect `FurnitureAsset` to `test_real_room.py`, `footprint.py`, `test_room_align.py`, `calculate_free_floor_ratio`, `test_layout_tools.py`, `propose_layout`, `BBoxM`, `test_objective.py`, `DraftSession`, `test_chat.py`, `test_room_correct.py`, `chat.py`, `furniture_footprint`, `calculate_brightness_approximation`, `detect_blocked_doors`, `detect_out_of_bounds`, `ContractModel`, `score_feng_shui`, `test_demo_cache.py`, `divided_access_room`, `test_contract_occupancy.py`, `room`, `models.py`, `SpatialInputError`, `detect_collisions`, `align_debug.py`, `catalog_router`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 244 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 244 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `FurnitureAsset` (e.g. with `check_placed()` and `deliver_furniture()`) actually correct?**
  _`FurnitureAsset` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 77 inferred relationships involving `Pose2D` (e.g. with `FurnitureAsset` and `_access()`) actually correct?**
  _`Pose2D` has 77 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `FurnitureItem` (e.g. with `FurnitureAsset` and `align_assets()`) actually correct?**
  _`FurnitureItem` has 76 INFERRED edges - model-reasoned connections that need verification._