# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 231 files · ~366,189 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3415 nodes · 10028 edges · 137 communities (121 shown, 16 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1171 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `50794aa3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- CatalogError
- test_room_align_vision.py
- RoomScene
- test_scene_routes.py
- audio.test.ts
- FurnitureAsset
- footprint.py
- test_segmentation.py
- main
- test_room_align.py
- calculate_reachable_floor_ratio
- test_delivery.py
- Frame
- BBoxM
- Registry
- App.tsx
- Pose2D
- FurnitureItem
- test_objective.py
- DraftSession
- regions.py
- test_chat.py
- test_room_correct.py
- test_room_parse.py
- test_reconstruction.py
- demo_cache.py
- detect_blocked_doors
- schema.ts
- parse.py
- calculate_brightness_approximation
- test_demo_cache_room.py
- walk.ts
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- RoomView.tsx
- test_room_shell.py
- ModelReply
- scenes.py
- test_layout_tools.py
- detect_front_clearance
- demo_assets.py
- ContractModel
- compilerOptions
- test_demo_cache.py
- .current_mesh
- Sidebar.tsx
- detect_out_of_bounds
- FloorPlanScreen.tsx
- generate_mock_glbs.py
- SpatialInputError
- test_contract_occupancy.py
- layout_tools.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_api.py
- Decisions
- fetch_product
- audit_scene
- routes.py
- compilerOptions
- Video frame selection and furniture identity — issue #14
- Furniture.tsx
- Dev 2 → Dev 1 asset handoff
- dependencies
- devDependencies
- raster.py
- polygon.py
- Architecture
- Dev 4 implementation and integration plan
- ProviderError
- Agent Instructions
- _Page
- test_fixture_scene.py
- test_shared_handoff_case
- Implementation plan: issue #14
- Spatial engine
- calculate_free_floor_ratio
- useStore
- scripts
- openings.py
- SpaceShift — System Architecture & 4-Developer Execution DAG
- Asset Handoff Agreement Implementation Plan
- Review Focus
- Review Focus
- Floor-plan parser (Dev 1)
- Furniture masks and placement evidence — issue #15
- invalid_request
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
- test_report.py
- model_validator
- README.md
- frontend/package.json
- video_furniture.py
- unpack_model
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- health
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift
- manifest.json
- retailer.py
- agent.py
- test_demo_assets.py
- vite
- objective.py
- Validated, cached demo assets (#20, Dev 2.8)
- PlayLighting.tsx
- .ok
- report.py
- inspect_asset
- plugins
- .to_item
- no_network
- demo_cache/README.md

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 212 edges
2. `FurnitureAsset` - 91 edges
3. `BBoxM` - 79 edges
4. `Pose2D` - 69 edges
5. `FurnitureItem` - 69 edges
6. `Registry` - 69 edges
7. `useStore` - 59 edges
8. `SpatialInputError` - 59 edges
9. `reconstruct_furniture()` - 57 edges
10. `audit_scene()` - 56 edges

## Surprising Connections (you probably didn't know these)
- `test_all_home_furniture_urls_have_canonical_models()` --uses--> `RoomScene`  [INFERRED]
  tests/test_demo_assets.py → contracts/schema.py
- `test_audit_report_must_echo_scene()` --uses--> `AuditReport`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_unassessed_audit_fields_round_trip_as_null()` --uses--> `AuditReport`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_evidence_matches_the_agreed_shape()` --uses--> `AssetEvidence`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `test_dev1_consumes_fixtures_through_the_asset_interface()` --uses--> `FurnitureAsset`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py

## Import Cycles
- None detected.

## Communities (137 total, 16 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.11
Nodes (42): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., bounds() (+34 more)

### Community 1 - "CatalogError"
Cohesion: 0.13
Nodes (18): CatalogError, _check_public(), fetch_public(), ValueError, The product cannot be imported at all. The message is safe to show., Refuse anything but http(s) to a public address: an imported URL is untrusted…, Download a public URL with a size cap, re-checking every redirect hop., import_url() (+10 more)

### Community 2 - "test_room_align_vision.py"
Cohesion: 0.04
Nodes (85): Image, MaskSource, main(), Path, build_prompt(), directory_frames(), _distance_to_wall(), _draw_marks() (+77 more)

### Community 3 - "RoomScene"
Cohesion: 0.06
Nodes (97): Collection, RoomScene, geometry_mismatch(), proxy_warning(), Why `room` is not the room `binding` was made for, or None when it is. Compares…, still_extracting(), clear_cache(), Forget assembled scenes (tests, or after the furniture source changes). (+89 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.16
Nodes (30): _audit(), auditor(), _door(), _leaf_end(), DoorOpening, parametrize, RoomScene, TestClient (+22 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 6 - "FurnitureAsset"
Cohesion: 0.04
Nodes (100): fetch(), main(), prepare(), Fetch a balanced, offline IKEA library using only published retailer meshes.…, Reuse bounded, public-only downloads; keep raw evidence outside the project., Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., write_atomic() (+92 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (60): any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach() (+52 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.09
Nodes (77): Rect, _fetch(), MaskError, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, main(), Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the… (+69 more)

### Community 9 - "main"
Cohesion: 0.19
Nodes (13): main(), Path, write_report(), Fetch, One retailer product, from its page (`url_import`) or a search result…, IKEA products matching `query`, as `catalog_search` results. A result carries…, RetailerProduct, search_ikea() (+5 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (56): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+48 more)

### Community 11 - "calculate_reachable_floor_ratio"
Cohesion: 0.17
Nodes (29): calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, divided_room(), obstacle(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.16
Nodes (37): check_placed(), deliver_furniture(), Path, RoomScene, A scene's furniture for Dev 1 to place: per item, its checked mesh or its…, Faults in how a scene carries delivered assets; empty when every asset appears…, audit(), bounds_of() (+29 more)

### Community 13 - "Frame"
Cohesion: 0.09
Nodes (36): ArtifactTooLarge, box_pixels(), fal_media_url(), FalSamProvider, fetch_bounded(), GrabCutProvider, MaskProvider, Any (+28 more)

### Community 14 - "BBoxM"
Cohesion: 0.11
Nodes (56): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, BBoxM, CollisionPart, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), NormalisedMesh (+48 more)

### Community 15 - "Registry"
Cohesion: 0.07
Nodes (81): Connection, DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery(), Exception, Path (+73 more)

### Community 16 - "App.tsx"
Cohesion: 0.09
Nodes (30): App(), ORDER, screenVariants, EditorScreen(), HomeScreen(), rise, Landscape(), LANDSCAPES (+22 more)

### Community 17 - "Pose2D"
Cohesion: 0.16
Nodes (47): OptimiseRequest, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, Step, interpret() (+39 more)

### Community 18 - "FurnitureItem"
Cohesion: 0.05
Nodes (62): FurnitureItem, Correction, Facing, _access(), AlignmentRecord, AlignmentResult, _Choice, _Capture (+54 more)

### Community 19 - "test_objective.py"
Cohesion: 0.14
Nodes (49): compare_evaluations(), compare_layouts(), evaluate_layout(), LayoutComparison, Measure a candidate against the immutable original, without modifying either.…, Rank two evaluations of the same original under the user's goal. Hard…, Compare to baseline (default original); movement always references original.…, item() (+41 more)

### Community 20 - "DraftSession"
Cohesion: 0.10
Nodes (37): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+29 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (32): int32, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point() (+24 more)

### Community 22 - "test_chat.py"
Cohesion: 0.15
Nodes (37): add_item(), chat(), ChatRequest, RoomScene, Validated tool handler. A rejected addition never mutates the caller's scene., arguments(), blocker(), move() (+29 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.08
Nodes (53): model_validator, floor_polygon is clockwise in plan view and every wall has the room on its…, apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, InvalidScale (+45 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.08
Nodes (62): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), FixedAnnotator, PlanAnnotations, Path, Returns pre-recorded annotations (tests, the debug CLI, cached demo plans). (+54 more)

### Community 25 - "test_reconstruction.py"
Cohesion: 0.06
Nodes (59): APIRouter, FailureKind, asset_router(), Path, Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset(), FalSam3dProvider (+51 more)

### Community 26 - "demo_cache.py"
Cohesion: 0.14
Nodes (31): CachedFile, CacheError, current_generation(), _inside(), install_demo_cache(), _intact(), main(), prune_demo_cache() (+23 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.20
Nodes (30): BlockedDoorIssue, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize, RoomScene, Door sweep checks using the shared stored hinge and opening conventions. (+22 more)

### Community 28 - "schema.ts"
Cohesion: 0.08
Nodes (33): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_PART_DIMENSION_M (+25 more)

### Community 29 - "parse.py"
Cohesion: 0.12
Nodes (39): FloorCaption, BaseModel, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance() (+31 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.13
Nodes (36): WindowOpening, BrightnessApproximation, calculate_brightness_approximation(), RoomScene, A window-openness proxy for layout comparison, not a lighting simulation., Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness (+28 more)

### Community 31 - "test_demo_cache_room.py"
Cohesion: 0.11
Nodes (36): furniture_data_dir(), Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, broken_cache(), from_demo_cache(), assert_readers_agree(), _audit(), auditor() (+28 more)

### Community 32 - "walk.ts"
Cohesion: 0.08
Nodes (26): WALK_HEADROOM_M, RotationRing(), captureEditorView(), EditorView, restoreEditorView(), Human(), PlaySession, fixture (+18 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.06
Nodes (42): le, demo_room_scenes(), profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, Each demo room with the furniture standing in it, as the editor builds them., solve() (+34 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "RoomView.tsx"
Cohesion: 0.13
Nodes (27): MIN_HEIGHT_OVERLAP_M, MIN_PLAN_OVERLAP_M2, DoorSwings(), flaggedFor(), Navigation(), RoomView(), doorSwing(), fitsRoom() (+19 more)

### Community 36 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 37 - "ModelReply"
Cohesion: 0.14
Nodes (20): ModelReply, Any, ToolCall, ActivityAnchor, assess_feng_shui(), Assessment, DetailModel, FengShuiRequest (+12 more)

### Community 38 - "scenes.py"
Cohesion: 0.06
Nodes (56): ge, HTTPException, Query, assemble_scene(), Assembly, assets_of(), FurnitureSource, Protocol (+48 more)

### Community 39 - "test_layout_tools.py"
Cohesion: 0.19
Nodes (25): LayoutPreferences, What the user asked for, already validated by the server., evaluate(), item(), move(), Any, FurnitureItem, parametrize (+17 more)

### Community 40 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.12
Nodes (26): FileResponse, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file() (+18 more)

### Community 42 - "ContractModel"
Cohesion: 0.11
Nodes (28): ContractModel, BaseModel, AuditReport, BlockedDoorIssue, ClearanceIssue, CollisionIssue, CollisionPart, FengShuiReport (+20 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.12
Nodes (43): cache_folder(), DemoCache, publish_catalog_scene(), Publish every product imported into `scene_id` (#19), with its retailer…, The scene's published cache, its files verified; None when none is published.…, A scene's folder: readable, and distinct for scene IDs that read alike., read_demo_cache(), _generation() (+35 more)

### Community 46 - "Sidebar.tsx"
Cohesion: 0.07
Nodes (34): AuditStats(), ChatTab(), LibraryTab(), Sidebar(), tabs, useLiveAudit(), ButtonProps, Chip() (+26 more)

### Community 47 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 48 - "FloorPlanScreen.tsx"
Cohesion: 0.17
Nodes (21): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), Panel(), area() (+13 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "SpatialInputError"
Cohesion: 0.09
Nodes (44): DoorOpening, Vec2, WallSegment, A point on the floor plan (Y omitted)., A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, LineString, Polygon, Spatial checks independent of HTTP, mesh loading and provider services. (+36 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.15
Nodes (22): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+14 more)

### Community 52 - "layout_tools.py"
Cohesion: 0.17
Nodes (16): _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, LayoutToolbox, _metrics(), _Move (+8 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_api.py"
Cohesion: 0.20
Nodes (16): payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422() (+8 more)

### Community 55 - "Decisions"
Cohesion: 0.07
Nodes (28): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+20 more)

### Community 56 - "fetch_product"
Cohesion: 0.22
Nodes (11): fetch_product(), guess_category(), Category, Classify the head phrase, using its last furniture or accessory noun.…, Download and read one retailer product page. Raises CatalogError. `source`…, parametrize, test_categories_come_from_the_products_own_words(), test_category_uses_head_noun() (+3 more)

### Community 57 - "audit_scene"
Cohesion: 0.22
Nodes (23): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+15 more)

### Community 58 - "routes.py"
Cohesion: 0.07
Nodes (36): File, AnnotationResult, Compass, FalVisionAnnotator, NullAnnotator, PlanAnnotator, Protocol, What computer vision cannot read off a floor plan: room labels with their… (+28 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "Furniture.tsx"
Cohesion: 0.19
Nodes (13): floorPlane, Mesh(), MeshBoundary, ProxyBox(), categoryWash, disposeInk(), inkify(), inkLine (+5 more)

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
Cohesion: 0.10
Nodes (20): Architecture, Backend-provided demo models, Bundled retailer library, Chat additions and application, Corrections (#11), Editor play mode, Frontend audio, Furniture evidence selection (#14) (+12 more)

### Community 68 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "ProviderError"
Cohesion: 0.22
Nodes (9): ProviderError, Exception, A failed model call. `kind` is safe to log; no key or payload is kept., Request, Response, sdk_model(), test_sdk_adapter_maps_http_failures_without_leaking_the_key(), test_sdk_adapter_maps_timeouts() (+1 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "_Page"
Cohesion: 0.29
Nodes (3): HTMLParser, _Page, The few things a product page is read for: JSON-LD, meta tags, title and…

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "test_shared_handoff_case"
Cohesion: 0.33
Nodes (4): Any, parametrize, Reusable scene variants and expected findings for Dev 3/4 integration., test_shared_handoff_case()

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.13
Nodes (15): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Free floor area, Front clearance, Internal layout comparison (issue #33) (+7 more)

### Community 76 - "calculate_free_floor_ratio"
Cohesion: 0.24
Nodes (23): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, item(), FurnitureItem, parametrize, RoomScene, Free floor area is distinct from reachable walking space., room() (+15 more)

### Community 77 - "useStore"
Cohesion: 0.15
Nodes (20): playCue(), Furniture, editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys (+12 more)

### Community 78 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 79 - "openings.py"
Cohesion: 0.22
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

### Community 86 - "invalid_request"
Cohesion: 0.28
Nodes (9): exception_handler, JSONResponse, RequestValidationError, invalid_request(), Exception, Request, Programming errors remain 500s; return structured output without leaking…, Keep standard actionable error keys without echoing input or non-JSON values. (+1 more)

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
Cohesion: 0.25
Nodes (7): Completion and follow-up, Consuming the findings, Editor integration status (issues #32 and #35), HTTP handoff contract, Layout suggestions (`POST /solve`), Load the same examples in the editor and backend, Spatial findings: Dev 3 / Dev 4 handoff

### Community 95 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

### Community 96 - "furniture_footprint"
Cohesion: 0.32
Nodes (13): furniture_footprint(), Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, make_item(), FurnitureItem, parametrize, Footprint examples independent of meshes, providers and HTTP routes., test_45_degree_corners_follow_threejs_yaw(), test_does_not_mutate_item() (+5 more)

### Community 97 - "test_report.py"
Cohesion: 0.47
Nodes (5): RoomScene, Regression checks for report composition and request-local geometry reuse., scene(), test_prepared_geometry_cannot_be_passed_to_different_scene(), test_volumes_built_once_per_item_and_not_retained_across_requests()

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "video_furniture.py"
Cohesion: 0.17
Nodes (15): NoFurniture, The room alone: what parsed rooms get until #16 produces furniture assets., default_bindings(), geometry_warning(), load_bindings(), BaseModel, Path, RoomScene (+7 more)

### Community 102 - "unpack_model"
Cohesion: 0.50
Nodes (4): Expand retailer Draco geometry and expose WebP sources to the shared reader.…, unpack_model(), Build-only codec checks; application/runtime installs do not need DracoPy., test_unpack_preserves_draco_geometry_and_uvs()

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "health"
Cohesion: 0.67
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "retailer.py"
Cohesion: 0.13
Nodes (25): _binary_models(), _dimensions(), _first_url(), _is_type(), _metres(), _model_urls(), _nodes(), parse_product_page() (+17 more)

### Community 124 - "agent.py"
Cohesion: 0.09
Nodes (26): Outcome, AgentLimits, _Budget, _explain_result(), _explore(), _interpret(), _Interpretation, LayoutModel (+18 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 128 - "objective.py"
Cohesion: 0.13
Nodes (16): _access_not_worse(), beats_original(), _check_comparable(), _door_overlap_area(), is_acceptable_proposal(), LayoutEvaluation, LayoutMetrics, AuditReport (+8 more)

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 130 - "PlayLighting.tsx"
Cohesion: 0.25
Nodes (15): DoorLightBlockers(), LightingEnvironment, PlayLighting(), useEnvironmentSettings(), bounds(), inwardNormal(), ceilingLights(), DEFAULT_PLAY_LIGHTING (+7 more)

### Community 132 - "report.py"
Cohesion: 0.19
Nodes (16): FengShuiReport, _angle_deg(), calculate_feng_shui(), _front(), _occupant(), FurnitureItem, RoomScene, A small, transparent Feng Shui placement metric from the command-position… (+8 more)

### Community 133 - "inspect_asset"
Cohesion: 0.29
Nodes (8): _declared_bounds(), _declared_bounds_problems(), _gltf_problems(), inspect_asset(), ndarray, The bounds the file declares: the union of its `POSITION` accessors' min/max.…, Re-read an asset's stored file and check it against the furniture profile and…, Scene-graph rules of the furniture profile, read from the file's JSON chunk.

### Community 135 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 136 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 137 - "no_network"
Cohesion: 0.67
Nodes (3): no_network(), MonkeyPatch, Any attempt to resolve or connect fails the test: no provider, no retailer.

## Knowledge Gaps
- **414 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+409 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `objective.py`, `test_room_align_vision.py`, `report.py`, `test_scene_routes.py`, `test_room_align.py`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `Pose2D`, `FurnitureItem`, `test_objective.py`, `DraftSession`, `test_chat.py`, `test_room_correct.py`, `test_room_parse.py`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `spatial_engine/main.py`, `test_room_shell.py`, `ModelReply`, `scenes.py`, `test_layout_tools.py`, `detect_front_clearance`, `demo_assets.py`, `ContractModel`, `detect_out_of_bounds`, `generate_mock_glbs.py`, `SpatialInputError`, `layout_tools.py`, `test_api.py`, `audit_scene`, `test_shared_handoff_case`, `calculate_free_floor_ratio`, `detect_collisions`, `test_report.py`, `video_furniture.py`, `test_demo_assets.py`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `test_room_align_vision.py`, `test_scene_routes.py`, `inspect_asset`, `scenes.py`, `video_furniture.py`, `.to_item`, `test_fixture_scene.py`, `ContractModel`, `test_room_align.py`, `test_delivery.py`, `test_demo_cache.py`, `BBoxM`, `demo_assets.py`, `Pose2D`, `FurnitureItem`, `test_contract_occupancy.py`, `test_reconstruction.py`, `demo_cache.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_catalog.py`, `FurnitureAsset`, `footprint.py`, `main`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `Pose2D`, `FurnitureItem`, `test_objective.py`, `DraftSession`, `test_chat.py`, `test_reconstruction.py`, `detect_blocked_doors`, `calculate_brightness_approximation`, `test_layout_tools.py`, `detect_front_clearance`, `ContractModel`, `detect_out_of_bounds`, `SpatialInputError`, `fetch_product`, `audit_scene`, `calculate_free_floor_ratio`, `detect_collisions`, `furniture_footprint`, `retailer.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 209 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 209 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 66 inferred relationships involving `Pose2D` (e.g. with `FurnitureAsset` and `_access()`) actually correct?**
  _`Pose2D` has 66 INFERRED edges - model-reasoned connections that need verification._