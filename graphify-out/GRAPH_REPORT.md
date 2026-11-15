# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 278 files · ~420,366 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4159 nodes · 12150 edges · 169 communities (134 shown, 35 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1304 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3d499177`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- test_scene_cache.py
- test_video_jobs.py
- TestClient
- test_scene_routes.py
- audio.test.ts
- test_reconstruction.py
- footprint.py
- test_segmentation.py
- test_room_shell.py
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
- layoutAgent.test.tsx
- AuditReport
- detect_blocked_doors
- schema.ts
- parse.py
- calculate_brightness_approximation
- test_demo_cache_room.py
- walk.ts
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- demo_assets.py
- shell.py
- test_feng_shui_optimisation.py
- RequestBudget
- detect_out_of_bounds
- ContractModel
- scenes.py
- score_feng_shui
- compilerOptions
- test_demo_cache.py
- .to_item
- layoutProgress.test.tsx
- scene_cache.py
- CatalogError
- generate_mock_glbs.py
- divided_access_room
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
- demo_cache.py
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
- detect_front_clearance
- PlacementHint
- SoundControls.tsx
- README.md
- frontend/package.json
- test_real_room.py
- AnnotationResult
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
- RetailerProduct
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
- spatialPreview.ts
- delivery.py
- Registry
- RoomScene
- demo_rooms
- furniture_footprint
- feng_shui_skill_unavailable
- model_validator
- asset_store.py
- clear_cache
- test_shared_handoff_case
- LayoutMetrics
- Vec2
- _HeldSource
- _inside
- .of
- test_shell_build_needs_no_optional_geometry_packages

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 195 edges
2. `useStore` - 96 edges
3. `FurnitureAsset` - 88 edges
4. `BBoxM` - 83 edges
5. `Pose2D` - 80 edges
6. `FurnitureItem` - 76 edges
7. `Registry` - 69 edges
8. `SpatialInputError` - 63 edges
9. `audit_scene()` - 63 edges
10. `propose_layout()` - 61 edges

## Surprising Connections (you probably didn't know these)
- `test_dev1_consumes_fixtures_through_the_asset_interface()` --uses--> `FurnitureAsset`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `test_evidence_matches_the_agreed_shape()` --uses--> `AssetEvidence`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `test_field_docstrings_reach_openapi()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_scene_rules_are_validated()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_all_home_furniture_urls_have_canonical_models()` --uses--> `RoomScene`  [INFERRED]
  tests/test_demo_assets.py → contracts/schema.py

## Import Cycles
- None detected.

## Communities (169 total, 35 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.08
Nodes (61): catalog_id(), catalog_scene(), import_catalog_asset(), import_product(), imported_assets(), _normalises(), Category, Fetch (+53 more)

### Community 1 - "test_scene_cache.py"
Cohesion: 0.08
Nodes (45): Serve a published plan (`scene_cache.py`, #12) as if it had been uploaded and…, restore_plan(), differences(), Serve every plan published in `cache_dir` (`routes.restore_plan`); a plan…, Where two JSON-like values differ: the paths, such as…, restore_published(), _audit(), auditor() (+37 more)

### Community 2 - "test_video_jobs.py"
Cohesion: 0.07
Nodes (42): MonkeyPatch, Runner, ExtractionError, ExtractionJob, Extractions, namespace_for(), Path, The latest extraction job of each plan, run one at a time in a background… (+34 more)

### Community 3 - "TestClient"
Cohesion: 0.19
Nodes (32): Collection, still_extracting(), _put(), Path, TestClient, A request while frame selection is still storing items must not freeze the room., Without labels (no FAL_KEY, or the call fails) the same image, and so the same…, PR #59 review: `"NaN"` was saved and came back as `null`, an invalid scene. (+24 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.16
Nodes (30): _audit(), auditor(), _door(), _leaf_end(), DoorOpening, parametrize, RoomScene, TestClient (+22 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.06
Nodes (18): renderCue(), AudioEngine, AudioPlatform, AudioStatus, browserPlatform, MusicStatus, ramp(), AUDIO_STORAGE_KEY (+10 more)

### Community 6 - "test_reconstruction.py"
Cohesion: 0.06
Nodes (79): ImageProvenance, Retailer products through the shared asset pipeline (#19). A product is…, The product image the item's view was made from., CatalogImportRequest, BaseModel, HTTP import of one retailer product (#19): a searched or pasted product page ->…, AssetCheck, What was delivered for one item and what re-reading its stored file found. (+71 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (59): DoorOpening, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by() (+51 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.09
Nodes (71): Rect, main(), Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the…, write_report(), _overlaps(), Path (+63 more)

### Community 9 - "test_room_shell.py"
Cohesion: 0.12
Nodes (39): build_shell(), Scene, The room shell as a trimesh Scene with nodes `floor`, `ceiling`, `wall_<id>`., corner_probes(), invalid_footprints(), _l_door(), make_scene(), parametrize (+31 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.11
Nodes (59): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, Path, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms). (+51 more)

### Community 11 - "calculate_free_floor_ratio"
Cohesion: 0.07
Nodes (68): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, payload(), Any, Exception (+60 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.15
Nodes (39): Store a finished, profile-conforming `.glb` and return its `glb_url`., store_asset(), check_placed(), deliver_furniture(), RoomScene, A scene's furniture for Dev 1 to place: per item, its checked mesh or its…, Faults in how a scene carries delivered assets; empty when every asset appears…, audit() (+31 more)

### Community 13 - "Box"
Cohesion: 0.09
Nodes (37): ArtifactTooLarge, box_pixels(), fal_media_url(), FalSamProvider, _fetch(), fetch_bounded(), GrabCutProvider, MaskError (+29 more)

### Community 14 - "BBoxM"
Cohesion: 0.11
Nodes (54): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, BBoxM, CollisionPart, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).…, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts() (+46 more)

### Community 15 - "test_selection.py"
Cohesion: 0.08
Nodes (81): DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery(), Exception, Path, Protocol (+73 more)

### Community 16 - "App.tsx"
Cohesion: 0.09
Nodes (28): App(), ORDER, screenVariants, FloorPlanScreen(), Openings(), PlanRoom(), plural(), points() (+20 more)

### Community 17 - "propose_layout"
Cohesion: 0.11
Nodes (59): OptimiseRequest, AgentLimits, propose_layout(), ProviderError, LayoutProposal, ProgressCallback, Explore within the request's limits and return a re-audited proposal or an…, One allowance per request. Retries and the interpretation call spend the same… (+51 more)

### Community 18 - "test_room_routes.py"
Cohesion: 0.13
Nodes (28): bay_room(), _canvas(), l_room(), _png(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),…, L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed., 4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m… (+20 more)

### Community 19 - "Pose2D"
Cohesion: 0.11
Nodes (58): Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., _access_not_worse(), beats_original(), compare_evaluations(), compare_layouts(), evaluate_layout(), is_acceptable_proposal() (+50 more)

### Community 20 - "DraftSession"
Cohesion: 0.10
Nodes (38): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+30 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (34): int32, Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction() (+26 more)

### Community 22 - "test_chat.py"
Cohesion: 0.08
Nodes (72): ChatRequest, Exception, ModelReply, ProgressCallback, add_item(), chat(), FurnitureItem, Validated tool handler. A rejected addition never mutates the caller's scene.… (+64 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.08
Nodes (53): model_validator, floor_polygon is clockwise in plan view and every wall has the room on its…, apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, InvalidScale (+45 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.08
Nodes (57): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, Compass, _extract_json(), FalVisionAnnotator, FixedAnnotator, NullAnnotator (+49 more)

### Community 25 - "layoutAgent.test.tsx"
Cohesion: 0.07
Nodes (32): AuditDiff(), LayoutProposalCard(), PlanDiff(), poseText(), ScoreComparison, useProposalScores(), useLiveAudit(), fixture (+24 more)

### Community 26 - "AuditReport"
Cohesion: 0.14
Nodes (22): AuditReport, FengShuiReport, load_generator(), load_mock(), parametrize, RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are… (+14 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.19
Nodes (31): BlockedDoorIssue, BlockedDoorIssue, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize, RoomScene (+23 more)

### Community 28 - "schema.ts"
Cohesion: 0.04
Nodes (48): ChatStreamEvent, GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, LayoutProgressStage, LayoutStreamEvent, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES (+40 more)

### Community 29 - "parse.py"
Cohesion: 0.14
Nodes (34): FloorCaption, BaseModel, RoomLabel, _assign_labels(), _bridge_sides(), _caption_distance(), _consensus(), _fallback_scale() (+26 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.18
Nodes (28): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item(), FurnitureItem (+20 more)

### Community 31 - "test_demo_cache_room.py"
Cohesion: 0.12
Nodes (35): broken_cache(), from_demo_cache(), load_bindings(), Bindings by scene ID., assert_readers_agree(), _audit(), auditor(), _client() (+27 more)

### Community 32 - "walk.ts"
Cohesion: 0.07
Nodes (38): WALK_HEADROOM_M, EditorScreen(), RotationRing(), captureEditorView(), EditorOrbit, EditorView, floor, PlayControllerHandle (+30 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.04
Nodes (76): ChatRequest, POST /chat and /chat/stream., FengShuiResult, Outcome, demo_room_scenes(), profile(), Any, RoomScene (+68 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "demo_assets.py"
Cohesion: 0.20
Nodes (15): FileResponse, HTTPException, demo_shell(), furniture_model(), legacy_model(), _model_file(), get, Path (+7 more)

### Community 36 - "shell.py"
Cohesion: 0.11
Nodes (37): int64, _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key(), _miter() (+29 more)

### Community 37 - "test_feng_shui_optimisation.py"
Cohesion: 0.10
Nodes (30): ModelReply, Any, ToolCall, assess_feng_shui(), Assessment, FengShuiResult, Finding, DetailModel (+22 more)

### Community 38 - "RequestBudget"
Cohesion: 0.08
Nodes (35): FailureKind, RuntimeError, _decode(), item_box(), Mask, NDArray, uint8, The next published model that is usable and within the triangle budget. Each… (+27 more)

### Community 39 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 40 - "ContractModel"
Cohesion: 0.08
Nodes (43): ChatErrorEvent, ChatProgressEvent, ChatReplyEvent, ContractModel, _FengShuiModel, LayoutErrorEvent, LayoutProgressEvent, LayoutResultEvent (+35 more)

### Community 41 - "scenes.py"
Cohesion: 0.05
Nodes (62): FurnitureAsset, ge, gt, Protocol, put, Query, assemble_scene(), Assembly (+54 more)

### Community 42 - "score_feng_shui"
Cohesion: 0.10
Nodes (65): FengShuiRequest, POST /feng-shui and /feng-shui/score., FengShuiSightline, RuleScore, AuditReport, FengShuiRequest, Shared validation for the assessment and the score; returns the audit and…, validate_feng_shui_request() (+57 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.14
Nodes (39): cache_folder(), DemoCache, publish_catalog_scene(), Publish every product imported into `scene_id` (#19), with its retailer…, The scene's published cache, its files verified; None when none is published.…, A scene's folder: readable, and distinct for scene IDs that read alike., read_demo_cache(), _generation() (+31 more)

### Community 45 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 46 - "layoutProgress.test.tsx"
Cohesion: 0.14
Nodes (15): HarnessProgress(), HarnessStatus(), proposalSummary(), initial, proposal(), propose(), report(), response() (+7 more)

### Community 47 - "scene_cache.py"
Cohesion: 0.08
Nodes (48): Path, Where published scene caches are read from when the service starts (#12).…, scene_cache_dir(), PlanAnnotator, Path, Protocol, plan_id_for(), ValueError (+40 more)

### Community 48 - "CatalogError"
Cohesion: 0.15
Nodes (14): CatalogError, _check_public(), fetch_public(), ValueError, The product cannot be imported at all. The message is safe to show., Refuse anything but http(s) to a public address: an imported URL is untrusted…, Download a public URL with a size cap, re-checking every redirect hop., test_download_deadline_stops_trickling_response() (+6 more)

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
Cohesion: 0.07
Nodes (49): FurnitureItem, Correction, Facing, FurnitureAsset, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence…, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., _access(), _Choice (+41 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_room_align_vision.py"
Cohesion: 0.04
Nodes (94): Image, MaskSource, EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., AlignmentRecord, AlignmentResult, main(), pose_error() (+86 more)

### Community 55 - "Decisions"
Cohesion: 0.06
Nodes (35): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+27 more)

### Community 56 - "LayoutToolbox"
Cohesion: 0.10
Nodes (41): _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, LayoutPreferences, LayoutToolbox, _metrics() (+33 more)

### Community 57 - "audit_scene"
Cohesion: 0.15
Nodes (30): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+22 more)

### Community 58 - "routes.py"
Cohesion: 0.07
Nodes (45): BinaryIO, File, ParsedFloorPlan, PlanAnnotator, Where walkthrough videos uploaded with a floor plan are kept…, upload_dir(), get_annotator(), get_extractions() (+37 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "demo_cache.py"
Cohesion: 0.13
Nodes (34): Readers never see a partial file., write_atomic(), CachedFile, CacheError, current_generation(), _inside(), install_demo_cache(), _intact() (+26 more)

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
Cohesion: 0.18
Nodes (14): Gray, decode(), estimate_wall_px(), flatten_illumination(), Mask, NDArray, uint8, rasterise() (+6 more)

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
Cohesion: 0.10
Nodes (35): floorPlane, Furniture, MeshBoundary, ProxyBox(), FurnitureMesh(), categoryWash, disposeInk(), inkify() (+27 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "test_streaming.py"
Cohesion: 0.16
Nodes (18): OptimiseRequest, audit(), AuditReport, RoomScene, Return current spatial findings; scoring, glare and Feng Shui are not assessed., event(), post(), Any (+10 more)

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "agent.ts"
Cohesion: 0.15
Nodes (32): isLibraryAsset(), AgentReply, describeOutlook(), EditorReply, LAYOUT_GOALS, PROGRESS_STAGES, readProducts(), readProposal() (+24 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.11
Nodes (19): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Feng shui score, Free floor area, Front clearance (+11 more)

### Community 76 - "SpatialInputError"
Cohesion: 0.07
Nodes (61): WallSegment, FengShuiReport, Spatial checks independent of HTTP, mesh loading and provider services., A window-openness proxy for layout comparison, not a lighting simulation., _angle_deg(), calculate_feng_shui(), _front(), _occupant() (+53 more)

### Community 77 - "store.ts"
Cohesion: 0.05
Nodes (71): CatalogPreview(), clock(), ExtractionProgress(), FengShuiScoreCard(), AuditStats(), ChatTab(), FengShuiSection(), LibraryTab() (+63 more)

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

### Community 97 - "PlacementHint"
Cohesion: 0.16
Nodes (12): _Capture, FrameSource, RoomScene, Passes hints through and keeps them, so a live run can be recorded., PlacementHint, PlacementHints, PlacementObserver, BaseModel (+4 more)

### Community 98 - "SoundControls.tsx"
Cohesion: 0.15
Nodes (17): listeners, onSoundCue(), PartialTone, playCue(), SoundCue, tones, useAudioPreferences, editorKey() (+9 more)

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "test_real_room.py"
Cohesion: 0.14
Nodes (27): proxy_warning(), _audit(), auditor(), _collides(), _findings(), _get_in_thread(), _item(), _moved() (+19 more)

### Community 102 - "AnnotationResult"
Cohesion: 0.40
Nodes (3): AnnotationResult, The label provider, for a service that must not need it., Unreachable

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "reconstruction/main.py"
Cohesion: 0.17
Nodes (13): import_url(), ImportRequest, BaseModel, Editor URL imports through the existing, public-address-only retailer pipeline., furniture_data_dir(), Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, health() (+5 more)

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "retailer.py"
Cohesion: 0.09
Nodes (32): HTMLParser, _binary_models(), _dimensions(), _first_url(), guess_category(), _is_type(), _metres(), _model_urls() (+24 more)

### Community 124 - "_Counted"
Cohesion: 0.29
Nodes (5): _Budget, LayoutModel, _Counted, Any, Charges the chat budget for the model calls a delegated harness makes.

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "RetailerProduct"
Cohesion: 0.08
Nodes (35): fetch(), main(), prepare(), Fetch a balanced, offline IKEA library using only published retailer meshes.…, Reuse bounded, public-only downloads; keep raw evidence outside the project., Expand retailer Draco geometry and expose WebP sources to the shared reader.…, unpack_model(), _along_mesh() (+27 more)

### Community 128 - "openings.py"
Cohesion: 0.15
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
Cohesion: 0.10
Nodes (30): DropCard(), rise, usePreview(), area(), DemoFloor, demoFloors, demoRooms, edgeDistance() (+22 more)

### Community 152 - "spatialPreview.ts"
Cohesion: 0.20
Nodes (19): DoorSwings(), doorSwing(), footprint(), Pt, toWorld(), byId(), collisionVolumes(), convexOverlapArea() (+11 more)

### Community 153 - "delivery.py"
Cohesion: 0.13
Nodes (19): main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), _declared_bounds(), _declared_bounds_problems(), Delivery, _gltf_problems() (+11 more)

### Community 154 - "Registry"
Cohesion: 0.24
Nodes (6): Connection, Any, Path, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle., Registry

### Community 155 - "RoomScene"
Cohesion: 0.21
Nodes (13): RoomScene, geometry_mismatch(), RoomScene, Why `room` is not the room `binding` was made for, or None when it is. Compares…, _length(), Response, WallSegment, The binding names a room by its shape: the user may correct its scale (#11). (+5 more)

### Community 156 - "demo_rooms"
Cohesion: 0.24
Nodes (13): demo_floors(), demo_room_scene(), demo_rooms(), RoomScene, The shared three-floor fixtures, one whole-floor scene per floor name., Split the shared floor fixtures by wall prefix, in the original floor…, One demo room as the editor opens it (`roomScene` in…, demo_selection() (+5 more)

### Community 157 - "furniture_footprint"
Cohesion: 0.10
Nodes (42): height_overlaps(), CollisionVolume, furniture_footprint(), An item's occupied box transformed into a vertical prism in room space., Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, _open_poses(), _overlaps(), place_item() (+34 more)

### Community 158 - "feng_shui_skill_unavailable"
Cohesion: 0.25
Nodes (11): exception_handler, JSONResponse, RequestValidationError, feng_shui_skill_unavailable(), invalid_request(), Exception, Request, A missing or malformed skill file is a server configuration error, never a 500… (+3 more)

### Community 160 - "asset_store.py"
Cohesion: 0.33
Nodes (5): asset_router(), APIRouter, Path, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`.

### Community 161 - "clear_cache"
Cohesion: 0.33
Nodes (6): clear_corrections(), Serve every plan as parsed again (tests)., clear_cache(), Forget assembled scenes (tests, or after the furniture source changes)., client(), The app with `three_floor.png` uploaded (recorded labels, no provider call).

### Community 162 - "test_shared_handoff_case"
Cohesion: 0.33
Nodes (4): Any, parametrize, Reusable scene variants and expected findings for Dev 3/4 integration., test_shared_handoff_case()

### Community 164 - "Vec2"
Cohesion: 0.50
Nodes (4): Vec2, A point on the floor plan (Y omitted)., RoomScene, room()

### Community 166 - "_inside"
Cohesion: 0.50
Nodes (4): _inside(), ndarray, Trimesh, Ray parity in plain numpy (Moller-Trumbore), so the probes need no SciPy or…

## Knowledge Gaps
- **490 isolated node(s):** `tabs`, `imports`, `PlaceReply`, `EditorMode`, `SavedRoom` (+485 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `openings.py`, `test_scene_cache.py`, `TestClient`, `test_scene_routes.py`, `test_room_shell.py`, `test_room_align.py`, `calculate_free_floor_ratio`, `test_delivery.py`, `propose_layout`, `Pose2D`, `DraftSession`, `test_room_correct.py`, `test_room_parse.py`, `AuditReport`, `detect_blocked_doors`, `demo_rooms`, `furniture_footprint`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `spatial_engine/main.py`, `test_shared_handoff_case`, `demo_assets.py`, `shell.py`, `Vec2`, `_HeldSource`, `detect_out_of_bounds`, `ContractModel`, `scenes.py`, `score_feng_shui`, `scene_cache.py`, `generate_mock_glbs.py`, `divided_access_room`, `FurnitureAsset`, `test_room_align_vision.py`, `LayoutToolbox`, `audit_scene`, `test_streaming.py`, `SpatialInputError`, `detect_collisions`, `detect_front_clearance`, `PlacementHint`, `test_real_room.py`, `test_demo_assets.py`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `PlacementHint`, `test_scene_routes.py`, `test_reconstruction.py`, `ContractModel`, `scenes.py`, `test_room_align.py`, `test_fixture_scene.py`, `test_delivery.py`, `test_demo_cache.py`, `BBoxM`, `.to_item`, `Pose2D`, `test_contract_occupancy.py`, `test_room_align_vision.py`, `delivery.py`, `demo_rooms`, `demo_cache.py`, `RetailerProduct`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_catalog.py`, `test_reconstruction.py`, `footprint.py`, `catalog_router`, `calculate_free_floor_ratio`, `test_delivery.py`, `propose_layout`, `Pose2D`, `DraftSession`, `test_chat.py`, `detect_blocked_doors`, `furniture_footprint`, `calculate_brightness_approximation`, `RequestBudget`, `detect_out_of_bounds`, `ContractModel`, `score_feng_shui`, `divided_access_room`, `FurnitureAsset`, `LayoutToolbox`, `audit_scene`, `furniture_search.py`, `detect_collisions`, `detect_front_clearance`, `retailer.py`, `RetailerProduct`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 192 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 192 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 80 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 80 INFERRED edges - model-reasoned connections that need verification._
- **Are the 77 inferred relationships involving `Pose2D` (e.g. with `catalog_router()` and `FurnitureAsset`) actually correct?**
  _`Pose2D` has 77 INFERRED edges - model-reasoned connections that need verification._