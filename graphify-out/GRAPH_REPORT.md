# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 262 files · ~404,079 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3836 nodes · 11452 edges · 132 communities (116 shown, 16 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1310 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `af20e02b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- test_scene_cache.py
- test_room_align_vision.py
- RoomScene
- test_scene_routes.py
- audio.test.ts
- models.py
- footprint.py
- test_segmentation.py
- selection_models.py
- test_room_align.py
- calculate_free_floor_ratio
- test_delivery.py
- Box
- BBoxM
- test_selection.py
- react
- propose_layout
- single_room
- Pose2D
- LayoutToolbox
- regions.py
- test_chat.py
- test_room_correct.py
- test_room_parse.py
- test_reconstruction.py
- test_contracts.py
- detect_blocked_doors
- contracts.ts
- parse.py
- calculate_brightness_approximation
- test_demo_cache_room.py
- walk.ts
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- geometry.ts
- test_room_shell.py
- test_feng_shui_optimisation.py
- scenes.py
- agent.ts
- ContractModel
- demo_assets.py
- score_feng_shui
- compilerOptions
- test_demo_cache.py
- .to_item
- Sidebar.tsx
- detect_out_of_bounds
- FloorPlanScreen.tsx
- generate_mock_glbs.py
- Vec2
- test_contract_occupancy.py
- FurnitureAsset
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- AnnotationResult
- Decisions
- test_report.py
- audit_scene
- scene_cache.py
- compilerOptions
- Video frame selection and furniture identity — issue #14
- RoomView.tsx
- Dev 2 → Dev 1 asset handoff
- dependencies
- devDependencies
- raster.py
- polygon.py
- Architecture
- Dev 4 implementation and integration plan
- AnthropicLayoutModel
- Agent Instructions
- validate_feng_shui_request
- test_fixture_scene.py
- Registry
- Implementation plan: issue #14
- Spatial engine
- detect_front_clearance
- store.ts
- scripts
- scene_cache/README.md
- SpaceShift — System Architecture & 4-Developer Execution DAG
- Asset Handoff Agreement Implementation Plan
- Review Focus
- Review Focus
- Floor-plan parser (Dev 1)
- Furniture masks and placement evidence — issue #15
- detect_collisions
- generate-landscapes.ts
- Individual furniture meshes with proxy fallback — issue #16
- Furniture asset delivery and checks (#18, Dev 2.6)
- Retailer asset import (#19, Dev 2.7)
- scripts
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- Spatial findings: Dev 3 / Dev 4 handoff
- Furniture mesh normalisation — issue #17
- furniture_footprint
- model_validator
- README.md
- frontend/package.json
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift
- SKILL.md
- manifest.json
- retailer.py
- agent.py
- test_demo_assets.py
- vite
- catalog.py
- Validated, cached demo assets (#20, Dev 2.8)
- PlayLighting.tsx
- test_streaming.py
- SpatialInputError
- AuditReport
- plugins
- demo_cache/README.md
- RetailerModelProvider
- furniture_proxy

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 225 edges
2. `FurnitureAsset` - 91 edges
3. `useStore` - 81 edges
4. `BBoxM` - 79 edges
5. `Pose2D` - 74 edges
6. `FurnitureItem` - 71 edges
7. `Registry` - 69 edges
8. `SpatialInputError` - 66 edges
9. `propose_layout()` - 64 edges
10. `reconstruct_furniture()` - 57 edges

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

## Communities (132 total, 16 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.09
Nodes (52): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., guess_category() (+44 more)

### Community 1 - "test_scene_cache.py"
Cohesion: 0.08
Nodes (45): clear_corrections(), Serve every plan as parsed again (tests)., Serve a published plan (`scene_cache.py`, #12) as if it had been uploaded and…, restore_plan(), Serve every plan published in `cache_dir` (`routes.restore_plan`); a plan…, restore_published(), _audit(), auditor() (+37 more)

### Community 2 - "test_room_align_vision.py"
Cohesion: 0.06
Nodes (61): Image, MaskSource, build_prompt(), _distance_to_wall(), _draw_marks(), _encode(), _facing(), FalVisionObserver (+53 more)

### Community 3 - "RoomScene"
Cohesion: 0.09
Nodes (74): Collection, RoomScene, clear_cache(), Forget assembled scenes (tests, or after the furniture source changes)., _audit(), auditor(), _clear(), client() (+66 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.11
Nodes (43): assemble_scene(), NoFurniture, RoomScene, What a furniture source supplies for one room., The room alone: what parsed rooms get until #16 produces furniture assets., The room with its furniture placed. Never drops the room: a source that fails…, SceneFurniture, conform_openings() (+35 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 6 - "models.py"
Cohesion: 0.06
Nodes (48): fetch(), main(), prepare(), Fetch a balanced, offline IKEA library using only published retailer meshes.…, Reuse bounded, public-only downloads; keep raw evidence outside the project., Expand retailer Draco geometry and expose WebP sources to the shared reader.…, unpack_model(), _along_mesh() (+40 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (60): any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach() (+52 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.12
Nodes (59): Rect, Store a mask and cut-out for every selected view of the scene's (or the named)…, Resolve an `EvidenceFrame.mask_url` (relative to the asset data directory)., read_mask(), segment_furniture(), Sighting, test_mesh_record_belongs_to_a_sighting_and_goes_stale_with_its_mask(), box_mask() (+51 more)

### Community 9 - "selection_models.py"
Cohesion: 0.11
Nodes (33): Download the product image and store it as the item's one source frame., _store_image(), Local SQLite transactions for scene identities and recoverable provider…, main(), Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the…, write_report() (+25 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (57): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+49 more)

### Community 11 - "calculate_free_floor_ratio"
Cohesion: 0.10
Nodes (52): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, item(), FurnitureItem, parametrize (+44 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.09
Nodes (54): APIRouter, asset_router(), Path, Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset(), main(), Path (+46 more)

### Community 13 - "Box"
Cohesion: 0.08
Nodes (39): ArtifactTooLarge, box_pixels(), fal_media_url(), FalSamProvider, _fetch(), fetch_bounded(), GrabCutProvider, MaskError (+31 more)

### Community 14 - "BBoxM"
Cohesion: 0.11
Nodes (55): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, BBoxM, CollisionPart, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).…, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts() (+47 more)

### Community 15 - "test_selection.py"
Cohesion: 0.13
Nodes (47): FalVisionProvider, Reviewed detections keyed by full source frame keys, never by batch position., RecordedProvider, main(), Path, Local #14 CLI. Defaults to offline sampling; --live explicitly permits provider…, Full-resolution source artifacts stay separate; the report shows boxes and IDs., write_report() (+39 more)

### Community 16 - "react"
Cohesion: 0.09
Nodes (29): App(), ORDER, screenVariants, EditorScreen(), useLiveAudit(), VersionTree(), HomeScreen(), rise (+21 more)

### Community 17 - "propose_layout"
Cohesion: 0.14
Nodes (53): OptimiseRequest, propose_layout(), ProviderError, LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, A failed model call. `kind` is safe to log; no key or payload is kept., Step, interpret() (+45 more)

### Community 18 - "single_room"
Cohesion: 0.16
Nodes (21): bay_room(), _canvas(), l_room(), _png(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),…, L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed., 4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m… (+13 more)

### Community 19 - "Pose2D"
Cohesion: 0.07
Nodes (82): FengShuiRequest, Pose2D, WindowOpening, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., POST /feng-shui and /feng-shui/score., beats_original(), _check_comparable(), compare_evaluations() (+74 more)

### Community 20 - "LayoutToolbox"
Cohesion: 0.05
Nodes (77): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+69 more)

### Community 21 - "regions.py"
Cohesion: 0.13
Nodes (33): int32, Raster, _accept(), _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point() (+25 more)

### Community 22 - "test_chat.py"
Cohesion: 0.06
Nodes (76): ChatRequest, POST /chat and /chat/stream., add_item(), AddItemArguments, chat(), _percent(), AuditReport, BaseModel (+68 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.07
Nodes (53): model_validator, floor_polygon is clockwise in plan view and every wall has the room on its…, AlignmentRecord, BaseModel, How one asset's pose was decided. Keyed by the asset's stable ID., apply_pose_edit(), carry_furniture(), corrected_shell_url() (+45 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.12
Nodes (39): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), NullAnnotator, PlanAnnotations, No labels: the parser falls back to estimated scale and generic names., _close() (+31 more)

### Community 25 - "test_reconstruction.py"
Cohesion: 0.09
Nodes (41): RuntimeError, inspect_mesh(), MeshError, Any, Exception, Mask, NDArray, uint8 (+33 more)

### Community 26 - "test_contracts.py"
Cohesion: 0.14
Nodes (20): load_generator(), load_mock(), parametrize, RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must…, solid_at() (+12 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.15
Nodes (35): BlockedDoorIssue, BlockedDoorIssue, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize, RoomScene (+27 more)

### Community 28 - "contracts.ts"
Cohesion: 0.06
Nodes (47): ChatStreamEvent, GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, LayoutProgressStage, LayoutStreamEvent, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES (+39 more)

### Community 29 - "parse.py"
Cohesion: 0.08
Nodes (50): Compass, FloorCaption, BaseModel, RoomLabel, attach(), door_leaf(), EdgeHit, _ink_along() (+42 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.18
Nodes (28): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item(), FurnitureItem (+20 more)

### Community 31 - "test_demo_cache_room.py"
Cohesion: 0.07
Nodes (51): broken_cache(), from_demo_cache(), geometry_mismatch(), geometry_warning(), load_bindings(), proxy_warning(), Path, RoomScene (+43 more)

### Community 32 - "walk.ts"
Cohesion: 0.10
Nodes (27): captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera(), restoreEditorView(), PlayController() (+19 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.06
Nodes (54): exception_handler, FengShuiResult, JSONResponse, RequestValidationError, demo_room_scenes(), profile(), Any, RoomScene (+46 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "geometry.ts"
Cohesion: 0.18
Nodes (21): DoorSwings(), clampToFloor(), doorSwing(), fitsRoom(), fitYaw(), footprint(), snapToNearestWall(), toWorld() (+13 more)

### Community 36 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 37 - "test_feng_shui_optimisation.py"
Cohesion: 0.13
Nodes (26): ModelReply, Any, ToolCall, assess_feng_shui(), FengShuiRequest, LayoutPreferences, What the user asked for, already validated by the server., Any (+18 more)

### Community 38 - "scenes.py"
Cohesion: 0.05
Nodes (57): ge, HTTPException, Query, demo_cache_dir(), furniture_data_dir(), Path, Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served… (+49 more)

### Community 39 - "agent.ts"
Cohesion: 0.06
Nodes (60): AuditDiff(), LayoutProposalCard(), PlanDiff(), poseText(), ScoreComparison, useProposalScores(), isLibraryAsset(), AgentReply (+52 more)

### Community 40 - "ContractModel"
Cohesion: 0.08
Nodes (41): ChatErrorEvent, ChatProgressEvent, ChatReplyEvent, ContractModel, _FengShuiModel, LayoutErrorEvent, LayoutProgressEvent, LayoutResultEvent (+33 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.12
Nodes (26): FileResponse, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file() (+18 more)

### Community 42 - "score_feng_shui"
Cohesion: 0.16
Nodes (40): FengShuiSightline, FengShuiSightline, RuleScore, _add(), _angle_deg(), _backing(), _balance(), _bed_side_access() (+32 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.08
Nodes (79): _declared_bounds(), _declared_bounds_problems(), _gltf_problems(), inspect_asset(), ndarray, The bounds the file declares: the union of its `POSITION` accessors' min/max.…, Re-read an asset's stored file and check it against the furniture profile and…, Scene-graph rules of the furniture profile, read from the file's JSON chunk. (+71 more)

### Community 45 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 46 - "Sidebar.tsx"
Cohesion: 0.05
Nodes (43): MAX_LAYOUT_INSTRUCTION_CHARS, FengShuiScoreCard(), AuditStats(), ChatTab(), FengShuiSection(), HarnessProgress(), HarnessStatus(), LibraryTab() (+35 more)

### Community 47 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 48 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (21): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+13 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "Vec2"
Cohesion: 0.17
Nodes (24): DoorOpening, Vec2, WallSegment, A point on the floor plan (Y omitted)., A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, door_center(), door_entry_segment(), _door_frame() (+16 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.15
Nodes (22): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+14 more)

### Community 52 - "FurnitureAsset"
Cohesion: 0.07
Nodes (56): FurnitureItem, Correction, Facing, FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., _access(), AlignmentResult, _Choice (+48 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "AnnotationResult"
Cohesion: 0.40
Nodes (3): AnnotationResult, The label provider, for a service that must not need it., Unreachable

### Community 55 - "Decisions"
Cohesion: 0.06
Nodes (35): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+27 more)

### Community 56 - "test_report.py"
Cohesion: 0.47
Nodes (5): RoomScene, Regression checks for report composition and request-local geometry reuse., scene(), test_prepared_geometry_cannot_be_passed_to_different_scene(), test_volumes_built_once_per_item_and_not_retained_across_requests()

### Community 57 - "audit_scene"
Cohesion: 0.15
Nodes (29): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 58 - "scene_cache.py"
Cohesion: 0.05
Nodes (72): File, FalVisionAnnotator, FixedAnnotator, PlanAnnotator, Path, Protocol, What computer vision cannot read off a floor plan: room labels with their…, Reads labels with a vision LLM on fal.ai (`FAL_KEY`). The endpoint and model… (+64 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "RoomView.tsx"
Cohesion: 0.11
Nodes (22): CatalogPreview(), floorPlane, Furniture, MeshBoundary, ProxyBox(), FurnitureMesh(), categoryWash, disposeInk() (+14 more)

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

### Community 69 - "AnthropicLayoutModel"
Cohesion: 0.29
Nodes (6): AnthropicLayoutModel, Claude through the official SDK. The loop above owns retries, so the SDK makes…, Request, Response, sdk_model(), test_sdk_adapter_sends_the_expected_request_and_parses_tool_calls()

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "validate_feng_shui_request"
Cohesion: 0.50
Nodes (4): AuditReport, FengShuiRequest, Shared validation for the assessment and the score; returns the audit and…, validate_feng_shui_request()

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "Registry"
Cohesion: 0.09
Nodes (27): Connection, MaskProvider, Protocol, One segment per box, in order; None where none was produced. Raises MaskError…, DiscoveryError, DiscoveryProvider, OfflineProvider, parse_discovery() (+19 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.11
Nodes (19): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Feng shui score, Free floor area, Front clearance (+11 more)

### Community 76 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 77 - "store.ts"
Cohesion: 0.13
Nodes (27): playCue(), editorKey(), handleItemKey(), handleSaveKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys (+19 more)

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

### Community 87 - "detect_collisions"
Cohesion: 0.12
Nodes (37): CollisionIssue, detect_collisions(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, item(), part(), CollisionPart (+29 more)

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

### Community 96 - "furniture_footprint"
Cohesion: 0.32
Nodes (13): furniture_footprint(), Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, make_item(), FurnitureItem, parametrize, Footprint examples independent of meshes, providers and HTTP routes., test_45_degree_corners_follow_threejs_yaw(), test_does_not_mutate_item() (+5 more)

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "retailer.py"
Cohesion: 0.04
Nodes (66): FailureKind, HTMLParser, CatalogImport, computed_field, One imported product: the placed-ready asset, its checks, and where it all came…, The delivered asset passed every check. A proxy or a requested correction is…, main(), Path (+58 more)

### Community 124 - "agent.py"
Cohesion: 0.06
Nodes (40): Outcome, AgentLimits, _Budget, _explain_result(), _explore(), _interpret(), _Interpretation, LayoutCancelled (+32 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "catalog.py"
Cohesion: 0.07
Nodes (59): Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., write_atomic(), ImageProvenance, import_product(), imported_assets(), _normalises(), Path (+51 more)

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 130 - "PlayLighting.tsx"
Cohesion: 0.25
Nodes (14): DoorLightBlockers(), LightingEnvironment, PlayLighting(), useEnvironmentSettings(), inwardNormal(), ceilingLights(), DEFAULT_PLAY_LIGHTING, LightPosition (+6 more)

### Community 131 - "test_streaming.py"
Cohesion: 0.30
Nodes (14): event(), post(), Any, OptimiseRequest, parametrize, Scripted, SSE progress is observable while the harness is blocked in a provider call., test_chat_stream_emits_progress_and_audited_additions_without_mutating_the_room() (+6 more)

### Community 132 - "SpatialInputError"
Cohesion: 0.09
Nodes (43): FengShuiReport, Spatial checks independent of HTTP, mesh loading and provider services., A window-openness proxy for layout comparison, not a lighting simulation., Shared Feng Shui inputs and validation, independent of the model harness., _angle_deg(), calculate_feng_shui(), _front(), _occupant() (+35 more)

### Community 133 - "AuditReport"
Cohesion: 0.20
Nodes (17): AuditReport, payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422() (+9 more)

### Community 135 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 140 - "RetailerModelProvider"
Cohesion: 0.16
Nodes (12): _decode(), item_box(), Fetch, Mask, NDArray, uint8, The retailer's own published model as the item's raw mesh. No inference and no…, The next published model that is usable and within the triangle budget. Each… (+4 more)

### Community 141 - "furniture_proxy"
Cohesion: 0.25
Nodes (8): le, furniture_proxy(), health(), get, gt, Path, Response, Process liveness only; does not probe external providers.

## Knowledge Gaps
- **463 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+458 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `test_scene_cache.py`, `test_room_align_vision.py`, `test_scene_routes.py`, `SpatialInputError`, `models.py`, `AuditReport`, `test_room_align.py`, `calculate_free_floor_ratio`, `test_delivery.py`, `propose_layout`, `single_room`, `Pose2D`, `LayoutToolbox`, `test_chat.py`, `test_room_correct.py`, `test_room_parse.py`, `test_contracts.py`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `spatial_engine/main.py`, `test_room_shell.py`, `scenes.py`, `ContractModel`, `demo_assets.py`, `score_feng_shui`, `detect_out_of_bounds`, `generate_mock_glbs.py`, `Vec2`, `FurnitureAsset`, `test_report.py`, `audit_scene`, `scene_cache.py`, `detect_front_clearance`, `detect_collisions`, `test_demo_assets.py`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `test_room_align_vision.py`, `test_scene_routes.py`, `models.py`, `ContractModel`, `selection_models.py`, `test_room_align.py`, `test_fixture_scene.py`, `test_delivery.py`, `test_demo_cache.py`, `BBoxM`, `.to_item`, `demo_assets.py`, `Pose2D`, `test_contract_occupancy.py`, `test_reconstruction.py`, `retailer.py`, `test_demo_cache_room.py`, `catalog.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_catalog.py`, `models.py`, `footprint.py`, `calculate_free_floor_ratio`, `test_delivery.py`, `propose_layout`, `Pose2D`, `LayoutToolbox`, `test_chat.py`, `test_reconstruction.py`, `detect_blocked_doors`, `calculate_brightness_approximation`, `ContractModel`, `detect_out_of_bounds`, `Vec2`, `FurnitureAsset`, `audit_scene`, `detect_front_clearance`, `detect_collisions`, `furniture_footprint`, `retailer.py`, `catalog.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 222 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 222 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 71 inferred relationships involving `Pose2D` (e.g. with `FurnitureAsset` and `_access()`) actually correct?**
  _`Pose2D` has 71 INFERRED edges - model-reasoned connections that need verification._