# Graph Report - AI_HACKATHON_PROJECT  (2026-11-15)

## Corpus Check
- 205 files · ~308,481 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2996 nodes · 8538 edges · 122 communities (109 shown, 13 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 973 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `799bf666`
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
- BBoxM
- test_room_align.py
- calculate_free_floor_ratio
- test_delivery.py
- RequestBudget
- test_normalisation.py
- test_selection.py
- useStore
- test_agent.py
- FurnitureAsset
- test_objective.py
- DraftSession
- regions.py
- detect_collisions
- Frame
- test_room_parse.py
- mesh_providers.py
- layout_tools.py
- detect_blocked_doors
- schema.ts
- parse.py
- calculate_brightness_approximation
- align_debug.py
- walk.ts
- SpatialInputError
- SpaceShift 3D representation and asset handoff — design
- Furniture.tsx
- RoomView.tsx
- agent.py
- annotate.py
- LayoutToolbox
- detect_front_clearance
- demo_assets.py
- ContractModel
- compilerOptions
- geometry.py
- routes.py
- Sidebar.tsx
- detect_out_of_bounds
- FloorPlanScreen.tsx
- generate_mock_glbs.py
- Vec2
- test_contract_occupancy.py
- selection_models.py
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
- geometry.ts
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
- _Page
- .to_item
- _door_overlap_area
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
- vite
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 155 edges
2. `FurnitureAsset` - 80 edges
3. `BBoxM` - 74 edges
4. `Registry` - 67 edges
5. `reconstruct_furniture()` - 57 edges
6. `Pose2D` - 56 edges
7. `useStore` - 55 edges
8. `FurnitureItem` - 53 edges
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

## Communities (122 total, 13 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.05
Nodes (90): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., _binary_models() (+82 more)

### Community 1 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 2 - "test_room_align_vision.py"
Cohesion: 0.05
Nodes (77): Image, MaskSource, EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., build_prompt(), directory_frames(), _distance_to_wall(), _draw_marks() (+69 more)

### Community 3 - "test_real_room.py"
Cohesion: 0.06
Nodes (69): Collection, furniture_data_dir(), Path, Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, health(), get, Process liveness only; does not probe external providers. (+61 more)

### Community 4 - "RoomScene"
Cohesion: 0.07
Nodes (65): RoomScene, model_validator, floor_polygon is clockwise in plan view and every wall has the room on its…, assemble_scene(), Assembly, assets_of(), FurnitureSource, NoFurniture (+57 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (26): listeners, onSoundCue(), PartialTone, playCue(), renderCue(), SoundCue, tones, AudioEngine (+18 more)

### Community 6 - "catalog.py"
Cohesion: 0.05
Nodes (60): Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., write_atomic(), _along_mesh(), CatalogImport, _decode(), ImageProvenance, import_product() (+52 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (61): DoorOpening, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by() (+53 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.11
Nodes (63): Rect, main(), Path, Review images plus the two machine-readable handoffs: the result and the…, write_report(), Store a mask and cut-out for every selected view of the scene's (or the named)…, Resolve an `EvidenceFrame.mask_url` (relative to the asset data directory)., read_mask() (+55 more)

### Community 9 - "BBoxM"
Cohesion: 0.08
Nodes (55): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, inspect_mesh(), MeshError, Exception, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, (triangles, extents) of a usable glTF 2.0 binary; MeshError("invalid_mesh")…, KnownDimensions (+47 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (56): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+48 more)

### Community 11 - "calculate_free_floor_ratio"
Cohesion: 0.10
Nodes (52): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, item(), FurnitureItem, parametrize (+44 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.11
Nodes (52): APIRouter, asset_router(), Path, Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset(), check_placed(), deliver_furniture() (+44 more)

### Community 13 - "RequestBudget"
Cohesion: 0.08
Nodes (42): ArtifactTooLarge, box_pixels(), FalSamProvider, _fetch(), GrabCutProvider, MaskError, MaskProvider, Any (+34 more)

### Community 14 - "test_normalisation.py"
Cohesion: 0.11
Nodes (51): Front, BBoxM, CollisionPart, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), _bounds(), _cap_textures(), _load() (+43 more)

### Community 15 - "test_selection.py"
Cohesion: 0.13
Nodes (46): FalVisionProvider, Reviewed detections keyed by full source frame keys, never by batch position., RecordedProvider, main(), Path, Local #14 CLI. Defaults to offline sampling; --live explicitly permits provider…, Full-resolution source artifacts stay separate; the report shows boxes and IDs., write_report() (+38 more)

### Community 16 - "useStore"
Cohesion: 0.08
Nodes (38): App(), ORDER, screenVariants, EditorScreen(), Furniture, Sidebar(), HomeScreen(), rise (+30 more)

### Community 17 - "test_agent.py"
Cohesion: 0.16
Nodes (47): OptimiseRequest, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, Step, interpret() (+39 more)

### Community 18 - "FurnitureAsset"
Cohesion: 0.09
Nodes (41): FurnitureItem, Correction, Facing, FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., _access(), _Choice, _extents() (+33 more)

### Community 19 - "test_objective.py"
Cohesion: 0.15
Nodes (45): WindowOpening, compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, item(), FurnitureItem, parametrize (+37 more)

### Community 20 - "DraftSession"
Cohesion: 0.11
Nodes (35): _arrangement(), DraftSession, _echo(), LayoutMoveError, PoseChange, RoomScene, A fresh scene at the base revision, so its audit identifies the submitted scene., None means unlimited. (+27 more)

### Community 21 - "regions.py"
Cohesion: 0.11
Nodes (38): int32, _fallback_scale(), ImageFloor, No usable labels: assume interior door gaps are ESTIMATED_DOOR_M wide, else…, Raster, _accept(), Bridge, _cast() (+30 more)

### Community 22 - "detect_collisions"
Cohesion: 0.11
Nodes (39): CollisionIssue, detect_collisions(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, furniture_collision_volumes(), Transform validated local collision boxes; absent parts mean one solid bbox.…, item() (+31 more)

### Community 23 - "Frame"
Cohesion: 0.12
Nodes (32): DiscoveryError, DiscoveryProvider, OfflineProvider, parse_discovery(), Exception, Path, Protocol, fal vision proposes instances across full images; reviewed recordings run… (+24 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.14
Nodes (38): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), PlanAnnotations, _close(), _example(), _has_vertex() (+30 more)

### Community 25 - "mesh_providers.py"
Cohesion: 0.08
Nodes (29): FailureKind, main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), Delivery, computed_field, Every delivered asset passed its checks. Proxies are allowed; they are listed. (+21 more)

### Community 26 - "layout_tools.py"
Cohesion: 0.12
Nodes (27): LayoutDraft, Request-local immutable layout drafts: pose-only edits audited against one…, _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, _metrics() (+19 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.15
Nodes (35): BlockedDoorIssue, BlockedDoorIssue, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize, RoomScene (+27 more)

### Community 28 - "schema.ts"
Cohesion: 0.07
Nodes (36): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M (+28 more)

### Community 29 - "parse.py"
Cohesion: 0.12
Nodes (36): FloorCaption, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance(), _consensus() (+28 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.13
Nodes (35): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, A window-openness proxy for layout comparison, not a lighting simulation., Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item() (+27 more)

### Community 31 - "align_debug.py"
Cohesion: 0.09
Nodes (27): AlignmentRecord, AlignmentResult, _Capture, main(), pose_error(), FrameSource, FurnitureItem, RoomScene (+19 more)

### Community 32 - "walk.ts"
Cohesion: 0.13
Nodes (26): captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera(), restoreEditorView(), Human() (+18 more)

### Community 33 - "SpatialInputError"
Cohesion: 0.11
Nodes (31): ActivityAnchor, assess_feng_shui(), Assessment, DetailModel, FengShuiRequest, FengShuiResult, Finding, Mirror (+23 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "Furniture.tsx"
Cohesion: 0.16
Nodes (23): Mesh(), ProxyBox(), categoryWash, disposeInk(), inkify(), inkLine, Shell, invalidatePlayShadows() (+15 more)

### Community 36 - "RoomView.tsx"
Cohesion: 0.14
Nodes (22): DoorSwings(), MeshBoundary, flaggedFor(), Navigation(), RoomView(), doorSwing(), footprint(), toWorld() (+14 more)

### Community 37 - "agent.py"
Cohesion: 0.11
Nodes (20): Outcome, _Budget, _explain_result(), _explore(), _interpret(), _Interpretation, LayoutModel, ModelReply (+12 more)

### Community 38 - "annotate.py"
Cohesion: 0.10
Nodes (21): ParsedFloor, AnnotationResult, Compass, FalVisionAnnotator, FixedAnnotator, NullAnnotator, BaseModel, Path (+13 more)

### Community 39 - "LayoutToolbox"
Cohesion: 0.18
Nodes (27): LayoutPreferences, LayoutToolbox, What the user asked for, already validated by the server., The three exploration tools for one request, over one `DraftSession`. `call`…, evaluate(), item(), move(), Any (+19 more)

### Community 40 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.12
Nodes (26): FileResponse, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file() (+18 more)

### Community 42 - "ContractModel"
Cohesion: 0.12
Nodes (25): ContractModel, BaseModel, ClearanceIssue, CollisionIssue, CollisionPart, FengShuiReport, FengShuiSightline, GlareAlert (+17 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "geometry.py"
Cohesion: 0.15
Nodes (21): Spatial checks independent of HTTP, mesh loading and provider services., CollisionVolume, front_clearance_zone(), FurnitureGeometry, prepare_furniture(), prepare_scene(), FurnitureItem, RoomScene (+13 more)

### Community 45 - "routes.py"
Cohesion: 0.11
Nodes (24): description, File, PlanAnnotator, Protocol, plan_id_for(), find_parsed_scene(), get_annotator(), get_plan() (+16 more)

### Community 46 - "Sidebar.tsx"
Cohesion: 0.11
Nodes (18): AuditStats(), ChatTab(), StatsTab(), tabs, ButtonProps, Chip(), dotColor, Panel() (+10 more)

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
Cohesion: 0.16
Nodes (21): Vec2, WallSegment, A point on the floor plan (Y omitted)., LineString, Polygon, door_entry_segment(), _door_frame(), door_swing_sector() (+13 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 52 - "selection_models.py"
Cohesion: 0.13
Nodes (16): DiscoveredObject, MissingMask, BaseModel, model_validator, Internal #14-#16 records. Source evidence is deliberately separate from…, Record, SegmentationResult, SelectionResult (+8 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_contracts.py"
Cohesion: 0.14
Nodes (21): AuditReport, load_generator(), load_mock(), parametrize, RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must… (+13 more)

### Community 55 - "Decisions"
Cohesion: 0.09
Nodes (22): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Backend-owned mock meshes, Bootstrap, Calm editor audio, Custom requests, Decisions (+14 more)

### Community 56 - "PlaySession"
Cohesion: 0.16
Nodes (5): PlaySession, fixture, mockScene, initial, setup()

### Community 57 - "audit_scene"
Cohesion: 0.13
Nodes (19): demo_room_scenes(), profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, Each demo room with the furniture standing in it, as the editor builds them., solve(), Timed (+11 more)

### Community 58 - "single_room"
Cohesion: 0.16
Nodes (21): bay_room(), _canvas(), l_room(), _png(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),…, L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed., 4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m… (+13 more)

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
Cohesion: 0.13
Nodes (13): AgentLimits, AnthropicLayoutModel, ProviderError, Exception, Claude through the official SDK. The loop above owns retries, so the SDK makes…, One allowance per request. Retries and the interpretation call spend the same…, A failed model call. `kind` is safe to log; no key or payload is kept., Request (+5 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "Registry"
Cohesion: 0.20
Nodes (7): Connection, Any, Path, Local SQLite transactions for scene identities and recoverable provider…, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle., Registry

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
Cohesion: 0.15
Nodes (13): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment, Free floor area, Front clearance, Internal layout comparison (issue #33), Layout drafts for proposed moves (issue #33) (+5 more)

### Community 76 - "geometry.ts"
Cohesion: 0.23
Nodes (9): floorPlane, RotationRing(), SelectionTools(), LibraryTab(), DEG, fitsRoom(), fitYaw(), planAngle() (+1 more)

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
Cohesion: 0.29
Nodes (6): Completion and follow-up, Consuming the findings, HTTP handoff contract, Layout suggestions (`POST /solve`), Load the same examples in the editor and backend, Spatial findings: Dev 3 / Dev 4 handoff

### Community 95 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

### Community 96 - "_Page"
Cohesion: 0.29
Nodes (3): HTMLParser, _Page, The few things a product page is read for: JSON-LD, meta tags, title and…

### Community 97 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 98 - "_door_overlap_area"
Cohesion: 0.29
Nodes (7): _check_comparable(), _door_overlap_area(), _near_window_shortfall(), AuditReport, RoomScene, Do not improve metrics by changing the room, removing items or shrinking them., Grade progress while a door is still blocked, using the audit's same thresholds.

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 102 - "divided_access_room"
Cohesion: 0.40
Nodes (4): divided_access_room(), RoomScene, Shared regression geometry for custom layout access checks., Clearing a wardrobe by moving its blocker behind the divider cuts circulation.

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

## Knowledge Gaps
- **386 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+381 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `test_room_shell.py`, `test_room_align_vision.py`, `test_real_room.py`, `test_room_align.py`, `calculate_free_floor_ratio`, `test_delivery.py`, `test_agent.py`, `FurnitureAsset`, `test_objective.py`, `DraftSession`, `detect_collisions`, `test_room_parse.py`, `layout_tools.py`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `align_debug.py`, `SpatialInputError`, `LayoutToolbox`, `detect_front_clearance`, `demo_assets.py`, `ContractModel`, `geometry.py`, `routes.py`, `detect_out_of_bounds`, `generate_mock_glbs.py`, `test_contracts.py`, `audit_scene`, `single_room`, `test_api.py`, `_door_overlap_area`, `divided_access_room`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_catalog.py`, `catalog.py`, `footprint.py`, `calculate_free_floor_ratio`, `test_delivery.py`, `test_normalisation.py`, `test_agent.py`, `FurnitureAsset`, `test_objective.py`, `DraftSession`, `detect_collisions`, `detect_blocked_doors`, `calculate_brightness_approximation`, `LayoutToolbox`, `detect_front_clearance`, `ContractModel`, `detect_out_of_bounds`, `furniture_footprint`, `divided_access_room`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `.to_item`, `test_room_align_vision.py`, `RoomScene`, `catalog.py`, `test_fixture_scene.py`, `BBoxM`, `ContractModel`, `test_room_align.py`, `test_delivery.py`, `demo_assets.py`, `test_normalisation.py`, `test_agent.py`, `test_contract_occupancy.py`, `selection_models.py`, `mesh_providers.py`, `align_debug.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 152 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 152 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 71 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Registry` (e.g. with `RetailerModelProvider` and `FalSamProvider`) actually correct?**
  _`Registry` has 13 INFERRED edges - model-reasoned connections that need verification._