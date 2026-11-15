# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 278 files · ~419,050 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4155 nodes · 12141 edges · 155 communities (124 shown, 31 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1304 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b12dca38`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- test_scene_cache.py
- SceneFurniture
- RoomScene
- test_scene_routes.py
- audio.test.ts
- mesh_providers.py
- footprint.py
- test_segmentation.py
- observe_vision.py
- test_room_align.py
- calculate_free_floor_ratio
- FurnitureAsset
- selection_models.py
- BBoxM
- Registry
- App.tsx
- audit_scene
- test_room_routes.py
- Pose2D
- LayoutToolbox
- regions.py
- test_chat.py
- FurnitureItem
- test_room_parse.py
- layoutAgent.test.tsx
- test_api.py
- detect_blocked_doors
- schema.ts
- parse.py
- calculate_brightness_approximation
- test_demo_cache_room.py
- walk.ts
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- demo_assets.py
- test_room_shell.py
- test_feng_shui_optimisation.py
- test_reconstruction.py
- detect_out_of_bounds
- ContractModel
- scenes.py
- score_feng_shui
- compilerOptions
- test_demo_cache.py
- .to_item
- Sidebar.tsx
- scene_cache.py
- CatalogError
- generate_mock_glbs.py
- Vec2
- test_contract_occupancy.py
- align.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_room_align_vision.py
- Decisions
- layout_tools.py
- room
- routes.py
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
- RoomView.tsx
- Agent Instructions
- test_streaming.py
- test_fixture_scene.py
- agent.ts
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
- Extractions
- PlacementHint
- SoundControls.tsx
- README.md
- frontend/package.json
- test_furniture_search.py
- annotate.py
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- reconstruction/main.py
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift
- SKILL.md
- manifest.json
- retailer.py
- _Counted
- test_demo_assets.py
- vite
- catalog.py
- openings.py
- Validated, cached demo assets (#20, Dev 2.8)
- Extractions
- Protocol
- no_network
- AuditReport
- BaseModel
- plugins
- chat.py
- catalog_router
- demo_cache/README.md
- ParsedFloorPlan
- gt
- furniture_proxy
- ChatReply
- ChatRequest
- LinkupPost
- ProgressCallback
- Exception
- MonkeyPatch
- Scripted
- OptimiseRequest
- demoHome.ts
- Scripted
- Timed
- fetch_product
- furniture_footprint

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 195 edges
2. `useStore` - 95 edges
3. `FurnitureAsset` - 88 edges
4. `BBoxM` - 83 edges
5. `Pose2D` - 80 edges
6. `FurnitureItem` - 76 edges
7. `Registry` - 69 edges
8. `SpatialInputError` - 63 edges
9. `audit_scene()` - 63 edges
10. `propose_layout()` - 61 edges

## Surprising Connections (you probably didn't know these)
- `test_evidence_matches_the_agreed_shape()` --uses--> `AssetEvidence`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `test_dev1_consumes_fixtures_through_the_asset_interface()` --uses--> `FurnitureAsset`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `test_field_docstrings_reach_openapi()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_scene_rules_are_validated()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_all_home_furniture_urls_have_canonical_models()` --uses--> `RoomScene`  [INFERRED]
  tests/test_demo_assets.py → contracts/schema.py

## Import Cycles
- None detected.

## Communities (155 total, 31 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.11
Nodes (45): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., bounds() (+37 more)

### Community 1 - "test_scene_cache.py"
Cohesion: 0.08
Nodes (43): clear_corrections(), Serve every plan as parsed again (tests)., Serve every plan published in `cache_dir` (`routes.restore_plan`); a plan…, restore_published(), _audit(), auditor(), _blockers(), client() (+35 more)

### Community 2 - "SceneFurniture"
Cohesion: 0.10
Nodes (40): MonkeyPatch, What a furniture source supplies for one room., SceneFurniture, extracting(), extraction_failed(), ExtractionError, ExtractionJob, RoomScene (+32 more)

### Community 3 - "RoomScene"
Cohesion: 0.09
Nodes (76): Collection, RoomScene, clear_cache(), Forget assembled scenes (tests, or after the furniture source changes)., _audit(), auditor(), _clear(), client() (+68 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.14
Nodes (34): conform_openings(), RoomScene, Put every door exactly on its wall, so the spatial audit accepts the room. Each…, _audit(), auditor(), client(), _door(), _leaf_end() (+26 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 6 - "mesh_providers.py"
Cohesion: 0.11
Nodes (24): FailureKind, CatalogImportRequest, BaseModel, HTTP import of one retailer product (#19): a searched or pasted product page ->…, main(), Path, Import a retailer product as a furniture asset through the shared pipeline…, write_report() (+16 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (61): any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach() (+53 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.09
Nodes (75): Rect, main(), Path, Review images plus the two machine-readable handoffs: the result and the…, write_report(), _overlaps(), Path, Store a mask and cut-out for every selected view of the scene's (or the named)… (+67 more)

### Community 9 - "observe_vision.py"
Cohesion: 0.08
Nodes (34): Image, build_prompt(), _distance_to_wall(), _draw_marks(), _encode(), _facing(), hints_from_reply(), _Mark (+26 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (57): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+49 more)

### Community 11 - "calculate_free_floor_ratio"
Cohesion: 0.10
Nodes (52): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, item(), FurnitureItem, parametrize (+44 more)

### Community 12 - "FurnitureAsset"
Cohesion: 0.07
Nodes (80): asset_router(), APIRouter, Path, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset(), main() (+72 more)

### Community 13 - "selection_models.py"
Cohesion: 0.06
Nodes (48): ArtifactTooLarge, box_pixels(), fal_media_url(), _fetch(), fetch_bounded(), GrabCutProvider, MaskError, MaskProvider (+40 more)

### Community 14 - "BBoxM"
Cohesion: 0.11
Nodes (54): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, BBoxM, CollisionPart, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).…, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts() (+46 more)

### Community 15 - "Registry"
Cohesion: 0.07
Nodes (89): Connection, DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery(), Exception, Path (+81 more)

### Community 16 - "App.tsx"
Cohesion: 0.06
Nodes (39): App(), ORDER, screenVariants, FloorPlanScreen(), Openings(), PlanRoom(), plural(), points() (+31 more)

### Community 17 - "audit_scene"
Cohesion: 0.10
Nodes (62): OptimiseRequest, AgentLimits, propose_layout(), ProviderError, LayoutProposal, ProgressCallback, Explore within the request's limits and return a re-audited proposal or an…, One allowance per request. Retries and the interpretation call spend the same… (+54 more)

### Community 18 - "test_room_routes.py"
Cohesion: 0.23
Nodes (14): _png(), _plan_file(), fixture, TestClient, Floor-plan routes on the reconstruction service, and the ParsedFloorPlan…, Uploads in tmp_path; extraction jobs recorded, never run against fal., test_errors(), test_oversized_video_is_rejected() (+6 more)

### Community 19 - "Pose2D"
Cohesion: 0.12
Nodes (54): Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., _check_comparable(), compare_layouts(), _door_overlap_area(), evaluate_layout(), AuditReport, RoomScene (+46 more)

### Community 20 - "LayoutToolbox"
Cohesion: 0.06
Nodes (65): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+57 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (32): int32, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point() (+24 more)

### Community 22 - "test_chat.py"
Cohesion: 0.08
Nodes (69): ChatRequest, Exception, ModelReply, ProgressCallback, add_item(), chat(), FurnitureItem, Validated tool handler. A rejected addition never mutates the caller's scene.… (+61 more)

### Community 23 - "FurnitureItem"
Cohesion: 0.05
Nodes (71): FurnitureItem, ParsedRoom, model_validator, floor_polygon is clockwise in plan view and every wall has the room on its…, One room parsed from a floor plan. `scene` uses its floor's shared frame (see…, Correction, AlignmentRecord, AlignmentResult (+63 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.10
Nodes (50): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, FixedAnnotator, PlanAnnotations, Path, Returns pre-recorded annotations (tests, the debug CLI, cached demo plans)., bay_room() (+42 more)

### Community 25 - "layoutAgent.test.tsx"
Cohesion: 0.07
Nodes (35): FengShuiScoreCard(), AuditDiff(), LayoutProposalCard(), PlanDiff(), poseText(), ScoreComparison, useProposalScores(), AuditStats() (+27 more)

### Community 26 - "test_api.py"
Cohesion: 0.09
Nodes (36): AuditReport, payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422() (+28 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.14
Nodes (37): BlockedDoorIssue, BlockedDoorIssue, CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem (+29 more)

### Community 28 - "schema.ts"
Cohesion: 0.05
Nodes (46): ChatStreamEvent, GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, LayoutProgressStage, LayoutStreamEvent, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES (+38 more)

### Community 29 - "parse.py"
Cohesion: 0.12
Nodes (39): FloorCaption, BaseModel, RoomLabel, _assign_labels(), _bridge_sides(), _caption_distance(), _consensus(), _fallback_scale() (+31 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.14
Nodes (34): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item(), FurnitureItem (+26 more)

### Community 31 - "test_demo_cache_room.py"
Cohesion: 0.08
Nodes (52): furniture_data_dir(), Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, broken_cache(), default_bindings(), from_demo_cache(), geometry_mismatch(), geometry_warning(), load_bindings() (+44 more)

### Community 32 - "walk.ts"
Cohesion: 0.07
Nodes (38): WALK_HEADROOM_M, RotationRing(), captureEditorView(), EditorOrbit, EditorView, floor, PlayControllerHandle, pointOnFloor() (+30 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.04
Nodes (85): ChatRequest, POST /chat and /chat/stream., exception_handler, FengShuiResult, JSONResponse, Outcome, RequestValidationError, demo_room_scenes() (+77 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "demo_assets.py"
Cohesion: 0.12
Nodes (27): FileResponse, HTTPException, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model() (+19 more)

### Community 36 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 37 - "test_feng_shui_optimisation.py"
Cohesion: 0.09
Nodes (35): ModelReply, Any, ToolCall, assess_feng_shui(), Assessment, FengShuiResult, Finding, DetailModel (+27 more)

### Community 38 - "test_reconstruction.py"
Cohesion: 0.09
Nodes (39): RuntimeError, MeshError, Any, Exception, Mask, NDArray, uint8, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP… (+31 more)

### Community 39 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 40 - "ContractModel"
Cohesion: 0.08
Nodes (40): ChatErrorEvent, ChatProgressEvent, ChatReplyEvent, ContractModel, _FengShuiModel, LayoutErrorEvent, LayoutProgressEvent, LayoutResultEvent (+32 more)

### Community 41 - "scenes.py"
Cohesion: 0.06
Nodes (48): FurnitureAsset, ge, gt, Protocol, put, Query, assemble_scene(), Assembly (+40 more)

### Community 42 - "score_feng_shui"
Cohesion: 0.10
Nodes (61): FengShuiRequest, POST /feng-shui and /feng-shui/score., FengShuiSightline, RuleScore, _add(), _angle_deg(), _backing(), _balance() (+53 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.07
Nodes (82): _declared_bounds(), _declared_bounds_problems(), _gltf_problems(), inspect_asset(), ndarray, Path, The bounds the file declares: the union of its `POSITION` accessors' min/max.…, Re-read an asset's stored file and check it against the furniture profile and… (+74 more)

### Community 45 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 46 - "Sidebar.tsx"
Cohesion: 0.07
Nodes (29): CatalogPreview(), ChatTab(), FengShuiSection(), HarnessProgress(), HarnessStatus(), LibraryTab(), ProductCard(), tabs (+21 more)

### Community 47 - "scene_cache.py"
Cohesion: 0.10
Nodes (40): Where published scene caches are read from when the service starts (#12).…, scene_cache_dir(), PlanAnnotator, Protocol, _annotator(), _assemble(), cache_path(), CachedScene (+32 more)

### Community 48 - "CatalogError"
Cohesion: 0.13
Nodes (17): CatalogError, _check_public(), fetch_public(), ValueError, The product cannot be imported at all. The message is safe to show., Refuse anything but http(s) to a public address: an imported URL is untrusted…, Download a public URL with a size cap, re-checking every redirect hop., _read_page() (+9 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "Vec2"
Cohesion: 0.15
Nodes (27): DoorOpening, Vec2, WallSegment, A point on the floor plan (Y omitted)., A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, door_center(), door_entry_segment(), _door_frame() (+19 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.15
Nodes (22): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+14 more)

### Community 52 - "align.py"
Cohesion: 0.11
Nodes (29): Facing, _access(), _Choice, _extents(), _front(), _nearby(), _no_frames(), _place_default() (+21 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_room_align_vision.py"
Cohesion: 0.07
Nodes (54): MaskSource, EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., SelectionResult, main(), Debug CLI for furniture alignment: place assets in a room and draw the result.…, Path, directory_frames() (+46 more)

### Community 55 - "Decisions"
Cohesion: 0.06
Nodes (35): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+27 more)

### Community 56 - "layout_tools.py"
Cohesion: 0.11
Nodes (27): _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, _metrics(), _Move, _num() (+19 more)

### Community 57 - "room"
Cohesion: 0.26
Nodes (19): piece(), FurnitureItem, parametrize, RoomScene, The placement metric: each tradition on hand-built geometry, and honest 'not…, A 6 m square room; the door is on the north (z=0) wall, centred at x=2.5., room(), test_a_bed_whose_foot_points_straight_at_the_door_is_in_coffin_position() (+11 more)

### Community 58 - "routes.py"
Cohesion: 0.07
Nodes (44): BinaryIO, File, ParsedFloorPlan, PlanAnnotator, get_annotator(), get_extractions(), get_plan(), get_room() (+36 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "react"
Cohesion: 0.20
Nodes (13): floorPlane, MeshBoundary, ProxyBox(), FurnitureMesh(), categoryWash, disposeInk(), inkify(), inkLine (+5 more)

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

### Community 69 - "RoomView.tsx"
Cohesion: 0.09
Nodes (44): MIN_HEIGHT_OVERLAP_M, MIN_PLAN_OVERLAP_M2, DoorSwings(), Furniture, flaggedFor(), Navigation(), RoomView(), DoorLightBlockers() (+36 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "test_streaming.py"
Cohesion: 0.17
Nodes (18): OptimiseRequest, audit(), AuditReport, RoomScene, Return current spatial findings; scoring, glare and Feng Shui are not assessed., event(), post(), Any (+10 more)

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "agent.ts"
Cohesion: 0.15
Nodes (31): isLibraryAsset(), AgentReply, describeOutlook(), EditorReply, LAYOUT_GOALS, PROGRESS_STAGES, readProducts(), readProposal() (+23 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.11
Nodes (19): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Feng shui score, Free floor area, Front clearance (+11 more)

### Community 76 - "SpatialInputError"
Cohesion: 0.08
Nodes (47): FengShuiReport, height_overlaps(), Spatial checks independent of HTTP, mesh loading and provider services., A window-openness proxy for layout comparison, not a lighting simulation., _angle_deg(), calculate_feng_shui(), _front(), _occupant() (+39 more)

### Community 77 - "store.ts"
Cohesion: 0.07
Nodes (51): playCue(), EditorScreen(), clock(), ExtractionProgress(), Sidebar(), StatsTab(), useLiveAudit(), VersionTree() (+43 more)

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
Cohesion: 0.16
Nodes (26): ProductOption, A real retailer product the chat agent found; the editor offers it to add to…, IkeaSearch, PageReader, ProductOption, _host(), _ikea_options(), linkup_client() (+18 more)

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

### Community 96 - "Extractions"
Cohesion: 0.12
Nodes (12): Runner, Extractions, namespace_for(), Path, The latest extraction job of each plan, run one at a time in a background…, Start extracting these videos' furniture for the plan. False when the same…, The job of the plan this room belongs to (`<plan_id>-<room_id>`), if any., How often the furniture source of this room's plan has changed (0 = never).… (+4 more)

### Community 97 - "PlacementHint"
Cohesion: 0.16
Nodes (12): _Capture, FrameSource, RoomScene, Passes hints through and keeps them, so a live run can be recorded., PlacementHint, PlacementHints, PlacementObserver, BaseModel (+4 more)

### Community 98 - "SoundControls.tsx"
Cohesion: 0.27
Nodes (8): editorKey(), handleItemKey(), handleSaveKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, initial

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "test_furniture_search.py"
Cohesion: 0.23
Nodes (17): Exception, No search could run (no key, provider down). The message is safe to show., SearchUnavailable, ikea(), Linkup, product(), Any, Exception (+9 more)

### Community 102 - "annotate.py"
Cohesion: 0.09
Nodes (23): AnnotationResult, Compass, _extract_json(), FalVisionAnnotator, NullAnnotator, What computer vision cannot read off a floor plan: room labels with their…, Reads labels with a vision LLM on fal.ai (`FAL_KEY`). The endpoint and model…, Plans print labels in capitals ("BEDROOM (4)"); show them in title case. (+15 more)

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "reconstruction/main.py"
Cohesion: 0.22
Nodes (7): Path, Runtime settings of the reconstruction service., Where walkthrough videos uploaded with a floor plan are kept…, upload_dir(), health(), get, Process liveness only; does not probe external providers.

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "retailer.py"
Cohesion: 0.10
Nodes (28): HTMLParser, _binary_models(), _dimensions(), _first_url(), _is_type(), _metres(), _model_urls(), _nodes() (+20 more)

### Community 124 - "_Counted"
Cohesion: 0.29
Nodes (5): _Budget, LayoutModel, _Counted, Any, Charges the chat budget for the model calls a delegated harness makes.

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "catalog.py"
Cohesion: 0.06
Nodes (53): fetch(), main(), prepare(), Fetch a balanced, offline IKEA library using only published retailer meshes.…, Reuse bounded, public-only downloads; keep raw evidence outside the project., Expand retailer Draco geometry and expose WebP sources to the shared reader.…, unpack_model(), Readers never see a partial file. (+45 more)

### Community 128 - "openings.py"
Cohesion: 0.16
Nodes (17): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+9 more)

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 132 - "no_network"
Cohesion: 0.67
Nodes (3): no_network(), MonkeyPatch, Any attempt to resolve or connect fails the test: no provider, no retailer.

### Community 135 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 136 - "chat.py"
Cohesion: 0.09
Nodes (35): AuditReport, BaseModel, ChatReply, LinkupPost, AddItemArguments, _apply(), _combine(), _error_text() (+27 more)

### Community 137 - "catalog_router"
Cohesion: 0.18
Nodes (13): catalog_router(), APIRouter, Fetch, Path, `fetch` replaces the public downloader (tests)., client(), MonkeyPatch, parametrize (+5 more)

### Community 141 - "furniture_proxy"
Cohesion: 0.15
Nodes (12): le, furniture_proxy(), health(), get, gt, Path, Response, Process liveness only; does not probe external providers. (+4 more)

### Community 150 - "demoHome.ts"
Cohesion: 0.17
Nodes (20): area(), DEFAULT_ROOM_ID, DemoFloor, demoFloors, demoRooms, edgeDistance(), findRoom(), floor() (+12 more)

### Community 154 - "fetch_product"
Cohesion: 0.15
Nodes (16): fetch_product(), guess_category(), Category, Fetch, Classify the head phrase, using its last furniture or accessory noun.…, Download and read one retailer product page. Raises CatalogError. `source`…, IKEA products matching `query`, as `catalog_search` results. A result carries…, search_ikea() (+8 more)

### Community 157 - "furniture_footprint"
Cohesion: 0.12
Nodes (36): furniture_footprint(), Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, _open_poses(), place_item(), Placement, FurnitureItem, Polygon, Pose2D (+28 more)

## Knowledge Gaps
- **488 isolated node(s):** `Internal layout comparison (issue #33)`, `Layout drafts for proposed moves (issue #33)`, `Layout exploration tools (issue #33)`, `Brightness approximation for layout comparison`, `Audit endpoint` (+483 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `openings.py`, `test_scene_cache.py`, `test_scene_routes.py`, `observe_vision.py`, `test_room_align.py`, `calculate_free_floor_ratio`, `FurnitureAsset`, `audit_scene`, `Pose2D`, `LayoutToolbox`, `FurnitureItem`, `test_room_parse.py`, `test_api.py`, `detect_blocked_doors`, `furniture_footprint`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `spatial_engine/main.py`, `demo_assets.py`, `test_room_shell.py`, `detect_out_of_bounds`, `ContractModel`, `score_feng_shui`, `scene_cache.py`, `generate_mock_glbs.py`, `Vec2`, `align.py`, `test_room_align_vision.py`, `layout_tools.py`, `room`, `test_streaming.py`, `SpatialInputError`, `detect_collisions`, `PlacementHint`, `test_demo_assets.py`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `test_scene_routes.py`, `observe_vision.py`, `test_room_align.py`, `selection_models.py`, `BBoxM`, `Registry`, `Pose2D`, `FurnitureItem`, `detect_blocked_doors`, `test_demo_cache_room.py`, `demo_assets.py`, `test_reconstruction.py`, `ContractModel`, `scenes.py`, `test_demo_cache.py`, `.to_item`, `test_contract_occupancy.py`, `align.py`, `test_room_align_vision.py`, `test_fixture_scene.py`, `PlacementHint`, `catalog.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `FurnitureItem` connect `FurnitureItem` to `RoomScene`, `footprint.py`, `catalog_router`, `test_room_align.py`, `observe_vision.py`, `FurnitureAsset`, `calculate_free_floor_ratio`, `BBoxM`, `audit_scene`, `Pose2D`, `LayoutToolbox`, `test_chat.py`, `detect_blocked_doors`, `furniture_footprint`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `detect_out_of_bounds`, `ContractModel`, `score_feng_shui`, `Vec2`, `test_contract_occupancy.py`, `align.py`, `room`, `test_fixture_scene.py`, `SpatialInputError`, `detect_collisions`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 192 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 192 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 80 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 80 INFERRED edges - model-reasoned connections that need verification._
- **Are the 77 inferred relationships involving `Pose2D` (e.g. with `catalog_router()` and `FurnitureAsset`) actually correct?**
  _`Pose2D` has 77 INFERRED edges - model-reasoned connections that need verification._