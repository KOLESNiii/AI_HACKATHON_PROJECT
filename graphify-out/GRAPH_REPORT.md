# Graph Report - AI_HACKATHON_PROJECT  (2026-11-15)

## Corpus Check
- 197 files · ~296,616 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2816 nodes · 7964 edges · 122 communities (107 shown, 15 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 913 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `260c2570`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DraftSession
- detect_blocked_doors
- test_room_shell.py
- test_segmentation.py
- align_debug.py
- test_room_align.py
- footprint.py
- test_selection.py
- geometry.ts
- calculate_free_floor_ratio
- test_room_align_vision.py
- test_reconstruction.py
- test_objective.py
- RoomScene
- test_room_parse.py
- test_contracts.py
- FurnitureAsset
- regions.py
- parse.py
- detect_collisions
- BBoxM
- Box
- selection.py
- demo_assets.py
- SpatialInputError
- schema.ts
- Furniture.tsx
- SpaceShift 3D representation and asset handoff — design
- models.py
- Registry
- test_agent.py
- annotate.py
- detect_front_clearance
- furniture_footprint
- walk.ts
- audit_scene
- compilerOptions
- calculate_brightness_approximation
- routes.py
- generate_mock_glbs.py
- proxy_asset
- FloorPlanScreen.tsx
- test_contract_occupancy.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- audio.test.ts
- test_real_room.py
- compilerOptions
- agent.py
- reconstruction.py
- Video frame selection and furniture identity — issue #14
- dependencies
- devDependencies
- openings.py
- polygon.py
- spatialPreview.ts
- Dev 4 implementation and integration plan
- Dev 2 → Dev 1 asset handoff
- Agent Instructions
- Decisions
- useStore
- test_delivery.py
- ProviderError
- Implementation plan: issue #14
- Architecture
- keyboard.ts
- scripts
- layout_tools.py
- test_demo_assets.py
- SpaceShift — System Architecture & 4-Developer Execution DAG
- Spatial findings: Dev 3 / Dev 4 handoff
- LayoutToolbox
- detect_out_of_bounds
- Spatial engine
- ContractModel
- Asset Handoff Agreement Implementation Plan
- Review Focus
- Review Focus
- Furniture masks and placement evidence — issue #15
- invalid_request
- plugins
- generate-landscapes.ts
- App.tsx
- Floor-plan parser (Dev 1)
- Individual furniture meshes with proxy fallback — issue #16
- scripts
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- Furniture mesh normalisation — issue #17
- .to_item
- model_validator
- scenes.py
- selection_models.py
- test_fixture_scene.py
- frontend/package.json
- ._check_winding
- health
- solve
- test_collision_parts.py
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
- segment_items.py
- check_delivery.py
- Furniture asset delivery and checks (#18, Dev 2.6)
- README.md
- _door_overlap_area
- test_shared_handoff_case
- LayoutMetrics
- divided_access_room
- tests/conftest.py

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 154 edges
2. `FurnitureAsset` - 77 edges
3. `Registry` - 63 edges
4. `BBoxM` - 59 edges
5. `Pose2D` - 56 edges
6. `useStore` - 55 edges
7. `reconstruct_furniture()` - 55 edges
8. `FurnitureItem` - 53 edges
9. `align_assets()` - 51 edges
10. `propose_layout()` - 51 edges

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

## Communities (122 total, 15 thin omitted)

### Community 0 - "DraftSession"
Cohesion: 0.10
Nodes (37): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+29 more)

### Community 1 - "detect_blocked_doors"
Cohesion: 0.18
Nodes (32): BlockedDoorIssue, CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize (+24 more)

### Community 2 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 3 - "test_segmentation.py"
Cohesion: 0.12
Nodes (60): Rect, GrabCutProvider, MaskError, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, No network or cost. Approximate: it can keep floor or an occluder inside the…, Store a mask and cut-out for every selected view of the scene's (or the named)…, Resolve an `EvidenceFrame.mask_url` (relative to the asset data directory)., read_mask() (+52 more)

### Community 4 - "align_debug.py"
Cohesion: 0.09
Nodes (27): AlignmentRecord, _Capture, main(), pose_error(), FrameSource, FurnitureItem, RoomScene, Debug CLI for furniture alignment: place assets in a room and draw the result.… (+19 more)

### Community 5 - "test_room_align.py"
Cohesion: 0.12
Nodes (59): DoorOpening, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction. (+51 more)

### Community 6 - "footprint.py"
Cohesion: 0.06
Nodes (58): any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach() (+50 more)

### Community 7 - "test_selection.py"
Cohesion: 0.16
Nodes (40): Reviewed detections keyed by full source frame keys, never by batch position., RecordedProvider, main(), Path, Local #14 CLI. Defaults to offline sampling; --live explicitly permits provider…, Full-resolution source artifacts stay separate; the report shows boxes and IDs., write_report(), Discovery (+32 more)

### Community 8 - "geometry.ts"
Cohesion: 0.09
Nodes (22): AuditStats(), ChatTab(), LibraryTab(), StatsTab(), tabs, ButtonProps, Chip(), dotColor (+14 more)

### Community 9 - "calculate_free_floor_ratio"
Cohesion: 0.07
Nodes (68): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, payload(), Any, Exception (+60 more)

### Community 10 - "test_room_align_vision.py"
Cohesion: 0.04
Nodes (86): Image, MaskSource, EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., item_occupied(), FurnitureItem, build_prompt(), directory_frames() (+78 more)

### Community 11 - "test_reconstruction.py"
Cohesion: 0.12
Nodes (42): inspect_mesh(), MeshError, Exception, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, (triangles, extents) of a usable glTF 2.0 binary; MeshError("invalid_mesh")…, choose_view(), _clipped(), Path (+34 more)

### Community 12 - "test_objective.py"
Cohesion: 0.15
Nodes (45): WindowOpening, compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, item(), FurnitureItem, parametrize (+37 more)

### Community 13 - "RoomScene"
Cohesion: 0.11
Nodes (43): RoomScene, Vec2, A point on the floor plan (Y omitted)., assemble_scene(), NoFurniture, RoomScene, What a furniture source supplies for one room., The room alone: what parsed rooms get until #16 produces furniture assets. (+35 more)

### Community 14 - "test_room_parse.py"
Cohesion: 0.10
Nodes (51): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), PlanAnnotations, bay_room(), _canvas(), _close() (+43 more)

### Community 15 - "test_contracts.py"
Cohesion: 0.16
Nodes (18): load_generator(), load_mock(), RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must…, solid_at(), test_audit_report_must_echo_scene() (+10 more)

### Community 16 - "FurnitureAsset"
Cohesion: 0.09
Nodes (41): FurnitureItem, Correction, Facing, FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., _access(), AlignmentResult, _Choice (+33 more)

### Community 17 - "regions.py"
Cohesion: 0.11
Nodes (38): int32, _fallback_scale(), ImageFloor, No usable labels: assume interior door gaps are ESTIMATED_DOOR_M wide, else…, Raster, _accept(), Bridge, _cast() (+30 more)

### Community 18 - "parse.py"
Cohesion: 0.12
Nodes (36): FloorCaption, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance(), _consensus() (+28 more)

### Community 19 - "detect_collisions"
Cohesion: 0.19
Nodes (21): CollisionIssue, detect_collisions(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, item(), FurnitureItem, parametrize (+13 more)

### Community 20 - "BBoxM"
Cohesion: 0.17
Nodes (40): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, NormalisationError, normalise_mesh(), BBoxM, ValueError, Fit a raw glTF 2.0 binary to the furniture profile, store it and return its… (+32 more)

### Community 21 - "Box"
Cohesion: 0.11
Nodes (26): box_pixels(), Any, NDArray, uint8, (x0, y0, x1, y1) with at least one pixel, matching `video.crop`., One segment per box, in order; None where none was produced. Raises MaskError…, Segment, _bounds() (+18 more)

### Community 22 - "selection.py"
Cohesion: 0.21
Nodes (18): _diagnostic(), SourceVideo, overlap(), Path, Frame discovery -> permanent scene IDs. Masks are segmentation.py (#15); no…, _score_sightings(), _select_views(), crop() (+10 more)

### Community 23 - "demo_assets.py"
Cohesion: 0.12
Nodes (26): FileResponse, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file() (+18 more)

### Community 24 - "SpatialInputError"
Cohesion: 0.07
Nodes (53): WallSegment, LineString, Polygon, Spatial checks independent of HTTP, mesh loading and provider services., A window-openness proxy for layout comparison, not a lighting simulation., CollisionVolume, door_entry_segment(), _door_frame() (+45 more)

### Community 25 - "schema.ts"
Cohesion: 0.07
Nodes (35): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M (+27 more)

### Community 26 - "Furniture.tsx"
Cohesion: 0.14
Nodes (24): Mesh(), MeshBoundary, ProxyBox(), categoryWash, disposeInk(), inkify(), inkLine, Shell (+16 more)

### Community 27 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 28 - "models.py"
Cohesion: 0.09
Nodes (27): BBoxM, CollisionPart, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).…, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), AssetCheck, _gltf_problems(), inspect_asset() (+19 more)

### Community 29 - "Registry"
Cohesion: 0.08
Nodes (37): Connection, ArtifactTooLarge, fal_media_url(), _fetch(), fetch_bounded(), Exception, Instance masks from item boxes (#15): local GrabCut offline, fal SAM 3 when…, A provider artifact exceeded its size cap; nothing was kept. (+29 more)

### Community 30 - "test_agent.py"
Cohesion: 0.16
Nodes (47): OptimiseRequest, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, Step, interpret() (+39 more)

### Community 31 - "annotate.py"
Cohesion: 0.11
Nodes (19): AnnotationResult, Compass, FixedAnnotator, NullAnnotator, BaseModel, Path, What computer vision cannot read off a floor plan: room labels with their…, Plans print labels in capitals ("BEDROOM (4)"); show them in title case. (+11 more)

### Community 32 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 33 - "furniture_footprint"
Cohesion: 0.32
Nodes (13): furniture_footprint(), Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, make_item(), FurnitureItem, parametrize, Footprint examples independent of meshes, providers and HTTP routes., test_45_degree_corners_follow_threejs_yaw(), test_does_not_mutate_item() (+5 more)

### Community 34 - "walk.ts"
Cohesion: 0.08
Nodes (33): WALK_HEADROOM_M, captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera(), restoreEditorView() (+25 more)

### Community 35 - "audit_scene"
Cohesion: 0.12
Nodes (22): demo_room_scenes(), profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, Each demo room with the furniture standing in it, as the editor builds them., solve(), Timed (+14 more)

### Community 36 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 37 - "calculate_brightness_approximation"
Cohesion: 0.18
Nodes (28): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item(), FurnitureItem (+20 more)

### Community 38 - "routes.py"
Cohesion: 0.08
Nodes (34): description, File, ParsedFloor, FalVisionAnnotator, PlanAnnotator, Protocol, Reads labels with a vision LLM on fal.ai (`FAL_KEY`). The endpoint and model…, main() (+26 more)

### Community 39 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 40 - "proxy_asset"
Cohesion: 0.09
Nodes (26): APIRouter, Category, asset_router(), Path, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`. (+18 more)

### Community 41 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (21): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+13 more)

### Community 42 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 43 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 44 - "audio.test.ts"
Cohesion: 0.05
Nodes (27): listeners, onSoundCue(), PartialTone, playCue(), renderCue(), SoundCue, tones, AudioEngine (+19 more)

### Community 45 - "test_real_room.py"
Cohesion: 0.08
Nodes (57): Collection, furniture_data_dir(), Path, Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, geometry_mismatch(), geometry_warning(), load_bindings() (+49 more)

### Community 46 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 47 - "agent.py"
Cohesion: 0.10
Nodes (21): Outcome, AnthropicLayoutModel, _Budget, _explain_result(), _explore(), _interpret(), _Interpretation, LayoutModel (+13 more)

### Community 48 - "reconstruction.py"
Cohesion: 0.09
Nodes (24): FailureKind, FalSam3dProvider, MeshProvider, Any, Mask, NDArray, Protocol, uint8 (+16 more)

### Community 49 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 50 - "dependencies"
Cohesion: 0.12
Nodes (17): framer-motion, dependencies, framer-motion, react, react-dom, @react-three/fiber, tailwindcss, @tailwindcss/vite (+9 more)

### Community 51 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, oxlint, prettier, @types/node, @types/react, @types/react-dom, @types/three, typescript (+9 more)

### Community 52 - "openings.py"
Cohesion: 0.10
Nodes (25): Gray, attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask (+17 more)

### Community 53 - "polygon.py"
Cohesion: 0.22
Nodes (16): area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), float64, Mask, NDArray (+8 more)

### Community 54 - "spatialPreview.ts"
Cohesion: 0.22
Nodes (17): DoorSwings(), doorSwing(), footprint(), toWorld(), byId(), collisionVolumes(), convexOverlapArea(), covered() (+9 more)

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
Cohesion: 0.10
Nodes (20): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Backend-owned mock meshes, Bootstrap, Calm editor audio, Custom requests, Decisions (+12 more)

### Community 59 - "useStore"
Cohesion: 0.11
Nodes (30): EditorScreen(), floorPlane, Furniture, flaggedFor(), Navigation(), RoomView(), RotationRing(), SelectionTools() (+22 more)

### Community 60 - "test_delivery.py"
Cohesion: 0.16
Nodes (37): check_placed(), deliver_furniture(), RoomScene, A scene's furniture for Dev 1 to place: per item, its checked mesh or its…, Faults in how a scene carries delivered assets; empty when every asset appears…, audit(), bounds_of(), client() (+29 more)

### Community 61 - "ProviderError"
Cohesion: 0.18
Nodes (10): AgentLimits, ProviderError, Exception, One allowance per request. Retries and the interpretation call spend the same…, A failed model call. `kind` is safe to log; no key or payload is kept., Request, Response, sdk_model() (+2 more)

### Community 62 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 63 - "Architecture"
Cohesion: 0.13
Nodes (15): Architecture, Backend-provided demo models, Editor play mode, Frontend audio, Furniture evidence selection (#14), Furniture masks and placement evidence (#15), Furniture normalisation (#17, PR #54 review), Home screen and intake presentation (+7 more)

### Community 64 - "keyboard.ts"
Cohesion: 0.32
Nodes (7): editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, initial

### Community 65 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 66 - "layout_tools.py"
Cohesion: 0.15
Nodes (25): _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, _metrics(), _Move, _num() (+17 more)

### Community 67 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 68 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 69 - "Spatial findings: Dev 3 / Dev 4 handoff"
Cohesion: 0.29
Nodes (6): Completion and follow-up, Consuming the findings, HTTP handoff contract, Layout suggestions (`POST /solve`), Load the same examples in the editor and backend, Spatial findings: Dev 3 / Dev 4 handoff

### Community 70 - "LayoutToolbox"
Cohesion: 0.16
Nodes (27): LayoutPreferences, LayoutToolbox, What the user asked for, already validated by the server., The three exploration tools for one request, over one `DraftSession`. `call`…, evaluate(), item(), move(), Any (+19 more)

### Community 71 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 72 - "Spatial engine"
Cohesion: 0.17
Nodes (12): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Free floor area, Front clearance, Internal layout comparison (issue #33), Layout drafts for proposed moves (issue #33), Layout exploration tools (issue #33) (+4 more)

### Community 73 - "ContractModel"
Cohesion: 0.13
Nodes (23): ContractModel, BaseModel, AuditReport, BlockedDoorIssue, ClearanceIssue, CollisionIssue, FengShuiReport, FengShuiSightline (+15 more)

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

### Community 81 - "App.tsx"
Cohesion: 0.14
Nodes (15): App(), ORDER, screenVariants, HomeScreen(), rise, Landscape(), LANDSCAPES, startAt() (+7 more)

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

### Community 89 - "scenes.py"
Cohesion: 0.13
Nodes (19): FurnitureSource, Protocol, find_parsed_scene(), A room of an uploaded plan by its `scene_id`, or None (plans are kept in…, default_bindings(), Video furniture for a real plan room (#10): Dev 2's extracted items, placed…, Furniture for rooms bound to a video, read from Dev 2's pipeline data directory., RealRoomFurniture (+11 more)

### Community 90 - "selection_models.py"
Cohesion: 0.15
Nodes (15): DiscoveredObject, MaskRecord, MissingMask, BaseModel, Internal #14-#16 records. Source evidence is deliberately separate from…, One stored instance mask (#15) for one sighting of one item., The stored mask for a sighting, unless its box has changed since., The stored raw mesh, unless the mask it was made from has been replaced since. (+7 more)

### Community 91 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 92 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 94 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 95 - "solve"
Cohesion: 0.17
Nodes (13): LayoutProposal, Proposed furniture poses. Only poses change: shell, openings, item IDs and…, audit(), _input_errors(), AuditReport, LayoutProposal, OptimiseRequest, post (+5 more)

### Community 96 - "test_collision_parts.py"
Cohesion: 0.26
Nodes (16): item(), part(), CollisionPart, FurnitureItem, parametrize, Occupied-volume integration with the merged Dev 2 contract and fixture., test_disjoint_intersections_are_summed(), test_fallback_solid_box_and_fixed_item_are_checked() (+8 more)

### Community 113 - "segment_items.py"
Cohesion: 0.18
Nodes (13): FalSamProvider, MaskProvider, Protocol, fal SAM 3 image: every item box of one frame in one request (verified live…, main(), Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the… (+5 more)

### Community 114 - "check_delivery.py"
Cohesion: 0.31
Nodes (7): computed_field, main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), Delivery, Every delivered asset passed its checks. Proxies are allowed; they are listed.

### Community 115 - "Furniture asset delivery and checks (#18, Dev 2.6)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Furniture asset delivery and checks (#18, Dev 2.6), Goals, Intent, Non-goals, Tests

### Community 117 - "_door_overlap_area"
Cohesion: 0.33
Nodes (6): _check_comparable(), _door_overlap_area(), AuditReport, RoomScene, Do not improve metrics by changing the room, removing items or shrinking them., Grade progress while a door is still blocked, using the audit's same thresholds.

### Community 118 - "test_shared_handoff_case"
Cohesion: 0.33
Nodes (4): Any, parametrize, Reusable scene variants and expected findings for Dev 3/4 integration., test_shared_handoff_case()

### Community 120 - "divided_access_room"
Cohesion: 0.40
Nodes (4): divided_access_room(), RoomScene, Shared regression geometry for custom layout access checks., Clearing a wardrobe by moving its blocker behind the divider cuts circulation.

## Knowledge Gaps
- **375 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+370 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `DraftSession`, `detect_blocked_doors`, `test_room_shell.py`, `align_debug.py`, `test_room_align.py`, `calculate_free_floor_ratio`, `test_room_align_vision.py`, `test_objective.py`, `test_room_parse.py`, `test_contracts.py`, `FurnitureAsset`, `parse.py`, `demo_assets.py`, `SpatialInputError`, `test_agent.py`, `annotate.py`, `detect_front_clearance`, `audit_scene`, `calculate_brightness_approximation`, `routes.py`, `generate_mock_glbs.py`, `test_real_room.py`, `test_delivery.py`, `layout_tools.py`, `test_demo_assets.py`, `LayoutToolbox`, `detect_out_of_bounds`, `ContractModel`, `scenes.py`, `._check_winding`, `solve`, `test_collision_parts.py`, `_door_overlap_area`, `test_shared_handoff_case`, `divided_access_room`?**
  _High betweenness centrality (0.137) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `detect_blocked_doors`, `align_debug.py`, `test_room_align.py`, `test_room_align_vision.py`, `test_reconstruction.py`, `RoomScene`, `BBoxM`, `demo_assets.py`, `models.py`, `test_agent.py`, `proxy_asset`, `test_contract_occupancy.py`, `reconstruction.py`, `test_delivery.py`, `ContractModel`, `.to_item`, `selection_models.py`, `test_fixture_scene.py`, `check_delivery.py`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `ContractModel` connect `ContractModel` to `detect_blocked_doors`, `test_room_align.py`, `test_room_align_vision.py`, `test_objective.py`, `RoomScene`, `test_room_parse.py`, `FurnitureAsset`, `BBoxM`, `SpatialInputError`, `models.py`, `test_agent.py`, `solve`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 151 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 151 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `FurnitureAsset` (e.g. with `check_placed()` and `deliver_furniture()`) actually correct?**
  _`FurnitureAsset` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `Registry` (e.g. with `FalSamProvider` and `GrabCutProvider`) actually correct?**
  _`Registry` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `BBoxM` (e.g. with `template_parts()` and `AssetCheck`) actually correct?**
  _`BBoxM` has 56 INFERRED edges - model-reasoned connections that need verification._