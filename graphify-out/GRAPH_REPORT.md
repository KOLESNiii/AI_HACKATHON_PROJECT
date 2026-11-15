# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 270 files · ~410,947 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3988 nodes · 11882 edges · 160 communities (134 shown, 26 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1378 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3e5b1182`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- test_scene_cache.py
- test_room_align_vision.py
- test_real_room.py
- test_scene_routes.py
- audio.test.ts
- cache_ikea_library.py
- footprint.py
- test_segmentation.py
- models.py
- test_room_align.py
- calculate_reachable_floor_ratio
- test_delivery.py
- .segment
- BBoxM
- test_selection.py
- react
- propose_layout
- FixedAnnotator
- Pose2D
- DraftSession
- regions.py
- RoomScene
- test_room_correct.py
- test_room_parse.py
- test_reconstruction.py
- AuditReport
- detect_blocked_doors
- contracts.ts
- parse.py
- calculate_brightness_approximation
- test_demo_cache_room.py
- walk.ts
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
- Sidebar.tsx
- scene_cache.py
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
- annotate.py
- compilerOptions
- Video frame selection and furniture identity — issue #14
- shell.py
- Dev 2 → Dev 1 asset handoff
- dependencies
- devDependencies
- raster.py
- polygon.py
- Architecture
- Dev 4 implementation and integration plan
- RoomView.tsx
- Agent Instructions
- delivery.py
- test_fixture_scene.py
- routes.py
- Implementation plan: issue #14
- Spatial engine
- report.py
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
- make_item
- test_layout_tools.py
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
- ProviderError
- test_demo_assets.py
- vite
- catalog.py
- openings.py
- Validated, cached demo assets (#20, Dev 2.8)
- normalise_mesh
- detect_out_of_bounds
- calculate_free_floor_ratio
- test_api.py
- add_item
- plugins
- chat
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
- layoutProgress.test.tsx
- reconstruct_furniture
- test_streaming.py
- check_layout_demo.py
- fetch_product
- feng_shui_skill_unavailable
- Any
- _open_poses
- test_shared_handoff_case
- proxy_glb

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
- `test_dev1_consumes_fixtures_through_the_asset_interface()` --uses--> `FurnitureAsset`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `test_evidence_matches_the_agreed_shape()` --uses--> `AssetEvidence`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py

## Import Cycles
- None detected.

## Communities (160 total, 26 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.09
Nodes (49): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., Labelled sizes in prose: "Width: 120 cm" for each axis, or "W120 x D60 x H75… (+41 more)

### Community 1 - "test_scene_cache.py"
Cohesion: 0.09
Nodes (41): Serve a published plan (`scene_cache.py`, #12) as if it had been uploaded and…, restore_plan(), Serve every plan published in `cache_dir` (`routes.restore_plan`); a plan…, restore_published(), _audit(), auditor(), _blockers(), client() (+33 more)

### Community 2 - "test_room_align_vision.py"
Cohesion: 0.05
Nodes (64): Image, MaskSource, build_prompt(), _distance_to_wall(), _draw_marks(), _encode(), _facing(), FalVisionObserver (+56 more)

### Community 3 - "test_real_room.py"
Cohesion: 0.08
Nodes (75): Collection, clear_cache(), Forget assembled scenes (tests, or after the furniture source changes)., _audit(), auditor(), _clear(), client(), _collides() (+67 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.10
Nodes (42): assets_of(), NoFurniture, RoomScene, One room + its furniture -> the `RoomScene` the editor and the audit load (#9).…, A scene's furniture as pose-less assets with placeholder evidence (no source…, What a furniture source supplies for one room., The room alone: what parsed rooms get until #16 produces furniture assets., SceneFurniture (+34 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 6 - "cache_ikea_library.py"
Cohesion: 0.19
Nodes (13): fetch(), main(), prepare(), Fetch a balanced, offline IKEA library using only published retailer meshes.…, Reuse bounded, public-only downloads; keep raw evidence outside the project., Expand retailer Draco geometry and expose WebP sources to the shared reader.…, unpack_model(), _along_mesh() (+5 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (57): any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach() (+49 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.07
Nodes (83): Connection, Rect, GrabCutProvider, MaskError, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, No network or cost. Approximate: it can keep floor or an occluder inside the…, Any, Path (+75 more)

### Community 9 - "models.py"
Cohesion: 0.07
Nodes (38): Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence…, AlignmentRecord, AlignmentResult, _Capture, main(), pose_error(), FrameSource, FurnitureItem (+30 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (58): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+50 more)

### Community 11 - "calculate_reachable_floor_ratio"
Cohesion: 0.17
Nodes (29): calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, divided_room(), obstacle(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.13
Nodes (43): asset_router(), APIRouter, Path, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset(), check_placed() (+35 more)

### Community 13 - ".segment"
Cohesion: 0.18
Nodes (14): box_pixels(), Any, NDArray, uint8, (x0, y0, x1, y1) with at least one pixel, matching `video.crop`., One segment per box, in order; None where none was produced. Raises MaskError…, Segment, _bounds() (+6 more)

### Community 14 - "BBoxM"
Cohesion: 0.20
Nodes (33): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, assert_fits(), chair_like(), gltf_json(), BBoxM, parametrize, Path (+25 more)

### Community 15 - "test_selection.py"
Cohesion: 0.07
Nodes (92): AssetEvidence, EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery() (+84 more)

### Community 16 - "react"
Cohesion: 0.07
Nodes (33): App(), ORDER, screenVariants, EditorScreen(), Sidebar(), useLiveAudit(), HomeScreen(), rise (+25 more)

### Community 17 - "propose_layout"
Cohesion: 0.16
Nodes (47): OptimiseRequest, propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, Step, interpret(), item(), move() (+39 more)

### Community 18 - "FixedAnnotator"
Cohesion: 0.21
Nodes (11): FixedAnnotator, Path, Returns pre-recorded annotations (tests, the debug CLI, cached demo plans)., _png(), client(), TestClient, Floor-plan routes on the reconstruction service, and the ParsedFloorPlan…, test_errors() (+3 more)

### Community 19 - "Pose2D"
Cohesion: 0.10
Nodes (67): Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., _access_not_worse(), beats_original(), _check_comparable(), compare_evaluations(), compare_layouts(), _door_overlap_area() (+59 more)

### Community 20 - "DraftSession"
Cohesion: 0.11
Nodes (36): _arrangement(), DraftSession, _echo(), LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one…, A fresh scene at the base revision, so its audit identifies the submitted scene. (+28 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (34): int32, Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction() (+26 more)

### Community 22 - "RoomScene"
Cohesion: 0.16
Nodes (40): ChatRequest, RoomScene, POST /chat and /chat/stream., MonkeyPatch, arguments(), blocker(), move(), fixture (+32 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.08
Nodes (50): floor_polygon is clockwise in plan view and every wall has the room on its…, model_validator, apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, InvalidScale (+42 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.12
Nodes (47): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, PlanAnnotations, bay_room(), _canvas(), _close(), _example() (+39 more)

### Community 25 - "test_reconstruction.py"
Cohesion: 0.07
Nodes (44): FailureKind, RuntimeError, Mask, The retailer's own published model as the item's raw mesh. No inference and no…, The next published model that is usable and within the triangle budget. Each…, RetailerModelProvider, inspect_mesh(), MeshError (+36 more)

### Community 26 - "AuditReport"
Cohesion: 0.14
Nodes (20): AuditReport, load_generator(), load_mock(), parametrize, RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must… (+12 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.18
Nodes (33): BlockedDoorIssue, BlockedDoorIssue, CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem (+25 more)

### Community 28 - "contracts.ts"
Cohesion: 0.06
Nodes (48): ChatStreamEvent, GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, LayoutProgressStage, LayoutStreamEvent, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES (+40 more)

### Community 29 - "parse.py"
Cohesion: 0.13
Nodes (33): RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _caption_distance(), _consensus(), _fallback_scale(), _floor_order() (+25 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.13
Nodes (35): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, A window-openness proxy for layout comparison, not a lighting simulation., Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item() (+27 more)

### Community 31 - "test_demo_cache_room.py"
Cohesion: 0.09
Nodes (44): broken_cache(), from_demo_cache(), geometry_mismatch(), geometry_warning(), load_bindings(), proxy_warning(), RoomScene, Video furniture for a real plan room (#10): Dev 2's extracted items, placed… (+36 more)

### Community 32 - "walk.ts"
Cohesion: 0.07
Nodes (34): WALK_HEADROOM_M, captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera(), restoreEditorView() (+26 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.05
Nodes (71): FengShuiResult, Outcome, AnthropicLayoutModel, _explain_result(), _explore(), _interpret(), _Interpretation, LayoutModel (+63 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "spatialPreview.ts"
Cohesion: 0.30
Nodes (15): footprint(), toWorld(), byId(), collisionVolumes(), convexOverlapArea(), covered(), detectBlockedDoors(), detectCollisions() (+7 more)

### Community 36 - "test_room_shell.py"
Cohesion: 0.10
Nodes (46): build_shell(), Scene, The room shell as a trimesh Scene with nodes `floor`, `ceiling`, `wall_<id>`., shell_glb(), corner_probes(), _inside(), invalid_footprints(), _l_door() (+38 more)

### Community 37 - "test_feng_shui_optimisation.py"
Cohesion: 0.14
Nodes (24): ModelReply, Any, ToolCall, assess_feng_shui(), FengShuiRequest, Any, original_room(), Scripted (+16 more)

### Community 38 - "scenes.py"
Cohesion: 0.06
Nodes (50): ge, Query, demo_cache_dir(), furniture_data_dir(), Path, Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, Where published demo furniture is read from when the pipeline has none (#20).… (+42 more)

### Community 39 - "agent.ts"
Cohesion: 0.07
Nodes (54): AuditDiff(), LayoutProposalCard(), PlanDiff(), poseText(), ScoreComparison, useProposalScores(), isLibraryAsset(), AgentReply (+46 more)

### Community 40 - "ContractModel"
Cohesion: 0.07
Nodes (45): ChatErrorEvent, ChatProgressEvent, ChatReplyEvent, ContractModel, _FengShuiModel, LayoutErrorEvent, LayoutProgressEvent, LayoutResultEvent (+37 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.12
Nodes (26): FileResponse, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file() (+18 more)

### Community 42 - "score_feng_shui"
Cohesion: 0.10
Nodes (65): FengShuiRequest, POST /feng-shui and /feng-shui/score., FengShuiSightline, RuleScore, AuditReport, FengShuiRequest, Shared validation for the assessment and the score; returns the audit and…, validate_feng_shui_request() (+57 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.09
Nodes (73): inspect_asset(), Re-read an asset's stored file and check it against the furniture profile and…, cache_folder(), CachedFile, CacheError, current_generation(), DemoCache, _inside() (+65 more)

### Community 45 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 46 - "Sidebar.tsx"
Cohesion: 0.12
Nodes (17): CatalogPreview(), FengShuiScoreCard(), AuditStats(), LibraryTab(), StatsTab(), tabs, catalog, catalogCategories (+9 more)

### Community 47 - "scene_cache.py"
Cohesion: 0.09
Nodes (47): Readers never see a partial file., write_atomic(), assemble_scene(), Assembly, The room with its furniture placed. Never drops the room: a source that fails…, _annotator(), _assemble(), cache_path() (+39 more)

### Community 48 - "CatalogError"
Cohesion: 0.15
Nodes (15): CatalogError, _check_public(), fetch_public(), ValueError, The product cannot be imported at all. The message is safe to show., Refuse anything but http(s) to a public address: an imported URL is untrusted…, Download a public URL with a size cap, re-checking every redirect hop., test_download_deadline_stops_trickling_response() (+7 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "SpatialInputError"
Cohesion: 0.08
Nodes (61): Vec2, WallSegment, A point on the floor plan (Y omitted)., height_overlaps(), Spatial checks independent of HTTP, mesh loading and provider services., Shared Feng Shui inputs and validation, independent of the model harness., CollisionVolume, door_center() (+53 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 52 - "FurnitureAsset"
Cohesion: 0.09
Nodes (44): FurnitureItem, Correction, Facing, FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., _access(), _Choice, _extents() (+36 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "FloorPlanScreen.tsx"
Cohesion: 0.19
Nodes (19): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DemoFloor (+11 more)

### Community 55 - "Decisions"
Cohesion: 0.06
Nodes (35): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+27 more)

### Community 56 - "LayoutToolbox"
Cohesion: 0.16
Nodes (17): LayoutDraft, _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, LayoutToolbox, _metrics() (+9 more)

### Community 57 - "audit_scene"
Cohesion: 0.22
Nodes (23): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+15 more)

### Community 58 - "annotate.py"
Cohesion: 0.09
Nodes (25): AnnotationResult, Compass, _extract_json(), FalVisionAnnotator, FloorCaption, NullAnnotator, BaseModel, What computer vision cannot read off a floor plan: room labels with their… (+17 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "shell.py"
Cohesion: 0.10
Nodes (38): int64, _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key(), _miter() (+30 more)

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
Nodes (41): DoorSwings(), floorPlane, Furniture, MeshBoundary, ProxyBox(), FurnitureMesh(), categoryWash, disposeInk() (+33 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "delivery.py"
Cohesion: 0.12
Nodes (20): main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), _declared_bounds(), _declared_bounds_problems(), Delivery, _gltf_problems() (+12 more)

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "routes.py"
Cohesion: 0.11
Nodes (26): File, HTTPException, PlanAnnotator, Protocol, parse_floor_plan(), plan_id_for(), ParsedFloorPlan, Parse 1..n floor-plan images (bytes, content type) into every floor and room. (+18 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.11
Nodes (19): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Feng shui score, Free floor area, Front clearance (+11 more)

### Community 76 - "report.py"
Cohesion: 0.13
Nodes (21): FengShuiReport, _angle_deg(), calculate_feng_shui(), _front(), _occupant(), FurnitureItem, RoomScene, A small, transparent Feng Shui placement metric from the command-position… (+13 more)

### Community 77 - "store.ts"
Cohesion: 0.08
Nodes (42): playCue(), ChatTab(), FengShuiSection(), ProductCard(), VersionTree(), VersionTreeView(), DEFAULT_ROOM_ID, FengShuiResult (+34 more)

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
Cohesion: 0.15
Nodes (26): IkeaSearch, PageReader, ProductOption, One retailer product, from its page (`url_import`) or a search result…, IKEA products matching `query`, as `catalog_search` results. A result carries…, RetailerProduct, search_ikea(), _host() (+18 more)

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

### Community 96 - "make_item"
Cohesion: 0.30
Nodes (11): make_item(), FurnitureItem, parametrize, Footprint examples independent of meshes, providers and HTTP routes., test_45_degree_corners_follow_threejs_yaw(), test_does_not_mutate_item(), test_front_edge_rotates_toward_positive_x(), test_rejects_invalid_dimensions() (+3 more)

### Community 97 - "test_layout_tools.py"
Cohesion: 0.19
Nodes (25): LayoutPreferences, What the user asked for, already validated by the server., evaluate(), item(), move(), Any, FurnitureItem, parametrize (+17 more)

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
Nodes (24): HTMLParser, _binary_models(), _dimensions(), _first_url(), _is_type(), _metres(), _model_urls(), _nodes() (+16 more)

### Community 124 - "ProviderError"
Cohesion: 0.11
Nodes (15): AgentLimits, _Budget, LayoutCancelled, ProviderError, Exception, ProgressCallback, One allowance per request. Retries and the interpretation call spend the same…, A failed model call. `kind` is safe to log; no key or payload is kept. (+7 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "catalog.py"
Cohesion: 0.04
Nodes (88): CatalogImport, _decode(), ImageProvenance, import_product(), imported_assets(), item_box(), _normalises(), computed_field (+80 more)

### Community 128 - "openings.py"
Cohesion: 0.24
Nodes (11): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+3 more)

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 130 - "normalise_mesh"
Cohesion: 0.12
Nodes (23): Front, BBoxM, CollisionPart, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).…, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), NormalisedMesh, Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`. (+15 more)

### Community 131 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 132 - "calculate_free_floor_ratio"
Cohesion: 0.24
Nodes (23): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, item(), FurnitureItem, parametrize, RoomScene, Free floor area is distinct from reachable walking space., room() (+15 more)

### Community 133 - "test_api.py"
Cohesion: 0.20
Nodes (16): payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422() (+8 more)

### Community 134 - "add_item"
Cohesion: 0.14
Nodes (22): add_item(), FurnitureItem, Validated tool handler. A rejected addition never mutates the caller's scene.…, describe_library(), _has_mesh(), library_assets(), FurnitureItem, Path (+14 more)

### Community 135 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 136 - "chat"
Cohesion: 0.11
Nodes (28): AuditReport, ChatReply, ChatRequest, ChatReply, POST /chat response, and the data of /chat/stream's terminal `reply` event., LayoutModel, LinkupPost, ProgressCallback (+20 more)

### Community 137 - "catalog_router"
Cohesion: 0.18
Nodes (13): catalog_router(), APIRouter, Fetch, Path, `fetch` replaces the public downloader (tests)., client(), MonkeyPatch, parametrize (+5 more)

### Community 141 - "furniture_proxy"
Cohesion: 0.25
Nodes (8): le, furniture_proxy(), health(), get, gt, Path, Response, Process liveness only; does not probe external providers.

### Community 150 - "layoutProgress.test.tsx"
Cohesion: 0.14
Nodes (15): HarnessProgress(), HarnessStatus(), proposalSummary(), initial, proposal(), propose(), report(), response() (+7 more)

### Community 151 - "reconstruct_furniture"
Cohesion: 0.21
Nodes (20): Path, Give every (or each named) item of the scene its own raw mesh, and always a…, reconstruct_furniture(), CaptureFixture, test_a_mesh_that_cannot_be_normalised_is_delivered_as_its_proxy(), test_a_provider_failure_keeps_both_items_as_proxies(), test_cli_runs_the_checks_and_reports(), test_a_mesh_that_cannot_be_normalised_keeps_its_proxy_and_says_so() (+12 more)

### Community 152 - "test_streaming.py"
Cohesion: 0.21
Nodes (18): audit(), AuditReport, RoomScene, Return current spatial findings; scoring, glare and Feng Shui are not assessed., event(), post(), Any, OptimiseRequest (+10 more)

### Community 153 - "check_layout_demo.py"
Cohesion: 0.18
Nodes (12): demo_room_scenes(), profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, Each demo room with the furniture standing in it, as the editor builds them., solve(), Timed (+4 more)

### Community 154 - "fetch_product"
Cohesion: 0.18
Nodes (13): fetch_product(), guess_category(), Category, Fetch, Classify the head phrase, using its last furniture or accessory noun.…, Download and read one retailer product page. Raises CatalogError. `source`…, parametrize, test_categories_come_from_the_products_own_words() (+5 more)

### Community 155 - "feng_shui_skill_unavailable"
Cohesion: 0.25
Nodes (11): exception_handler, JSONResponse, RequestValidationError, feng_shui_skill_unavailable(), invalid_request(), Exception, Request, A missing or malformed skill file is a server configuration error, never a 500… (+3 more)

### Community 156 - "Any"
Cohesion: 0.43
Nodes (5): Any, Exception, ModelReply, remove_turn(), search_turn()

### Community 157 - "_open_poses"
Cohesion: 0.38
Nodes (7): _open_poses(), FurnitureItem, Polygon, Pose2D, Back to each floor edge, front facing into the room, sampled along the edge., A coarse grid over the floor, facing the four axes., _wall_poses()

### Community 158 - "test_shared_handoff_case"
Cohesion: 0.33
Nodes (4): Any, parametrize, Reusable scene variants and expected findings for Dev 3/4 integration., test_shared_handoff_case()

### Community 159 - "proxy_glb"
Cohesion: 0.40
Nodes (4): proxy_glb(), Small dimensioned GLB box, without a reconstruction dependency., test_proxy_faces_wind_outward(), test_proxy_has_metric_bottom_centred_bounds()

## Knowledge Gaps
- **467 isolated node(s):** `EditorMode`, `SavedRoom`, `Toast`, `State`, `initialScene` (+462 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `test_scene_cache.py`, `test_room_align_vision.py`, `detect_out_of_bounds`, `test_scene_routes.py`, `calculate_free_floor_ratio`, `add_item`, `test_api.py`, `chat`, `models.py`, `test_room_align.py`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `test_real_room.py`, `propose_layout`, `FixedAnnotator`, `Pose2D`, `DraftSession`, `test_room_correct.py`, `test_streaming.py`, `check_layout_demo.py`, `AuditReport`, `detect_blocked_doors`, `test_room_parse.py`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `test_shared_handoff_case`, `test_room_shell.py`, `scenes.py`, `ContractModel`, `demo_assets.py`, `score_feng_shui`, `scene_cache.py`, `generate_mock_glbs.py`, `SpatialInputError`, `FurnitureAsset`, `LayoutToolbox`, `audit_scene`, `shell.py`, `routes.py`, `report.py`, `detect_collisions`, `test_layout_tools.py`, `divided_access_room`, `test_demo_assets.py`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `test_room_align_vision.py`, `test_scene_routes.py`, `cache_ikea_library.py`, `models.py`, `test_room_align.py`, `test_delivery.py`, `BBoxM`, `test_selection.py`, `Pose2D`, `reconstruct_furniture`, `test_reconstruction.py`, `detect_blocked_doors`, `test_demo_cache_room.py`, `scenes.py`, `ContractModel`, `demo_assets.py`, `test_demo_cache.py`, `.to_item`, `test_contract_occupancy.py`, `delivery.py`, `test_fixture_scene.py`, `catalog.py`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_catalog.py`, `normalise_mesh`, `detect_out_of_bounds`, `calculate_free_floor_ratio`, `cache_ikea_library.py`, `footprint.py`, `catalog_router`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `propose_layout`, `Pose2D`, `DraftSession`, `RoomScene`, `reconstruct_furniture`, `test_reconstruction.py`, `fetch_product`, `detect_blocked_doors`, `calculate_brightness_approximation`, `ContractModel`, `score_feng_shui`, `SpatialInputError`, `FurnitureAsset`, `audit_scene`, `detect_collisions`, `make_item`, `test_layout_tools.py`, `search_products`, `divided_access_room`, `retailer.py`, `catalog.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 232 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 232 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 80 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 80 INFERRED edges - model-reasoned connections that need verification._
- **Are the 77 inferred relationships involving `Pose2D` (e.g. with `catalog_router()` and `FurnitureAsset`) actually correct?**
  _`Pose2D` has 77 INFERRED edges - model-reasoned connections that need verification._