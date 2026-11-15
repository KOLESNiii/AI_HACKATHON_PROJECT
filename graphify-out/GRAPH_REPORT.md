# Graph Report - spaceshift-library-main  (2026-11-15)

## Corpus Check
- 225 files · ~337,515 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3395 nodes · 9963 edges · 139 communities (123 shown, 16 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1165 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `64f1c7b8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- CatalogError
- observe_vision.py
- test_real_room.py
- RoomScene
- audio.test.ts
- catalog.py
- footprint.py
- test_segmentation.py
- FurnitureAsset
- test_room_align.py
- calculate_reachable_floor_ratio
- test_delivery.py
- Box
- BBoxM
- test_selection.py
- App.tsx
- test_agent.py
- Pose2D
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
- LayoutToolbox
- detect_front_clearance
- demo_assets.py
- Vec2
- compilerOptions
- test_demo_cache.py
- selection_models.py
- useStore
- detect_out_of_bounds
- FloorPlanScreen.tsx
- generate_mock_glbs.py
- SpatialInputError
- test_contract_occupancy.py
- layout_tools.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_api.py
- Decisions
- Frame
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
- test_room_align_vision.py
- Implementation plan: issue #14
- Spatial engine
- calculate_free_floor_ratio
- SoundControls.tsx
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
- Prism
- model_validator
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
- FixedAnnotator
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
- ._check_winding
- LayoutMetrics
- Validated, cached demo assets (#20, Dev 2.8)
- PlayLighting.tsx
- reconstruct_items.py
- FurnitureItem
- inspect_asset
- rescale_floor
- plugins
- .to_item
- no_network
- demo_cache/README.md

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 212 edges
2. `FurnitureAsset` - 87 edges
3. `BBoxM` - 79 edges
4. `Pose2D` - 69 edges
5. `FurnitureItem` - 69 edges
6. `Registry` - 69 edges
7. `useStore` - 59 edges
8. `SpatialInputError` - 59 edges
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

## Communities (139 total, 16 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.08
Nodes (60): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., fetch_product() (+52 more)

### Community 1 - "CatalogError"
Cohesion: 0.06
Nodes (37): APIRouter, asset_router(), Path, `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., _decode(), item_box(), NDArray, uint8 (+29 more)

### Community 2 - "observe_vision.py"
Cohesion: 0.07
Nodes (43): Image, MaskSource, build_prompt(), directory_frames(), _distance_to_wall(), _draw_marks(), _encode(), _facing() (+35 more)

### Community 3 - "test_real_room.py"
Cohesion: 0.08
Nodes (75): Collection, proxy_warning(), still_extracting(), _audit(), auditor(), _clear(), client(), _collides() (+67 more)

### Community 4 - "RoomScene"
Cohesion: 0.16
Nodes (34): RoomScene, What a furniture source supplies for one room., SceneFurniture, _audit(), auditor(), _door(), _leaf_end(), DoorOpening (+26 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 6 - "catalog.py"
Cohesion: 0.07
Nodes (51): Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., write_atomic(), _along_mesh(), CatalogImport, ImageProvenance, import_product(), imported_assets() (+43 more)

### Community 7 - "footprint.py"
Cohesion: 0.09
Nodes (39): boundary_distance(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach(), door_sweep(), front_direction() (+31 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.11
Nodes (63): Rect, FalSamProvider, fal SAM 3 image: every item box of one frame in one request (verified live…, main(), Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the…, write_report() (+55 more)

### Community 9 - "FurnitureAsset"
Cohesion: 0.09
Nodes (32): FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., AlignmentRecord, AlignmentResult, _Capture, main(), pose_error(), FrameSource (+24 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (56): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+48 more)

### Community 11 - "calculate_reachable_floor_ratio"
Cohesion: 0.17
Nodes (29): calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, divided_room(), obstacle(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.11
Nodes (56): Store a finished, profile-conforming `.glb` and return its `glb_url`., store_asset(), check_placed(), deliver_furniture(), Path, RoomScene, A scene's furniture for Dev 1 to place: per item, its checked mesh or its…, Faults in how a scene carries delivered assets; empty when every asset appears… (+48 more)

### Community 13 - "Box"
Cohesion: 0.09
Nodes (38): ArtifactTooLarge, box_pixels(), fal_media_url(), _fetch(), GrabCutProvider, MaskError, MaskProvider, Any (+30 more)

### Community 14 - "BBoxM"
Cohesion: 0.11
Nodes (55): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, BBoxM, CollisionPart, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).…, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts() (+47 more)

### Community 15 - "test_selection.py"
Cohesion: 0.13
Nodes (47): FalVisionProvider, Reviewed detections keyed by full source frame keys, never by batch position., RecordedProvider, main(), Path, Local #14 CLI. Defaults to offline sampling; --live explicitly permits provider…, Full-resolution source artifacts stay separate; the report shows boxes and IDs., write_report() (+39 more)

### Community 16 - "App.tsx"
Cohesion: 0.08
Nodes (32): App(), ORDER, screenVariants, EditorScreen(), HomeScreen(), rise, Landscape(), LANDSCAPES (+24 more)

### Community 17 - "test_agent.py"
Cohesion: 0.16
Nodes (47): OptimiseRequest, AgentLimits, propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, One allowance per request. Retries and the interpretation call spend the same…, Step, interpret() (+39 more)

### Community 18 - "Pose2D"
Cohesion: 0.10
Nodes (34): Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., Correction, Facing, _access(), _Choice, _extents(), _front() (+26 more)

### Community 19 - "test_objective.py"
Cohesion: 0.13
Nodes (49): WindowOpening, _check_comparable(), compare_layouts(), evaluate_layout(), RoomScene, Do not improve metrics by changing the room, removing items or shrinking them., Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.… (+41 more)

### Community 20 - "DraftSession"
Cohesion: 0.12
Nodes (33): DraftSession, _echo(), LayoutMoveError, PoseChange, RoomScene, A fresh scene at the base revision, so its audit identifies the submitted scene., None means unlimited., The draft as a new `RoomScene`; changing the returned copy affects nothing… (+25 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (32): int32, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point() (+24 more)

### Community 22 - "test_chat.py"
Cohesion: 0.10
Nodes (49): add_item(), AddItemArguments, chat(), ChatReply, ChatRequest, _percent(), AuditReport, BaseModel (+41 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.11
Nodes (42): apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, _perimeter(), _point(), Exception (+34 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.09
Nodes (58): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), PlanAnnotations, bay_room(), _canvas(), _close() (+50 more)

### Community 25 - "test_reconstruction.py"
Cohesion: 0.07
Nodes (46): FailureKind, Mask, The next published model that is usable and within the triangle budget. Each…, fetch_bounded(), Stream a provider artifact without redirects, enforcing `limit` while reading., FalSam3dProvider, _fetch(), inspect_mesh() (+38 more)

### Community 26 - "demo_cache.py"
Cohesion: 0.14
Nodes (31): CachedFile, CacheError, current_generation(), _inside(), install_demo_cache(), _intact(), main(), prune_demo_cache() (+23 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.13
Nodes (38): BlockedDoorIssue, BlockedDoorIssue, CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, detect_blocked_doors(), _height_overlaps(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item() (+30 more)

### Community 28 - "schema.ts"
Cohesion: 0.06
Nodes (40): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M (+32 more)

### Community 29 - "parse.py"
Cohesion: 0.11
Nodes (43): FloorCaption, BaseModel, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance() (+35 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.18
Nodes (28): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item(), FurnitureItem (+20 more)

### Community 31 - "test_demo_cache_room.py"
Cohesion: 0.15
Nodes (31): broken_cache(), from_demo_cache(), assert_readers_agree(), _audit(), auditor(), _client(), _collides(), data_dir() (+23 more)

### Community 32 - "walk.ts"
Cohesion: 0.08
Nodes (30): WALK_HEADROOM_M, RotationRing(), captureEditorView(), EditorOrbit, EditorView, pointOnFloor(), resizePlayCamera(), restoreEditorView() (+22 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.07
Nodes (38): le, profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, solve(), Timed, AnthropicLayoutModel (+30 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "RoomView.tsx"
Cohesion: 0.16
Nodes (23): DoorSwings(), flaggedFor(), Navigation(), RoomView(), doorSwing(), footprint(), Pt, toWorld() (+15 more)

### Community 36 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 37 - "ModelReply"
Cohesion: 0.15
Nodes (18): ModelReply, Any, ToolCall, ActivityAnchor, assess_feng_shui(), Assessment, DetailModel, FengShuiRequest (+10 more)

### Community 38 - "scenes.py"
Cohesion: 0.07
Nodes (43): ge, Query, assemble_scene(), Assembly, assets_of(), FurnitureSource, Protocol, RoomScene (+35 more)

### Community 39 - "LayoutToolbox"
Cohesion: 0.14
Nodes (28): LayoutPreferences, LayoutToolbox, RoomScene, What the user asked for, already validated by the server., The three exploration tools for one request, over one `DraftSession`. `call`…, evaluate(), item(), move() (+20 more)

### Community 40 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.11
Nodes (29): FileResponse, HTTPException, demo_room_scenes(), Each demo room with the furniture standing in it, as the editor builds them., demo_floors(), demo_room_scene(), demo_rooms(), demo_shell() (+21 more)

### Community 42 - "Vec2"
Cohesion: 0.07
Nodes (39): ContractModel, BaseModel, AuditReport, ClearanceIssue, CollisionIssue, DoorOpening, FengShuiReport, FengShuiSightline (+31 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.14
Nodes (39): cache_folder(), DemoCache, publish_catalog_scene(), Publish every product imported into `scene_id` (#19), with its retailer…, The scene's published cache, its files verified; None when none is published.…, A scene's folder: readable, and distinct for scene IDs that read alike., read_demo_cache(), _generation() (+31 more)

### Community 45 - "selection_models.py"
Cohesion: 0.09
Nodes (34): Local SQLite transactions for scene identities and recoverable provider…, _diagnostic(), DiscoveredObject, MaskRecord, MeshRecord, MissingMask, BaseModel, Internal #14-#16 records. Source evidence is deliberately separate from… (+26 more)

### Community 46 - "useStore"
Cohesion: 0.09
Nodes (39): playCue(), Furniture, ChatTab(), LibraryTab(), Sidebar(), StatsTab(), tabs, useLiveAudit() (+31 more)

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
Cohesion: 0.08
Nodes (52): WallSegment, LineString, Polygon, Spatial checks independent of HTTP, mesh loading and provider services., A window-openness proxy for layout comparison, not a lighting simulation., CollisionVolume, door_center(), door_entry_segment() (+44 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.15
Nodes (22): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+14 more)

### Community 52 - "layout_tools.py"
Cohesion: 0.13
Nodes (28): _arrangement(), LayoutDraft, Request-local immutable layout drafts: pose-only edits audited against one…, Identity of a layout: equal yaws modulo a full turn are the same arrangement., _Arguments, _CompareArguments, _EvaluateArguments, _findings() (+20 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_api.py"
Cohesion: 0.20
Nodes (16): payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422() (+8 more)

### Community 55 - "Decisions"
Cohesion: 0.07
Nodes (27): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+19 more)

### Community 56 - "Frame"
Cohesion: 0.14
Nodes (22): DiscoveryError, DiscoveryProvider, OfflineProvider, parse_discovery(), Exception, Path, Protocol, fal vision proposes instances across full images; reviewed recordings run… (+14 more)

### Community 57 - "audit_scene"
Cohesion: 0.15
Nodes (29): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 58 - "routes.py"
Cohesion: 0.08
Nodes (30): File, AnnotationResult, Compass, FalVisionAnnotator, NullAnnotator, PlanAnnotator, Protocol, What computer vision cannot read off a floor plan: room labels with their… (+22 more)

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
Cohesion: 0.11
Nodes (19): Architecture, Backend-provided demo models, Chat additions and application, Corrections (#11), Editor play mode, Frontend audio, Furniture evidence selection (#14), Furniture masks and placement evidence (#15) (+11 more)

### Community 68 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "ProviderError"
Cohesion: 0.20
Nodes (9): ProviderError, Exception, A failed model call. `kind` is safe to log; no key or payload is kept., Request, Response, sdk_model(), test_sdk_adapter_maps_http_failures_without_leaking_the_key(), test_sdk_adapter_maps_timeouts() (+1 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "Registry"
Cohesion: 0.24
Nodes (6): Connection, Any, Path, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle., Registry

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "test_room_align_vision.py"
Cohesion: 0.09
Nodes (42): EvidenceFrame, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence…, One video frame an asset was seen in. Optional fields are null for fixtures., The upright frames Dev 2's pipeline stored, for evidence made by…, selection_frames(), _by_index(), _decode(), _fractions() (+34 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.13
Nodes (15): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Free floor area, Front clearance, Internal layout comparison (issue #33) (+7 more)

### Community 76 - "calculate_free_floor_ratio"
Cohesion: 0.24
Nodes (23): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, item(), FurnitureItem, parametrize, RoomScene, Free floor area is distinct from reachable walking space., room() (+15 more)

### Community 77 - "SoundControls.tsx"
Cohesion: 0.26
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

### Community 87 - "detect_collisions"
Cohesion: 0.13
Nodes (36): CollisionIssue, detect_collisions(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, item(), part(), CollisionPart, FurnitureItem (+28 more)

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

### Community 97 - "Prism"
Cohesion: 0.13
Nodes (22): any_overlap(), _bounds_apart(), footprint(), front_zone(), item_occupied(), occupied(), Prism, prisms_overlap() (+14 more)

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "video_furniture.py"
Cohesion: 0.18
Nodes (14): NoFurniture, The room alone: what parsed rooms get until #16 produces furniture assets., geometry_mismatch(), geometry_warning(), BaseModel, RoomScene, Video furniture for a real plan room (#10): Dev 2's extracted items, placed…, Furniture for rooms bound to a video, read from Dev 2's pipeline data directory. (+6 more)

### Community 102 - "test_contracts.py"
Cohesion: 0.16
Nodes (17): load_generator(), load_mock(), RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must…, solid_at(), test_audit_report_must_echo_scene() (+9 more)

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "FixedAnnotator"
Cohesion: 0.12
Nodes (18): FixedAnnotator, Path, Returns pre-recorded annotations (tests, the debug CLI, cached demo plans)., main(), ndarray, ParsedFloor, Debug CLI: parse floor-plan images and write the JSON plus an overlay per…, Draw the contract geometry exactly as returned (metres), not the source image:… (+10 more)

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "retailer.py"
Cohesion: 0.10
Nodes (28): HTMLParser, _binary_models(), _dimensions(), _first_url(), _is_type(), _metres(), _model_urls(), _nodes() (+20 more)

### Community 124 - "agent.py"
Cohesion: 0.17
Nodes (12): Outcome, _Budget, _explain_result(), _explore(), _interpret(), _Interpretation, _percent(), BaseModel (+4 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 130 - "PlayLighting.tsx"
Cohesion: 0.27
Nodes (14): DoorLightBlockers(), LightingEnvironment, PlayLighting(), useEnvironmentSettings(), bounds(), inwardNormal(), ceilingLights(), DEFAULT_PLAY_LIGHTING (+6 more)

### Community 131 - "reconstruct_items.py"
Cohesion: 0.18
Nodes (15): main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), Delivery, computed_field, Every delivered asset passed its checks. Proxies are allowed; they are listed., load_dimensions() (+7 more)

### Community 132 - "FurnitureItem"
Cohesion: 0.29
Nodes (11): FurnitureItem, FengShuiReport, _angle_deg(), calculate_feng_shui(), _front(), _occupant(), FurnitureItem, RoomScene (+3 more)

### Community 133 - "inspect_asset"
Cohesion: 0.18
Nodes (11): _gltf_problems(), inspect_asset(), Re-read an asset's stored file and check it against the furniture profile and…, Scene-graph rules of the furniture profile, read from the file's JSON chunk., load_bindings(), Path, Bindings by scene ID., An asset store served from another prefix publishes, reads and installs alike. (+3 more)

### Community 134 - "rescale_floor"
Cohesion: 0.20
Nodes (11): InvalidScale, ParsedFloor, ValueError, A room of the floor cannot exist at that scale (it would break the contract)., Every room of the floor rescaled; the dimensions now come from the user. Raises…, rescale_floor(), prepare_floor_scale(), The floor of `scene_id` rescaled so that its wall `wall_id` is `length_m` long;… (+3 more)

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
- **410 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+405 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `observe_vision.py`, `test_real_room.py`, `FurnitureItem`, `FurnitureAsset`, `test_room_align.py`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `test_agent.py`, `Pose2D`, `test_objective.py`, `DraftSession`, `test_chat.py`, `test_room_correct.py`, `test_room_parse.py`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `spatial_engine/main.py`, `test_room_shell.py`, `ModelReply`, `scenes.py`, `LayoutToolbox`, `detect_front_clearance`, `demo_assets.py`, `Vec2`, `detect_out_of_bounds`, `generate_mock_glbs.py`, `SpatialInputError`, `layout_tools.py`, `test_api.py`, `audit_scene`, `routes.py`, `test_room_align_vision.py`, `calculate_free_floor_ratio`, `detect_collisions`, `video_furniture.py`, `test_contracts.py`, `FixedAnnotator`, `test_demo_assets.py`, `._check_winding`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `observe_vision.py`, `reconstruct_items.py`, `FurnitureItem`, `inspect_asset`, `catalog.py`, `RoomScene`, `.to_item`, `test_room_align.py`, `test_delivery.py`, `BBoxM`, `Pose2D`, `test_reconstruction.py`, `demo_cache.py`, `detect_blocked_doors`, `scenes.py`, `demo_assets.py`, `Vec2`, `test_demo_cache.py`, `selection_models.py`, `test_contract_occupancy.py`, `test_fixture_scene.py`, `test_room_align_vision.py`, `video_furniture.py`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `FurnitureItem` connect `FurnitureItem` to `observe_vision.py`, `test_real_room.py`, `FurnitureAsset`, `test_room_align.py`, `calculate_reachable_floor_ratio`, `BBoxM`, `test_agent.py`, `Pose2D`, `test_objective.py`, `DraftSession`, `test_chat.py`, `test_room_correct.py`, `detect_blocked_doors`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `LayoutToolbox`, `detect_front_clearance`, `Vec2`, `detect_out_of_bounds`, `SpatialInputError`, `test_contract_occupancy.py`, `audit_scene`, `test_fixture_scene.py`, `calculate_free_floor_ratio`, `detect_collisions`, `furniture_footprint`, `Prism`, `._check_winding`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 209 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 209 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 66 inferred relationships involving `Pose2D` (e.g. with `FurnitureAsset` and `_access()`) actually correct?**
  _`Pose2D` has 66 INFERRED edges - model-reasoned connections that need verification._