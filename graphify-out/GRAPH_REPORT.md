# Graph Report - AI_HACKATHON_PROJECT  (2026-11-15)

## Corpus Check
- 209 files · ~311,661 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3043 nodes · 8695 edges · 129 communities (113 shown, 16 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 997 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5b5d067e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- test_room_shell.py
- test_room_align_vision.py
- test_real_room.py
- RoomScene
- audio.test.ts
- catalog.py
- footprint.py
- test_segmentation.py
- shell.py
- test_room_align.py
- calculate_free_floor_ratio
- test_delivery.py
- RequestBudget
- BBoxM
- test_selection.py
- useStore
- Pose2D
- FurnitureAsset
- test_objective.py
- DraftSession
- regions.py
- detect_collisions
- read_mask
- test_room_parse.py
- test_reconstruction.py
- layout_tools.py
- detect_blocked_doors
- schema.ts
- parse.py
- calculate_brightness_approximation
- health
- RoomView.tsx
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- Furniture.tsx
- geometry.ts
- feng_shui.py
- routes.py
- LayoutToolbox
- detect_front_clearance
- demo_assets.py
- ContractModel
- compilerOptions
- CatalogError
- import_product.py
- Sidebar.tsx
- ArtifactTooLarge
- FloorPlanScreen.tsx
- generate_mock_glbs.py
- SpatialInputError
- test_contract_occupancy.py
- fetch_product
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_contracts.py
- Decisions
- PlaySession
- audit_scene
- single_room
- compilerOptions
- Video frame selection and furniture identity — issue #14
- test_api.py
- Dev 2 → Dev 1 asset handoff
- dependencies
- devDependencies
- raster.py
- polygon.py
- Architecture
- Dev 4 implementation and integration plan
- ProviderError
- Agent Instructions
- Registry
- test_fixture_scene.py
- furniture_footprint
- Implementation plan: issue #14
- Spatial engine
- _store
- store.ts
- scripts
- openings.py
- SpaceShift — System Architecture & 4-Developer Execution DAG
- Asset Handoff Agreement Implementation Plan
- Review Focus
- Review Focus
- Floor-plan parser (Dev 1)
- Furniture masks and placement evidence — issue #15
- invalid_request
- plugins
- generate-landscapes.ts
- Individual furniture meshes with proxy fallback — issue #16
- Furniture asset delivery and checks (#18, Dev 2.6)
- Retailer asset import (#19, Dev 2.7)
- scripts
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- Spatial findings: Dev 3 / Dev 4 handoff
- Furniture mesh normalisation — issue #17
- _Page
- .to_item
- model_validator
- README.md
- frontend/package.json
- LayoutMetrics
- divided_access_room
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- RetailerModelProvider
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift
- ._check_winding
- retailer.py
- LayoutModel
- test_demo_assets.py
- vite
- test_reception_fixture_assets_use_the_served_model_urls
- _along_mesh

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 158 edges
2. `FurnitureAsset` - 80 edges
3. `BBoxM` - 76 edges
4. `Registry` - 67 edges
5. `Pose2D` - 58 edges
6. `FurnitureItem` - 58 edges
7. `useStore` - 57 edges
8. `reconstruct_furniture()` - 57 edges
9. `Frame` - 52 edges
10. `SpatialInputError` - 52 edges

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

## Communities (129 total, 16 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.13
Nodes (36): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., bounds() (+28 more)

### Community 1 - "test_room_shell.py"
Cohesion: 0.10
Nodes (46): build_shell(), Scene, The room shell as a trimesh Scene with nodes `floor`, `ceiling`, `wall_<id>`., shell_glb(), corner_probes(), _inside(), invalid_footprints(), _l_door() (+38 more)

### Community 2 - "test_room_align_vision.py"
Cohesion: 0.04
Nodes (81): Image, MaskSource, build_prompt(), directory_frames(), _distance_to_wall(), _draw_marks(), _encode(), _facing() (+73 more)

### Community 3 - "test_real_room.py"
Cohesion: 0.11
Nodes (46): Collection, load_bindings(), proxy_warning(), Path, Bindings by scene ID., still_extracting(), clear_cache(), Forget assembled scenes (tests, or after the furniture source changes). (+38 more)

### Community 4 - "RoomScene"
Cohesion: 0.05
Nodes (86): RoomScene, furniture_data_dir(), Path, Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, demo_floors(), demo_room_scene(), demo_rooms() (+78 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (26): listeners, onSoundCue(), PartialTone, playCue(), renderCue(), SoundCue, tones, AudioEngine (+18 more)

### Community 6 - "catalog.py"
Cohesion: 0.06
Nodes (61): Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., write_atomic(), CatalogImport, ImageProvenance, import_product(), imported_assets(), _normalises() (+53 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (63): DoorOpening, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by() (+55 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.17
Nodes (28): Rect, box_mask(), iou(), loose_box(), make_scene_frame_dict(), png(), Mask, parametrize (+20 more)

### Community 9 - "shell.py"
Cohesion: 0.10
Nodes (38): int64, _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key(), _miter() (+30 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (56): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+48 more)

### Community 11 - "calculate_free_floor_ratio"
Cohesion: 0.10
Nodes (52): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, item(), FurnitureItem, parametrize (+44 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.09
Nodes (55): APIRouter, asset_router(), Path, Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset(), main(), Path (+47 more)

### Community 13 - "RequestBudget"
Cohesion: 0.11
Nodes (29): box_pixels(), fal_media_url(), FalSamProvider, GrabCutProvider, MaskError, MaskProvider, Any, NDArray (+21 more)

### Community 14 - "BBoxM"
Cohesion: 0.08
Nodes (70): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, BBoxM, CollisionPart, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), _bounds() (+62 more)

### Community 15 - "test_selection.py"
Cohesion: 0.09
Nodes (69): DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery(), Exception, Path, Protocol (+61 more)

### Community 16 - "useStore"
Cohesion: 0.09
Nodes (34): App(), ORDER, screenVariants, EditorScreen(), Navigation(), RoomView(), Sidebar(), useLiveAudit() (+26 more)

### Community 17 - "Pose2D"
Cohesion: 0.16
Nodes (47): OptimiseRequest, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, Step, interpret() (+39 more)

### Community 18 - "FurnitureAsset"
Cohesion: 0.05
Nodes (65): FurnitureItem, Correction, Facing, FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., _access(), AlignmentRecord, AlignmentResult (+57 more)

### Community 19 - "test_objective.py"
Cohesion: 0.13
Nodes (51): WindowOpening, beats_original(), compare_evaluations(), compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Rank two evaluations of the same original under the user's goal. Hard…, Compare to baseline (default original); movement always references original.… (+43 more)

### Community 20 - "DraftSession"
Cohesion: 0.10
Nodes (37): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+29 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (34): int32, Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction() (+26 more)

### Community 22 - "detect_collisions"
Cohesion: 0.11
Nodes (41): CollisionIssue, detect_collisions(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, CollisionVolume, furniture_collision_volumes(), An item's occupied box transformed into a vertical prism in room space. (+33 more)

### Community 23 - "read_mask"
Cohesion: 0.22
Nodes (14): main(), Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the…, write_report(), Mask, Resolve an `EvidenceFrame.mask_url` (relative to the asset data directory)., read_mask() (+6 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.13
Nodes (39): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), NullAnnotator, PlanAnnotations, No labels: the parser falls back to estimated scale and generic names., _close() (+31 more)

### Community 25 - "test_reconstruction.py"
Cohesion: 0.08
Nodes (55): FailureKind, Mask, The next published model that is usable and within the triangle budget. Each…, FalSam3dProvider, inspect_mesh(), MeshError, MeshProvider, Any (+47 more)

### Community 26 - "layout_tools.py"
Cohesion: 0.13
Nodes (24): Outcome, _explain_result(), _percent(), Bounded Sonnet layout exploration. The model reads the user's request and…, _Arguments, _CompareArguments, _EvaluateArguments, _findings() (+16 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.09
Nodes (59): BlockedDoorIssue, BlockedDoorIssue, detect_blocked_doors(), detect_out_of_bounds(), RoomScene, Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item() (+51 more)

### Community 28 - "schema.ts"
Cohesion: 0.07
Nodes (34): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M (+26 more)

### Community 29 - "parse.py"
Cohesion: 0.13
Nodes (34): FloorCaption, BaseModel, RoomLabel, _assign_labels(), _bridge_sides(), _caption_distance(), _consensus(), _fallback_scale() (+26 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.13
Nodes (35): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, A window-openness proxy for layout comparison, not a lighting simulation., Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item() (+27 more)

### Community 31 - "health"
Cohesion: 0.67
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 32 - "RoomView.tsx"
Cohesion: 0.10
Nodes (32): WALK_HEADROOM_M, floorPlane, RotationRing(), SelectionTools(), captureEditorView(), EditorOrbit, EditorView, floor (+24 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.08
Nodes (33): demo_room_scenes(), profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, Each demo room with the furniture standing in it, as the editor builds them., solve(), Timed (+25 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "Furniture.tsx"
Cohesion: 0.14
Nodes (24): Mesh(), MeshBoundary, ProxyBox(), categoryWash, disposeInk(), inkify(), inkLine, Shell (+16 more)

### Community 36 - "geometry.ts"
Cohesion: 0.16
Nodes (24): DoorSwings(), Furniture, flaggedFor(), clampToFloor(), doorSwing(), footprint(), Pt, snapToNearestWall() (+16 more)

### Community 37 - "feng_shui.py"
Cohesion: 0.20
Nodes (16): ToolCall, ActivityAnchor, assess_feng_shui(), Assessment, DetailModel, FengShuiRequest, FengShuiResult, Finding (+8 more)

### Community 38 - "routes.py"
Cohesion: 0.06
Nodes (40): description, File, ParsedFloor, AnnotationResult, Compass, FalVisionAnnotator, FixedAnnotator, PlanAnnotator (+32 more)

### Community 39 - "LayoutToolbox"
Cohesion: 0.16
Nodes (27): LayoutPreferences, LayoutToolbox, What the user asked for, already validated by the server., The three exploration tools for one request, over one `DraftSession`. `call`…, evaluate(), item(), move(), Any (+19 more)

### Community 40 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.22
Nodes (13): FileResponse, demo_shell(), furniture_model(), legacy_model(), _model_file(), get, Path, Response (+5 more)

### Community 42 - "ContractModel"
Cohesion: 0.12
Nodes (25): ContractModel, BaseModel, ClearanceIssue, CollisionIssue, CollisionPart, FengShuiReport, FengShuiSightline, GlareAlert (+17 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "CatalogError"
Cohesion: 0.14
Nodes (17): _decode(), item_box(), NDArray, uint8, An upright BGR image; transparency becomes white, as in a product shot., Where the product is in its image, and whether that was read off a plain…, CatalogError, _check_public() (+9 more)

### Community 45 - "import_product.py"
Cohesion: 0.19
Nodes (14): main(), Path, Import a retailer product as a furniture asset through the shared pipeline…, write_report(), Fetch, One retailer product, from its page (`url_import`) or a search result…, IKEA products matching `query`, as `catalog_search` results. A result carries…, RetailerProduct (+6 more)

### Community 46 - "Sidebar.tsx"
Cohesion: 0.09
Nodes (24): LayoutGoal, AuditStats(), ChatTab(), LibraryTab(), StatsTab(), tabs, catalog, catalogCategories (+16 more)

### Community 47 - "ArtifactTooLarge"
Cohesion: 0.20
Nodes (11): ArtifactTooLarge, _fetch(), fetch_bounded(), Exception, A provider artifact exceeded its size cap; nothing was kept., Stream a provider artifact without redirects, enforcing `limit` while reading., _fetch(), MonkeyPatch (+3 more)

### Community 48 - "FloorPlanScreen.tsx"
Cohesion: 0.17
Nodes (22): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), Panel(), area() (+14 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "SpatialInputError"
Cohesion: 0.07
Nodes (62): Vec2, WallSegment, A point on the floor plan (Y omitted)., FengShuiReport, LineString, Polygon, Spatial checks independent of HTTP, mesh loading and provider services., _angle_deg() (+54 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 52 - "fetch_product"
Cohesion: 0.22
Nodes (11): fetch_product(), guess_category(), Category, Classify the head phrase, using its last furniture or accessory noun.…, Download and read one retailer product page. Raises CatalogError. `source`…, parametrize, test_categories_come_from_the_products_own_words(), test_category_uses_head_noun() (+3 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_contracts.py"
Cohesion: 0.14
Nodes (21): AuditReport, load_generator(), load_mock(), parametrize, RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must… (+13 more)

### Community 55 - "Decisions"
Cohesion: 0.09
Nodes (23): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Backend-owned mock meshes, Bootstrap, Calm editor audio, Custom requests, Decisions (+15 more)

### Community 56 - "PlaySession"
Cohesion: 0.20
Nodes (3): PlaySession, initial, setup()

### Community 57 - "audit_scene"
Cohesion: 0.22
Nodes (23): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+15 more)

### Community 58 - "single_room"
Cohesion: 0.15
Nodes (22): bay_room(), _canvas(), l_room(), _png(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),…, L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed., 4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m… (+14 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "test_api.py"
Cohesion: 0.20
Nodes (16): payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422() (+8 more)

### Community 62 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.11
Nodes (18): 10. Room inputs (#5), 1. IDs, 2. What Dev 2 returns, 3. Evidence, 4. Mesh references, 5. Normalisation guarantee, 6. Occupied volume, 7. Dimension provenance (+10 more)

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
Cohesion: 0.12
Nodes (16): Architecture, Backend-provided demo models, Editor play mode, Frontend audio, Furniture evidence selection (#14), Furniture masks and placement evidence (#15), Furniture normalisation (#17, PR #54 review), Home screen and intake presentation (+8 more)

### Community 68 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "ProviderError"
Cohesion: 0.29
Nodes (8): ProviderError, Exception, A failed model call. `kind` is safe to log; no key or payload is kept., Request, Response, sdk_model(), test_sdk_adapter_maps_http_failures_without_leaking_the_key(), test_sdk_adapter_maps_timeouts()

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "Registry"
Cohesion: 0.15
Nodes (31): Connection, Any, Path, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle., Registry, Store a mask and cut-out for every selected view of the scene's (or the named)…, segment_furniture() (+23 more)

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "furniture_footprint"
Cohesion: 0.32
Nodes (13): furniture_footprint(), Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, make_item(), FurnitureItem, parametrize, Footprint examples independent of meshes, providers and HTTP routes., test_45_degree_corners_follow_threejs_yaw(), test_does_not_mutate_item() (+5 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.14
Nodes (14): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Free floor area, Front clearance, Internal layout comparison (issue #33) (+6 more)

### Community 76 - "_store"
Cohesion: 0.43
Nodes (7): _overlaps(), NDArray, Path, uint8, Masks of different items should not claim the same pixels; flag it, do not edit…, _store(), _write()

### Community 77 - "store.ts"
Cohesion: 0.15
Nodes (16): editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, CatalogItem, bump() (+8 more)

### Community 78 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 79 - "openings.py"
Cohesion: 0.15
Nodes (18): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+10 more)

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
Cohesion: 0.22
Nodes (7): Floor-plan parser (Dev 1), Furniture alignment (#8), How it works, Real-input room (#10), Scene assembly (#9), Status and limits, Use

### Community 85 - "Furniture masks and placement evidence — issue #15"
Cohesion: 0.22
Nodes (8): Approaches, Design, Furniture masks and placement evidence — issue #15, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 20 requests), Live result (2026-11-14), Needs coordination

### Community 86 - "invalid_request"
Cohesion: 0.28
Nodes (9): exception_handler, JSONResponse, RequestValidationError, invalid_request(), Exception, Request, Programming errors remain 500s; return structured output without leaking…, Keep standard actionable error keys without echoing input or non-JSON values. (+1 more)

### Community 87 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

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

### Community 96 - "_Page"
Cohesion: 0.29
Nodes (3): HTMLParser, _Page, The few things a product page is read for: JSON-LD, meta tags, title and…

### Community 97 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 102 - "divided_access_room"
Cohesion: 0.40
Nodes (4): divided_access_room(), RoomScene, Shared regression geometry for custom layout access checks., Clearing a wardrobe by moving its blocker behind the divider cuts circulation.

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "RetailerModelProvider"
Cohesion: 0.40
Nodes (4): Fetch, The retailer's own published model as the item's raw mesh. No inference and no…, RetailerModelProvider, test_retailer_model_provider_skips_unreadable_and_repeated_files()

### Community 123 - "retailer.py"
Cohesion: 0.14
Nodes (24): _binary_models(), _dimensions(), _first_url(), _is_type(), _metres(), _model_urls(), _nodes(), parse_product_page() (+16 more)

### Community 124 - "LayoutModel"
Cohesion: 0.11
Nodes (15): AgentLimits, _Budget, _explore(), _interpret(), _Interpretation, LayoutModel, ModelReply, Any (+7 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 128 - "_along_mesh"
Cohesion: 0.67
Nodes (3): _along_mesh(), BBoxM, Published width and depth, assigned to X and Z of a shape with these extents.…

## Knowledge Gaps
- **385 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+380 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `test_room_shell.py`, `test_room_align_vision.py`, `test_real_room.py`, `shell.py`, `test_room_align.py`, `calculate_free_floor_ratio`, `test_delivery.py`, `Pose2D`, `FurnitureAsset`, `test_objective.py`, `DraftSession`, `detect_collisions`, `test_room_parse.py`, `detect_blocked_doors`, `calculate_brightness_approximation`, `spatial_engine/main.py`, `feng_shui.py`, `routes.py`, `LayoutToolbox`, `detect_front_clearance`, `ContractModel`, `generate_mock_glbs.py`, `SpatialInputError`, `test_contracts.py`, `audit_scene`, `single_room`, `test_api.py`, `openings.py`, `divided_access_room`, `._check_winding`, `test_demo_assets.py`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `.to_item`, `test_room_align_vision.py`, `RoomScene`, `catalog.py`, `test_fixture_scene.py`, `ContractModel`, `test_room_align.py`, `test_delivery.py`, `BBoxM`, `Pose2D`, `test_contract_occupancy.py`, `test_reconstruction.py`, `test_reception_fixture_assets_use_the_served_model_urls`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `_along_mesh`, `test_catalog.py`, `catalog.py`, `footprint.py`, `calculate_free_floor_ratio`, `test_delivery.py`, `Pose2D`, `FurnitureAsset`, `test_objective.py`, `DraftSession`, `detect_collisions`, `test_reconstruction.py`, `detect_blocked_doors`, `calculate_brightness_approximation`, `LayoutToolbox`, `detect_front_clearance`, `ContractModel`, `import_product.py`, `fetch_product`, `audit_scene`, `furniture_footprint`, `divided_access_room`, `retailer.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 155 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 155 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 73 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 73 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Registry` (e.g. with `RetailerModelProvider` and `FalSamProvider`) actually correct?**
  _`Registry` has 13 INFERRED edges - model-reasoned connections that need verification._