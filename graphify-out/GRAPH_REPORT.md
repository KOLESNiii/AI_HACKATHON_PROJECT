# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 213 files · ~327,557 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3254 nodes · 9460 edges · 140 communities (123 shown, 17 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1086 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `efe63424`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- shell.py
- test_room_align_vision.py
- RoomScene
- test_scene_routes.py
- audio.test.ts
- catalog.py
- footprint.py
- test_segmentation.py
- observe_vision.py
- test_room_align.py
- calculate_reachable_floor_ratio
- test_delivery.py
- Box
- BBoxM
- test_selection.py
- useStore
- Pose2D
- FurnitureAsset
- test_objective.py
- DraftSession
- regions.py
- detect_collisions
- test_demo_cache_room.py
- test_room_parse.py
- test_reconstruction.py
- objective.py
- detect_blocked_doors
- schema.ts
- parse.py
- calculate_brightness_approximation
- align_debug.py
- walk.ts
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- PlayLighting.tsx
- geometry.ts
- agent.py
- routes.py
- selection_models.py
- FurnitureItem
- demo_assets.py
- detect_front_clearance
- compilerOptions
- test_demo_cache.py
- scenes.py
- Sidebar.tsx
- detect_out_of_bounds
- FloorPlanScreen.tsx
- generate_mock_glbs.py
- SpatialInputError
- test_contract_occupancy.py
- model_validator
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_api.py
- Decisions
- test_real_room.py
- check_layout_demo.py
- single_room
- compilerOptions
- Video frame selection and furniture identity — issue #14
- Vec2
- Dev 2 → Dev 1 asset handoff
- dependencies
- devDependencies
- raster.py
- polygon.py
- Architecture
- Dev 4 implementation and integration plan
- test_room_shell.py
- Agent Instructions
- retailer.py
- FixedAnnotator
- layout_tools.py
- Implementation plan: issue #14
- Spatial engine
- RoomView.tsx
- keyboard.ts
- scripts
- test_layout_tools.py
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
- Registry
- .to_item
- Validated, cached demo assets (#20, Dev 2.8)
- README.md
- frontend/package.json
- calculate_free_floor_ratio
- _Page
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
- manifest.json
- check_delivery.py
- audit.py
- normalisation.py
- demo_cache/README.md
- CatalogError
- furniture_footprint
- test_demo_assets.py
- ContractModel
- openings.py
- masked_scene
- item_box
- guess_category
- LayoutMetrics
- _inside
- _along_mesh
- .of
- test_shell_build_needs_no_optional_geometry_packages

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 191 edges
2. `FurnitureAsset` - 87 edges
3. `BBoxM` - 74 edges
4. `Registry` - 67 edges
5. `Pose2D` - 61 edges
6. `FurnitureItem` - 60 edges
7. `reconstruct_furniture()` - 57 edges
8. `useStore` - 55 edges
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

## Communities (140 total, 17 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.12
Nodes (40): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., bounds() (+32 more)

### Community 1 - "shell.py"
Cohesion: 0.11
Nodes (37): int64, _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key(), _miter() (+29 more)

### Community 2 - "test_room_align_vision.py"
Cohesion: 0.09
Nodes (45): EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., directory_frames(), FrameSource, Path, Frames of one video stored as `<frame_index>.jpg` or `.png` (upright, as…, The upright frames Dev 2's pipeline stored, for evidence made by…, The evidence frames worth sending: every asset shown at least once, widest… (+37 more)

### Community 3 - "RoomScene"
Cohesion: 0.20
Nodes (14): RoomScene, geometry_mismatch(), Why `room` is not the room `binding` was made for, or None when it is. Compares…, _length(), Response, WallSegment, The binding names a room by its shape: the user may correct its scale (#11)., PR #59 review: x1.1 made floor-1-room-5's door1 wider than its diagonal wall w6. (+6 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.16
Nodes (30): _audit(), auditor(), _door(), _leaf_end(), DoorOpening, parametrize, RoomScene, TestClient (+22 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 6 - "catalog.py"
Cohesion: 0.05
Nodes (78): Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., write_atomic(), CatalogImport, ImageProvenance, import_product(), imported_assets(), _normalises() (+70 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (61): any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach() (+53 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.12
Nodes (61): Rect, main(), Store a mask and cut-out for every selected view of the scene's (or the named)…, Resolve an `EvidenceFrame.mask_url` (relative to the asset data directory)., read_mask(), segment_furniture(), Sighting, test_mesh_record_belongs_to_a_sighting_and_goes_stale_with_its_mask() (+53 more)

### Community 9 - "observe_vision.py"
Cohesion: 0.08
Nodes (36): Image, build_prompt(), _distance_to_wall(), _draw_marks(), _encode(), _facing(), FalVisionObserver, hints_from_reply() (+28 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (58): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+50 more)

### Community 11 - "calculate_reachable_floor_ratio"
Cohesion: 0.17
Nodes (29): calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, divided_room(), obstacle(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.13
Nodes (43): APIRouter, asset_router(), Path, Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset(), check_placed(), deliver_furniture() (+35 more)

### Community 13 - "Box"
Cohesion: 0.09
Nodes (38): ArtifactTooLarge, box_pixels(), FalSamProvider, _fetch(), GrabCutProvider, MaskError, MaskProvider, Any (+30 more)

### Community 14 - "BBoxM"
Cohesion: 0.18
Nodes (38): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, normalise_mesh(), BBoxM, Fit a raw glTF 2.0 binary to the furniture profile, store it and return its…, assert_fits(), chair_like() (+30 more)

### Community 15 - "test_selection.py"
Cohesion: 0.10
Nodes (61): DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery(), Exception, Path, Protocol (+53 more)

### Community 16 - "useStore"
Cohesion: 0.09
Nodes (34): App(), ORDER, screenVariants, playCue(), EditorScreen(), Sidebar(), HomeScreen(), rise (+26 more)

### Community 17 - "Pose2D"
Cohesion: 0.15
Nodes (51): OptimiseRequest, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., AgentLimits, propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, One allowance per request. Retries and the interpretation call spend the same… (+43 more)

### Community 18 - "FurnitureAsset"
Cohesion: 0.11
Nodes (31): Facing, FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., _access(), _Choice, _extents(), _front(), _nearby() (+23 more)

### Community 19 - "test_objective.py"
Cohesion: 0.15
Nodes (45): WindowOpening, compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, item(), FurnitureItem, parametrize (+37 more)

### Community 20 - "DraftSession"
Cohesion: 0.11
Nodes (36): _arrangement(), DraftSession, _echo(), LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one…, A fresh scene at the base revision, so its audit identifies the submitted scene. (+28 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (34): int32, Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction() (+26 more)

### Community 22 - "detect_collisions"
Cohesion: 0.07
Nodes (50): CollisionIssue, Polygon, detect_collisions(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, CollisionVolume, furniture_collision_volumes(), An item's occupied box transformed into a vertical prism in room space. (+42 more)

### Community 23 - "test_demo_cache_room.py"
Cohesion: 0.13
Nodes (33): broken_cache(), from_demo_cache(), proxy_warning(), assert_readers_agree(), _audit(), auditor(), _collides(), data_dir() (+25 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.14
Nodes (37): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), PlanAnnotations, _close(), _example(), _has_vertex() (+29 more)

### Community 25 - "test_reconstruction.py"
Cohesion: 0.07
Nodes (47): FailureKind, Mask, The retailer's own published model as the item's raw mesh. No inference and no…, The next published model that is usable and within the triangle budget. Each…, RetailerModelProvider, fal_media_url(), fetch_bounded(), Provider artifacts are fetched over HTTPS from fal's media hosts only. (+39 more)

### Community 26 - "objective.py"
Cohesion: 0.14
Nodes (22): WindowOpening, The opening's extent along its wall's interior face, in room X/Z coordinates., window_plan_segment(), _access_not_worse(), beats_original(), _check_comparable(), compare_evaluations(), _door_overlap_area() (+14 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.18
Nodes (32): BlockedDoorIssue, CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize (+24 more)

### Community 28 - "schema.ts"
Cohesion: 0.07
Nodes (35): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M (+27 more)

### Community 29 - "parse.py"
Cohesion: 0.11
Nodes (41): FloorCaption, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance(), _consensus() (+33 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.20
Nodes (27): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, item(), FurnitureItem, parametrize (+19 more)

### Community 31 - "align_debug.py"
Cohesion: 0.08
Nodes (32): MaskSource, demo_floors(), demo_room_scene(), demo_rooms(), RoomScene, The shared three-floor fixtures, one whole-floor scene per floor name., Split the shared floor fixtures by wall prefix, in the original floor…, One demo room as the editor opens it (`roomScene` in… (+24 more)

### Community 32 - "walk.ts"
Cohesion: 0.07
Nodes (35): WALK_HEADROOM_M, RotationRing(), captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera() (+27 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.08
Nodes (42): LayoutModel, ModelReply, Any, Protocol, ToolCall, ActivityAnchor, assess_feng_shui(), Assessment (+34 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "PlayLighting.tsx"
Cohesion: 0.25
Nodes (15): DoorLightBlockers(), LightingEnvironment, PlayLighting(), useEnvironmentSettings(), bounds(), inwardNormal(), ceilingLights(), DEFAULT_PLAY_LIGHTING (+7 more)

### Community 36 - "geometry.ts"
Cohesion: 0.16
Nodes (20): DoorSwings(), clampToFloor(), doorSwing(), footprint(), snapToNearestWall(), toWorld(), byId(), collisionVolumes() (+12 more)

### Community 37 - "agent.py"
Cohesion: 0.09
Nodes (22): Outcome, AnthropicLayoutModel, _Budget, _explain_result(), _explore(), _interpret(), _Interpretation, _percent() (+14 more)

### Community 38 - "routes.py"
Cohesion: 0.05
Nodes (53): File, ge, gt, HTTPException, Query, clear_corrections(), find_parsed_scene(), get_annotator() (+45 more)

### Community 39 - "selection_models.py"
Cohesion: 0.14
Nodes (26): Local SQLite transactions for scene identities and recoverable provider…, Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the…, write_report(), _diagnostic(), DiscoveredObject, MissingMask (+18 more)

### Community 40 - "FurnitureItem"
Cohesion: 0.06
Nodes (71): FurnitureItem, model_validator, floor_polygon is clockwise in plan view and every wall has the room on its…, Correction, AlignmentRecord, AlignmentResult, pose_error(), FurnitureItem (+63 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.21
Nodes (14): FileResponse, demo_shell(), furniture_model(), legacy_model(), _model_file(), get, Path, Response (+6 more)

### Community 42 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.07
Nodes (80): _declared_bounds(), _declared_bounds_problems(), _gltf_problems(), inspect_asset(), ndarray, Path, The bounds the file declares: the union of its `POSITION` accessors' min/max.…, Re-read an asset's stored file and check it against the furniture profile and… (+72 more)

### Community 45 - "scenes.py"
Cohesion: 0.07
Nodes (43): demo_cache_dir(), furniture_data_dir(), Path, Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, Where published demo furniture is read from when the pipeline has none (#20).…, health(), get (+35 more)

### Community 46 - "Sidebar.tsx"
Cohesion: 0.09
Nodes (23): AuditStats(), ChatTab(), LibraryTab(), StatsTab(), tabs, ButtonProps, Chip(), dotColor (+15 more)

### Community 47 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 48 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (20): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+12 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "SpatialInputError"
Cohesion: 0.10
Nodes (33): A window-openness proxy for layout comparison, not a lighting simulation., WindowOpenness, front_clearance_zone(), FurnitureGeometry, prepare_furniture(), prepare_scene(), FurnitureItem, RoomScene (+25 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.15
Nodes (22): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+14 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_api.py"
Cohesion: 0.09
Nodes (37): AuditReport, payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422() (+29 more)

### Community 55 - "Decisions"
Cohesion: 0.08
Nodes (24): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11), Custom requests (+16 more)

### Community 56 - "test_real_room.py"
Cohesion: 0.11
Nodes (62): Collection, _audit(), auditor(), _clear(), client(), _collides(), data_dir(), _findings() (+54 more)

### Community 57 - "check_layout_demo.py"
Cohesion: 0.25
Nodes (8): demo_room_scenes(), profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, Each demo room with the furniture standing in it, as the editor builds them., solve(), Timed

### Community 58 - "single_room"
Cohesion: 0.15
Nodes (22): bay_room(), _canvas(), l_room(), _png(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),…, L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed., 4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m… (+14 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "Vec2"
Cohesion: 0.15
Nodes (22): DoorOpening, Vec2, WallSegment, A point on the floor plan (Y omitted)., A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, LineString, door_entry_segment(), _door_frame() (+14 more)

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
Cohesion: 0.12
Nodes (17): Architecture, Backend-provided demo models, Corrections (#11), Editor play mode, Frontend audio, Furniture evidence selection (#14), Furniture masks and placement evidence (#15), Furniture normalisation (#17, PR #54 review) (+9 more)

### Community 68 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "test_room_shell.py"
Cohesion: 0.12
Nodes (39): build_shell(), Scene, The room shell as a trimesh Scene with nodes `floor`, `ceiling`, `wall_<id>`., corner_probes(), invalid_footprints(), _l_door(), make_scene(), parametrize (+31 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "retailer.py"
Cohesion: 0.14
Nodes (24): _binary_models(), _dimensions(), _first_url(), _is_type(), _metres(), _model_urls(), _nodes(), parse_product_page() (+16 more)

### Community 72 - "FixedAnnotator"
Cohesion: 0.09
Nodes (23): AnnotationResult, Compass, FalVisionAnnotator, FixedAnnotator, NullAnnotator, PlanAnnotator, BaseModel, Path (+15 more)

### Community 73 - "layout_tools.py"
Cohesion: 0.16
Nodes (17): LayoutDraft, _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, LayoutToolbox, _metrics() (+9 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.15
Nodes (13): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment, Free floor area, Front clearance, Internal layout comparison (issue #33), Layout drafts for proposed moves (issue #33) (+5 more)

### Community 76 - "RoomView.tsx"
Cohesion: 0.14
Nodes (18): floorPlane, Furniture, Mesh(), MeshBoundary, ProxyBox(), categoryWash, disposeInk(), inkify() (+10 more)

### Community 77 - "keyboard.ts"
Cohesion: 0.50
Nodes (6): editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys

### Community 78 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 79 - "test_layout_tools.py"
Cohesion: 0.19
Nodes (25): LayoutPreferences, What the user asked for, already validated by the server., evaluate(), item(), move(), Any, FurnitureItem, parametrize (+17 more)

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
Cohesion: 0.29
Nodes (6): Completion and follow-up, Consuming the findings, HTTP handoff contract, Layout suggestions (`POST /solve`), Load the same examples in the editor and backend, Spatial findings: Dev 3 / Dev 4 handoff

### Community 95 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

### Community 96 - "Registry"
Cohesion: 0.22
Nodes (7): Connection, Any, Path, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle., Registry, test_changed_mask_invalidates_mesh_and_racing_mask_is_not_attached()

### Community 97 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 98 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "calculate_free_floor_ratio"
Cohesion: 0.24
Nodes (23): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, item(), FurnitureItem, parametrize, RoomScene, Free floor area is distinct from reachable walking space., room() (+15 more)

### Community 102 - "_Page"
Cohesion: 0.29
Nodes (3): HTMLParser, _Page, The few things a product page is read for: JSON-LD, meta tags, title and…

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "check_delivery.py"
Cohesion: 0.31
Nodes (7): main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), Delivery, computed_field, Every delivered asset passed its checks. Proxies are allowed; they are listed.

### Community 124 - "audit.py"
Cohesion: 0.33
Nodes (3): _height_overlaps(), Spatial checks independent of HTTP, mesh loading and provider services., Reusable scene variants and expected findings for Dev 3/4 integration.

### Community 125 - "normalisation.py"
Cohesion: 0.12
Nodes (19): BBoxM, CollisionPart, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).…, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), NormalisedMesh, Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`., _bounds() (+11 more)

### Community 127 - "CatalogError"
Cohesion: 0.13
Nodes (19): CatalogError, _check_public(), fetch_product(), fetch_public(), Fetch, ValueError, The product cannot be imported at all. The message is safe to show., Download and read one retailer product page. Raises CatalogError. `source`… (+11 more)

### Community 128 - "furniture_footprint"
Cohesion: 0.32
Nodes (13): furniture_footprint(), Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, make_item(), FurnitureItem, parametrize, Footprint examples independent of meshes, providers and HTTP routes., test_45_degree_corners_follow_threejs_yaw(), test_does_not_mutate_item() (+5 more)

### Community 129 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 130 - "ContractModel"
Cohesion: 0.12
Nodes (25): ContractModel, BaseModel, BlockedDoorIssue, ClearanceIssue, CollisionIssue, FengShuiReport, FengShuiSightline, GlareAlert (+17 more)

### Community 131 - "openings.py"
Cohesion: 0.22
Nodes (11): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+3 more)

### Community 132 - "masked_scene"
Cohesion: 0.31
Nodes (9): CaptureFixture, test_cli_runs_the_checks_and_reports(), test_a_mesh_that_cannot_be_normalised_keeps_its_proxy_and_says_so(), masked_scene(), MeshDouble, test_invalid_meshes_fall_back(), test_pipeline_runs_items_concurrently(), test_pipeline_stores_separate_meshes_reuses_and_preserves_pose() (+1 more)

### Community 133 - "item_box"
Cohesion: 0.29
Nodes (8): _decode(), item_box(), NDArray, uint8, An upright BGR image; transparency becomes white, as in a product shot., Where the product is in its image, and whether that was read off a plain…, test_image_pixel_limit_is_checked_before_opencv_decode(), test_item_box_finds_the_product_on_a_plain_background()

### Community 134 - "guess_category"
Cohesion: 0.29
Nodes (8): guess_category(), Category, Classify the head phrase, using its last furniture or accessory noun.…, parametrize, test_categories_come_from_the_products_own_words(), test_category_uses_head_noun(), test_missing_or_unusable_dimensions_are_not_invented(), test_review_categories()

### Community 136 - "_inside"
Cohesion: 0.50
Nodes (4): _inside(), ndarray, Trimesh, Ray parity in plain numpy (Moller-Trumbore), so the probes need no SciPy or…

### Community 137 - "_along_mesh"
Cohesion: 0.67
Nodes (3): _along_mesh(), BBoxM, Published width and depth, assigned to X and Z of a shape with these extents.…

## Knowledge Gaps
- **405 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+400 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `shell.py`, `ContractModel`, `test_demo_assets.py`, `test_room_align_vision.py`, `test_scene_routes.py`, `observe_vision.py`, `test_room_align.py`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `Pose2D`, `FurnitureAsset`, `test_objective.py`, `DraftSession`, `detect_collisions`, `test_demo_cache_room.py`, `test_room_parse.py`, `objective.py`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `align_debug.py`, `spatial_engine/main.py`, `routes.py`, `FurnitureItem`, `demo_assets.py`, `detect_front_clearance`, `scenes.py`, `detect_out_of_bounds`, `generate_mock_glbs.py`, `SpatialInputError`, `test_api.py`, `test_real_room.py`, `check_layout_demo.py`, `single_room`, `Vec2`, `test_room_shell.py`, `layout_tools.py`, `test_layout_tools.py`, `calculate_free_floor_ratio`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `ContractModel`, `test_room_align_vision.py`, `masked_scene`, `test_scene_routes.py`, `catalog.py`, `observe_vision.py`, `test_room_align.py`, `test_delivery.py`, `BBoxM`, `Pose2D`, `detect_collisions`, `test_reconstruction.py`, `detect_blocked_doors`, `align_debug.py`, `selection_models.py`, `FurnitureItem`, `test_demo_cache.py`, `scenes.py`, `test_contract_occupancy.py`, `.to_item`, `check_delivery.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_catalog.py`, `furniture_footprint`, `ContractModel`, `masked_scene`, `catalog.py`, `footprint.py`, `_along_mesh`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `Pose2D`, `FurnitureAsset`, `test_objective.py`, `DraftSession`, `detect_collisions`, `test_reconstruction.py`, `detect_blocked_doors`, `calculate_brightness_approximation`, `detect_front_clearance`, `detect_out_of_bounds`, `Vec2`, `retailer.py`, `test_layout_tools.py`, `calculate_free_floor_ratio`, `normalisation.py`, `CatalogError`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 188 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 188 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 71 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Registry` (e.g. with `RetailerModelProvider` and `FalSamProvider`) actually correct?**
  _`Registry` has 13 INFERRED edges - model-reasoned connections that need verification._