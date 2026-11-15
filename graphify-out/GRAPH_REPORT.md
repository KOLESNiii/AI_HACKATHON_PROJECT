# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 221 files · ~335,949 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3389 nodes · 9864 edges · 145 communities (114 shown, 31 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1153 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `471905d7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- shell.py
- test_room_align_vision.py
- test_real_room.py
- RoomScene
- audio.test.ts
- catalog.py
- Pose2D
- test_segmentation.py
- FurnitureAsset
- test_room_align.py
- calculate_free_floor_ratio
- test_delivery.py
- RequestBudget
- BBoxM
- test_selection.py
- App.tsx
- test_agent.py
- FurnitureItem
- test_objective.py
- test_drafts.py
- regions.py
- test_chat.py
- test_room_correct.py
- test_room_parse.py
- test_reconstruction.py
- LayoutToolbox
- detect_blocked_doors
- schema.ts
- parse.py
- calculate_brightness_approximation
- test_demo_cache_room.py
- walk.ts
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- geometry.ts
- test_room_shell.py
- SpatialInputError
- correct_scale
- test_layout_tools.py
- detect_front_clearance
- demo_assets.py
- Vec2
- compilerOptions
- test_demo_cache.py
- Frame
- Sidebar.tsx
- detect_out_of_bounds
- FloorPlanScreen.tsx
- generate_mock_glbs.py
- geometry.py
- test_contract_occupancy.py
- layout_tools.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_api.py
- Decisions
- useStore
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
- Registry
- test_fixture_scene.py
- EvidenceFrame
- Implementation plan: issue #14
- Spatial engine
- CollisionPart
- keyboard.ts
- scripts
- openings.py
- SpaceShift — System Architecture & 4-Developer Execution DAG
- Asset Handoff Agreement Implementation Plan
- Review Focus
- Review Focus
- Floor-plan parser (Dev 1)
- Furniture masks and placement evidence — issue #15
- Request
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
- Context
- model_validator
- README.md
- frontend/package.json
- scenes.py
- test_contracts.py
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- WindowOpening
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift
- manifest.json
- _Page
- agent.py
- test_demo_assets.py
- vite
- ._check_winding
- LayoutMetrics
- Validated, cached demo assets (#20, Dev 2.8)
- get
- test_the_geometry_check_compares_shape_and_names_a_wrong_wall
- model_validator
- Protocol
- DoorOpening
- ValueError
- Vec2
- WallSegment
- demo_cache/README.md
- WindowOpening
- gt
- Path
- post
- Response
- MonkeyPatch

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

## Communities (145 total, 31 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.04
Nodes (95): catalog_id(), _decode(), item_box(), Mask, NDArray, uint8, The retailer's own published model as the item's raw mesh. No inference and no…, The next published model that is usable and within the triangle budget. Each… (+87 more)

### Community 1 - "shell.py"
Cohesion: 0.10
Nodes (38): int64, _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key(), _miter() (+30 more)

### Community 2 - "test_room_align_vision.py"
Cohesion: 0.06
Nodes (62): Image, MaskSource, build_prompt(), _distance_to_wall(), _draw_marks(), _encode(), _facing(), FalVisionObserver (+54 more)

### Community 3 - "test_real_room.py"
Cohesion: 0.09
Nodes (73): Collection, proxy_warning(), clear_cache(), Forget assembled scenes (tests, or after the furniture source changes)., _audit(), auditor(), _clear(), client() (+65 more)

### Community 4 - "RoomScene"
Cohesion: 0.13
Nodes (39): RoomScene, NoFurniture, The room alone: what parsed rooms get until #16 produces furniture assets., conform_openings(), RoomScene, Put every door exactly on its wall, so the spatial audit accepts the room. Each…, clear_corrections(), Serve every plan as parsed again (tests). (+31 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.07
Nodes (25): listeners, onSoundCue(), PartialTone, playCue(), renderCue(), SoundCue, tones, AudioEngine (+17 more)

### Community 6 - "catalog.py"
Cohesion: 0.05
Nodes (68): Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., write_atomic(), catalog_scene(), CatalogImport, ImageProvenance, import_catalog_asset(), import_product() (+60 more)

### Community 7 - "Pose2D"
Cohesion: 0.06
Nodes (59): Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by() (+51 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.10
Nodes (69): Rect, _fetch(), MaskError, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, main(), Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the… (+61 more)

### Community 9 - "FurnitureAsset"
Cohesion: 0.08
Nodes (29): FurnitureAsset, FurnitureItem, model_validator, Pose2D, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., Dev 1 places the asset: add the pose it aligned from the floor plan., AlignmentResult, _Capture (+21 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (58): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+50 more)

### Community 11 - "calculate_free_floor_ratio"
Cohesion: 0.10
Nodes (52): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, item(), FurnitureItem, parametrize (+44 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.10
Nodes (51): APIRouter, asset_router(), Path, Store a finished, profile-conforming `.glb` and return its `glb_url`., `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., store_asset(), main(), Path (+43 more)

### Community 13 - "RequestBudget"
Cohesion: 0.09
Nodes (35): ArtifactTooLarge, box_pixels(), FalSamProvider, GrabCutProvider, MaskProvider, Any, Exception, NDArray (+27 more)

### Community 14 - "BBoxM"
Cohesion: 0.10
Nodes (57): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, _along_mesh(), BBoxM, Published width and depth, assigned to X and Z of a shape with these extents.…, BBoxM, CollisionPart (+49 more)

### Community 15 - "test_selection.py"
Cohesion: 0.13
Nodes (47): FalVisionProvider, Reviewed detections keyed by full source frame keys, never by batch position., RecordedProvider, main(), Path, Local #14 CLI. Defaults to offline sampling; --live explicitly permits provider…, Full-resolution source artifacts stay separate; the report shows boxes and IDs., write_report() (+39 more)

### Community 16 - "App.tsx"
Cohesion: 0.07
Nodes (33): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, App(), ORDER, screenVariants (+25 more)

### Community 17 - "test_agent.py"
Cohesion: 0.17
Nodes (45): OptimiseRequest, propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, Step, interpret(), item(), move() (+37 more)

### Community 18 - "FurnitureItem"
Cohesion: 0.10
Nodes (36): FurnitureItem, Correction, Facing, _access(), _Choice, _extents(), _front(), _nearby() (+28 more)

### Community 19 - "test_objective.py"
Cohesion: 0.15
Nodes (45): compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, item(), FurnitureItem, parametrize, RoomScene (+37 more)

### Community 20 - "test_drafts.py"
Cohesion: 0.11
Nodes (37): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+29 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (34): int32, Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction() (+26 more)

### Community 22 - "test_chat.py"
Cohesion: 0.09
Nodes (52): fixture, add_item(), AddItemArguments, chat(), ChatReply, ChatRequest, _percent(), AuditReport (+44 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.08
Nodes (51): AlignmentRecord, BaseModel, How one asset's pose was decided. Keyed by the asset's stable ID., apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit (+43 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.08
Nodes (61): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), FixedAnnotator, PlanAnnotations, Path, Returns pre-recorded annotations (tests, the debug CLI, cached demo plans). (+53 more)

### Community 25 - "test_reconstruction.py"
Cohesion: 0.06
Nodes (71): FailureKind, fal_media_url(), fetch_bounded(), Provider artifacts are fetched over HTTPS from fal's media hosts only., Stream a provider artifact without redirects, enforcing `limit` while reading., FalSam3dProvider, _fetch(), inspect_mesh() (+63 more)

### Community 26 - "LayoutToolbox"
Cohesion: 0.24
Nodes (7): LayoutDraft, LayoutToolbox, _num(), _point(), Any, RoomScene, The three exploration tools for one request, over one `DraftSession`. `call`…

### Community 27 - "detect_blocked_doors"
Cohesion: 0.15
Nodes (35): BlockedDoorIssue, BlockedDoorIssue, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize, RoomScene (+27 more)

### Community 28 - "schema.ts"
Cohesion: 0.07
Nodes (34): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M (+26 more)

### Community 29 - "parse.py"
Cohesion: 0.11
Nodes (41): FloorCaption, BaseModel, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance() (+33 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.13
Nodes (35): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, A window-openness proxy for layout comparison, not a lighting simulation., Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item() (+27 more)

### Community 31 - "test_demo_cache_room.py"
Cohesion: 0.12
Nodes (36): from_demo_cache(), test_download_deadline_stops_trickling_response(), assert_readers_agree(), _audit(), auditor(), _client(), _collides(), data_dir() (+28 more)

### Community 32 - "walk.ts"
Cohesion: 0.08
Nodes (33): WALK_HEADROOM_M, captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera(), restoreEditorView() (+25 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.07
Nodes (39): exception_handler, FengShuiRequest, FengShuiResult, get, gt, JSONResponse, le, Path (+31 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "geometry.ts"
Cohesion: 0.18
Nodes (20): DoorSwings(), LibraryTab(), doorSwing(), fitsRoom(), fitYaw(), footprint(), toWorld(), byId() (+12 more)

### Community 36 - "test_room_shell.py"
Cohesion: 0.10
Nodes (46): build_shell(), Scene, The room shell as a trimesh Scene with nodes `floor`, `ceiling`, `wall_<id>`., shell_glb(), corner_probes(), _inside(), invalid_footprints(), _l_door() (+38 more)

### Community 37 - "SpatialInputError"
Cohesion: 0.20
Nodes (17): ToolCall, ActivityAnchor, assess_feng_shui(), Assessment, DetailModel, FengShuiRequest, FengShuiResult, Finding (+9 more)

### Community 38 - "correct_scale"
Cohesion: 0.07
Nodes (38): ge, HTTPException, Query, find_parsed_scene(), get_plan(), get_room(), get_shell(), prepare_floor_scale() (+30 more)

### Community 39 - "test_layout_tools.py"
Cohesion: 0.19
Nodes (25): LayoutPreferences, What the user asked for, already validated by the server., evaluate(), item(), move(), Any, FurnitureItem, parametrize (+17 more)

### Community 40 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.11
Nodes (28): FileResponse, demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file() (+20 more)

### Community 42 - "Vec2"
Cohesion: 0.08
Nodes (48): ContractModel, BaseModel, AuditReport, ClearanceIssue, CollisionIssue, DoorOpening, FengShuiReport, FengShuiSightline (+40 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.09
Nodes (73): inspect_asset(), Re-read an asset's stored file and check it against the furniture profile and…, cache_folder(), CachedFile, CacheError, current_generation(), DemoCache, _inside() (+65 more)

### Community 45 - "Frame"
Cohesion: 0.11
Nodes (38): DiscoveryError, DiscoveryProvider, OfflineProvider, parse_discovery(), Exception, Path, Protocol, fal vision proposes instances across full images; reviewed recordings run… (+30 more)

### Community 46 - "Sidebar.tsx"
Cohesion: 0.12
Nodes (21): LayoutGoal, AuditStats(), ChatTab(), StatsTab(), tabs, catalog, catalogCategories, AgentReply (+13 more)

### Community 47 - "detect_out_of_bounds"
Cohesion: 0.22
Nodes (24): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+16 more)

### Community 48 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (21): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+13 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "geometry.py"
Cohesion: 0.11
Nodes (27): FengShuiReport, LineString, _height_overlaps(), Spatial checks independent of HTTP, mesh loading and provider services., _angle_deg(), calculate_feng_shui(), _front(), _occupant() (+19 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 52 - "layout_tools.py"
Cohesion: 0.16
Nodes (22): _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, _metrics(), _Move, BaseModel (+14 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_api.py"
Cohesion: 0.20
Nodes (16): MonkeyPatch, payload(), Any, Exception, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422() (+8 more)

### Community 55 - "Decisions"
Cohesion: 0.08
Nodes (26): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+18 more)

### Community 56 - "useStore"
Cohesion: 0.12
Nodes (29): EditorScreen(), floorPlane, Furniture, flaggedFor(), Navigation(), RoomView(), RotationRing(), SelectionTools() (+21 more)

### Community 57 - "audit_scene"
Cohesion: 0.20
Nodes (24): audit_scene(), AuditReport, RoomScene, Compose the implemented checks into the shared audit response., Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize (+16 more)

### Community 58 - "routes.py"
Cohesion: 0.08
Nodes (31): File, AnnotationResult, Compass, FalVisionAnnotator, NullAnnotator, PlanAnnotator, Protocol, What computer vision cannot read off a floor plan: room labels with their… (+23 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "Furniture.tsx"
Cohesion: 0.14
Nodes (24): Mesh(), MeshBoundary, ProxyBox(), categoryWash, disposeInk(), inkify(), inkLine, Shell (+16 more)

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

### Community 69 - "ProviderError"
Cohesion: 0.11
Nodes (21): demo_room_scenes(), profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, Each demo room with the furniture standing in it, as the editor builds them., solve(), Timed (+13 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "Registry"
Cohesion: 0.10
Nodes (16): Connection, choose_view(), _clipped(), _Job, Masked views -> one stored raw mesh per item, or an explicit failure, and…, The one masked view to reconstruct from: confident, then whole, then large., Any, Path (+8 more)

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "EvidenceFrame"
Cohesion: 0.11
Nodes (26): EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., main(), _no_frames(), Path, directory_frames(), FrameSource, Path (+18 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.13
Nodes (15): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Free floor area, Front clearance, Internal layout comparison (issue #33) (+7 more)

### Community 76 - "CollisionPart"
Cohesion: 0.17
Nodes (23): CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, NormalisedMesh, Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`., CollisionVolume, furniture_collision_volumes(), An item's occupied box transformed into a vertical prism in room space., Transform validated local collision boxes; absent parts mean one solid bbox.… (+15 more)

### Community 77 - "keyboard.ts"
Cohesion: 0.32
Nodes (7): editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, initial

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

### Community 87 - "detect_collisions"
Cohesion: 0.19
Nodes (21): CollisionIssue, detect_collisions(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, test_shared_nested_fixture_has_no_furniture_collisions(), item(), FurnitureItem, parametrize (+13 more)

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
Cohesion: 0.23
Nodes (17): Polygon, front_clearance_zone(), furniture_footprint(), FurnitureItem, Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the…, Full-width rectangle from the bbox front, rotated/placed in room X/Z. Zero…, make_item(), FurnitureItem (+9 more)

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "scenes.py"
Cohesion: 0.09
Nodes (34): assemble_scene(), Assembly, assets_of(), FurnitureSource, Protocol, RoomScene, One room + its furniture -> the `RoomScene` the editor and the audit load (#9).…, A scene's furniture as pose-less assets with placeholder evidence (no source… (+26 more)

### Community 102 - "test_contracts.py"
Cohesion: 0.16
Nodes (17): load_generator(), load_mock(), RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must…, solid_at(), test_audit_report_must_echo_scene() (+9 more)

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "WindowOpening"
Cohesion: 0.18
Nodes (11): WindowOpening, The opening's extent along its wall's interior face, in room X/Z coordinates., window_plan_segment(), _check_comparable(), _door_overlap_area(), _near_window_shortfall(), AuditReport, RoomScene (+3 more)

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "_Page"
Cohesion: 0.29
Nodes (3): HTMLParser, _Page, The few things a product page is read for: JSON-LD, meta tags, title and…

### Community 124 - "agent.py"
Cohesion: 0.10
Nodes (19): Outcome, Protocol, AgentLimits, _Budget, _explain_result(), _explore(), _interpret(), _Interpretation (+11 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "._check_winding"
Cohesion: 0.50
Nodes (3): floor_polygon is clockwise in plan view and every wall has the room on its…, model_validator, ValueError

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

## Knowledge Gaps
- **408 isolated node(s):** `1. The Core Differentiator (Why We Beat Existing Tools)`, `2. What We Stole (And Improved) From Competitors`, `**Design & Frontend (`frontend/`)**`, `**AI & Generative Media (`services/reconstruction` & `services/media_gen`)**`, `**Spatial Audit & Solver Engine (`services/spatial_engine`)**` (+403 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `shell.py`, `test_room_align_vision.py`, `test_real_room.py`, `test_the_geometry_check_compares_shape_and_names_a_wrong_wall`, `FurnitureAsset`, `test_room_align.py`, `calculate_free_floor_ratio`, `test_delivery.py`, `test_agent.py`, `FurnitureItem`, `test_objective.py`, `test_drafts.py`, `test_chat.py`, `test_room_correct.py`, `test_room_parse.py`, `LayoutToolbox`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `spatial_engine/main.py`, `test_room_shell.py`, `SpatialInputError`, `correct_scale`, `test_layout_tools.py`, `detect_front_clearance`, `demo_assets.py`, `Vec2`, `detect_out_of_bounds`, `generate_mock_glbs.py`, `geometry.py`, `layout_tools.py`, `test_api.py`, `audit_scene`, `ProviderError`, `EvidenceFrame`, `detect_collisions`, `scenes.py`, `test_contracts.py`, `WindowOpening`, `test_demo_assets.py`, `._check_winding`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `test_room_align_vision.py`, `RoomScene`, `catalog.py`, `Pose2D`, `test_room_align.py`, `test_delivery.py`, `BBoxM`, `FurnitureItem`, `test_reconstruction.py`, `demo_assets.py`, `Vec2`, `test_demo_cache.py`, `Frame`, `test_contract_occupancy.py`, `Registry`, `test_fixture_scene.py`, `EvidenceFrame`, `CollisionPart`, `scenes.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_catalog.py`, `catalog.py`, `Pose2D`, `FurnitureAsset`, `calculate_free_floor_ratio`, `test_delivery.py`, `test_agent.py`, `FurnitureItem`, `test_objective.py`, `test_drafts.py`, `test_chat.py`, `test_reconstruction.py`, `detect_blocked_doors`, `calculate_brightness_approximation`, `test_layout_tools.py`, `detect_front_clearance`, `Vec2`, `detect_out_of_bounds`, `audit_scene`, `CollisionPart`, `detect_collisions`, `furniture_footprint`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 209 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 209 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 66 inferred relationships involving `Pose2D` (e.g. with `FurnitureAsset` and `_access()`) actually correct?**
  _`Pose2D` has 66 INFERRED edges - model-reasoned connections that need verification._