# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 278 files · ~425,965 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4219 nodes · 12731 edges · 157 communities (139 shown, 18 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1474 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e02affcb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- test_scene_cache.py
- test_video_jobs.py
- TestClient
- test_scene_routes.py
- audio.test.ts
- selection_models.py
- footprint.py
- test_segmentation.py
- test_room_shell.py
- test_room_align.py
- calculate_reachable_floor_ratio
- Sidebar.tsx
- test_layout_tools.py
- test_delivery.py
- test_selection.py
- test_demo_cache_room.py
- propose_layout
- test_normalisation.py
- test_objective.py
- DraftSession
- regions.py
- RoomScene
- test_room_correct.py
- test_room_parse.py
- agent.ts
- test_contracts.py
- chat.py
- contracts.ts
- parse.py
- calculate_brightness_approximation
- useStore
- PlaySession
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
- layoutAgent.test.tsx
- scene_cache.py
- Box
- generate_mock_glbs.py
- Vec2
- test_contract_occupancy.py
- FurnitureAsset
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_room_align_vision.py
- Decisions
- LayoutToolbox
- audit_scene
- routes.py
- compilerOptions
- Video frame selection and furniture identity — issue #14
- BBoxM
- Dev 2 → Dev 1 asset handoff
- dependencies
- devDependencies
- raster.py
- polygon.py
- Architecture
- Dev 4 implementation and integration plan
- react
- Agent Instructions
- demo_cache.py
- test_fixture_scene.py
- test_real_room.py
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
- detect_front_clearance
- render_room
- test_room_routes.py
- README.md
- frontend/package.json
- test_catalog_imports.py
- LayoutModel
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
- video_jobs.py
- test_demo_assets.py
- vite
- catalog.py
- openings.py
- Validated, cached demo assets (#20, Dev 2.8)
- agent.py
- check_delivery.py
- objective.py
- calculate_free_floor_ratio
- Extractions
- plugins
- test_api.py
- delivery.py
- demo_cache/README.md
- EditorScreen.tsx
- SceneFurniture
- SoundControls.tsx
- Registry
- _ScriptedSource
- calculate_feng_shui
- test_an_assembly_overtaken_by_a_scale_correction_is_done_again
- test_video_furniture_by_room_state
- _walls
- clear_cache
- .to_item
- demoHome.ts
- ._check_winding
- spatialPreview.ts
- .current_mesh
- no_network
- furniture_footprint
- model_validator

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 250 edges
2. `useStore` - 96 edges
3. `FurnitureAsset` - 93 edges
4. `BBoxM` - 87 edges
5. `Pose2D` - 81 edges
6. `FurnitureItem` - 80 edges
7. `SpatialInputError` - 75 edges
8. `Registry` - 69 edges
9. `audit_scene()` - 66 edges
10. `propose_layout()` - 64 edges

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

## Communities (157 total, 18 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.09
Nodes (54): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., bounds() (+46 more)

### Community 1 - "test_scene_cache.py"
Cohesion: 0.08
Nodes (43): Serve a published plan (`scene_cache.py`, #12) as if it had been uploaded and…, restore_plan(), differences(), Serve every plan published in `cache_dir` (`routes.restore_plan`); a plan…, Where two JSON-like values differ: the paths, such as…, restore_published(), _audit(), auditor() (+35 more)

### Community 2 - "test_video_jobs.py"
Cohesion: 0.30
Nodes (15): ExtractionError, ExtractionJob, RuntimeError, A reason safe to show the user (no keys, paths or provider bodies)., Path, Live furniture extraction from uploaded videos (`room/video_jobs.py`), with…, _rooms(), test_a_room_is_measured_against_its_own_plan_room() (+7 more)

### Community 3 - "TestClient"
Cohesion: 0.17
Nodes (39): Collection, _audit(), _item(), _moved(), _put(), FurnitureItem, MonkeyPatch, Path (+31 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.15
Nodes (33): conform_openings(), RoomScene, Put every door exactly on its wall, so the spatial audit accepts the room. Each…, _audit(), auditor(), _door(), _leaf_end(), DoorOpening (+25 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 6 - "selection_models.py"
Cohesion: 0.14
Nodes (29): AssetEvidence, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, _diagnostic(), evidence_for(), DiscoveredObject, MissingMask, BaseModel, Internal #14-#16 records. Source evidence is deliberately separate from… (+21 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (61): any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach() (+53 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.10
Nodes (65): Rect, main(), Path, Review images plus the two machine-readable handoffs: the result and the…, write_report(), Store a mask and cut-out for every selected view of the scene's (or the named)…, Resolve an `EvidenceFrame.mask_url` (relative to the asset data directory)., read_mask() (+57 more)

### Community 9 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.11
Nodes (60): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, assemble_scene(), The room with its furniture placed. Never drops the room: a source that fails…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction. (+52 more)

### Community 11 - "calculate_reachable_floor_ratio"
Cohesion: 0.17
Nodes (29): calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, divided_room(), obstacle(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 12 - "Sidebar.tsx"
Cohesion: 0.06
Nodes (40): App(), ORDER, screenVariants, CatalogPreview(), FengShuiScoreCard(), AuditStats(), ChatTab(), FengShuiSection() (+32 more)

### Community 13 - "test_layout_tools.py"
Cohesion: 0.19
Nodes (25): LayoutPreferences, What the user asked for, already validated by the server., evaluate(), item(), move(), Any, FurnitureItem, parametrize (+17 more)

### Community 14 - "test_delivery.py"
Cohesion: 0.15
Nodes (40): check_placed(), deliver_furniture(), Path, RoomScene, A scene's furniture for Dev 1 to place: per item, its checked mesh or its…, Faults in how a scene carries delivered assets; empty when every asset appears…, audit(), bounds_of() (+32 more)

### Community 15 - "test_selection.py"
Cohesion: 0.09
Nodes (70): DiscoveryError, DiscoveryProvider, FalVisionProvider, _lenient(), OfflineProvider, parse_discovery(), Any, Exception (+62 more)

### Community 16 - "test_demo_cache_room.py"
Cohesion: 0.13
Nodes (34): broken_cache(), from_demo_cache(), test_download_deadline_stops_trickling_response(), assert_readers_agree(), _audit(), auditor(), _client(), _collides() (+26 more)

### Community 17 - "propose_layout"
Cohesion: 0.09
Nodes (78): OptimiseRequest, AgentLimits, _interpret(), prepare_layout(), propose_layout(), ProviderError, LayoutProposal, OptimiseRequest (+70 more)

### Community 18 - "test_normalisation.py"
Cohesion: 0.13
Nodes (45): Front, _normalises(), Whether the item's stored raw mesh meets the furniture profile at its size., NormalisationError, normalise_mesh(), BBoxM, ValueError, Fit a raw glTF 2.0 binary to the furniture profile, store it and return its… (+37 more)

### Community 19 - "test_objective.py"
Cohesion: 0.15
Nodes (45): compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, item(), FurnitureItem, parametrize, RoomScene (+37 more)

### Community 20 - "DraftSession"
Cohesion: 0.11
Nodes (36): _arrangement(), DraftSession, _echo(), LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one…, A fresh scene at the base revision, so its audit identifies the submitted scene. (+28 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (34): int32, Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction() (+26 more)

### Community 22 - "RoomScene"
Cohesion: 0.09
Nodes (72): ChatRequest, RoomScene, POST /chat and /chat/stream., add_item(), chat(), ChatRequest, FurnitureItem, ProgressCallback (+64 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.09
Nodes (48): apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, InvalidScale, _perimeter(), _point() (+40 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.13
Nodes (39): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), NullAnnotator, PlanAnnotations, No labels: the parser falls back to estimated scale and generic names., _close() (+31 more)

### Community 25 - "agent.ts"
Cohesion: 0.12
Nodes (40): LayoutGoal, isLibraryAsset(), AgentReply, describeOutlook(), EditorReply, LAYOUT_GOALS, PROGRESS_STAGES, readProducts() (+32 more)

### Community 26 - "test_contracts.py"
Cohesion: 0.16
Nodes (17): load_generator(), load_mock(), RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must…, solid_at(), test_audit_report_must_echo_scene() (+9 more)

### Community 27 - "chat.py"
Cohesion: 0.09
Nodes (36): ChatReply, POST /chat response, and the data of /chat/stream's terminal `reply` event., AddItemArguments, _apply(), _combine(), _error_text(), _percent(), place() (+28 more)

### Community 28 - "contracts.ts"
Cohesion: 0.05
Nodes (60): ChatStreamEvent, GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutProgressStage, LayoutStreamEvent, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS (+52 more)

### Community 29 - "parse.py"
Cohesion: 0.10
Nodes (45): Compass, FloorCaption, BaseModel, What computer vision cannot read off a floor plan: room labels with their…, Plans print labels in capitals ("BEDROOM (4)"); show them in title case., RoomLabel, _tidy_name(), _assign_labels() (+37 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.18
Nodes (28): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item(), FurnitureItem (+20 more)

### Community 31 - "useStore"
Cohesion: 0.08
Nodes (48): DoorSwings(), floorPlane, Furniture, flaggedFor(), Navigation(), RoomView(), RotationRing(), SelectionTools() (+40 more)

### Community 32 - "PlaySession"
Cohesion: 0.19
Nodes (4): EditorView, PlaySession, initial, setup()

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.04
Nodes (72): exception_handler, FengShuiResult, JSONResponse, le, RequestValidationError, demo_room_scenes(), profile(), Any (+64 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "demo_assets.py"
Cohesion: 0.12
Nodes (26): FileResponse, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file() (+18 more)

### Community 36 - "detect_blocked_doors"
Cohesion: 0.14
Nodes (37): BlockedDoorIssue, BlockedDoorIssue, CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem (+29 more)

### Community 37 - "test_feng_shui_optimisation.py"
Cohesion: 0.11
Nodes (31): ModelReply, ToolCall, assess_feng_shui(), Assessment, FengShuiResult, Finding, DetailModel, BaseModel (+23 more)

### Community 38 - "test_reconstruction.py"
Cohesion: 0.05
Nodes (79): FailureKind, fal_media_url(), Provider artifacts are fetched over HTTPS from fal's media hosts only., _encode_png(), _FalMeshProvider, FalSam3dProvider, FalTrellis2Provider, inspect_mesh() (+71 more)

### Community 39 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 40 - "ContractModel"
Cohesion: 0.08
Nodes (41): ChatErrorEvent, ChatProgressEvent, ChatReplyEvent, ContractModel, _FengShuiModel, LayoutErrorEvent, LayoutProgressEvent, LayoutResultEvent (+33 more)

### Community 41 - "scenes.py"
Cohesion: 0.06
Nodes (48): ge, Query, demo_cache_dir(), furniture_data_dir(), Path, Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, Where published demo furniture is read from when the pipeline has none (#20).… (+40 more)

### Community 42 - "score_feng_shui"
Cohesion: 0.10
Nodes (65): FengShuiRequest, POST /feng-shui and /feng-shui/score., FengShuiSightline, RuleScore, AuditReport, FengShuiRequest, Shared validation for the assessment and the score; returns the audit and…, validate_feng_shui_request() (+57 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.14
Nodes (33): cache_folder(), CacheError, current_generation(), prune_demo_cache(), ValueError, Delete every generation but the published one, and staging left by a killed…, The folder of the scene's published generation; None when none is published., A cache that cannot be published, or a published cache that is broken. (+25 more)

### Community 45 - "FixedAnnotator"
Cohesion: 0.11
Nodes (16): AnnotationResult, FalVisionAnnotator, FixedAnnotator, Path, Reads labels with a vision LLM on fal.ai (`FAL_KEY`). The endpoint and model…, Returns pre-recorded annotations (tests, the debug CLI, cached demo plans)., main(), ndarray (+8 more)

### Community 46 - "layoutAgent.test.tsx"
Cohesion: 0.06
Nodes (39): AuditDiff(), LayoutProposalCard(), PlanDiff(), poseText(), ScoreComparison, useProposalScores(), HarnessProgress(), HarnessStatus() (+31 more)

### Community 47 - "scene_cache.py"
Cohesion: 0.09
Nodes (45): PlanAnnotator, Protocol, _annotator(), _assemble(), cache_path(), CachedScene, _check(), _faults() (+37 more)

### Community 48 - "Box"
Cohesion: 0.08
Nodes (37): ArtifactTooLarge, box_pixels(), FalSamProvider, _fetch(), fetch_bounded(), GrabCutProvider, MaskError, Any (+29 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "Vec2"
Cohesion: 0.13
Nodes (32): DoorOpening, Vec2, WallSegment, A point on the floor plan (Y omitted)., A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, door_center(), door_entry_segment(), _door_frame() (+24 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 52 - "FurnitureAsset"
Cohesion: 0.06
Nodes (67): FurnitureItem, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., Correction, Facing, FurnitureAsset, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence…, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence. (+59 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_room_align_vision.py"
Cohesion: 0.05
Nodes (75): MaskSource, EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., main(), Path, build_prompt(), directory_frames(), _distance_to_wall() (+67 more)

### Community 55 - "Decisions"
Cohesion: 0.06
Nodes (35): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+27 more)

### Community 56 - "LayoutToolbox"
Cohesion: 0.16
Nodes (17): LayoutDraft, _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, LayoutToolbox, _metrics() (+9 more)

### Community 57 - "audit_scene"
Cohesion: 0.22
Nodes (23): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+15 more)

### Community 58 - "routes.py"
Cohesion: 0.08
Nodes (44): BinaryIO, File, HTTPException, plan_id_for(), get_annotator(), get_extractions(), get_plan(), get_room() (+36 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "BBoxM"
Cohesion: 0.07
Nodes (41): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, asset_router(), APIRouter, Path, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`. (+33 more)

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

### Community 69 - "react"
Cohesion: 0.14
Nodes (25): MeshBoundary, ProxyBox(), FurnitureMesh(), categoryWash, disposeInk(), inkify(), inkLine, Shell (+17 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "demo_cache.py"
Cohesion: 0.14
Nodes (31): CachedFile, DemoCache, _inside(), _intact(), main(), publish_catalog_scene(), publish_demo_cache(), publish_video_scene() (+23 more)

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "test_real_room.py"
Cohesion: 0.11
Nodes (25): NoFurniture, The room alone: what parsed rooms get until #16 produces furniture assets., geometry_mismatch(), geometry_warning(), proxy_warning(), RoomScene, Video furniture for a real plan room (#10): Dev 2's extracted items, placed…, Furniture for rooms bound to a video, read from Dev 2's pipeline data directory. (+17 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.11
Nodes (19): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Feng shui score, Free floor area, Front clearance (+11 more)

### Community 76 - "SpatialInputError"
Cohesion: 0.08
Nodes (47): height_overlaps(), Spatial checks independent of HTTP, mesh loading and provider services., A window-openness proxy for layout comparison, not a lighting simulation., CollisionVolume, front_clearance_zone(), furniture_collision_volumes(), prepare_furniture(), prepare_scene() (+39 more)

### Community 77 - "store.ts"
Cohesion: 0.06
Nodes (50): playCue(), ProductCard(), VersionTree(), VersionTreeView(), catalog, catalogCategories, CatalogItem, DEFAULT_ROOM_ID (+42 more)

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
Cohesion: 0.10
Nodes (43): ProductOption, A real retailer product the chat agent found; the editor offers it to add to…, IkeaSearch, PageReader, ProductOption, _host(), _ikea_options(), linkup_client() (+35 more)

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

### Community 96 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 97 - "render_room"
Cohesion: 0.13
Nodes (17): AlignmentRecord, BaseModel, How one asset's pose was decided. Keyed by the asset's stable ID., PlanView, FurnitureItem, Image, Point, RoomScene (+9 more)

### Community 98 - "test_room_routes.py"
Cohesion: 0.13
Nodes (29): bay_room(), _canvas(), l_room(), _png(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),…, L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed., 4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m… (+21 more)

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "test_catalog_imports.py"
Cohesion: 0.28
Nodes (8): client(), MonkeyPatch, parametrize, Path, TestClient, HTTP import of a searched product: page -> unplaced, catalog-sized item., test_import_returns_the_retailer_model_at_catalog_size(), test_unusable_imports_are_422()

### Community 102 - "LayoutModel"
Cohesion: 0.15
Nodes (8): _Budget, LayoutModel, Any, ProgressCallback, Protocol, _Counted, Any, Charges the chat budget for the model calls a delegated harness makes.

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "CatalogError"
Cohesion: 0.07
Nodes (41): fetch(), main(), prepare(), Fetch a balanced, offline IKEA library using only published retailer meshes.…, Reuse bounded, public-only downloads; keep raw evidence outside the project., Expand retailer Draco geometry and expose WebP sources to the shared reader.…, unpack_model(), _along_mesh() (+33 more)

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "retailer.py"
Cohesion: 0.08
Nodes (34): HTMLParser, _binary_models(), _dimensions(), _first_url(), guess_category(), _is_type(), _item_text(), _metres() (+26 more)

### Community 124 - "video_jobs.py"
Cohesion: 0.12
Nodes (24): FalSizeEstimator, batch_failures(), extracting(), extraction_failed(), find_live(), _key(), mesh_live(), namespace_for() (+16 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "catalog.py"
Cohesion: 0.06
Nodes (49): Readers never see a partial file., write_atomic(), card_like(), CatalogImport, _decode(), ImageProvenance, import_product(), imported_assets() (+41 more)

### Community 128 - "openings.py"
Cohesion: 0.24
Nodes (11): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+3 more)

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 130 - "agent.py"
Cohesion: 0.12
Nodes (22): Outcome, _explain_result(), _explore(), _Interpretation, LayoutCancelled, _percent(), BaseModel, Exception (+14 more)

### Community 131 - "check_delivery.py"
Cohesion: 0.25
Nodes (9): main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), Delivery, computed_field, Every delivered asset passed its checks. Proxies are allowed; they are listed., load_dimensions() (+1 more)

### Community 132 - "objective.py"
Cohesion: 0.12
Nodes (21): _access_not_worse(), beats_original(), _check_comparable(), compare_evaluations(), _door_overlap_area(), is_acceptable_proposal(), LayoutComparison, LayoutEvaluation (+13 more)

### Community 133 - "calculate_free_floor_ratio"
Cohesion: 0.24
Nodes (23): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, item(), FurnitureItem, parametrize, RoomScene, Free floor area is distinct from reachable walking space., room() (+15 more)

### Community 134 - "Extractions"
Cohesion: 0.11
Nodes (13): FindRoom, MeshRoom, Prepare, Extractions, The latest extraction job of each plan. Jobs run one at a time (steps 1-2, then…, The room's mesh build, queued now if this is the first time it is asked for., The job of the plan this room belongs to (`<plan_id>-<room_id>`), if any., How often the furniture source of this room's plan has changed (0 = never).… (+5 more)

### Community 135 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 136 - "test_api.py"
Cohesion: 0.20
Nodes (16): payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422() (+8 more)

### Community 137 - "delivery.py"
Cohesion: 0.13
Nodes (20): AssetCheck, _declared_bounds(), _declared_bounds_problems(), _gltf_problems(), inspect_asset(), ndarray, The handoff to Dev 1, with its checks (#18): one servable asset per item,…, The bounds the file declares: the union of its `POSITION` accessors' min/max.… (+12 more)

### Community 139 - "EditorScreen.tsx"
Cohesion: 0.19
Nodes (8): EditorScreen(), clock(), ExtractionProgress(), Sidebar(), useLiveAudit(), connectEditorServices(), isExtractingWarning(), initial

### Community 140 - "SceneFurniture"
Cohesion: 0.21
Nodes (9): FurnitureSource, Protocol, RoomScene, What a furniture source supplies for one room., SceneFurniture, RoomScene, The room as parsed from the plan., Furniture for rooms of plans uploaded with videos; every other room uses… (+1 more)

### Community 141 - "SoundControls.tsx"
Cohesion: 0.27
Nodes (8): editorKey(), handleItemKey(), handleSaveKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, initial

### Community 142 - "Registry"
Cohesion: 0.24
Nodes (6): Connection, Any, Path, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle., Registry

### Community 143 - "_ScriptedSource"
Cohesion: 0.22
Nodes (11): client(), TestClient, Answers `furniture_for` from a script, one entry per call (the last one…, The job finished after `furniture_for` answered "still extracting" (no job is…, Even when the job's progress is gone by the time the response is written., New videos start a job while a request is assembling from the old furniture…, _ScriptedSource, test_a_pending_room_always_tells_the_client_to_ask_again() (+3 more)

### Community 144 - "calculate_feng_shui"
Cohesion: 0.29
Nodes (10): FengShuiReport, _angle_deg(), calculate_feng_shui(), _front(), _occupant(), FurnitureItem, RoomScene, A small, transparent Feng Shui placement metric from the command-position… (+2 more)

### Community 145 - "test_an_assembly_overtaken_by_a_scale_correction_is_done_again"
Cohesion: 0.27
Nodes (8): _get_in_thread(), _HeldSource, RoomScene, A furniture source that waits until released, like a slow pipeline read., PR #59 review: an overtaken GET returned a scene whose shell URL was retired…, _save_in_thread(), test_an_assembly_overtaken_by_a_scale_correction_is_done_again(), Thread

### Community 146 - "test_video_furniture_by_room_state"
Cohesion: 0.29
Nodes (9): _Fallback, plan_room(), MonkeyPatch, RoomScene, A parsed room and a client; extraction jobs run a no-op, never fal., _room(), test_a_room_is_built_while_other_rooms_are_still_searched(), test_video_furniture_by_room_state() (+1 more)

### Community 147 - "_walls"
Cohesion: 0.25
Nodes (9): _length(), Response, WallSegment, PR #59 review: x1.1 made floor-1-room-5's door1 wider than its diagonal wall w6., PR #59 review: x0.25 made floor-1-room-0 invalid and the route answered 500., _scale_room(), test_a_rescaled_diagonal_door_is_accepted_by_the_audit(), test_a_scale_that_breaks_a_room_is_refused_and_changes_nothing() (+1 more)

### Community 148 - "clear_cache"
Cohesion: 0.29
Nodes (8): clear_corrections(), Serve every plan as parsed again (tests)., clear_cache(), Forget assembled scenes (tests, or after the furniture source changes)., client(), The app with `three_floor.png` uploaded (recorded labels, no provider call)., Without labels (no FAL_KEY, or the call fails) the same image, and so the same…, test_the_plan_parsed_without_its_labels_gets_no_video_furniture()

### Community 149 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 150 - "demoHome.ts"
Cohesion: 0.18
Nodes (20): area(), DemoFloor, demoFloors, demoRooms, edgeDistance(), findRoom(), floor(), inside() (+12 more)

### Community 152 - "spatialPreview.ts"
Cohesion: 0.27
Nodes (16): footprint(), toWorld(), byId(), collisionVolumes(), convexOverlapArea(), covered(), detectBlockedDoors(), detectCollisions() (+8 more)

### Community 154 - "no_network"
Cohesion: 0.67
Nodes (3): no_network(), MonkeyPatch, Any attempt to resolve or connect fails the test: no provider, no retailer.

### Community 157 - "furniture_footprint"
Cohesion: 0.17
Nodes (25): furniture_footprint(), Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, make_item(), FurnitureItem, parametrize, Footprint examples independent of meshes, providers and HTTP routes., test_45_degree_corners_follow_threejs_yaw(), test_does_not_mutate_item() (+17 more)

## Knowledge Gaps
- **469 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `Vec3` (+464 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `test_scene_cache.py`, `test_video_jobs.py`, `TestClient`, `test_scene_routes.py`, `calculate_free_floor_ratio`, `objective.py`, `test_api.py`, `test_room_shell.py`, `test_room_align.py`, `calculate_reachable_floor_ratio`, `SceneFurniture`, `test_layout_tools.py`, `test_delivery.py`, `_ScriptedSource`, `calculate_feng_shui`, `propose_layout`, `test_demo_cache_room.py`, `test_objective.py`, `DraftSession`, `test_an_assembly_overtaken_by_a_scale_correction_is_done_again`, `_walls`, `test_room_correct.py`, `._check_winding`, `test_room_parse.py`, `test_contracts.py`, `chat.py`, `parse.py`, `calculate_brightness_approximation`, `furniture_footprint`, `spatial_engine/main.py`, `demo_assets.py`, `detect_blocked_doors`, `detect_out_of_bounds`, `ContractModel`, `scenes.py`, `score_feng_shui`, `scene_cache.py`, `generate_mock_glbs.py`, `Vec2`, `FurnitureAsset`, `test_room_align_vision.py`, `LayoutToolbox`, `audit_scene`, `routes.py`, `test_real_room.py`, `SpatialInputError`, `detect_collisions`, `test_video_furniture_by_room_state`, `detect_front_clearance`, `render_room`, `test_room_routes.py`, `test_demo_assets.py`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `check_delivery.py`, `test_scene_routes.py`, `selection_models.py`, `delivery.py`, `test_room_align.py`, `SceneFurniture`, `test_delivery.py`, `test_normalisation.py`, `.to_item`, `demo_assets.py`, `detect_blocked_doors`, `test_reconstruction.py`, `ContractModel`, `test_contract_occupancy.py`, `test_room_align_vision.py`, `BBoxM`, `demo_cache.py`, `test_fixture_scene.py`, `test_real_room.py`, `CatalogError`, `video_jobs.py`, `catalog.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_catalog.py`, `test_video_jobs.py`, `calculate_free_floor_ratio`, `footprint.py`, `delivery.py`, `calculate_reachable_floor_ratio`, `test_layout_tools.py`, `test_delivery.py`, `propose_layout`, `test_normalisation.py`, `test_objective.py`, `DraftSession`, `test_video_furniture_by_room_state`, `RoomScene`, `furniture_footprint`, `calculate_brightness_approximation`, `detect_blocked_doors`, `test_reconstruction.py`, `detect_out_of_bounds`, `ContractModel`, `score_feng_shui`, `Vec2`, `FurnitureAsset`, `audit_scene`, `furniture_search.py`, `detect_collisions`, `detect_front_clearance`, `test_catalog_imports.py`, `CatalogError`, `retailer.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 247 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 247 INFERRED edges - model-reasoned connections that need verification._
- **Are the 53 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 53 INFERRED edges - model-reasoned connections that need verification._
- **Are the 84 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 84 INFERRED edges - model-reasoned connections that need verification._
- **Are the 78 inferred relationships involving `Pose2D` (e.g. with `catalog_router()` and `FurnitureAsset`) actually correct?**
  _`Pose2D` has 78 INFERRED edges - model-reasoned connections that need verification._