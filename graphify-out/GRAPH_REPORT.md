# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 270 files · ~410,460 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3986 nodes · 11879 edges · 150 communities (122 shown, 28 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1378 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e036411a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- test_scene_cache.py
- test_room_align_vision.py
- test_real_room.py
- RoomScene
- audio.test.ts
- models.py
- footprint.py
- test_segmentation.py
- demo_cache.py
- test_room_align.py
- calculate_free_floor_ratio
- test_delivery.py
- Box
- BBoxM
- test_selection.py
- App.tsx
- propose_layout
- test_room_routes.py
- Pose2D
- DraftSession
- regions.py
- test_chat.py
- test_room_correct.py
- test_room_parse.py
- RequestBudget
- AuditReport
- detect_blocked_doors
- contracts.ts
- parse.py
- calculate_brightness_approximation
- test_demo_cache_room.py
- RoomView.tsx
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- spatialPreview.ts
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
- LayoutProposalCard.tsx
- FengShuiRequest
- CatalogError
- generate_mock_glbs.py
- SpatialInputError
- test_contract_occupancy.py
- FurnitureAsset
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- FloorPlanScreen.tsx
- Decisions
- LayoutToolbox
- audit_scene
- PlanAnnotations
- compilerOptions
- Video frame selection and furniture identity — issue #14
- react
- Dev 2 → Dev 1 asset handoff
- dependencies
- devDependencies
- raster.py
- polygon.py
- Architecture
- Dev 4 implementation and integration plan
- PlayLighting.tsx
- Agent Instructions
- inspect_asset
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
- FurnitureItem
- _Page
- model_validator
- README.md
- frontend/package.json
- search_products
- divided_access_room
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- editorControls.test.ts
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
- test_reconstruction.py
- openings.py
- Validated, cached demo assets (#20, Dev 2.8)
- CollisionPart
- .current_mesh
- .ok
- test_api.py
- no_network
- plugins
- chat.py
- catalog_router
- demo_cache/README.md
- model_validator
- AuditReport
- furniture_proxy
- ChatReply
- LayoutMetrics
- ChatRequest
- LinkupPost
- ProgressCallback
- Any
- Exception
- MonkeyPatch

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 235 edges
2. `FurnitureAsset` - 91 edges
3. `useStore` - 88 edges
4. `BBoxM` - 83 edges
5. `Pose2D` - 80 edges
6. `FurnitureItem` - 80 edges
7. `Registry` - 69 edges
8. `SpatialInputError` - 64 edges
9. `propose_layout()` - 63 edges
10. `audit_scene()` - 61 edges

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

## Communities (150 total, 28 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.08
Nodes (54): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., Labelled sizes in prose: "Width: 120 cm" for each axis, or "W120 x D60 x H75… (+46 more)

### Community 1 - "test_scene_cache.py"
Cohesion: 0.04
Nodes (93): health(), get, Process liveness only; does not probe external providers., plan_id_for(), _assemble(), cache_path(), CachedScene, _check() (+85 more)

### Community 2 - "test_room_align_vision.py"
Cohesion: 0.04
Nodes (85): Image, MaskSource, main(), PlacementHint, FrameSource, Path, RoomScene, build_prompt() (+77 more)

### Community 3 - "test_real_room.py"
Cohesion: 0.08
Nodes (77): Collection, proxy_warning(), still_extracting(), clear_cache(), Forget assembled scenes (tests, or after the furniture source changes)., _audit(), auditor(), _clear() (+69 more)

### Community 4 - "RoomScene"
Cohesion: 0.12
Nodes (41): RoomScene, _Capture, Passes hints through and keeps them, so a live run can be recorded., NoFurniture, What a furniture source supplies for one room., The room alone: what parsed rooms get until #16 produces furniture assets., SceneFurniture, PlacementObserver (+33 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 6 - "models.py"
Cohesion: 0.13
Nodes (21): fetch(), main(), prepare(), Fetch a balanced, offline IKEA library using only published retailer meshes.…, Reuse bounded, public-only downloads; keep raw evidence outside the project., Expand retailer Draco geometry and expose WebP sources to the shared reader.…, unpack_model(), _along_mesh() (+13 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (57): any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach() (+49 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.10
Nodes (63): Rect, Store a mask and cut-out for every selected view of the scene's (or the named)…, segment_furniture(), MaskRecord, One stored instance mask (#15) for one sighting of one item., Sighting, test_mesh_record_belongs_to_a_sighting_and_goes_stale_with_its_mask(), box_mask() (+55 more)

### Community 9 - "demo_cache.py"
Cohesion: 0.11
Nodes (34): CachedFile, CacheError, current_generation(), _inside(), _intact(), main(), prune_demo_cache(), publish_demo_cache() (+26 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (58): align_assets(), AlignmentResult, FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms). (+50 more)

### Community 11 - "calculate_free_floor_ratio"
Cohesion: 0.10
Nodes (52): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, item(), FurnitureItem, parametrize (+44 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.11
Nodes (46): main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), check_placed(), deliver_furniture(), Delivery, computed_field (+38 more)

### Community 13 - "Box"
Cohesion: 0.08
Nodes (47): ArtifactTooLarge, box_pixels(), fal_media_url(), FalSamProvider, _fetch(), fetch_bounded(), GrabCutProvider, MaskError (+39 more)

### Community 14 - "BBoxM"
Cohesion: 0.13
Nodes (49): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, BBoxM, CollisionPart, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).…, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts() (+41 more)

### Community 15 - "test_selection.py"
Cohesion: 0.08
Nodes (79): DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery(), Exception, Path, Protocol (+71 more)

### Community 16 - "App.tsx"
Cohesion: 0.07
Nodes (32): App(), ORDER, screenVariants, EditorScreen(), Sidebar(), useLiveAudit(), HomeScreen(), rise (+24 more)

### Community 17 - "propose_layout"
Cohesion: 0.10
Nodes (71): OptimiseRequest, propose_layout(), ProviderError, LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, A failed model call. `kind` is safe to log; no key or payload is kept., OptimiseRequest, solve_events() (+63 more)

### Community 18 - "test_room_routes.py"
Cohesion: 0.27
Nodes (10): _png(), client(), TestClient, Floor-plan routes on the reconstruction service, and the ParsedFloorPlan…, test_errors(), test_parsed_room_contract(), test_same_upload_returns_the_same_plan_id(), test_upload_then_fetch_plan_and_room() (+2 more)

### Community 19 - "Pose2D"
Cohesion: 0.11
Nodes (59): Pose2D, WindowOpening, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., _access_not_worse(), beats_original(), compare_evaluations(), compare_layouts(), evaluate_layout() (+51 more)

### Community 20 - "DraftSession"
Cohesion: 0.11
Nodes (36): _arrangement(), DraftSession, _echo(), LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one…, A fresh scene at the base revision, so its audit identifies the submitted scene. (+28 more)

### Community 21 - "regions.py"
Cohesion: 0.13
Nodes (33): int32, Raster, _accept(), _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point() (+25 more)

### Community 22 - "test_chat.py"
Cohesion: 0.06
Nodes (86): Any, ChatReply, ChatRequest, ChatReply, ChatRequest, POST /chat and /chat/stream., POST /chat response, and the data of /chat/stream's terminal `reply` event., Exception (+78 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.08
Nodes (53): floor_polygon is clockwise in plan view and every wall has the room on its…, model_validator, apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, InvalidScale (+45 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.12
Nodes (43): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, bay_room(), _canvas(), _close(), _example(), _has_vertex() (+35 more)

### Community 25 - "RequestBudget"
Cohesion: 0.07
Nodes (38): FailureKind, RuntimeError, _decode(), item_box(), Fetch, Mask, NDArray, uint8 (+30 more)

### Community 26 - "AuditReport"
Cohesion: 0.14
Nodes (22): AuditReport, FengShuiReport, load_generator(), load_mock(), parametrize, RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are… (+14 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.09
Nodes (59): BlockedDoorIssue, BlockedDoorIssue, detect_blocked_doors(), detect_out_of_bounds(), RoomScene, Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item() (+51 more)

### Community 28 - "contracts.ts"
Cohesion: 0.06
Nodes (48): ChatStreamEvent, GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, LayoutProgressStage, LayoutStreamEvent, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES (+40 more)

### Community 29 - "parse.py"
Cohesion: 0.12
Nodes (39): FloorCaption, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance(), _consensus() (+31 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.18
Nodes (28): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item(), FurnitureItem (+20 more)

### Community 31 - "test_demo_cache_room.py"
Cohesion: 0.15
Nodes (30): broken_cache(), assert_readers_agree(), _audit(), auditor(), _client(), _collides(), data_dir(), _declared_size() (+22 more)

### Community 32 - "RoomView.tsx"
Cohesion: 0.07
Nodes (38): WALK_HEADROOM_M, DoorSwings(), floorPlane, RotationRing(), SelectionTools(), captureEditorView(), EditorOrbit, EditorView (+30 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.05
Nodes (55): exception_handler, FengShuiResult, JSONResponse, RequestValidationError, AnthropicLayoutModel, LayoutModel, Any, Protocol (+47 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "spatialPreview.ts"
Cohesion: 0.20
Nodes (20): PlanDiff(), flaggedFor(), RoomView(), footprint(), toWorld(), byId(), collisionVolumes(), convexOverlapArea() (+12 more)

### Community 36 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 37 - "test_feng_shui_optimisation.py"
Cohesion: 0.15
Nodes (23): ModelReply, ToolCall, assess_feng_shui(), FengShuiRequest, Any, original_room(), Scripted, Feng Shui optimisation uses the runtime skill and the same full score as Stats. (+15 more)

### Community 38 - "scenes.py"
Cohesion: 0.05
Nodes (64): ge, HTTPException, Query, AlignmentRecord, Debug CLI for furniture alignment: place assets in a room and draw the result.…, BaseModel, How one asset's pose was decided. Keyed by the asset's stable ID., assemble_scene() (+56 more)

### Community 39 - "agent.ts"
Cohesion: 0.08
Nodes (45): HarnessProgress(), HarnessStatus(), isLibraryAsset(), AgentReply, describeOutlook(), EditorReply, LAYOUT_GOALS, PROGRESS_STAGES (+37 more)

### Community 40 - "ContractModel"
Cohesion: 0.09
Nodes (36): ChatErrorEvent, ChatProgressEvent, ChatReplyEvent, ContractModel, _FengShuiModel, LayoutErrorEvent, LayoutProgressEvent, LayoutResultEvent (+28 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.09
Nodes (34): FileResponse, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file() (+26 more)

### Community 42 - "score_feng_shui"
Cohesion: 0.13
Nodes (44): FengShuiSightline, FengShuiSightline, RuleScore, AuditReport, FengShuiRequest, Shared validation for the assessment and the score; returns the audit and…, validate_feng_shui_request(), _add() (+36 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.16
Nodes (34): cache_folder(), DemoCache, publish_catalog_scene(), Publish every product imported into `scene_id` (#19), with its retailer…, The scene's published cache, its files verified; None when none is published.…, A scene's folder: readable, and distinct for scene IDs that read alike., read_demo_cache(), _generation() (+26 more)

### Community 45 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 46 - "LayoutProposalCard.tsx"
Cohesion: 0.08
Nodes (31): FengShuiScoreCard(), AuditDiff(), LayoutProposalCard(), poseText(), ScoreComparison, useProposalScores(), AuditStats(), fixture (+23 more)

### Community 47 - "FengShuiRequest"
Cohesion: 0.26
Nodes (22): FengShuiRequest, POST /feng-shui and /feng-shui/score., test_full_goal_improves_backing_even_when_the_door_placement_score_is_unchanged(), bed(), item(), FurnitureItem, RoomScene, Headboard on the south wall, facing the door side of the room (-Z). (+14 more)

### Community 48 - "CatalogError"
Cohesion: 0.09
Nodes (30): CatalogError, _check_public(), fetch_product(), fetch_public(), Fetch, ValueError, The product cannot be imported at all. The message is safe to show., Download and read one retailer product page. Raises CatalogError. `source`… (+22 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "SpatialInputError"
Cohesion: 0.06
Nodes (71): DoorOpening, Vec2, WallSegment, A point on the floor plan (Y omitted)., A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, FengShuiReport, height_overlaps(), Spatial checks independent of HTTP, mesh loading and provider services. (+63 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.15
Nodes (22): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+14 more)

### Community 52 - "FurnitureAsset"
Cohesion: 0.09
Nodes (41): Correction, Facing, FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., _access(), _Choice, _extents(), _front() (+33 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (20): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+12 more)

### Community 55 - "Decisions"
Cohesion: 0.06
Nodes (35): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+27 more)

### Community 56 - "LayoutToolbox"
Cohesion: 0.10
Nodes (40): LayoutDraft, _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, LayoutToolbox, _metrics() (+32 more)

### Community 57 - "audit_scene"
Cohesion: 0.13
Nodes (31): demo_room_scenes(), profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, Each demo room with the furniture standing in it, as the editor builds them., solve(), Timed (+23 more)

### Community 58 - "PlanAnnotations"
Cohesion: 0.07
Nodes (37): AnnotationResult, Compass, _extract_json(), FalVisionAnnotator, FixedAnnotator, NullAnnotator, PlanAnnotations, PlanAnnotator (+29 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "react"
Cohesion: 0.26
Nodes (11): MeshBoundary, ProxyBox(), FurnitureMesh(), categoryWash, disposeInk(), inkify(), inkLine, Shell (+3 more)

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
Cohesion: 0.11
Nodes (22): File, Gray, decode(), estimate_wall_px(), flatten_illumination(), Mask, NDArray, uint8 (+14 more)

### Community 66 - "polygon.py"
Cohesion: 0.22
Nodes (16): area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), float64, Mask, NDArray (+8 more)

### Community 67 - "Architecture"
Cohesion: 0.07
Nodes (28): Architecture, Backend-provided demo models, Bundled retailer library, Chat additions and application, Corrections (#11), Demo scene cache (#12), Editor Feng Shui score integration, Editor layout review and live Stats (+20 more)

### Community 68 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "PlayLighting.tsx"
Cohesion: 0.25
Nodes (15): DoorLightBlockers(), LightingEnvironment, PlayLighting(), useEnvironmentSettings(), bounds(), inwardNormal(), ceilingLights(), DEFAULT_PLAY_LIGHTING (+7 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "inspect_asset"
Cohesion: 0.14
Nodes (18): _declared_bounds(), _declared_bounds_problems(), _gltf_problems(), inspect_asset(), ndarray, The bounds the file declares: the union of its `POSITION` accessors' min/max.…, Re-read an asset's stored file and check it against the furniture profile and…, Scene-graph rules of the furniture profile, read from the file's JSON chunk. (+10 more)

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "Registry"
Cohesion: 0.24
Nodes (6): Connection, Any, Path, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle., Registry

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.11
Nodes (19): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Feng shui score, Free floor area, Front clearance (+11 more)

### Community 76 - "detect_front_clearance"
Cohesion: 0.18
Nodes (32): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+24 more)

### Community 77 - "store.ts"
Cohesion: 0.06
Nodes (57): playCue(), CatalogPreview(), Furniture, Navigation(), ChatTab(), FengShuiSection(), LibraryTab(), ProductCard() (+49 more)

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
Cohesion: 0.17
Nodes (22): IkeaSearch, PageReader, ProductOption, _host(), _ikea_options(), linkup_client(), _linkup_urls(), _option() (+14 more)

### Community 87 - "detect_collisions"
Cohesion: 0.13
Nodes (36): CollisionIssue, detect_collisions(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, item(), part(), CollisionPart, FurnitureItem (+28 more)

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

### Community 96 - "FurnitureItem"
Cohesion: 0.10
Nodes (44): FurnitureItem, front_clearance_zone(), furniture_collision_volumes(), furniture_footprint(), prepare_furniture(), FurnitureItem, Polygon, Transform validated local collision boxes; absent parts mean one solid bbox.… (+36 more)

### Community 97 - "_Page"
Cohesion: 0.29
Nodes (3): HTMLParser, _Page, The few things a product page is read for: JSON-LD, meta tags, title and…

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "search_products"
Cohesion: 0.23
Nodes (19): Exception, Up to three purchasable products for `query`, IKEA first when IKEA has a match.…, No search could run (no key, provider down). The message is safe to show., search_products(), SearchUnavailable, ikea(), Linkup, product() (+11 more)

### Community 102 - "divided_access_room"
Cohesion: 0.40
Nodes (4): divided_access_room(), RoomScene, Shared regression geometry for custom layout access checks., Clearing a wardrobe by moving its blocker behind the divider cuts circulation.

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "editorControls.test.ts"
Cohesion: 0.32
Nodes (8): editorKey(), handleItemKey(), handleSaveKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, initial

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "retailer.py"
Cohesion: 0.11
Nodes (29): _binary_models(), _dimensions(), _first_url(), guess_category(), _is_type(), _metres(), _model_urls(), _nodes() (+21 more)

### Community 124 - "agent.py"
Cohesion: 0.07
Nodes (33): Outcome, AgentLimits, _Budget, _explain_result(), _explore(), _interpret(), _Interpretation, LayoutCancelled (+25 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "test_reconstruction.py"
Cohesion: 0.04
Nodes (105): asset_router(), APIRouter, Path, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset() (+97 more)

### Community 128 - "openings.py"
Cohesion: 0.21
Nodes (12): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+4 more)

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 130 - "CollisionPart"
Cohesion: 0.50
Nodes (4): CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, NormalisedMesh, Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`.

### Community 133 - "test_api.py"
Cohesion: 0.20
Nodes (16): payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422() (+8 more)

### Community 134 - "no_network"
Cohesion: 0.67
Nodes (3): no_network(), MonkeyPatch, Any attempt to resolve or connect fails the test: no provider, no retailer.

### Community 135 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 136 - "chat.py"
Cohesion: 0.15
Nodes (16): AuditReport, AddItemArguments, place(), PlaceRequest, BaseModel, Room chat with audited additions; existing pose-only solve contracts stay…, Why a candidate is refused. Only the new item and moved items are held to…, The words of a model turn, bounded for display. Blocks are SDK objects or dicts. (+8 more)

### Community 137 - "catalog_router"
Cohesion: 0.18
Nodes (13): catalog_router(), APIRouter, Fetch, Path, `fetch` replaces the public downloader (tests)., client(), MonkeyPatch, parametrize (+5 more)

### Community 141 - "furniture_proxy"
Cohesion: 0.18
Nodes (11): le, furniture_proxy(), health(), get, gt, Path, Response, Process liveness only; does not probe external providers. (+3 more)

## Knowledge Gaps
- **466 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+461 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `test_scene_cache.py`, `test_room_align_vision.py`, `test_real_room.py`, `test_api.py`, `chat.py`, `test_room_align.py`, `calculate_free_floor_ratio`, `test_delivery.py`, `propose_layout`, `test_room_routes.py`, `Pose2D`, `DraftSession`, `test_chat.py`, `test_room_correct.py`, `test_room_parse.py`, `AuditReport`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `spatial_engine/main.py`, `test_room_shell.py`, `scenes.py`, `ContractModel`, `demo_assets.py`, `score_feng_shui`, `FengShuiRequest`, `generate_mock_glbs.py`, `SpatialInputError`, `FurnitureAsset`, `LayoutToolbox`, `audit_scene`, `detect_front_clearance`, `detect_collisions`, `FurnitureItem`, `divided_access_room`, `test_demo_assets.py`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `test_scene_cache.py`, `CollisionPart`, `test_room_align_vision.py`, `RoomScene`, `models.py`, `demo_cache.py`, `test_room_align.py`, `test_delivery.py`, `BBoxM`, `Pose2D`, `scenes.py`, `ContractModel`, `demo_assets.py`, `test_demo_cache.py`, `.to_item`, `test_contract_occupancy.py`, `inspect_asset`, `test_fixture_scene.py`, `FurnitureItem`, `test_reconstruction.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_catalog.py`, `CollisionPart`, `models.py`, `footprint.py`, `catalog_router`, `calculate_free_floor_ratio`, `test_delivery.py`, `propose_layout`, `Pose2D`, `DraftSession`, `test_chat.py`, `RequestBudget`, `detect_blocked_doors`, `calculate_brightness_approximation`, `ContractModel`, `FengShuiRequest`, `SpatialInputError`, `FurnitureAsset`, `LayoutToolbox`, `audit_scene`, `detect_front_clearance`, `detect_collisions`, `FurnitureItem`, `search_products`, `divided_access_room`, `retailer.py`, `test_reconstruction.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 232 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 232 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 80 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 80 INFERRED edges - model-reasoned connections that need verification._
- **Are the 77 inferred relationships involving `Pose2D` (e.g. with `catalog_router()` and `FurnitureAsset`) actually correct?**
  _`Pose2D` has 77 INFERRED edges - model-reasoned connections that need verification._