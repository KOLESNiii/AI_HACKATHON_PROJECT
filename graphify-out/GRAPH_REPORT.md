# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 258 files · ~389,778 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3740 nodes · 11135 edges · 148 communities (131 shown, 17 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1267 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b1c78ded`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- import_catalog_asset
- CatalogError
- observe_vision.py
- test_real_room.py
- test_scene_routes.py
- audio.test.ts
- FurnitureAsset
- footprint.py
- test_segmentation.py
- selection_models.py
- test_room_align.py
- calculate_reachable_floor_ratio
- test_delivery.py
- Registry
- BBoxM
- test_selection.py
- react
- propose_layout
- _Room
- Pose2D
- DraftSession
- regions.py
- SpatialInputError
- test_room_correct.py
- test_room_parse.py
- test_reconstruction.py
- demo_cache.py
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
- correct_scale
- agent.ts
- ContractModel
- demo_assets.py
- score_feng_shui
- compilerOptions
- test_demo_cache.py
- MaskRecord
- Sidebar.tsx
- detect_out_of_bounds
- FloorPlanScreen.tsx
- generate_mock_glbs.py
- Vec2
- test_contract_occupancy.py
- FurnitureItem
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- shell.py
- Decisions
- fetch_product
- audit_scene
- routes.py
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
- ProviderError
- Agent Instructions
- test_room_align_vision.py
- test_fixture_scene.py
- Frame
- Implementation plan: issue #14
- Spatial engine
- detect_front_clearance
- store.ts
- scripts
- openings.py
- SpaceShift — System Architecture & 4-Developer Execution DAG
- Asset Handoff Agreement Implementation Plan
- Review Focus
- Review Focus
- Floor-plan parser (Dev 1)
- Furniture masks and placement evidence — issue #15
- feng_shui_skill_unavailable
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
- test_layout_tools.py
- model_validator
- README.md
- frontend/package.json
- scenes.py
- calculate_free_floor_ratio
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- catalog_routes.py
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift
- SKILL.md
- manifest.json
- parse_product_page
- prepare_layout
- test_demo_assets.py
- vite
- catalog.py
- LayoutToolbox
- Validated, cached demo assets (#20, Dev 2.8)
- PlayLighting.tsx
- test_streaming.py
- report.py
- test_api.py
- reconstruct_items.py
- plugins
- test_the_real_video_furnishes_the_real_room
- no_network
- demo_cache/README.md
- proxy_asset
- test_catalog.py
- furniture_proxy
- RoomScene
- page
- _door_overlap_area
- catalog_id
- LayoutMetrics
- .__init__

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 212 edges
2. `FurnitureAsset` - 91 edges
3. `useStore` - 81 edges
4. `BBoxM` - 79 edges
5. `Pose2D` - 73 edges
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
- `test_evidence_matches_the_agreed_shape()` --uses--> `AssetEvidence`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `test_dev1_consumes_fixtures_through_the_asset_interface()` --uses--> `FurnitureAsset`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py

## Import Cycles
- None detected.

## Communities (148 total, 17 thin omitted)

### Community 0 - "import_catalog_asset"
Cohesion: 0.17
Nodes (24): catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, bounds(), ndarray, Path (+16 more)

### Community 1 - "CatalogError"
Cohesion: 0.12
Nodes (19): fetch(), Reuse bounded, public-only downloads; keep raw evidence outside the project., CatalogError, _check_public(), fetch_public(), ValueError, The product cannot be imported at all. The message is safe to show., Refuse anything but http(s) to a public address: an imported URL is untrusted… (+11 more)

### Community 2 - "observe_vision.py"
Cohesion: 0.07
Nodes (40): Image, MaskSource, build_prompt(), directory_frames(), _distance_to_wall(), _draw_marks(), _encode(), _facing() (+32 more)

### Community 3 - "test_real_room.py"
Cohesion: 0.11
Nodes (59): Collection, clear_cache(), Forget assembled scenes (tests, or after the furniture source changes)., auditor(), _clear(), client(), _collides(), data_dir() (+51 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.14
Nodes (34): conform_openings(), RoomScene, Put every door exactly on its wall, so the spatial audit accepts the room. Each…, _audit(), auditor(), client(), _door(), _leaf_end() (+26 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 6 - "FurnitureAsset"
Cohesion: 0.06
Nodes (47): main(), prepare(), Fetch a balanced, offline IKEA library using only published retailer meshes.…, Expand retailer Draco geometry and expose WebP sources to the shared reader.…, unpack_model(), _along_mesh(), BBoxM, Published width and depth, assigned to X and Z of a shape with these extents.… (+39 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (61): any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach() (+53 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.10
Nodes (70): Rect, _fetch(), MaskError, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, main(), Path, Review images plus the two machine-readable handoffs: the result and the…, write_report() (+62 more)

### Community 9 - "selection_models.py"
Cohesion: 0.08
Nodes (46): CatalogImport, computed_field, One imported product: the placed-ready asset, its checks, and where it all came…, The delivered asset passed every check. A proxy or a requested correction is…, _dimensions(), ProductDimensions, A retailer product page or search result -> what the asset pipeline needs…, All three sides, each plausible, or nothing: a partial size is not a size. (+38 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (58): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+50 more)

### Community 11 - "calculate_reachable_floor_ratio"
Cohesion: 0.17
Nodes (29): calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, divided_room(), obstacle(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.12
Nodes (45): APIRouter, asset_router(), Path, Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset(), check_placed(), deliver_furniture() (+37 more)

### Community 13 - "Registry"
Cohesion: 0.06
Nodes (51): Connection, main(), Path, Import a retailer product as a furniture asset through the shared pipeline…, write_report(), ArtifactTooLarge, box_pixels(), fal_media_url() (+43 more)

### Community 14 - "BBoxM"
Cohesion: 0.13
Nodes (48): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, BBoxM, CollisionPart, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), _load() (+40 more)

### Community 15 - "test_selection.py"
Cohesion: 0.15
Nodes (40): FalVisionProvider, Reviewed detections keyed by full source frame keys, never by batch position., RecordedProvider, main(), Path, Full-resolution source artifacts stay separate; the report shows boxes and IDs., write_report(), Discovery (+32 more)

### Community 16 - "react"
Cohesion: 0.09
Nodes (29): App(), ORDER, screenVariants, EditorScreen(), useLiveAudit(), VersionTree(), HomeScreen(), rise (+21 more)

### Community 17 - "propose_layout"
Cohesion: 0.15
Nodes (50): OptimiseRequest, propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, Step, interpret(), item(), move() (+42 more)

### Community 18 - "_Room"
Cohesion: 0.08
Nodes (34): Correction, Facing, _access(), _Choice, _extents(), _front(), _nearby(), nearest_fit() (+26 more)

### Community 19 - "Pose2D"
Cohesion: 0.14
Nodes (49): Pose2D, WindowOpening, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, test_full_scoring_is_opt_in_and_the_comparator_requires_it() (+41 more)

### Community 20 - "DraftSession"
Cohesion: 0.11
Nodes (36): _arrangement(), DraftSession, _echo(), LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one…, A fresh scene at the base revision, so its audit identifies the submitted scene. (+28 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (32): int32, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point() (+24 more)

### Community 22 - "SpatialInputError"
Cohesion: 0.07
Nodes (72): ChatRequest, POST /chat and /chat/stream., add_item(), AddItemArguments, chat(), _percent(), AuditReport, BaseModel (+64 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.09
Nodes (48): apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, InvalidScale, _perimeter(), _point() (+40 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.07
Nodes (72): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, AnnotationResult, Compass, _extract_json(), FalVisionAnnotator, FixedAnnotator (+64 more)

### Community 25 - "test_reconstruction.py"
Cohesion: 0.10
Nodes (49): RuntimeError, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., write_atomic(), inspect_mesh(), MeshError, Exception, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP… (+41 more)

### Community 26 - "demo_cache.py"
Cohesion: 0.15
Nodes (30): CachedFile, CacheError, current_generation(), _inside(), install_demo_cache(), _intact(), main(), prune_demo_cache() (+22 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.18
Nodes (32): BlockedDoorIssue, CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize (+24 more)

### Community 28 - "contracts.ts"
Cohesion: 0.06
Nodes (47): ChatStreamEvent, GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, LayoutProgressStage, LayoutStreamEvent, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES (+39 more)

### Community 29 - "parse.py"
Cohesion: 0.11
Nodes (41): RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance(), _consensus(), _fallback_scale() (+33 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.13
Nodes (35): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, A window-openness proxy for layout comparison, not a lighting simulation., Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item() (+27 more)

### Community 31 - "test_demo_cache_room.py"
Cohesion: 0.13
Nodes (33): clear_corrections(), Serve every plan as parsed again (tests)., broken_cache(), from_demo_cache(), assert_readers_agree(), _audit(), auditor(), _client() (+25 more)

### Community 32 - "walk.ts"
Cohesion: 0.10
Nodes (27): captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera(), restoreEditorView(), PlayController() (+19 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.05
Nodes (73): FengShuiResult, Outcome, demo_room_scenes(), profile(), RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, Each demo room with the furniture standing in it, as the editor builds them., solve() (+65 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "geometry.ts"
Cohesion: 0.18
Nodes (21): DoorSwings(), clampToFloor(), doorSwing(), fitsRoom(), fitYaw(), footprint(), snapToNearestWall(), toWorld() (+13 more)

### Community 36 - "test_room_shell.py"
Cohesion: 0.10
Nodes (46): build_shell(), Scene, The room shell as a trimesh Scene with nodes `floor`, `ceiling`, `wall_<id>`., shell_glb(), corner_probes(), _inside(), invalid_footprints(), _l_door() (+38 more)

### Community 37 - "test_feng_shui_optimisation.py"
Cohesion: 0.14
Nodes (22): ModelReply, Any, ToolCall, Any, original_room(), Scripted, Feng Shui optimisation uses the runtime skill and the same full score as Stats., The audit only needs IDs unique per type; the optimiser must accept what /audit… (+14 more)

### Community 38 - "correct_scale"
Cohesion: 0.08
Nodes (33): ge, HTTPException, Query, Assembly, find_parsed_scene(), prepare_floor_scale(), publish(), RoomScene (+25 more)

### Community 39 - "agent.ts"
Cohesion: 0.06
Nodes (60): AuditDiff(), LayoutProposalCard(), PlanDiff(), poseText(), ScoreComparison, useProposalScores(), isLibraryAsset(), AgentReply (+52 more)

### Community 40 - "ContractModel"
Cohesion: 0.05
Nodes (63): ChatErrorEvent, ChatProgressEvent, ChatReplyEvent, ContractModel, _FengShuiModel, LayoutErrorEvent, LayoutProgressEvent, LayoutResultEvent (+55 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.12
Nodes (26): FileResponse, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file() (+18 more)

### Community 42 - "score_feng_shui"
Cohesion: 0.11
Nodes (61): FengShuiRequest, POST /feng-shui and /feng-shui/score., FengShuiSightline, RuleScore, _add(), _angle_deg(), _backing(), _balance() (+53 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.12
Nodes (41): cache_folder(), DemoCache, The scene's published cache, its files verified; None when none is published.…, A scene's folder: readable, and distinct for scene IDs that read alike., read_demo_cache(), _generation(), import_two(), _manifest() (+33 more)

### Community 45 - "MaskRecord"
Cohesion: 0.18
Nodes (11): _overlaps(), NDArray, Path, uint8, Masks of different items should not claim the same pixels; flag it, do not edit…, _store(), _write(), MaskRecord (+3 more)

### Community 46 - "Sidebar.tsx"
Cohesion: 0.05
Nodes (43): MAX_LAYOUT_INSTRUCTION_CHARS, FengShuiScoreCard(), AuditStats(), ChatTab(), FengShuiSection(), HarnessProgress(), HarnessStatus(), LibraryTab() (+35 more)

### Community 47 - "detect_out_of_bounds"
Cohesion: 0.18
Nodes (25): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+17 more)

### Community 48 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (21): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+13 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "Vec2"
Cohesion: 0.12
Nodes (33): DoorOpening, Vec2, WallSegment, A point on the floor plan (Y omitted)., A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, CollisionVolume, door_center(), door_entry_segment() (+25 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.15
Nodes (22): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+14 more)

### Community 52 - "FurnitureItem"
Cohesion: 0.08
Nodes (37): FurnitureItem, model_validator, AlignmentRecord, AlignmentResult, _Capture, main(), pose_error(), FrameSource (+29 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "shell.py"
Cohesion: 0.10
Nodes (38): int64, _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key(), _miter() (+30 more)

### Community 55 - "Decisions"
Cohesion: 0.06
Nodes (34): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+26 more)

### Community 56 - "fetch_product"
Cohesion: 0.18
Nodes (12): fetch_product(), guess_category(), Category, Fetch, Classify the head phrase, using its last furniture or accessory noun.…, Download and read one retailer product page. Raises CatalogError. `source`…, parametrize, test_categories_come_from_the_products_own_words() (+4 more)

### Community 57 - "audit_scene"
Cohesion: 0.22
Nodes (23): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+15 more)

### Community 58 - "routes.py"
Cohesion: 0.09
Nodes (28): File, PlanAnnotator, Protocol, main(), ndarray, ParsedFloor, Debug CLI: parse floor-plan images and write the JSON plus an overlay per…, Draw the contract geometry exactly as returned (metres), not the source image:… (+20 more)

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
Nodes (27): Architecture, Backend-provided demo models, Bundled retailer library, Chat additions and application, Corrections (#11), Editor Feng Shui score integration, Editor layout review and live Stats, Editor play mode (+19 more)

### Community 68 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "ProviderError"
Cohesion: 0.18
Nodes (10): Any, Timed, ProviderError, Exception, A failed model call. `kind` is safe to log; no key or payload is kept., Request, Response, sdk_model() (+2 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "test_room_align_vision.py"
Cohesion: 0.11
Nodes (34): _by_index(), _decode(), _fractions(), _frame_record(), _jpeg(), CaptureFixture, Exception, MonkeyPatch (+26 more)

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "Frame"
Cohesion: 0.12
Nodes (21): ImageProvenance, Fetch, Mask, The retailer's own published model as the item's raw mesh. No inference and no…, The next published model that is usable and within the triangle budget. Each…, Download the product image and store it as the item's one source frame., The product image the item's view was made from., RetailerModelProvider (+13 more)

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

### Community 79 - "openings.py"
Cohesion: 0.24
Nodes (11): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+3 more)

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
Cohesion: 0.20
Nodes (8): Corrections (#11), Floor-plan parser (Dev 1), Furniture alignment (#8), How it works, Real-input room (#10), Scene assembly (#9), Status and limits, Use

### Community 85 - "Furniture masks and placement evidence — issue #15"
Cohesion: 0.22
Nodes (8): Approaches, Design, Furniture masks and placement evidence — issue #15, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 20 requests), Live result (2026-11-14), Needs coordination

### Community 86 - "feng_shui_skill_unavailable"
Cohesion: 0.25
Nodes (11): exception_handler, JSONResponse, RequestValidationError, feng_shui_skill_unavailable(), invalid_request(), Exception, Request, A missing or malformed skill file is a server configuration error, never a 500… (+3 more)

### Community 87 - "detect_collisions"
Cohesion: 0.12
Nodes (38): CollisionIssue, detect_collisions(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, furniture_collision_volumes(), Transform validated local collision boxes; absent parts mean one solid bbox.…, item(), part() (+30 more)

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
Cohesion: 0.24
Nodes (16): front_clearance_zone(), furniture_footprint(), FurnitureItem, Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, Full-width rectangle from the bbox front, rotated/placed in room X/Z. Zero…, make_item(), FurnitureItem, parametrize (+8 more)

### Community 97 - "test_layout_tools.py"
Cohesion: 0.19
Nodes (25): LayoutPreferences, What the user asked for, already validated by the server., evaluate(), item(), move(), Any, FurnitureItem, parametrize (+17 more)

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "scenes.py"
Cohesion: 0.12
Nodes (24): assemble_scene(), FurnitureSource, NoFurniture, Protocol, RoomScene, What a furniture source supplies for one room., The room alone: what parsed rooms get until #16 produces furniture assets., The room with its furniture placed. Never drops the room: a source that fails… (+16 more)

### Community 102 - "calculate_free_floor_ratio"
Cohesion: 0.24
Nodes (23): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, item(), FurnitureItem, parametrize, RoomScene, Free floor area is distinct from reachable walking space., room() (+15 more)

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "catalog_routes.py"
Cohesion: 0.17
Nodes (13): import_url(), ImportRequest, BaseModel, Editor URL imports through the existing, public-address-only retailer pipeline., demo_cache_dir(), furniture_data_dir(), Path, Runtime settings of the reconstruction service. (+5 more)

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "parse_product_page"
Cohesion: 0.09
Nodes (24): HTMLParser, _binary_models(), _first_url(), _is_type(), _metres(), _model_urls(), _nodes(), _Page (+16 more)

### Community 124 - "prepare_layout"
Cohesion: 0.14
Nodes (11): AgentLimits, _Budget, _interpret(), _Interpretation, prepare_layout(), BaseModel, OptimiseRequest, ProgressCallback (+3 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "catalog.py"
Cohesion: 0.16
Nodes (18): import_product(), imported_assets(), _normalises(), Path, Retailer products through the shared asset pipeline (#19). A product is…, Whether the item's stored raw mesh meets the furniture profile at its size., The pipeline's asset, carrying the product's own source, link and price., Turn one retailer product into a furniture asset through the shared pipeline.… (+10 more)

### Community 128 - "LayoutToolbox"
Cohesion: 0.12
Nodes (29): LayoutDraft, _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, LayoutToolbox, _metrics() (+21 more)

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 130 - "PlayLighting.tsx"
Cohesion: 0.25
Nodes (14): DoorLightBlockers(), LightingEnvironment, PlayLighting(), useEnvironmentSettings(), inwardNormal(), ceilingLights(), DEFAULT_PLAY_LIGHTING, LightPosition (+6 more)

### Community 131 - "test_streaming.py"
Cohesion: 0.21
Nodes (18): audit(), AuditReport, RoomScene, Return current spatial findings; scoring, glare and Feng Shui are not assessed., event(), post(), Any, OptimiseRequest (+10 more)

### Community 132 - "report.py"
Cohesion: 0.12
Nodes (25): FengShuiReport, _height_overlaps(), Spatial checks independent of HTTP, mesh loading and provider services., _angle_deg(), calculate_feng_shui(), _front(), _occupant(), FurnitureItem (+17 more)

### Community 133 - "test_api.py"
Cohesion: 0.20
Nodes (16): payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422() (+8 more)

### Community 134 - "reconstruct_items.py"
Cohesion: 0.19
Nodes (14): main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), Delivery, computed_field, Every delivered asset passed its checks. Proxies are allowed; they are listed., load_dimensions() (+6 more)

### Community 135 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 136 - "test_the_real_video_furnishes_the_real_room"
Cohesion: 0.16
Nodes (16): load_bindings(), proxy_warning(), Bindings by scene ID., _audit(), _length(), Response, skipif, WallSegment (+8 more)

### Community 137 - "no_network"
Cohesion: 0.67
Nodes (3): no_network(), MonkeyPatch, Any attempt to resolve or connect fails the test: no provider, no retailer.

### Community 139 - "proxy_asset"
Cohesion: 0.17
Nodes (14): proxy_asset(), proxy_glb(), BBoxM, Category, Path, A box of exactly `bbox`: bottom-centre at the origin, front +Z. The dark strip…, The fallback asset for an item: same ID, a stored box, and honest dimension…, bounds() (+6 more)

### Community 140 - "test_catalog.py"
Cohesion: 0.19
Nodes (13): _decode(), item_box(), NDArray, uint8, An upright BGR image; transparency becomes white, as in a product shot., Where the product is in its image, and whether that was read off a plain…, product_image(), Retailer products through the shared asset pipeline (Dev 2.7, #19): source,… (+5 more)

### Community 141 - "furniture_proxy"
Cohesion: 0.15
Nodes (12): le, furniture_proxy(), health(), get, gt, Path, Response, Process liveness only; does not probe external providers. (+4 more)

### Community 142 - "RoomScene"
Cohesion: 0.32
Nodes (7): RoomScene, floor_polygon is clockwise in plan view and every wall has the room on its…, geometry_mismatch(), Why `room` is not the room `binding` was made for, or None when it is. Compares…, The binding names a room by its shape: the user may correct its scale (#11)., test_the_binding_names_a_room_and_walls_of_the_parsed_plan(), test_the_geometry_check_compares_shape_and_names_a_wrong_wall()

### Community 143 - "page"
Cohesion: 0.25
Nodes (7): model_glb(), page(), A retailer page the way IKEA writes one: schema.org Product and 3DModel JSON-LD., A published model in metres, centred like a retailer's, not on the floor., test_a_combination_is_priced_by_its_current_price_specification(), test_a_page_that_names_no_product_is_refused(), test_units_and_quantitative_values_become_metres()

### Community 144 - "_door_overlap_area"
Cohesion: 0.29
Nodes (7): _check_comparable(), _door_overlap_area(), _near_window_shortfall(), AuditReport, RoomScene, Do not improve metrics by changing the room, removing items or shrinking them., Grade progress while a door is still blocked, using the audit's same thresholds.

### Community 145 - "catalog_id"
Cohesion: 0.33
Nodes (6): catalog_id(), One product URL is one item ID, so importing it again updates the same item., CaptureFixture, MonkeyPatch, test_catalog_identity_ignores_tracking_and_trailing_slashes(), test_cli_lists_search_results_and_reports_unusable_input()

## Knowledge Gaps
- **459 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+454 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `LayoutToolbox`, `observe_vision.py`, `test_streaming.py`, `test_scene_routes.py`, `report.py`, `FurnitureAsset`, `test_api.py`, `test_the_real_video_furnishes_the_real_room`, `test_real_room.py`, `test_room_align.py`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `_door_overlap_area`, `propose_layout`, `_Room`, `Pose2D`, `DraftSession`, `SpatialInputError`, `test_room_correct.py`, `test_room_parse.py`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `spatial_engine/main.py`, `test_room_shell.py`, `correct_scale`, `ContractModel`, `demo_assets.py`, `score_feng_shui`, `detect_out_of_bounds`, `generate_mock_glbs.py`, `Vec2`, `FurnitureItem`, `shell.py`, `audit_scene`, `routes.py`, `test_room_align_vision.py`, `detect_front_clearance`, `detect_collisions`, `test_layout_tools.py`, `scenes.py`, `calculate_free_floor_ratio`, `test_demo_assets.py`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `observe_vision.py`, `test_scene_routes.py`, `reconstruct_items.py`, `selection_models.py`, `test_room_align.py`, `proxy_asset`, `test_delivery.py`, `BBoxM`, `_Room`, `Pose2D`, `test_reconstruction.py`, `demo_cache.py`, `detect_blocked_doors`, `ContractModel`, `demo_assets.py`, `test_demo_cache.py`, `test_contract_occupancy.py`, `FurnitureItem`, `test_room_align_vision.py`, `test_fixture_scene.py`, `scenes.py`, `catalog.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `import_catalog_asset`, `FurnitureAsset`, `footprint.py`, `selection_models.py`, `proxy_asset`, `test_catalog.py`, `Registry`, `test_delivery.py`, `page`, `calculate_reachable_floor_ratio`, `propose_layout`, `_Room`, `Pose2D`, `DraftSession`, `SpatialInputError`, `test_reconstruction.py`, `detect_blocked_doors`, `calculate_brightness_approximation`, `ContractModel`, `score_feng_shui`, `detect_out_of_bounds`, `Vec2`, `fetch_product`, `audit_scene`, `detect_front_clearance`, `detect_collisions`, `furniture_footprint`, `test_layout_tools.py`, `calculate_free_floor_ratio`, `parse_product_page`, `catalog.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 209 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 209 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 70 inferred relationships involving `Pose2D` (e.g. with `FurnitureAsset` and `_access()`) actually correct?**
  _`Pose2D` has 70 INFERRED edges - model-reasoned connections that need verification._