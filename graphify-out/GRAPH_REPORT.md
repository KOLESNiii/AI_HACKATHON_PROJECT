# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 221 files · ~335,949 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3371 nodes · 9883 edges · 142 communities (125 shown, 17 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1158 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1a8ef73e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- shell.py
- test_room_align_vision.py
- test_real_room.py
- test_scene_routes.py
- audio.test.ts
- catalog.py
- footprint.py
- test_segmentation.py
- FurnitureAsset
- test_room_align.py
- calculate_reachable_floor_ratio
- test_delivery.py
- _store
- BBoxM
- test_selection.py
- useStore
- test_agent.py
- FurnitureItem
- Pose2D
- DraftSession
- regions.py
- test_chat.py
- test_room_correct.py
- test_room_parse.py
- test_reconstruction.py
- layout_tools.py
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
- ProviderError
- scenes.py
- LayoutToolbox
- detect_collisions
- demo_assets.py
- ContractModel
- compilerOptions
- test_demo_cache.py
- Frame
- Sidebar.tsx
- detect_out_of_bounds
- FloorPlanScreen.tsx
- generate_mock_glbs.py
- Vec2
- test_contract_occupancy.py
- SpatialInputError
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_api.py
- Decisions
- calculate_free_floor_ratio
- audit_scene
- annotate.py
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
- check_layout_demo.py
- Agent Instructions
- Registry
- test_fixture_scene.py
- RoomScene
- Implementation plan: issue #14
- Spatial engine
- demo_cache.py
- keyboard.ts
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
- Point
- .to_item
- DiscoveredObject
- README.md
- frontend/package.json
- video_furniture.py
- test_contracts.py
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- footprint
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift
- manifest.json
- _Page
- chat.py
- test_demo_assets.py
- vite
- rescale_floor
- proxy_asset
- Validated, cached demo assets (#20, Dev 2.8)
- furniture_proxy
- item_box
- _inside
- _along_mesh
- .ok
- ArtifactTooLarge
- health
- test_every_example_room_is_accepted_by_the_audit
- demo_cache/README.md
- .from_file
- .of
- test_shell_build_needs_no_optional_geometry_packages

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 212 edges
2. `FurnitureAsset` - 87 edges
3. `BBoxM` - 79 edges
4. `Pose2D` - 69 edges
5. `FurnitureItem` - 69 edges
6. `Registry` - 67 edges
7. `SpatialInputError` - 59 edges
8. `useStore` - 58 edges
9. `reconstruct_furniture()` - 57 edges
10. `audit_scene()` - 56 edges

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

## Communities (142 total, 17 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.05
Nodes (95): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., main() (+87 more)

### Community 1 - "shell.py"
Cohesion: 0.11
Nodes (37): int64, _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key(), _miter() (+29 more)

### Community 2 - "test_room_align_vision.py"
Cohesion: 0.06
Nodes (69): Image, MaskSource, EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., build_prompt(), directory_frames(), _distance_to_wall(), _draw_marks() (+61 more)

### Community 3 - "test_real_room.py"
Cohesion: 0.09
Nodes (73): Collection, _audit(), auditor(), _clear(), client(), _collides(), data_dir(), _findings() (+65 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.09
Nodes (49): assemble_scene(), Assembly, assets_of(), NoFurniture, RoomScene, One room + its furniture -> the `RoomScene` the editor and the audit load (#9).…, A scene's furniture as pose-less assets with placeholder evidence (no source…, What a furniture source supplies for one room. (+41 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 6 - "catalog.py"
Cohesion: 0.06
Nodes (63): Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, CatalogImport, ImageProvenance, import_product(), imported_assets(), _normalises(), Fetch, Path (+55 more)

### Community 7 - "footprint.py"
Cohesion: 0.15
Nodes (23): any_overlap(), _bounds_apart(), closed_leaf(), door_approach(), door_sweep(), Prism, prisms_overlap(), DoorOpening (+15 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.08
Nodes (87): Rect, box_pixels(), FalSamProvider, _fetch(), GrabCutProvider, MaskError, MaskProvider, Protocol (+79 more)

### Community 9 - "FurnitureAsset"
Cohesion: 0.15
Nodes (14): FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., _Capture, FrameSource, RoomScene, Passes hints through and keeps them, so a live run can be recorded., Drop hints that name an unknown asset or wall; keep the most confident per…, _usable_hints() (+6 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (56): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+48 more)

### Community 11 - "calculate_reachable_floor_ratio"
Cohesion: 0.17
Nodes (29): calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, divided_room(), obstacle(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.11
Nodes (50): main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), check_placed(), deliver_furniture(), Delivery, _gltf_problems() (+42 more)

### Community 13 - "_store"
Cohesion: 0.43
Nodes (7): _bounds(), Mask, NDArray, Path, uint8, _store(), _write()

### Community 14 - "BBoxM"
Cohesion: 0.11
Nodes (54): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, BBoxM, CollisionPart, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), _bounds() (+46 more)

### Community 15 - "test_selection.py"
Cohesion: 0.13
Nodes (48): FalVisionProvider, Reviewed detections keyed by full source frame keys, never by batch position., RecordedProvider, main(), Path, Local #14 CLI. Defaults to offline sampling; --live explicitly permits provider…, Full-resolution source artifacts stay separate; the report shows boxes and IDs., write_report() (+40 more)

### Community 16 - "useStore"
Cohesion: 0.09
Nodes (34): App(), ORDER, screenVariants, playCue(), EditorScreen(), floorPlane, SelectionTools(), Sidebar() (+26 more)

### Community 17 - "test_agent.py"
Cohesion: 0.17
Nodes (45): OptimiseRequest, propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, Step, interpret(), item(), move() (+37 more)

### Community 18 - "FurnitureItem"
Cohesion: 0.06
Nodes (60): FurnitureItem, Correction, Facing, _access(), AlignmentRecord, AlignmentResult, _Choice, pose_error() (+52 more)

### Community 19 - "Pose2D"
Cohesion: 0.16
Nodes (42): Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., compare_layouts(), Compare to baseline (default original); movement always references original.…, item(), FurnitureItem, RoomScene, Layout ranking uses real audited geometry and explicit, stable priorities. (+34 more)

### Community 20 - "DraftSession"
Cohesion: 0.11
Nodes (36): _arrangement(), DraftSession, _echo(), LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one…, A fresh scene at the base revision, so its audit identifies the submitted scene. (+28 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (34): int32, Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction() (+26 more)

### Community 22 - "test_chat.py"
Cohesion: 0.13
Nodes (41): add_item(), chat(), ChatRequest, RoomScene, Validated tool handler. A rejected addition never mutates the caller's scene., proxy_glb(), Small dimensioned GLB box, without a reconstruction dependency., arguments() (+33 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.11
Nodes (39): apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, _perimeter(), _point(), Exception (+31 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.10
Nodes (57): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, FixedAnnotator, PlanAnnotations, Returns pre-recorded annotations (tests, the debug CLI, cached demo plans)., client(), The reconstruction routes with the asset store mounted on this test's data… (+49 more)

### Community 25 - "test_reconstruction.py"
Cohesion: 0.07
Nodes (54): FailureKind, Mask, The retailer's own published model as the item's raw mesh. No inference and no…, The next published model that is usable and within the triangle budget. Each…, RetailerModelProvider, fal_media_url(), Provider artifacts are fetched over HTTPS from fal's media hosts only., FalSam3dProvider (+46 more)

### Community 26 - "layout_tools.py"
Cohesion: 0.16
Nodes (15): LayoutDraft, _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, _metrics(), _Move (+7 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.14
Nodes (37): BlockedDoorIssue, BlockedDoorIssue, CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem (+29 more)

### Community 28 - "schema.ts"
Cohesion: 0.08
Nodes (33): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_PART_DIMENSION_M, AuditReport (+25 more)

### Community 29 - "parse.py"
Cohesion: 0.11
Nodes (40): FloorCaption, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance(), _consensus() (+32 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.13
Nodes (35): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, A window-openness proxy for layout comparison, not a lighting simulation., Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item() (+27 more)

### Community 31 - "test_demo_cache_room.py"
Cohesion: 0.10
Nodes (38): furniture_data_dir(), Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, from_demo_cache(), assert_readers_agree(), _audit(), auditor(), _client() (+30 more)

### Community 32 - "walk.ts"
Cohesion: 0.08
Nodes (33): RotationRing(), captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera(), restoreEditorView() (+25 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.12
Nodes (30): LayoutModel, Protocol, ChatReply, ActivityAnchor, assess_feng_shui(), Assessment, DetailModel, FengShuiRequest (+22 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "RoomView.tsx"
Cohesion: 0.09
Nodes (44): MIN_HEIGHT_OVERLAP_M, MIN_PLAN_OVERLAP_M2, DoorSwings(), Furniture, flaggedFor(), Navigation(), RoomView(), DoorLightBlockers() (+36 more)

### Community 36 - "test_room_shell.py"
Cohesion: 0.12
Nodes (39): build_shell(), Scene, The room shell as a trimesh Scene with nodes `floor`, `ceiling`, `wall_<id>`., corner_probes(), invalid_footprints(), _l_door(), make_scene(), parametrize (+31 more)

### Community 37 - "ProviderError"
Cohesion: 0.11
Nodes (17): AnthropicLayoutModel, ModelReply, ProviderError, Any, Exception, Claude through the official SDK. The loop above owns retries, so the SDK makes…, A failed model call. `kind` is safe to log; no key or payload is kept., ToolCall (+9 more)

### Community 38 - "scenes.py"
Cohesion: 0.05
Nodes (63): File, ge, HTTPException, Query, demo_cache_dir(), Path, Where published demo furniture is read from when the pipeline has none (#20).…, FurnitureSource (+55 more)

### Community 39 - "LayoutToolbox"
Cohesion: 0.18
Nodes (27): LayoutPreferences, LayoutToolbox, What the user asked for, already validated by the server., The three exploration tools for one request, over one `DraftSession`. `call`…, evaluate(), item(), move(), Any (+19 more)

### Community 40 - "detect_collisions"
Cohesion: 0.06
Nodes (84): ClearanceIssue, CollisionIssue, detect_collisions(), detect_front_clearance(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, Check full-width front access strips, returning one issue per blocker. actual_m… (+76 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.21
Nodes (14): FileResponse, demo_shell(), furniture_model(), legacy_model(), _model_file(), get, Path, Response (+6 more)

### Community 42 - "ContractModel"
Cohesion: 0.08
Nodes (35): ContractModel, BaseModel, AuditReport, ClearanceIssue, CollisionIssue, DoorOpening, FengShuiReport, FengShuiSightline (+27 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.12
Nodes (44): cache_folder(), DemoCache, publish_catalog_scene(), publish_demo_cache(), Publish delivered assets and their files as the scene's cache, replacing any…, Publish every product imported into `scene_id` (#19), with its retailer…, The scene's published cache, its files verified; None when none is published.…, A scene's folder: readable, and distinct for scene IDs that read alike. (+36 more)

### Community 45 - "Frame"
Cohesion: 0.13
Nodes (29): DiscoveryError, DiscoveryProvider, OfflineProvider, parse_discovery(), Exception, Path, Protocol, fal vision proposes instances across full images; reviewed recordings run… (+21 more)

### Community 46 - "Sidebar.tsx"
Cohesion: 0.07
Nodes (35): LayoutGoal, AuditStats(), ChatTab(), LibraryTab(), StatsTab(), tabs, ButtonProps, Chip() (+27 more)

### Community 47 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 48 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (20): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+12 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "Vec2"
Cohesion: 0.07
Nodes (51): Vec2, A point on the floor plan (Y omitted)., FengShuiReport, LineString, Polygon, Spatial checks independent of HTTP, mesh loading and provider services., _angle_deg(), calculate_feng_shui() (+43 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 52 - "SpatialInputError"
Cohesion: 0.09
Nodes (35): Outcome, _explain_result(), _Interpretation, _percent(), BaseModel, Bounded Sonnet layout exploration. The model reads the user's request and…, ValueError, A validated domain-input failure whose message is safe to show to the caller. (+27 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_api.py"
Cohesion: 0.20
Nodes (16): payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422() (+8 more)

### Community 55 - "Decisions"
Cohesion: 0.08
Nodes (26): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+18 more)

### Community 56 - "calculate_free_floor_ratio"
Cohesion: 0.24
Nodes (23): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, item(), FurnitureItem, parametrize, RoomScene, Free floor area is distinct from reachable walking space., room() (+15 more)

### Community 57 - "audit_scene"
Cohesion: 0.22
Nodes (23): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+15 more)

### Community 58 - "annotate.py"
Cohesion: 0.09
Nodes (24): AnnotationResult, Compass, _extract_json(), FalVisionAnnotator, NullAnnotator, PlanAnnotator, BaseModel, Protocol (+16 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "Furniture.tsx"
Cohesion: 0.26
Nodes (10): Mesh(), MeshBoundary, ProxyBox(), categoryWash, disposeInk(), inkify(), inkLine, Shell (+2 more)

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
Cohesion: 0.11
Nodes (18): Architecture, Backend-provided demo models, Chat additions and application, Corrections (#11), Editor play mode, Frontend audio, Furniture evidence selection (#14), Furniture masks and placement evidence (#15) (+10 more)

### Community 68 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "check_layout_demo.py"
Cohesion: 0.16
Nodes (15): demo_room_scenes(), profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, Each demo room with the furniture standing in it, as the editor builds them., solve(), Timed (+7 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "Registry"
Cohesion: 0.13
Nodes (13): Connection, Any, NDArray, uint8, One segment per box, in order; None where none was produced. Raises MaskError…, Segment, Any, Path (+5 more)

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.18
Nodes (5): The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape(), test_fixture_scene_has_no_collisions()

### Community 73 - "RoomScene"
Cohesion: 0.12
Nodes (23): RoomScene, model_validator, floor_polygon is clockwise in plan view and every wall has the room on its…, demo_floors(), demo_room_scene(), demo_rooms(), RoomScene, The shared three-floor fixtures, one whole-floor scene per floor name. (+15 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.13
Nodes (15): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Free floor area, Front clearance, Internal layout comparison (issue #33) (+7 more)

### Community 76 - "demo_cache.py"
Cohesion: 0.17
Nodes (25): CachedFile, CacheError, current_generation(), _inside(), install_demo_cache(), _intact(), main(), prune_demo_cache() (+17 more)

### Community 77 - "keyboard.ts"
Cohesion: 0.32
Nodes (7): editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, initial

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

### Community 96 - "Point"
Cohesion: 0.11
Nodes (23): boundary_distance(), clip_convex(), covered_by(), _crosses_interior(), front_direction(), overlap_area(), point_in_polygon(), Point (+15 more)

### Community 97 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 98 - "DiscoveredObject"
Cohesion: 0.22
Nodes (3): _diagnostic(), DiscoveredObject, model_validator

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "video_furniture.py"
Cohesion: 0.14
Nodes (20): broken_cache(), default_bindings(), geometry_mismatch(), geometry_warning(), load_bindings(), proxy_warning(), BaseModel, Path (+12 more)

### Community 102 - "test_contracts.py"
Cohesion: 0.16
Nodes (17): load_generator(), load_mock(), RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must…, solid_at(), test_audit_report_must_echo_scene() (+9 more)

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "footprint"
Cohesion: 0.26
Nodes (12): footprint(), front_zone(), occupied(), BBoxM, CollisionPart, Pose2D, A local rectangle (centre x/z, extents along local X/Z) in room coordinates., The whole `bbox_m` box: what must stay inside the room. (+4 more)

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "_Page"
Cohesion: 0.29
Nodes (3): HTMLParser, _Page, The few things a product page is read for: JSON-LD, meta tags, title and…

### Community 124 - "chat.py"
Cohesion: 0.10
Nodes (17): AgentLimits, _Budget, _explore(), _interpret(), OptimiseRequest, Read the instruction. Returns (interpretation or None, assistant still usable)., Run the tool loop. Returns (model finished normally, a provider call failed)., One allowance per request. Retries and the interpretation call spend the same… (+9 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "rescale_floor"
Cohesion: 0.25
Nodes (9): InvalidScale, ParsedFloor, ValueError, A room of the floor cannot exist at that scale (it would break the contract)., Every room of the floor rescaled; the dimensions now come from the user. Raises…, rescale_floor(), parametrize, PR #59 review: rounding made a door wider than its rescaled wall (the audit… (+1 more)

### Community 128 - "proxy_asset"
Cohesion: 0.11
Nodes (22): APIRouter, asset_router(), Path, Readers never see a partial file., Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset(), write_atomic() (+14 more)

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 130 - "furniture_proxy"
Cohesion: 0.25
Nodes (8): le, furniture_proxy(), health(), get, gt, Path, Response, Process liveness only; does not probe external providers.

### Community 131 - "item_box"
Cohesion: 0.33
Nodes (7): _decode(), item_box(), NDArray, uint8, An upright BGR image; transparency becomes white, as in a product shot., Where the product is in its image, and whether that was read off a plain…, test_image_pixel_limit_is_checked_before_opencv_decode()

### Community 132 - "_inside"
Cohesion: 0.50
Nodes (4): _inside(), ndarray, Trimesh, Ray parity in plain numpy (Moller-Trumbore), so the probes need no SciPy or…

### Community 133 - "_along_mesh"
Cohesion: 0.67
Nodes (3): _along_mesh(), BBoxM, Published width and depth, assigned to X and Z of a shape with these extents.…

### Community 135 - "ArtifactTooLarge"
Cohesion: 0.67
Nodes (3): ArtifactTooLarge, Exception, A provider artifact exceeded its size cap; nothing was kept.

### Community 136 - "health"
Cohesion: 0.67
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 137 - "test_every_example_room_is_accepted_by_the_audit"
Cohesion: 0.67
Nodes (3): parametrize, Coordinates are rounded to the millimetre, which left hinges up to 0.9 mm off…, test_every_example_room_is_accepted_by_the_audit()

## Knowledge Gaps
- **407 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+402 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `shell.py`, `test_room_align_vision.py`, `test_real_room.py`, `test_scene_routes.py`, `FurnitureAsset`, `test_room_align.py`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `test_agent.py`, `FurnitureItem`, `Pose2D`, `DraftSession`, `test_chat.py`, `test_room_correct.py`, `test_room_parse.py`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `spatial_engine/main.py`, `test_room_shell.py`, `scenes.py`, `LayoutToolbox`, `detect_collisions`, `demo_assets.py`, `ContractModel`, `detect_out_of_bounds`, `generate_mock_glbs.py`, `Vec2`, `SpatialInputError`, `test_api.py`, `calculate_free_floor_ratio`, `audit_scene`, `check_layout_demo.py`, `video_furniture.py`, `test_contracts.py`, `test_demo_assets.py`?**
  _High betweenness centrality (0.167) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `proxy_asset`, `test_room_align_vision.py`, `test_scene_routes.py`, `catalog.py`, `test_room_align.py`, `test_delivery.py`, `BBoxM`, `FurnitureItem`, `Pose2D`, `test_reconstruction.py`, `detect_blocked_doors`, `ContractModel`, `test_demo_cache.py`, `test_contract_occupancy.py`, `test_fixture_scene.py`, `RoomScene`, `demo_cache.py`, `.to_item`, `video_furniture.py`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_catalog.py`, `proxy_asset`, `_along_mesh`, `catalog.py`, `FurnitureAsset`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `test_agent.py`, `FurnitureItem`, `Pose2D`, `DraftSession`, `test_chat.py`, `test_reconstruction.py`, `detect_blocked_doors`, `calculate_brightness_approximation`, `LayoutToolbox`, `detect_collisions`, `ContractModel`, `detect_out_of_bounds`, `calculate_free_floor_ratio`, `audit_scene`, `Point`, `footprint`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 209 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 209 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 66 inferred relationships involving `Pose2D` (e.g. with `FurnitureAsset` and `_access()`) actually correct?**
  _`Pose2D` has 66 INFERRED edges - model-reasoned connections that need verification._