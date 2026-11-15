# Graph Report - AI_HACKATHON_PROJECT_1  (2026-11-15)

## Corpus Check
- 204 files · ~300,695 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2884 nodes · 8199 edges · 122 communities (108 shown, 14 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 952 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c1b81a55`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DraftSession
- detect_blocked_doors
- test_room_shell.py
- test_segmentation.py
- FurnitureAsset
- test_room_align.py
- footprint.py
- test_selection.py
- Sidebar.tsx
- calculate_free_floor_ratio
- audio.test.ts
- test_reconstruction.py
- test_objective.py
- RoomScene
- test_room_parse.py
- ContractModel
- align.py
- regions.py
- parse.py
- detect_collisions
- KnownDimensions
- Registry
- test_real_room.py
- scenes.py
- layout_tools.py
- schema.ts
- useStore
- SpaceShift 3D representation and asset handoff — design
- test_fixture_scene.py
- Frame
- Pose2D
- routes.py
- detect_front_clearance
- SpatialInputError
- walk.ts
- spatial_engine/main.py
- compilerOptions
- calculate_brightness_approximation
- BBoxM
- generate_mock_glbs.py
- observe_vision.py
- App.tsx
- test_contract_occupancy.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_room_align_vision.py
- shell.py
- compilerOptions
- agent.py
- Furniture.tsx
- Video frame selection and furniture identity — issue #14
- dependencies
- devDependencies
- raster.py
- polygon.py
- RoomView.tsx
- Dev 4 implementation and integration plan
- Dev 2 → Dev 1 asset handoff
- Agent Instructions
- Decisions
- make_item
- test_delivery.py
- ProviderError
- Implementation plan: issue #14
- Architecture
- react
- scripts
- attach
- test_demo_assets.py
- SpaceShift — System Architecture & 4-Developer Execution DAG
- Spatial findings: Dev 3 / Dev 4 handoff
- test_chat.py
- test_layout_tools.py
- Spatial engine
- audit_scene
- Asset Handoff Agreement Implementation Plan
- Review Focus
- Review Focus
- Furniture masks and placement evidence — issue #15
- invalid_request
- plugins
- generate-landscapes.ts
- detect_out_of_bounds
- Floor-plan parser (Dev 1)
- Individual furniture meshes with proxy fallback — issue #16
- scripts
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- Furniture mesh normalisation — issue #17
- .to_item
- furniture_proxy
- Vec2
- PlayLighting.tsx
- frontend/package.json
- ._check_winding
- health
- SelectedObject
- segmentation.py
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- vite
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- spaceshift
- RequestBudget
- check_delivery.py
- reconstruction/main.py
- Furniture asset delivery and checks (#18, Dev 2.6)
- test_rounded_coordinates.py
- README.md
- test_shared_handoff_case
- LayoutMetrics
- tests/conftest.py

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 164 edges
2. `FurnitureAsset` - 77 edges
3. `Registry` - 63 edges
4. `BBoxM` - 61 edges
5. `Pose2D` - 59 edges
6. `SpatialInputError` - 57 edges
7. `FurnitureItem` - 56 edges
8. `useStore` - 56 edges
9. `reconstruct_furniture()` - 55 edges
10. `propose_layout()` - 53 edges

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

## Communities (122 total, 14 thin omitted)

### Community 0 - "DraftSession"
Cohesion: 0.11
Nodes (37): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+29 more)

### Community 1 - "detect_blocked_doors"
Cohesion: 0.18
Nodes (33): BlockedDoorIssue, BlockedDoorIssue, CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem (+25 more)

### Community 2 - "test_room_shell.py"
Cohesion: 0.10
Nodes (46): build_shell(), Scene, The room shell as a trimesh Scene with nodes `floor`, `ceiling`, `wall_<id>`., shell_glb(), corner_probes(), _inside(), invalid_footprints(), _l_door() (+38 more)

### Community 3 - "test_segmentation.py"
Cohesion: 0.12
Nodes (58): Rect, MaskError, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, main(), Store a mask and cut-out for every selected view of the scene's (or the named)…, segment_furniture(), box_mask(), FakeProvider (+50 more)

### Community 4 - "FurnitureAsset"
Cohesion: 0.09
Nodes (34): FurnitureAsset, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence…, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., AlignmentRecord, _Capture, main(), pose_error(), FrameSource (+26 more)

### Community 5 - "test_room_align.py"
Cohesion: 0.12
Nodes (58): FurnitureItem, align_assets(), AlignmentResult, FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction. (+50 more)

### Community 6 - "footprint.py"
Cohesion: 0.06
Nodes (61): DoorOpening, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by() (+53 more)

### Community 7 - "test_selection.py"
Cohesion: 0.09
Nodes (70): DiscoveryProvider, FalVisionProvider, OfflineProvider, Protocol, fal vision proposes instances across full images; reviewed recordings run…, Reviewed detections keyed by full source frame keys, never by batch position., RecordedProvider, main() (+62 more)

### Community 8 - "Sidebar.tsx"
Cohesion: 0.10
Nodes (18): ChatTab(), LibraryTab(), StatsTab(), tabs, ButtonProps, Chip(), dotColor, Panel() (+10 more)

### Community 9 - "calculate_free_floor_ratio"
Cohesion: 0.10
Nodes (52): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, item(), FurnitureItem, parametrize (+44 more)

### Community 10 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 11 - "test_reconstruction.py"
Cohesion: 0.09
Nodes (47): FailureKind, FalSam3dProvider, inspect_mesh(), MeshError, Any, Exception, Mask, NDArray (+39 more)

### Community 12 - "test_objective.py"
Cohesion: 0.16
Nodes (43): WindowOpening, compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, item(), FurnitureItem, RoomScene (+35 more)

### Community 13 - "RoomScene"
Cohesion: 0.11
Nodes (45): RoomScene, assemble_scene(), FurnitureSource, NoFurniture, Protocol, RoomScene, What a furniture source supplies for one room., The room alone: what parsed rooms get until #16 produces furniture assets. (+37 more)

### Community 14 - "test_room_parse.py"
Cohesion: 0.08
Nodes (62): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), FixedAnnotator, PlanAnnotations, Path, Returns pre-recorded annotations (tests, the debug CLI, cached demo plans). (+54 more)

### Community 15 - "ContractModel"
Cohesion: 0.06
Nodes (56): ContractModel, BaseModel, AuditReport, ClearanceIssue, CollisionIssue, FengShuiReport, FengShuiSightline, GlareAlert (+48 more)

### Community 16 - "align.py"
Cohesion: 0.09
Nodes (36): Correction, Facing, _access(), _Choice, _extents(), _front(), _nearby(), _no_frames() (+28 more)

### Community 17 - "regions.py"
Cohesion: 0.12
Nodes (34): int32, Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction() (+26 more)

### Community 18 - "parse.py"
Cohesion: 0.11
Nodes (42): FloorCaption, BaseModel, RoomLabel, kind(), _assign_labels(), _bearing(), _bridge_sides(), _build_scene() (+34 more)

### Community 19 - "detect_collisions"
Cohesion: 0.12
Nodes (37): CollisionIssue, detect_collisions(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, item(), part(), CollisionPart (+29 more)

### Community 20 - "KnownDimensions"
Cohesion: 0.06
Nodes (44): APIRouter, Category, asset_router(), Path, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`. (+36 more)

### Community 21 - "Registry"
Cohesion: 0.10
Nodes (23): Connection, box_pixels(), FalSamProvider, GrabCutProvider, MaskProvider, Any, NDArray, Protocol (+15 more)

### Community 22 - "test_real_room.py"
Cohesion: 0.09
Nodes (53): Collection, geometry_mismatch(), geometry_warning(), load_bindings(), proxy_warning(), BaseModel, Path, RoomScene (+45 more)

### Community 23 - "scenes.py"
Cohesion: 0.07
Nodes (40): FileResponse, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file() (+32 more)

### Community 24 - "layout_tools.py"
Cohesion: 0.11
Nodes (29): _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, LayoutToolbox, _metrics(), _Move (+21 more)

### Community 25 - "schema.ts"
Cohesion: 0.07
Nodes (33): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_PART_DIMENSION_M (+25 more)

### Community 26 - "useStore"
Cohesion: 0.10
Nodes (32): playCue(), EditorScreen(), floorPlane, Furniture, RotationRing(), SelectionTools(), Sidebar(), HomeScreen() (+24 more)

### Community 27 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 28 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 29 - "Frame"
Cohesion: 0.09
Nodes (33): ArtifactTooLarge, fal_media_url(), _fetch(), fetch_bounded(), Exception, Instance masks from item boxes (#15): local GrabCut offline, fal SAM 3 when…, A provider artifact exceeded its size cap; nothing was kept., Provider artifacts are fetched over HTTPS from fal's media hosts only. (+25 more)

### Community 30 - "Pose2D"
Cohesion: 0.16
Nodes (47): OptimiseRequest, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, Step, interpret() (+39 more)

### Community 31 - "routes.py"
Cohesion: 0.06
Nodes (41): description, File, ParsedFloor, AnnotationResult, Compass, FalVisionAnnotator, NullAnnotator, PlanAnnotator (+33 more)

### Community 32 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 33 - "SpatialInputError"
Cohesion: 0.10
Nodes (40): Polygon, Spatial checks independent of HTTP, mesh loading and provider services., A window-openness proxy for layout comparison, not a lighting simulation., CollisionVolume, front_clearance_zone(), furniture_collision_volumes(), furniture_footprint(), FurnitureGeometry (+32 more)

### Community 34 - "walk.ts"
Cohesion: 0.07
Nodes (33): WALK_HEADROOM_M, AuditStats(), captureEditorView(), EditorOrbit, EditorView, floor, PlayControllerHandle, pointOnFloor() (+25 more)

### Community 35 - "spatial_engine/main.py"
Cohesion: 0.12
Nodes (29): LayoutProposal, Proposed furniture poses. Only poses change: shell, openings, item IDs and…, ActivityAnchor, assess_feng_shui(), Assessment, DetailModel, FengShuiRequest, FengShuiResult (+21 more)

### Community 36 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 37 - "calculate_brightness_approximation"
Cohesion: 0.18
Nodes (28): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item(), FurnitureItem (+20 more)

### Community 38 - "BBoxM"
Cohesion: 0.14
Nodes (45): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, NormalisedMesh, Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`., _load(), NormalisationError, normalise_mesh() (+37 more)

### Community 39 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 40 - "observe_vision.py"
Cohesion: 0.07
Nodes (38): Image, MaskSource, build_prompt(), _distance_to_wall(), _draw_marks(), _encode(), _facing(), FalVisionObserver (+30 more)

### Community 41 - "App.tsx"
Cohesion: 0.09
Nodes (30): App(), ORDER, screenVariants, FloorPlanScreen(), Openings(), PlanRoom(), plural(), points() (+22 more)

### Community 42 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 43 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 44 - "test_room_align_vision.py"
Cohesion: 0.09
Nodes (45): EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., directory_frames(), FrameSource, Path, Frames of one video stored as `<frame_index>.jpg` or `.png` (upright, as…, The upright frames Dev 2's pipeline stored, for evidence made by…, selection_frames() (+37 more)

### Community 45 - "shell.py"
Cohesion: 0.10
Nodes (38): int64, _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key(), _miter() (+30 more)

### Community 46 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 47 - "agent.py"
Cohesion: 0.11
Nodes (20): Outcome, _Budget, _explain_result(), _explore(), _interpret(), _Interpretation, LayoutModel, ModelReply (+12 more)

### Community 48 - "Furniture.tsx"
Cohesion: 0.26
Nodes (10): Mesh(), MeshBoundary, ProxyBox(), categoryWash, disposeInk(), inkify(), inkLine, Shell (+2 more)

### Community 49 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 50 - "dependencies"
Cohesion: 0.12
Nodes (17): framer-motion, dependencies, framer-motion, react, react-dom, @react-three/fiber, tailwindcss, @tailwindcss/vite (+9 more)

### Community 51 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, oxlint, prettier, @types/node, @types/react, @types/react-dom, @types/three, typescript (+9 more)

### Community 52 - "raster.py"
Cohesion: 0.17
Nodes (16): Gray, decode(), estimate_wall_px(), flatten_illumination(), Mask, NDArray, uint8, ValueError (+8 more)

### Community 53 - "polygon.py"
Cohesion: 0.22
Nodes (16): area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), float64, Mask, NDArray (+8 more)

### Community 54 - "RoomView.tsx"
Cohesion: 0.13
Nodes (27): MIN_HEIGHT_OVERLAP_M, MIN_PLAN_OVERLAP_M2, DoorSwings(), flaggedFor(), Navigation(), RoomView(), doorSwing(), fitsRoom() (+19 more)

### Community 55 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 56 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.12
Nodes (17): 10. Room inputs (#5), 1. IDs, 2. What Dev 2 returns, 3. Evidence, 4. Mesh references, 5. Normalisation guarantee, 6. Occupied volume, 7. Dimension provenance (+9 more)

### Community 57 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 58 - "Decisions"
Cohesion: 0.09
Nodes (22): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Custom requests (+14 more)

### Community 59 - "make_item"
Cohesion: 0.30
Nodes (11): make_item(), FurnitureItem, parametrize, Footprint examples independent of meshes, providers and HTTP routes., test_45_degree_corners_follow_threejs_yaw(), test_does_not_mutate_item(), test_front_edge_rotates_toward_positive_x(), test_rejects_invalid_dimensions() (+3 more)

### Community 60 - "test_delivery.py"
Cohesion: 0.14
Nodes (42): check_placed(), deliver_furniture(), inspect_asset(), Path, RoomScene, Re-read an asset's stored file and check it against the furniture profile and…, A scene's furniture for Dev 1 to place: per item, its checked mesh or its…, Faults in how a scene carries delivered assets; empty when every asset appears… (+34 more)

### Community 61 - "ProviderError"
Cohesion: 0.17
Nodes (11): AgentLimits, ProviderError, Exception, One allowance per request. Retries and the interpretation call spend the same…, A failed model call. `kind` is safe to log; no key or payload is kept., Request, Response, sdk_model() (+3 more)

### Community 62 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 63 - "Architecture"
Cohesion: 0.12
Nodes (17): Architecture, Backend-provided demo models, Chat additions and application, Editor play mode, Frontend audio, Furniture evidence selection (#14), Furniture masks and placement evidence (#15), Furniture normalisation (#17, PR #54 review) (+9 more)

### Community 64 - "react"
Cohesion: 0.25
Nodes (8): editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, initial, react

### Community 65 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 66 - "attach"
Cohesion: 0.25
Nodes (9): attach(), door_leaf(), EdgeHit, _ink_along(), Leaf, Mask, Point, Score the four hinge × swing-side hypotheses by ink along the open leaf (any… (+1 more)

### Community 67 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 68 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 69 - "Spatial findings: Dev 3 / Dev 4 handoff"
Cohesion: 0.29
Nodes (6): Completion and follow-up, Consuming the findings, HTTP handoff contract, Layout suggestions (`POST /solve`), Load the same examples in the editor and backend, Spatial findings: Dev 3 / Dev 4 handoff

### Community 70 - "test_chat.py"
Cohesion: 0.14
Nodes (26): add_item(), AddItemArguments, chat(), ChatReply, ChatRequest, BaseModel, RoomScene, Room chat with audited additions; existing pose-only solve contracts stay… (+18 more)

### Community 71 - "test_layout_tools.py"
Cohesion: 0.19
Nodes (25): LayoutPreferences, What the user asked for, already validated by the server., evaluate(), item(), move(), Any, FurnitureItem, parametrize (+17 more)

### Community 72 - "Spatial engine"
Cohesion: 0.14
Nodes (14): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment, Free floor area, Front clearance, Internal layout comparison (issue #33), Layout drafts for proposed moves (issue #33) (+6 more)

### Community 73 - "audit_scene"
Cohesion: 0.11
Nodes (21): demo_room_scenes(), profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, Each demo room with the furniture standing in it, as the editor builds them., solve(), Timed (+13 more)

### Community 74 - "Asset Handoff Agreement Implementation Plan"
Cohesion: 0.20
Nodes (9): Asset Handoff Agreement Implementation Plan, Deferred, each under its own issue, Execution notes (2026-11-14), File Structure, Global Constraints, Review Focus, Task 1: Contract additions, Task 2: One fixture scene (+1 more)

### Community 75 - "Review Focus"
Cohesion: 0.20
Nodes (9): Completed verification, Furniture Mesh Reconstruction Implementation Plan, Global Constraints, Review Focus, Task 1: Mesh records, Task 2: Proxy assets and the asset store, Task 3: Pipeline with a test provider, Task 4: Live SAM 3D provider (+1 more)

### Community 76 - "Review Focus"
Cohesion: 0.20
Nodes (9): Execution record, Furniture Segmentation Implementation Plan, Global Constraints, Review Focus, Task 1: Mask records, Task 2: Pipeline with the offline provider, Task 3: Evidence handoff, Task 4: Live SAM 3 provider (+1 more)

### Community 77 - "Furniture masks and placement evidence — issue #15"
Cohesion: 0.22
Nodes (8): Approaches, Design, Furniture masks and placement evidence — issue #15, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 20 requests), Live result (2026-11-14), Needs coordination

### Community 78 - "invalid_request"
Cohesion: 0.28
Nodes (9): exception_handler, JSONResponse, RequestValidationError, invalid_request(), Exception, Request, Programming errors remain 500s; return structured output without leaking…, Keep standard actionable error keys without echoing input or non-JSON values. (+1 more)

### Community 79 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 80 - "generate-landscapes.ts"
Cohesion: 0.22
Nodes (7): file, outDir, page, root, SEEDS, tmp, vendor

### Community 81 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 82 - "Floor-plan parser (Dev 1)"
Cohesion: 0.22
Nodes (7): Floor-plan parser (Dev 1), Furniture alignment (#8), How it works, Real-input room (#10), Scene assembly (#9), Status and limits, Use

### Community 83 - "Individual furniture meshes with proxy fallback — issue #16"
Cohesion: 0.25
Nodes (7): Approaches, Design, Individual furniture meshes with proxy fallback — issue #16, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 15 requests for this issue), Needs coordination

### Community 84 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, format, format:check, lint, preview, typecheck

### Community 85 - "SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin"
Cohesion: 0.25
Nodes (8): 1. The Core Differentiator (Why We Beat Existing Tools), 2. What We Stole (And Improved) From Competitors, 3. Full Tech Stack, 4. Quickstart (Local Development), **AI & Generative Media (`services/reconstruction` & `services/media_gen`)**, **Design & Frontend (`frontend/`)**, SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin, **Spatial Audit & Solver Engine (`services/spatial_engine`)**

### Community 86 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

### Community 87 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 88 - "furniture_proxy"
Cohesion: 0.25
Nodes (8): gt, le, furniture_proxy(), health(), get, Path, Response, Process liveness only; does not probe external providers.

### Community 90 - "Vec2"
Cohesion: 0.15
Nodes (21): Vec2, WallSegment, A point on the floor plan (Y omitted)., LineString, door_entry_segment(), _door_frame(), door_swing_sector(), _DoorFrame (+13 more)

### Community 91 - "PlayLighting.tsx"
Cohesion: 0.22
Nodes (16): LightingPanel(), DoorLightBlockers(), LightingEnvironment, PlayLighting(), useEnvironmentSettings(), bounds(), inwardNormal(), ceilingLights() (+8 more)

### Community 92 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 94 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 95 - "SelectedObject"
Cohesion: 0.14
Nodes (14): AssetEvidence, evidence_for(), model_validator, The stored mask for a sighting, unless its box has changed since., The stored raw mesh, unless the mask it was made from has been replaced since., SelectedObject, Sighting, overlap() (+6 more)

### Community 96 - "segmentation.py"
Cohesion: 0.17
Nodes (18): Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the…, write_report(), _bounds(), _check(), _overlaps(), Mask (+10 more)

### Community 113 - "RequestBudget"
Cohesion: 0.24
Nodes (8): DiscoveryError, parse_discovery(), Exception, Path, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, Per-run inference submission attempts; cache reads and handle recovery are free., RequestBudget, test_shared_budget_allows_only_one_concurrent_submission()

### Community 114 - "check_delivery.py"
Cohesion: 0.31
Nodes (7): computed_field, main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), Delivery, Every delivered asset passed its checks. Proxies are allowed; they are listed.

### Community 115 - "reconstruction/main.py"
Cohesion: 0.25
Nodes (7): furniture_data_dir(), Path, Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, health(), get, Process liveness only; does not probe external providers.

### Community 116 - "Furniture asset delivery and checks (#18, Dev 2.6)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Furniture asset delivery and checks (#18, Dev 2.6), Goals, Intent, Non-goals, Tests

### Community 117 - "test_rounded_coordinates.py"
Cohesion: 0.38
Nodes (6): parametrize, RoomScene, Reconstructed scenes round coordinates; openings a fraction of a millimetre off…, room(), test_clearly_misplaced_openings_are_still_rejected(), test_slightly_misaligned_openings_are_audited_and_the_room_stays_reachable()

### Community 119 - "test_shared_handoff_case"
Cohesion: 0.33
Nodes (4): Any, parametrize, Reusable scene variants and expected findings for Dev 3/4 integration., test_shared_handoff_case()

## Knowledge Gaps
- **382 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+377 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `DraftSession`, `detect_blocked_doors`, `test_room_shell.py`, `FurnitureAsset`, `test_room_align.py`, `calculate_free_floor_ratio`, `test_objective.py`, `test_room_parse.py`, `ContractModel`, `align.py`, `parse.py`, `detect_collisions`, `test_real_room.py`, `scenes.py`, `layout_tools.py`, `Pose2D`, `routes.py`, `detect_front_clearance`, `SpatialInputError`, `spatial_engine/main.py`, `calculate_brightness_approximation`, `generate_mock_glbs.py`, `observe_vision.py`, `test_room_align_vision.py`, `shell.py`, `test_delivery.py`, `test_demo_assets.py`, `test_chat.py`, `test_layout_tools.py`, `audit_scene`, `detect_out_of_bounds`, `Vec2`, `._check_winding`, `test_rounded_coordinates.py`, `test_shared_handoff_case`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `detect_blocked_doors`, `test_room_align.py`, `BBoxM`, `observe_vision.py`, `test_contract_occupancy.py`, `test_reconstruction.py`, `test_room_align_vision.py`, `RoomScene`, `test_fixture_scene.py`, `ContractModel`, `align.py`, `check_delivery.py`, `KnownDimensions`, `scenes.py`, `.to_item`, `test_delivery.py`, `Frame`, `Pose2D`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `DraftSession`, `detect_blocked_doors`, `FurnitureAsset`, `footprint.py`, `calculate_free_floor_ratio`, `test_reconstruction.py`, `test_objective.py`, `ContractModel`, `align.py`, `detect_collisions`, `KnownDimensions`, `Pose2D`, `detect_front_clearance`, `calculate_brightness_approximation`, `make_item`, `test_delivery.py`, `test_chat.py`, `test_layout_tools.py`, `detect_out_of_bounds`, `Vec2`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 161 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 161 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `FurnitureAsset` (e.g. with `check_placed()` and `deliver_furniture()`) actually correct?**
  _`FurnitureAsset` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `Registry` (e.g. with `FalSamProvider` and `GrabCutProvider`) actually correct?**
  _`Registry` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 58 inferred relationships involving `BBoxM` (e.g. with `template_parts()` and `AssetCheck`) actually correct?**
  _`BBoxM` has 58 INFERRED edges - model-reasoned connections that need verification._