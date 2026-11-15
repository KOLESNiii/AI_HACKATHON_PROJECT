# Graph Report - AI_HACKATHON_PROJECT_1  (2026-11-15)

## Corpus Check
- 215 files · ~324,651 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3232 nodes · 9406 edges · 124 communities (111 shown, 13 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1120 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a34e021e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- test_room_shell.py
- test_room_align_vision.py
- RoomScene
- test_scene_routes.py
- audio.test.ts
- catalog.py
- footprint.py
- test_segmentation.py
- FurnitureAsset
- test_room_align.py
- calculate_reachable_floor_ratio
- test_delivery.py
- Box
- test_normalisation.py
- test_selection.py
- useStore
- test_agent.py
- FurnitureItem
- Pose2D
- DraftSession
- regions.py
- detect_collisions
- test_room_correct.py
- test_room_parse.py
- test_reconstruction.py
- layout_tools.py
- detect_blocked_doors
- schema.ts
- parse.py
- calculate_brightness_approximation
- scenes.py
- walk.ts
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- geometry.ts
- spatialPreview.ts
- SpatialInputError
- routes.py
- LayoutToolbox
- detect_front_clearance
- demo_assets.py
- Vec2
- compilerOptions
- test_chat.py
- Frame
- Sidebar.tsx
- detect_out_of_bounds
- FloorPlanScreen.tsx
- generate_mock_glbs.py
- report.py
- test_contract_occupancy.py
- objective.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_api.py
- Decisions
- calculate_free_floor_ratio
- audit_scene
- CollisionPart
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
- Registry
- test_fixture_scene.py
- furniture_footprint
- Implementation plan: issue #14
- Spatial engine
- brightness.py
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
- .to_item
- DiscoveredObject
- README.md
- frontend/package.json
- LayoutMetrics
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift
- retailer.py
- agent.py
- test_demo_assets.py
- vite
- BBoxM

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 207 edges
2. `FurnitureAsset` - 80 edges
3. `BBoxM` - 79 edges
4. `Pose2D` - 67 edges
5. `FurnitureItem` - 67 edges
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
- `test_evidence_matches_the_agreed_shape()` --uses--> `AssetEvidence`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `test_dev1_consumes_fixtures_through_the_asset_interface()` --uses--> `FurnitureAsset`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py

## Import Cycles
- None detected.

## Communities (124 total, 13 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.07
Nodes (69): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., main() (+61 more)

### Community 1 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 2 - "test_room_align_vision.py"
Cohesion: 0.08
Nodes (48): EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., SelectionResult, directory_frames(), FrameSource, Path, Frames of one video stored as `<frame_index>.jpg` or `.png` (upright, as…, The upright frames Dev 2's pipeline stored, for evidence made by… (+40 more)

### Community 3 - "RoomScene"
Cohesion: 0.06
Nodes (96): Collection, RoomScene, model_validator, floor_polygon is clockwise in plan view and every wall has the room on its…, NoFurniture, The room alone: what parsed rooms get until #16 produces furniture assets., default_bindings(), geometry_mismatch() (+88 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.14
Nodes (36): What a furniture source supplies for one room., SceneFurniture, conform_openings(), RoomScene, Put every door exactly on its wall, so the spatial audit accepts the room. Each…, _audit(), auditor(), _door() (+28 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (23): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+15 more)

### Community 6 - "catalog.py"
Cohesion: 0.07
Nodes (43): Readers never see a partial file., write_atomic(), CatalogImport, _decode(), ImageProvenance, import_product(), imported_assets(), item_box() (+35 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (61): DoorOpening, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by() (+53 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.13
Nodes (55): Rect, Store a mask and cut-out for every selected view of the scene's (or the named)…, Resolve an `EvidenceFrame.mask_url` (relative to the asset data directory)., read_mask(), segment_furniture(), test_view_choice_prefers_confident_whole_views(), box_mask(), FakeProvider (+47 more)

### Community 9 - "FurnitureAsset"
Cohesion: 0.05
Nodes (64): Image, MaskSource, FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., _Capture, main(), pose_error(), FrameSource (+56 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (57): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+49 more)

### Community 11 - "calculate_reachable_floor_ratio"
Cohesion: 0.17
Nodes (29): calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, divided_room(), obstacle(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.08
Nodes (65): APIRouter, asset_router(), Path, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset(), main() (+57 more)

### Community 13 - "Box"
Cohesion: 0.07
Nodes (48): ArtifactTooLarge, box_pixels(), fal_media_url(), FalSamProvider, _fetch(), fetch_bounded(), GrabCutProvider, MaskError (+40 more)

### Community 14 - "test_normalisation.py"
Cohesion: 0.12
Nodes (50): Front, NormalisedMesh, Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`., _bounds(), _cap_textures(), _load(), NormalisationError, normalise_mesh() (+42 more)

### Community 15 - "test_selection.py"
Cohesion: 0.13
Nodes (47): FalVisionProvider, Reviewed detections keyed by full source frame keys, never by batch position., RecordedProvider, main(), Path, Local #14 CLI. Defaults to offline sampling; --live explicitly permits provider…, Full-resolution source artifacts stay separate; the report shows boxes and IDs., write_report() (+39 more)

### Community 16 - "useStore"
Cohesion: 0.10
Nodes (30): App(), ORDER, screenVariants, EditorScreen(), floorPlane, flaggedFor(), Navigation(), RoomView() (+22 more)

### Community 17 - "test_agent.py"
Cohesion: 0.15
Nodes (49): OptimiseRequest, AgentLimits, propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, One allowance per request. Retries and the interpretation call spend the same…, Step, interpret() (+41 more)

### Community 18 - "FurnitureItem"
Cohesion: 0.09
Nodes (39): FurnitureItem, Correction, Facing, _access(), AlignmentResult, _Choice, _extents(), _front() (+31 more)

### Community 19 - "Pose2D"
Cohesion: 0.14
Nodes (48): Pose2D, WindowOpening, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, item() (+40 more)

### Community 20 - "DraftSession"
Cohesion: 0.11
Nodes (36): _arrangement(), DraftSession, _echo(), LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one…, A fresh scene at the base revision, so its audit identifies the submitted scene. (+28 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (34): int32, Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction() (+26 more)

### Community 22 - "detect_collisions"
Cohesion: 0.13
Nodes (26): CollisionIssue, detect_collisions(), _height_overlaps(), FurnitureItem, Spatial checks independent of HTTP, mesh loading and provider services., Report each overlapping pair once, in stable item-ID order. Whole bounding…, item(), FurnitureItem (+18 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.08
Nodes (53): apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, InvalidScale, _perimeter(), _point() (+45 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.08
Nodes (62): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), FixedAnnotator, PlanAnnotations, Path, Returns pre-recorded annotations (tests, the debug CLI, cached demo plans). (+54 more)

### Community 25 - "test_reconstruction.py"
Cohesion: 0.06
Nodes (67): FailureKind, FalSam3dProvider, _fetch(), inspect_mesh(), MeshError, MeshProvider, Any, Exception (+59 more)

### Community 26 - "layout_tools.py"
Cohesion: 0.16
Nodes (15): LayoutDraft, _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, _metrics(), _Move (+7 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.18
Nodes (32): BlockedDoorIssue, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, door_swing_sector(), Conservative zero-thickness door sweep, using stored opening conventions.…, item(), FurnitureItem, parametrize (+24 more)

### Community 28 - "schema.ts"
Cohesion: 0.07
Nodes (34): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M (+26 more)

### Community 29 - "parse.py"
Cohesion: 0.12
Nodes (37): FloorCaption, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance(), _consensus() (+29 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.22
Nodes (25): calculate_brightness_approximation(), RoomScene, Project nearby occupied parts onto each window and union their shadows. The…, item(), FurnitureItem, parametrize, RoomScene, Analytic window-area cases for a declared geometric brightness proxy. (+17 more)

### Community 31 - "scenes.py"
Cohesion: 0.07
Nodes (44): ge, HTTPException, Query, furniture_data_dir(), Path, Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, health() (+36 more)

### Community 32 - "walk.ts"
Cohesion: 0.08
Nodes (31): WALK_HEADROOM_M, captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera(), restoreEditorView() (+23 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.08
Nodes (34): le, AnthropicLayoutModel, LayoutModel, Any, Protocol, Claude through the official SDK. The loop above owns retries, so the SDK makes…, ChatReply, audit() (+26 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "geometry.ts"
Cohesion: 0.16
Nodes (23): Furniture, RotationRing(), DoorLightBlockers(), LightingEnvironment, PlayLighting(), useEnvironmentSettings(), bounds(), clampToFloor() (+15 more)

### Community 36 - "spatialPreview.ts"
Cohesion: 0.20
Nodes (19): DoorSwings(), doorSwing(), footprint(), Pt, toWorld(), byId(), collisionVolumes(), convexOverlapArea() (+11 more)

### Community 37 - "SpatialInputError"
Cohesion: 0.12
Nodes (30): ActivityAnchor, assess_feng_shui(), Assessment, DetailModel, FengShuiRequest, FengShuiResult, Finding, Mirror (+22 more)

### Community 38 - "routes.py"
Cohesion: 0.05
Nodes (47): File, AnnotationResult, Compass, FalVisionAnnotator, NullAnnotator, PlanAnnotator, BaseModel, Protocol (+39 more)

### Community 39 - "LayoutToolbox"
Cohesion: 0.18
Nodes (27): LayoutPreferences, LayoutToolbox, What the user asked for, already validated by the server., The three exploration tools for one request, over one `DraftSession`. `call`…, evaluate(), item(), move(), Any (+19 more)

### Community 40 - "detect_front_clearance"
Cohesion: 0.18
Nodes (32): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+24 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.11
Nodes (28): FileResponse, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file() (+20 more)

### Community 42 - "Vec2"
Cohesion: 0.10
Nodes (29): ContractModel, BaseModel, BlockedDoorIssue, ClearanceIssue, CollisionIssue, FengShuiReport, FengShuiSightline, GlareAlert (+21 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_chat.py"
Cohesion: 0.11
Nodes (44): ModelReply, ToolCall, add_item(), chat(), ChatRequest, RoomScene, Validated tool handler. A rejected addition never mutates the caller's scene., proxy_glb() (+36 more)

### Community 45 - "Frame"
Cohesion: 0.13
Nodes (29): DiscoveryError, DiscoveryProvider, OfflineProvider, parse_discovery(), Exception, Path, Protocol, fal vision proposes instances across full images; reviewed recordings run… (+21 more)

### Community 46 - "Sidebar.tsx"
Cohesion: 0.08
Nodes (32): LayoutGoal, AuditStats(), ChatTab(), LibraryTab(), StatsTab(), tabs, ButtonProps, Chip() (+24 more)

### Community 47 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 48 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (20): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+12 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "report.py"
Cohesion: 0.18
Nodes (17): FengShuiReport, _angle_deg(), calculate_feng_shui(), _front(), _occupant(), FurnitureItem, RoomScene, A small, transparent Feng Shui placement metric from the command-position… (+9 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 52 - "objective.py"
Cohesion: 0.13
Nodes (23): LineString, WindowOpening, The opening's extent along its wall's interior face, in room X/Z coordinates., window_plan_segment(), _access_not_worse(), beats_original(), _check_comparable(), compare_evaluations() (+15 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_api.py"
Cohesion: 0.09
Nodes (37): AuditReport, payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422() (+29 more)

### Community 55 - "Decisions"
Cohesion: 0.08
Nodes (25): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+17 more)

### Community 56 - "calculate_free_floor_ratio"
Cohesion: 0.24
Nodes (23): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, item(), FurnitureItem, parametrize, RoomScene, Free floor area is distinct from reachable walking space., room() (+15 more)

### Community 57 - "audit_scene"
Cohesion: 0.22
Nodes (23): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+15 more)

### Community 58 - "CollisionPart"
Cohesion: 0.18
Nodes (22): CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, CollisionVolume, furniture_collision_volumes(), An item's occupied box transformed into a vertical prism in room space., Transform validated local collision boxes; absent parts mean one solid bbox.…, item(), part() (+14 more)

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
Cohesion: 0.11
Nodes (18): Architecture, Backend-provided demo models, Chat additions and application, Corrections (#11), Editor play mode, Frontend audio, Furniture evidence selection (#14), Furniture masks and placement evidence (#15) (+10 more)

### Community 68 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "ProviderError"
Cohesion: 0.13
Nodes (17): demo_room_scenes(), profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, Each demo room with the furniture standing in it, as the editor builds them., solve(), Timed (+9 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "Registry"
Cohesion: 0.18
Nodes (8): Connection, Any, Path, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle., Registry, NDArray, uint8

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "furniture_footprint"
Cohesion: 0.20
Nodes (19): Polygon, front_clearance_zone(), furniture_footprint(), FurnitureGeometry, prepare_furniture(), FurnitureItem, Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, Full-width rectangle from the bbox front, rotated/placed in room X/Z. Zero… (+11 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.13
Nodes (15): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Free floor area, Front clearance, Internal layout comparison (issue #33) (+7 more)

### Community 76 - "brightness.py"
Cohesion: 0.20
Nodes (10): BrightnessApproximation, A window-openness proxy for layout comparison, not a lighting simulation., Ratios describe geometric openness, never percentage brightness or lux., WindowOpenness, parametrize, RoomScene, Reconstructed scenes round coordinates; openings a fraction of a millimetre off…, room() (+2 more)

### Community 77 - "store.ts"
Cohesion: 0.13
Nodes (19): playCue(), useAudioPreferences, editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys (+11 more)

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
Cohesion: 0.29
Nodes (7): Completion and follow-up, Consuming the findings, Editor integration status (issues #32 and #35), HTTP handoff contract, Layout suggestions (`POST /solve`), Load the same examples in the editor and backend, Spatial findings: Dev 3 / Dev 4 handoff

### Community 95 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

### Community 97 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 98 - "DiscoveredObject"
Cohesion: 0.22
Nodes (3): _diagnostic(), DiscoveredObject, model_validator

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 123 - "retailer.py"
Cohesion: 0.10
Nodes (28): HTMLParser, _binary_models(), _dimensions(), _first_url(), _is_type(), _metres(), _model_urls(), _nodes() (+20 more)

### Community 124 - "agent.py"
Cohesion: 0.09
Nodes (21): Outcome, _Budget, _explain_result(), _explore(), _interpret(), _Interpretation, _percent(), BaseModel (+13 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 128 - "BBoxM"
Cohesion: 0.10
Nodes (30): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, _along_mesh(), BBoxM, Published width and depth, assigned to X and Z of a shape with these extents.…, BBoxM, CollisionPart, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).… (+22 more)

## Knowledge Gaps
- **391 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+386 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `test_room_shell.py`, `test_room_align_vision.py`, `test_scene_routes.py`, `FurnitureAsset`, `test_room_align.py`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `test_agent.py`, `FurnitureItem`, `Pose2D`, `DraftSession`, `detect_collisions`, `test_room_correct.py`, `test_room_parse.py`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `scenes.py`, `spatial_engine/main.py`, `SpatialInputError`, `routes.py`, `LayoutToolbox`, `detect_front_clearance`, `demo_assets.py`, `Vec2`, `test_chat.py`, `detect_out_of_bounds`, `generate_mock_glbs.py`, `report.py`, `objective.py`, `test_api.py`, `calculate_free_floor_ratio`, `audit_scene`, `CollisionPart`, `ProviderError`, `brightness.py`, `test_demo_assets.py`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `BBoxM`, `.to_item`, `test_room_align_vision.py`, `test_scene_routes.py`, `catalog.py`, `test_fixture_scene.py`, `demo_assets.py`, `Vec2`, `test_room_align.py`, `test_delivery.py`, `test_normalisation.py`, `FurnitureItem`, `Pose2D`, `test_contract_occupancy.py`, `test_reconstruction.py`, `CollisionPart`, `scenes.py`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_catalog.py`, `catalog.py`, `footprint.py`, `FurnitureAsset`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `test_normalisation.py`, `test_agent.py`, `FurnitureItem`, `Pose2D`, `DraftSession`, `detect_collisions`, `test_reconstruction.py`, `detect_blocked_doors`, `calculate_brightness_approximation`, `LayoutToolbox`, `detect_front_clearance`, `Vec2`, `test_chat.py`, `detect_out_of_bounds`, `calculate_free_floor_ratio`, `audit_scene`, `CollisionPart`, `furniture_footprint`, `retailer.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 204 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 204 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 64 inferred relationships involving `Pose2D` (e.g. with `FurnitureAsset` and `_access()`) actually correct?**
  _`Pose2D` has 64 INFERRED edges - model-reasoned connections that need verification._