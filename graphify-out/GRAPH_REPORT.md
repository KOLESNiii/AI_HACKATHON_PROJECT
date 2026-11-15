# Graph Report - spaceshift-library-main  (2026-11-15)

## Corpus Check
- 219 files · ~326,217 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3256 nodes · 9486 edges · 136 communities (121 shown, 15 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1127 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2fe5a3e7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- test_room_shell.py
- test_room_align_vision.py
- test_real_room.py
- test_scene_routes.py
- audio.test.ts
- catalog.py
- footprint
- test_segmentation.py
- routes.py
- test_room_align.py
- calculate_free_floor_ratio
- test_delivery.py
- segmentation.py
- BBoxM
- test_selection.py
- useStore
- Pose2D
- FurnitureAsset
- test_objective.py
- DraftSession
- regions.py
- detect_collisions
- test_room_correct.py
- test_room_parse.py
- reconstruct_furniture
- layout_tools.py
- detect_blocked_doors
- schema.ts
- parse.py
- calculate_brightness_approximation
- RoomScene
- walk.ts
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- PlayLighting.tsx
- RoomView.tsx
- ModelReply
- annotate.py
- LayoutToolbox
- detect_front_clearance
- demo_assets.py
- ContractModel
- compilerOptions
- test_chat.py
- KnownDimensions
- store.ts
- detect_out_of_bounds
- FloorPlanScreen.tsx
- generate_mock_glbs.py
- SpatialInputError
- test_contract_occupancy.py
- footprint.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_api.py
- Decisions
- DoorOpening
- audit_scene
- test_collision_parts.py
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
- normalisation.py
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
- CatalogError
- .to_item
- model_validator
- README.md
- frontend/package.json
- LayoutMetrics
- main
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- conform_openings
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift
- MeshDouble
- retailer.py
- _Budget
- test_demo_assets.py
- vite
- fetch_product
- test_reconstruction.py
- furniture_proxy
- _Page
- asset_store.py
- test_shared_handoff_case
- divided_access_room
- ._check_winding
- _along_mesh

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 207 edges
2. `FurnitureAsset` - 80 edges
3. `BBoxM` - 79 edges
4. `Registry` - 69 edges
5. `Pose2D` - 67 edges
6. `FurnitureItem` - 67 edges
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
- `test_evidence_matches_the_agreed_shape()` --uses--> `AssetEvidence`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py
- `test_dev1_consumes_fixtures_through_the_asset_interface()` --uses--> `FurnitureAsset`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py

## Import Cycles
- None detected.

## Communities (136 total, 15 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.11
Nodes (42): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., bounds() (+34 more)

### Community 1 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 2 - "test_room_align_vision.py"
Cohesion: 0.04
Nodes (90): Image, MaskSource, EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., AlignmentRecord, main(), _no_frames(), BaseModel (+82 more)

### Community 3 - "test_real_room.py"
Cohesion: 0.07
Nodes (87): Collection, geometry_mismatch(), geometry_warning(), load_bindings(), proxy_warning(), BaseModel, Path, RoomScene (+79 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.16
Nodes (30): _audit(), auditor(), _door(), _leaf_end(), DoorOpening, parametrize, RoomScene, TestClient (+22 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 6 - "catalog.py"
Cohesion: 0.07
Nodes (41): Readers never see a partial file., write_atomic(), CatalogImport, _decode(), ImageProvenance, import_product(), imported_assets(), item_box() (+33 more)

### Community 7 - "footprint"
Cohesion: 0.11
Nodes (25): boundary_distance(), clip_convex(), covered_by(), _crosses_interior(), footprint(), overlap_area(), point_in_polygon(), Point (+17 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.09
Nodes (73): Rect, main(), Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the…, write_report(), Store a mask and cut-out for every selected view of the scene's (or the named)…, Resolve an `EvidenceFrame.mask_url` (relative to the asset data directory). (+65 more)

### Community 9 - "routes.py"
Cohesion: 0.12
Nodes (24): File, HTTPException, PlanAnnotator, Protocol, plan_id_for(), clear_corrections(), get_annotator(), get_plan() (+16 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.12
Nodes (56): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction., Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)., _asset() (+48 more)

### Community 11 - "calculate_free_floor_ratio"
Cohesion: 0.10
Nodes (53): calculate_free_floor_ratio(), RoomScene, Return the usable floor fraction not blocked under the shared headroom rule.…, calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, item(), FurnitureItem (+45 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.16
Nodes (37): Store a finished, profile-conforming `.glb` and return its `glb_url`., store_asset(), check_placed(), deliver_furniture(), RoomScene, A scene's furniture for Dev 1 to place: per item, its checked mesh or its…, Faults in how a scene carries delivered assets; empty when every asset appears…, audit() (+29 more)

### Community 13 - "segmentation.py"
Cohesion: 0.09
Nodes (34): ArtifactTooLarge, box_pixels(), fal_media_url(), FalSamProvider, _fetch(), GrabCutProvider, MaskError, Any (+26 more)

### Community 14 - "BBoxM"
Cohesion: 0.17
Nodes (41): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, NormalisationError, normalise_mesh(), BBoxM, ValueError, Fit a raw glTF 2.0 binary to the furniture profile, store it and return its… (+33 more)

### Community 15 - "test_selection.py"
Cohesion: 0.09
Nodes (76): DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery(), Exception, Path, Protocol (+68 more)

### Community 16 - "useStore"
Cohesion: 0.08
Nodes (35): App(), ORDER, screenVariants, playCue(), EditorScreen(), Sidebar(), useLiveAudit(), HomeScreen() (+27 more)

### Community 17 - "Pose2D"
Cohesion: 0.15
Nodes (51): LayoutProposal, OptimiseRequest, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., Proposed furniture poses. Only poses change: shell, openings, item IDs and…, propose_layout(), LayoutProposal, Explore within the request's limits and return a re-audited proposal or an… (+43 more)

### Community 18 - "FurnitureAsset"
Cohesion: 0.06
Nodes (63): FurnitureItem, Correction, Facing, FurnitureAsset, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder). Evidence…, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., _access(), AlignmentResult (+55 more)

### Community 19 - "test_objective.py"
Cohesion: 0.15
Nodes (46): WindowOpening, compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, item(), FurnitureItem, parametrize (+38 more)

### Community 20 - "DraftSession"
Cohesion: 0.11
Nodes (37): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+29 more)

### Community 21 - "regions.py"
Cohesion: 0.11
Nodes (38): int32, _fallback_scale(), ImageFloor, No usable labels: assume interior door gaps are ESTIMATED_DOOR_M wide, else…, Raster, _accept(), Bridge, _cast() (+30 more)

### Community 22 - "detect_collisions"
Cohesion: 0.19
Nodes (21): CollisionIssue, detect_collisions(), _height_overlaps(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, item(), FurnitureItem, parametrize (+13 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.11
Nodes (38): ParsedFloor, One storey. Every room's coordinates share this floor's frame: metres, origin…, apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, _perimeter() (+30 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.09
Nodes (59): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, FixedAnnotator, PlanAnnotations, Path, Returns pre-recorded annotations (tests, the debug CLI, cached demo plans)., bay_room() (+51 more)

### Community 25 - "reconstruct_furniture"
Cohesion: 0.09
Nodes (34): Labelled, dimensioned proxy boxes (#16): what an item is when it has no usable…, main(), Path, Reconstruct registered furniture. Offline proxies by default; --live uploads to…, write_report(), choose_view(), _clipped(), _Job (+26 more)

### Community 26 - "layout_tools.py"
Cohesion: 0.13
Nodes (25): _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, _metrics(), _Move, _num() (+17 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.20
Nodes (30): BlockedDoorIssue, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize, RoomScene, Door sweep checks using the shared stored hinge and opening conventions. (+22 more)

### Community 28 - "schema.ts"
Cohesion: 0.08
Nodes (32): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_PART_DIMENSION_M, AuditReport (+24 more)

### Community 29 - "parse.py"
Cohesion: 0.12
Nodes (36): FloorCaption, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance(), _consensus() (+28 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.18
Nodes (28): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item(), FurnitureItem (+20 more)

### Community 31 - "RoomScene"
Cohesion: 0.06
Nodes (62): RoomScene, ge, Query, furniture_data_dir(), Path, Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served…, health() (+54 more)

### Community 32 - "walk.ts"
Cohesion: 0.07
Nodes (35): WALK_HEADROOM_M, AuditStats(), captureEditorView(), EditorOrbit, EditorView, floor, PlayControllerHandle, pointOnFloor() (+27 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.08
Nodes (46): Outcome, profile(), RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, solve(), AnthropicLayoutModel, _explain_result(), _explore() (+38 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "PlayLighting.tsx"
Cohesion: 0.28
Nodes (13): LightingEnvironment, PlayLighting(), useEnvironmentSettings(), bounds(), ceilingLights(), DEFAULT_PLAY_LIGHTING, LightPosition, PlayLightingSettings (+5 more)

### Community 36 - "RoomView.tsx"
Cohesion: 0.12
Nodes (29): MIN_HEIGHT_OVERLAP_M, MIN_PLAN_OVERLAP_M2, DoorSwings(), Furniture, flaggedFor(), Navigation(), RoomView(), DoorLightBlockers() (+21 more)

### Community 37 - "ModelReply"
Cohesion: 0.23
Nodes (6): ModelReply, Any, ToolCall, Any, RecordedModel, test_route()

### Community 38 - "annotate.py"
Cohesion: 0.10
Nodes (21): AnnotationResult, Compass, _extract_json(), FalVisionAnnotator, NullAnnotator, BaseModel, What computer vision cannot read off a floor plan: room labels with their…, Reads labels with a vision LLM on fal.ai (`FAL_KEY`). The endpoint and model… (+13 more)

### Community 39 - "LayoutToolbox"
Cohesion: 0.17
Nodes (27): LayoutPreferences, LayoutToolbox, What the user asked for, already validated by the server., The three exploration tools for one request, over one `DraftSession`. `call`…, evaluate(), item(), move(), Any (+19 more)

### Community 40 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 41 - "demo_assets.py"
Cohesion: 0.11
Nodes (28): FileResponse, demo_room_scenes(), Each demo room with the furniture standing in it, as the editor builds them., demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model() (+20 more)

### Community 42 - "ContractModel"
Cohesion: 0.15
Nodes (20): ContractModel, BaseModel, BlockedDoorIssue, ClearanceIssue, CollisionIssue, CollisionPart, FengShuiReport, FengShuiSightline (+12 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_chat.py"
Cohesion: 0.09
Nodes (51): add_item(), AddItemArguments, chat(), ChatReply, ChatRequest, _percent(), AuditReport, BaseModel (+43 more)

### Community 45 - "KnownDimensions"
Cohesion: 0.11
Nodes (20): main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), AssetCheck, Delivery, _gltf_problems(), inspect_asset() (+12 more)

### Community 46 - "store.ts"
Cohesion: 0.09
Nodes (31): LayoutGoal, ChatTab(), LibraryTab(), StatsTab(), tabs, catalog, catalogCategories, CatalogItem (+23 more)

### Community 47 - "detect_out_of_bounds"
Cohesion: 0.23
Nodes (23): detect_out_of_bounds(), Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary., room() (+15 more)

### Community 48 - "FloorPlanScreen.tsx"
Cohesion: 0.18
Nodes (20): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), area(), DEFAULT_ROOM_ID (+12 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "SpatialInputError"
Cohesion: 0.06
Nodes (65): Vec2, WallSegment, A point on the floor plan (Y omitted)., FengShuiReport, LineString, Spatial checks independent of HTTP, mesh loading and provider services., A window-openness proxy for layout comparison, not a lighting simulation., _angle_deg() (+57 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.16
Nodes (21): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+13 more)

### Community 52 - "footprint.py"
Cohesion: 0.17
Nodes (19): any_overlap(), _bounds_apart(), front_zone(), item_occupied(), occupied(), Prism, prisms_overlap(), BBoxM (+11 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_api.py"
Cohesion: 0.09
Nodes (37): AuditReport, payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422() (+29 more)

### Community 55 - "Decisions"
Cohesion: 0.08
Nodes (26): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+18 more)

### Community 56 - "DoorOpening"
Cohesion: 0.15
Nodes (19): DoorOpening, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, closed_leaf(), door_approach(), door_sweep(), DoorOpening, WallSegment, WindowOpening (+11 more)

### Community 57 - "audit_scene"
Cohesion: 0.22
Nodes (23): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+15 more)

### Community 58 - "test_collision_parts.py"
Cohesion: 0.26
Nodes (16): item(), part(), CollisionPart, FurnitureItem, parametrize, Occupied-volume integration with the merged Dev 2 contract and fixture., test_disjoint_intersections_are_summed(), test_fallback_solid_box_and_fixed_item_are_checked() (+8 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "Furniture.tsx"
Cohesion: 0.16
Nodes (16): floorPlane, Mesh(), MeshBoundary, ProxyBox(), categoryWash, disposeInk(), inkify(), inkLine (+8 more)

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
Nodes (19): Architecture, Backend-provided demo models, Chat additions and application, Corrections (#11), Editor play mode, Frontend audio, Furniture evidence selection (#14), Furniture masks and placement evidence (#15) (+11 more)

### Community 68 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "ProviderError"
Cohesion: 0.18
Nodes (11): Any, Timed, ProviderError, Exception, A failed model call. `kind` is safe to log; no key or payload is kept., Request, Response, sdk_model() (+3 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "Registry"
Cohesion: 0.22
Nodes (7): Connection, Any, Path, Only the winner submits; a crash before recording its handle is explicit…, Only a known pre-submit failure is safe to release; never remove a saved handle., Registry, test_changed_mask_invalidates_mesh_and_racing_mask_is_not_attached()

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "furniture_footprint"
Cohesion: 0.18
Nodes (21): Polygon, CollisionVolume, front_clearance_zone(), furniture_collision_volumes(), furniture_footprint(), FurnitureItem, An item's occupied box transformed into a vertical prism in room space., Transform validated local collision boxes; absent parts mean one solid bbox.… (+13 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.13
Nodes (15): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Free floor area, Front clearance, Internal layout comparison (issue #33) (+7 more)

### Community 76 - "normalisation.py"
Cohesion: 0.14
Nodes (16): BBoxM, CollisionPart, Category collision templates fitted to `bbox_m` (spec 6.4, source 1).…, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), NormalisedMesh, Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`., _bounds() (+8 more)

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
Cohesion: 0.29
Nodes (7): Completion and follow-up, Consuming the findings, Editor integration status (issues #32 and #35), HTTP handoff contract, Layout suggestions (`POST /solve`), Load the same examples in the editor and backend, Spatial findings: Dev 3 / Dev 4 handoff

### Community 95 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

### Community 96 - "CatalogError"
Cohesion: 0.17
Nodes (14): CatalogError, _check_public(), fetch_public(), ValueError, The product cannot be imported at all. The message is safe to show., Refuse anything but http(s) to a public address: an imported URL is untrusted…, Download a public URL with a size cap, re-checking every redirect hop., test_download_deadline_stops_trickling_response() (+6 more)

### Community 97 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 102 - "main"
Cohesion: 0.19
Nodes (13): main(), Path, write_report(), Fetch, One retailer product, from its page (`url_import`) or a search result…, IKEA products matching `query`, as `catalog_search` results. A result carries…, RetailerProduct, search_ikea() (+5 more)

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "conform_openings"
Cohesion: 0.15
Nodes (13): InvalidScale, ValueError, A room of the floor cannot exist at that scale (it would break the contract)., conform_openings(), RoomScene, Put every door exactly on its wall, so the spatial audit accepts the room. Each…, length(), parametrize (+5 more)

### Community 122 - "MeshDouble"
Cohesion: 0.26
Nodes (12): CaptureFixture, test_a_mesh_that_cannot_be_normalised_is_delivered_as_its_proxy(), test_a_provider_failure_keeps_both_items_as_proxies(), test_cli_runs_the_checks_and_reports(), test_a_mesh_that_cannot_be_normalised_keeps_its_proxy_and_says_so(), masked_scene(), MeshDouble, test_failures_are_explicit_with_dimensioned_proxies_and_keep_old_mesh() (+4 more)

### Community 123 - "retailer.py"
Cohesion: 0.14
Nodes (24): _binary_models(), _dimensions(), _first_url(), _is_type(), _metres(), _model_urls(), _nodes(), parse_product_page() (+16 more)

### Community 124 - "_Budget"
Cohesion: 0.17
Nodes (8): AgentLimits, _Budget, _interpret(), _Interpretation, BaseModel, OptimiseRequest, Read the instruction. Returns (interpretation or None, assistant still usable)., One allowance per request. Retries and the interpretation call spend the same…

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "fetch_product"
Cohesion: 0.22
Nodes (11): fetch_product(), guess_category(), Category, Classify the head phrase, using its last furniture or accessory noun.…, Download and read one retailer product page. Raises CatalogError. `source`…, parametrize, test_categories_come_from_the_products_own_words(), test_category_uses_head_noun() (+3 more)

### Community 128 - "test_reconstruction.py"
Cohesion: 0.07
Nodes (48): FailureKind, Mask, The next published model that is usable and within the triangle budget. Each…, fetch_bounded(), Stream a provider artifact without redirects, enforcing `limit` while reading., FalSam3dProvider, _fetch(), inspect_mesh() (+40 more)

### Community 129 - "furniture_proxy"
Cohesion: 0.25
Nodes (8): le, furniture_proxy(), health(), get, gt, Path, Response, Process liveness only; does not probe external providers.

### Community 130 - "_Page"
Cohesion: 0.29
Nodes (3): HTMLParser, _Page, The few things a product page is read for: JSON-LD, meta tags, title and…

### Community 131 - "asset_store.py"
Cohesion: 0.33
Nodes (5): APIRouter, asset_router(), Path, Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`.

### Community 132 - "test_shared_handoff_case"
Cohesion: 0.33
Nodes (4): Any, parametrize, Reusable scene variants and expected findings for Dev 3/4 integration., test_shared_handoff_case()

### Community 133 - "divided_access_room"
Cohesion: 0.40
Nodes (4): divided_access_room(), RoomScene, Shared regression geometry for custom layout access checks., Clearing a wardrobe by moving its blocker behind the divider cuts circulation.

### Community 135 - "_along_mesh"
Cohesion: 0.67
Nodes (3): _along_mesh(), BBoxM, Published width and depth, assigned to X and Z of a shape with these extents.…

## Knowledge Gaps
- **394 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+389 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `test_room_shell.py`, `test_room_align_vision.py`, `test_real_room.py`, `test_shared_handoff_case`, `divided_access_room`, `._check_winding`, `footprint`, `test_scene_routes.py`, `routes.py`, `test_room_align.py`, `calculate_free_floor_ratio`, `test_delivery.py`, `Pose2D`, `FurnitureAsset`, `test_objective.py`, `DraftSession`, `test_room_correct.py`, `test_room_parse.py`, `layout_tools.py`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `spatial_engine/main.py`, `LayoutToolbox`, `detect_front_clearance`, `demo_assets.py`, `ContractModel`, `test_chat.py`, `detect_out_of_bounds`, `generate_mock_glbs.py`, `SpatialInputError`, `test_api.py`, `audit_scene`, `test_collision_parts.py`, `conform_openings`, `test_demo_assets.py`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `test_reconstruction.py`, `.to_item`, `test_room_align_vision.py`, `test_scene_routes.py`, `catalog.py`, `test_fixture_scene.py`, `demo_assets.py`, `ContractModel`, `test_room_align.py`, `test_delivery.py`, `KnownDimensions`, `BBoxM`, `Pose2D`, `test_contract_occupancy.py`, `reconstruct_furniture`, `MeshDouble`, `RoomScene`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_reconstruction.py`, `test_catalog.py`, `divided_access_room`, `_along_mesh`, `footprint`, `calculate_free_floor_ratio`, `test_delivery.py`, `Pose2D`, `FurnitureAsset`, `test_objective.py`, `DraftSession`, `detect_collisions`, `detect_blocked_doors`, `calculate_brightness_approximation`, `LayoutToolbox`, `detect_front_clearance`, `ContractModel`, `test_chat.py`, `KnownDimensions`, `detect_out_of_bounds`, `footprint.py`, `audit_scene`, `test_collision_parts.py`, `furniture_footprint`, `normalisation.py`, `main`, `MeshDouble`, `retailer.py`, `fetch_product`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 204 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 204 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 76 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Registry` (e.g. with `RetailerModelProvider` and `FalSamProvider`) actually correct?**
  _`Registry` has 13 INFERRED edges - model-reasoned connections that need verification._