# Graph Report - AI_HACKATHON_PROJECT  (2026-11-15)

## Corpus Check
- 270 files · ~411,052 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3971 nodes · 11903 edges · 148 communities (131 shown, 17 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1381 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4f669e8b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- test_scene_cache.py
- align_debug.py
- test_real_room.py
- test_scene_routes.py
- audio.test.ts
- test_room_align_vision.py
- footprint.py
- test_segmentation.py
- Frame
- test_room_align.py
- calculate_reachable_floor_ratio
- test_delivery.py
- Box
- BBoxM
- test_selection.py
- App.tsx
- propose_layout
- single_room
- Pose2D
- DraftSession
- regions.py
- SpatialInputError
- test_room_correct.py
- test_room_parse.py
- reconstruct_furniture
- test_contracts.py
- detect_blocked_doors
- contracts.ts
- parse.py
- calculate_brightness_approximation
- routes.py
- walk.ts
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- RoomView.tsx
- test_room_shell.py
- test_feng_shui_optimisation.py
- RoomScene
- agent.ts
- ContractModel
- chat.py
- score_feng_shui
- compilerOptions
- test_demo_cache.py
- Sidebar.tsx
- layoutProgress.test.tsx
- detect_out_of_bounds
- feng_shui.py
- generate_mock_glbs.py
- Vec2
- test_contract_occupancy.py
- FurnitureAsset
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- FixedAnnotator
- Decisions
- LayoutToolbox
- audit_scene
- scene_cache.py
- compilerOptions
- Video frame selection and furniture identity — issue #14
- react
- Dev 2 → Dev 1 asset handoff
- dependencies
- devDependencies
- raster.py
- polygon.py
- Architecture
- Dev 4 implementation and integration plan
- AnthropicLayoutModel
- Agent Instructions
- test_fixture_scene.py
- Registry
- Implementation plan: issue #14
- Spatial engine
- Point
- store.ts
- scripts
- scene_cache/README.md
- SpaceShift — System Architecture & 4-Developer Execution DAG
- Asset Handoff Agreement Implementation Plan
- Review Focus
- Review Focus
- Floor-plan parser (Dev 1)
- Furniture masks and placement evidence — issue #15
- calculate_free_floor_ratio
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
- test_layout_tools.py
- SelectedObject
- README.md
- frontend/package.json
- furniture_search.py
- objective.py
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- RetailerProduct
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift
- SKILL.md
- manifest.json
- retailer.py
- agent.py
- test_demo_assets.py
- vite
- catalog.py
- openings.py
- Validated, cached demo assets (#20, Dev 2.8)
- PlayLighting.tsx
- fetch_product
- FurnitureItem
- AuditReport
- reconstruction/main.py
- plugins
- test_reconstruction.py
- catalog_router
- demo_cache/README.md
- editorControls.test.ts
- CatalogError
- furniture_proxy
- footprint
- rescale_floor
- apply_pose_edit
- _plan_parts
- unpack_model
- ._check_winding
- _point

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 230 edges
2. `useStore` - 91 edges
3. `FurnitureAsset` - 91 edges
4. `BBoxM` - 83 edges
5. `Pose2D` - 80 edges
6. `FurnitureItem` - 80 edges
7. `SpatialInputError` - 72 edges
8. `Registry` - 69 edges
9. `propose_layout()` - 64 edges
10. `audit_scene()` - 61 edges

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

## Communities (148 total, 17 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.10
Nodes (47): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., bounds() (+39 more)

### Community 1 - "test_scene_cache.py"
Cohesion: 0.08
Nodes (45): Serve a published plan (`scene_cache.py`, #12) as if it had been uploaded and…, restore_plan(), differences(), Serve every plan published in `cache_dir` (`routes.restore_plan`); a plan…, Where two JSON-like values differ: the paths, such as…, restore_published(), _audit(), auditor() (+37 more)

### Community 2 - "align_debug.py"
Cohesion: 0.06
Nodes (44): AlignmentRecord, AlignmentResult, _Capture, pose_error(), FrameSource, FurnitureItem, RoomScene, Debug CLI for furniture alignment: place assets in a room and draw the result.… (+36 more)

### Community 3 - "test_real_room.py"
Cohesion: 0.08
Nodes (80): Collection, geometry_mismatch(), proxy_warning(), RoomScene, Why `room` is not the room `binding` was made for, or None when it is. Compares…, still_extracting(), clear_cache(), Forget assembled scenes (tests, or after the furniture source changes). (+72 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.11
Nodes (39): NoFurniture, What a furniture source supplies for one room., The room alone: what parsed rooms get until #16 produces furniture assets., SceneFurniture, geometry_warning(), Video furniture for a real plan room (#10): Dev 2's extracted items, placed…, Furniture for rooms bound to a video, read from Dev 2's pipeline data directory., The video's published demo cache, or the not-extracted answer when there is… (+31 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (25): listeners, onSoundCue(), PartialTone, renderCue(), SoundCue, tones, AudioEngine, AudioPlatform (+17 more)

### Community 6 - "test_room_align_vision.py"
Cohesion: 0.06
Nodes (67): Image, MaskSource, EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., SelectionResult, main(), Path, build_prompt() (+59 more)

### Community 7 - "footprint.py"
Cohesion: 0.15
Nodes (23): any_overlap(), _bounds_apart(), closed_leaf(), door_approach(), door_sweep(), Prism, prisms_overlap(), DoorOpening (+15 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.13
Nodes (55): Rect, Store a mask and cut-out for every selected view of the scene's (or the named)…, Resolve an `EvidenceFrame.mask_url` (relative to the asset data directory)., read_mask(), segment_furniture(), box_mask(), FakeProvider, iou() (+47 more)

### Community 9 - "Frame"
Cohesion: 0.14
Nodes (34): DiscoveryProvider, OfflineProvider, Protocol, fal vision proposes instances across full images; reviewed recordings run…, Reviewed detections keyed by full source frame keys, never by batch position., RecordedProvider, Local SQLite transactions for scene identities and recoverable provider…, main() (+26 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.11
Nodes (60): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, item_occupied(), FurnitureItem, FixedObserver, NullObserver, No hints: every asset gets the default wall placement, flagged for correction. (+52 more)

### Community 11 - "calculate_reachable_floor_ratio"
Cohesion: 0.17
Nodes (29): calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, divided_room(), obstacle(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.14
Nodes (41): Store a finished, profile-conforming `.glb` and return its `glb_url`., store_asset(), main(), Path, write_report(), check_placed(), deliver_furniture(), Path (+33 more)

### Community 13 - "Box"
Cohesion: 0.07
Nodes (50): ArtifactTooLarge, box_pixels(), fal_media_url(), FalSamProvider, _fetch(), fetch_bounded(), GrabCutProvider, MaskError (+42 more)

### Community 14 - "BBoxM"
Cohesion: 0.13
Nodes (48): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, BBoxM, CollisionPart, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), NormalisedMesh (+40 more)

### Community 15 - "test_selection.py"
Cohesion: 0.15
Nodes (38): DiscoveryError, FalVisionProvider, parse_discovery(), Exception, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, _diagnostic(), DiscoveredObject, Discovery (+30 more)

### Community 16 - "App.tsx"
Cohesion: 0.08
Nodes (36): App(), ORDER, screenVariants, FloorPlanScreen(), Openings(), PlanRoom(), plural(), points() (+28 more)

### Community 17 - "propose_layout"
Cohesion: 0.11
Nodes (69): OptimiseRequest, propose_layout(), ProviderError, LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, A failed model call. `kind` is safe to log; no key or payload is kept., OptimiseRequest, solve_events() (+61 more)

### Community 18 - "single_room"
Cohesion: 0.16
Nodes (21): bay_room(), _canvas(), l_room(), _png(), ndarray, Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820),…, L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed., 4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m… (+13 more)

### Community 19 - "Pose2D"
Cohesion: 0.14
Nodes (49): Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, test_full_scoring_is_opt_in_and_the_comparator_requires_it(), item() (+41 more)

### Community 20 - "DraftSession"
Cohesion: 0.11
Nodes (38): _arrangement(), DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one… (+30 more)

### Community 21 - "regions.py"
Cohesion: 0.14
Nodes (31): int32, Raster, _accept(), _cast(), draw_bridges(), _end_direction(), _exit_point(), find_bridges() (+23 more)

### Community 22 - "SpatialInputError"
Cohesion: 0.08
Nodes (69): ChatRequest, POST /chat and /chat/stream., add_item(), chat(), ChatReply, ChatRequest, FurnitureItem, ProgressCallback (+61 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.15
Nodes (29): carry_furniture(), corrected_shell_url(), geometry_digest(), _perimeter(), RoomScene, `old`'s furniture in the rescaled `room`, relative to the same walls. Each…, Short hash of the geometry a shell is built from., `.../shells/<scene_id>.glb` -> `.../shells/<scene_id>.<digest>.glb`. (+21 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.14
Nodes (38): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, PlanAnnotations, client(), The reconstruction routes with the asset store mounted on this test's data…, _close(), _example() (+30 more)

### Community 25 - "reconstruct_furniture"
Cohesion: 0.18
Nodes (24): RawMesh, main(), choose_view(), _clipped(), Path, The one masked view to reconstruct from: confident, then whole, then large., Give every (or each named) item of the scene its own raw mesh, and always a…, reconstruct_furniture() (+16 more)

### Community 26 - "test_contracts.py"
Cohesion: 0.16
Nodes (17): load_generator(), load_mock(), RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are…, schema.ts treats every non-nullable field as present, so the fixture must…, solid_at(), test_audit_report_must_echo_scene() (+9 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.18
Nodes (33): BlockedDoorIssue, BlockedDoorIssue, CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem (+25 more)

### Community 28 - "contracts.ts"
Cohesion: 0.06
Nodes (47): ChatStreamEvent, GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, LayoutProgressStage, LayoutStreamEvent, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES (+39 more)

### Community 29 - "parse.py"
Cohesion: 0.11
Nodes (38): RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance(), _consensus(), _fallback_scale() (+30 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.13
Nodes (35): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, A window-openness proxy for layout comparison, not a lighting simulation., Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item() (+27 more)

### Community 31 - "routes.py"
Cohesion: 0.07
Nodes (34): File, plan_id_for(), decode(), NDArray, uint8, ValueError, UnreadableImage, clear_corrections() (+26 more)

### Community 32 - "walk.ts"
Cohesion: 0.09
Nodes (30): WALK_HEADROOM_M, captureEditorView(), EditorOrbit, EditorView, floor, PlayControllerHandle, pointOnFloor(), resizePlayCamera() (+22 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.05
Nodes (62): exception_handler, FengShuiResult, JSONResponse, RequestValidationError, demo_room_scenes(), profile(), Any, RoomScene (+54 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "RoomView.tsx"
Cohesion: 0.11
Nodes (33): DoorSwings(), floorPlane, Furniture, PlanDiff(), flaggedFor(), Navigation(), RoomView(), RotationRing() (+25 more)

### Community 36 - "test_room_shell.py"
Cohesion: 0.05
Nodes (84): int64, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+76 more)

### Community 37 - "test_feng_shui_optimisation.py"
Cohesion: 0.14
Nodes (24): ModelReply, Any, ToolCall, assess_feng_shui(), FengShuiRequest, Any, original_room(), Scripted (+16 more)

### Community 38 - "RoomScene"
Cohesion: 0.05
Nodes (70): RoomScene, FileResponse, ge, HTTPException, Query, demo_cache_dir(), Where published demo furniture is read from when the pipeline has none (#20).…, demo_floors() (+62 more)

### Community 39 - "agent.ts"
Cohesion: 0.08
Nodes (50): AuditDiff(), LayoutProposalCard(), poseText(), ScoreComparison, useProposalScores(), isLibraryAsset(), AgentReply, describeOutlook() (+42 more)

### Community 40 - "ContractModel"
Cohesion: 0.08
Nodes (40): ChatErrorEvent, ChatProgressEvent, ChatReplyEvent, ContractModel, _FengShuiModel, LayoutErrorEvent, LayoutProgressEvent, LayoutResultEvent (+32 more)

### Community 41 - "chat.py"
Cohesion: 0.11
Nodes (21): ChatReply, POST /chat response, and the data of /chat/stream's terminal `reply` event., AddItemArguments, _percent(), place(), PlaceRequest, AuditReport, BaseModel (+13 more)

### Community 42 - "score_feng_shui"
Cohesion: 0.11
Nodes (61): FengShuiRequest, POST /feng-shui and /feng-shui/score., FengShuiSightline, RuleScore, _add(), _angle_deg(), _backing(), _balance() (+53 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.05
Nodes (105): cache_folder(), CachedFile, CacheError, current_generation(), DemoCache, _inside(), install_demo_cache(), _intact() (+97 more)

### Community 45 - "Sidebar.tsx"
Cohesion: 0.09
Nodes (25): MAX_LAYOUT_INSTRUCTION_CHARS, CatalogPreview(), FengShuiScoreCard(), AuditStats(), ChatTab(), FengShuiSection(), LibraryTab(), ProductCard() (+17 more)

### Community 46 - "layoutProgress.test.tsx"
Cohesion: 0.08
Nodes (29): HarnessProgress(), HarnessStatus(), catalog, catalogCategories, fixture, freshMockScene(), mockScene, proposalSummary() (+21 more)

### Community 47 - "detect_out_of_bounds"
Cohesion: 0.15
Nodes (28): detect_out_of_bounds(), RoomScene, Return sorted item IDs whose rectangular footprint leaves the interior floor.…, item(), FurnitureItem, parametrize, RoomScene, Whole-footprint containment against the authoritative usable floor boundary. (+20 more)

### Community 48 - "feng_shui.py"
Cohesion: 0.22
Nodes (11): Assessment, FengShuiResult, Finding, DetailModel, AuditReport, BaseModel, FengShuiRequest, Shared Feng Shui inputs and validation, independent of the model harness. (+3 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "Vec2"
Cohesion: 0.13
Nodes (32): DoorOpening, Vec2, WallSegment, A point on the floor plan (Y omitted)., A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, door_center(), door_entry_segment(), _door_frame() (+24 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.15
Nodes (22): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+14 more)

### Community 52 - "FurnitureAsset"
Cohesion: 0.08
Nodes (43): Correction, Facing, FurnitureAsset, FurnitureItem, model_validator, Pose2D, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., Dev 1 places the asset: add the pose it aligned from the floor plan. (+35 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "FixedAnnotator"
Cohesion: 0.08
Nodes (29): AnnotationResult, Compass, _extract_json(), FalVisionAnnotator, FixedAnnotator, FloorCaption, NullAnnotator, PlanAnnotator (+21 more)

### Community 55 - "Decisions"
Cohesion: 0.06
Nodes (35): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+27 more)

### Community 56 - "LayoutToolbox"
Cohesion: 0.16
Nodes (16): _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, LayoutToolbox, _metrics(), _Move (+8 more)

### Community 57 - "audit_scene"
Cohesion: 0.22
Nodes (23): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+15 more)

### Community 58 - "scene_cache.py"
Cohesion: 0.10
Nodes (40): _assemble(), cache_path(), CachedScene, _check(), _faults(), _images(), main(), _named() (+32 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "react"
Cohesion: 0.26
Nodes (11): MeshBoundary, ProxyBox(), FurnitureMesh(), categoryWash, disposeInk(), inkify(), inkLine, Shell (+3 more)

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
Cohesion: 0.25
Nodes (10): Gray, estimate_wall_px(), flatten_illumination(), Mask, rasterise(), Image → binary masks: all ink, and the structural strokes that are walls.…, Divide by a smooth estimate of the paper so a photographed printout thresholds…, Thickness of the main walls: the dominant stroke width, weighted towards thick… (+2 more)

### Community 66 - "polygon.py"
Cohesion: 0.22
Nodes (16): area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), float64, Mask, NDArray (+8 more)

### Community 67 - "Architecture"
Cohesion: 0.07
Nodes (28): Architecture, Backend-provided demo models, Bundled retailer library, Chat additions and application, Corrections (#11), Demo scene cache (#12), Editor Feng Shui score integration, Editor layout review and live Stats (+20 more)

### Community 68 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "AnthropicLayoutModel"
Cohesion: 0.29
Nodes (6): AnthropicLayoutModel, Claude through the official SDK. The loop above owns retries, so the SDK makes…, Request, Response, sdk_model(), test_sdk_adapter_sends_the_expected_request_and_parses_tool_calls()

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "test_fixture_scene.py"
Cohesion: 0.22
Nodes (3): The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape()

### Community 73 - "Registry"
Cohesion: 0.08
Nodes (22): Connection, Mask, The retailer's own published model as the item's raw mesh. No inference and no…, The next published model that is usable and within the triangle budget. Each…, RetailerModelProvider, FalSam3dProvider, Any, Mask (+14 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.11
Nodes (19): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Feng shui score, Free floor area, Front clearance (+11 more)

### Community 76 - "Point"
Cohesion: 0.11
Nodes (23): boundary_distance(), clip_convex(), covered_by(), _crosses_interior(), overlap_area(), point_in_polygon(), Point, Sutherland-Hodgman: the part of `subject` inside the convex polygon `clip`. (+15 more)

### Community 77 - "store.ts"
Cohesion: 0.08
Nodes (41): playCue(), EditorScreen(), Sidebar(), useLiveAudit(), VersionTree(), VersionTreeView(), CatalogItem, connectEditorServices() (+33 more)

### Community 78 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

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
Cohesion: 0.18
Nodes (9): Corrections (#11), Demo scene cache (#12), Floor-plan parser (Dev 1), Furniture alignment (#8), How it works, Real-input room (#10), Scene assembly (#9), Status and limits (+1 more)

### Community 85 - "Furniture masks and placement evidence — issue #15"
Cohesion: 0.22
Nodes (8): Approaches, Design, Furniture masks and placement evidence — issue #15, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 20 requests), Live result (2026-11-14), Needs coordination

### Community 86 - "calculate_free_floor_ratio"
Cohesion: 0.24
Nodes (23): calculate_free_floor_ratio(), Return the usable floor fraction not blocked under the shared headroom rule.…, item(), FurnitureItem, parametrize, RoomScene, Free floor area is distinct from reachable walking space., room() (+15 more)

### Community 87 - "detect_collisions"
Cohesion: 0.09
Nodes (63): ClearanceIssue, CollisionIssue, detect_collisions(), detect_front_clearance(), FurnitureItem, Report each overlapping pair once, in stable item-ID order. Whole bounding…, Check full-width front access strips, returning one issue per blocker. actual_m…, item() (+55 more)

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
Cohesion: 0.17
Nodes (12): Bot additions restricted to mesh Library assets, Completion and follow-up, Consuming the findings, Deterministic Feng Shui score in the editor, Editor integration status (issues #32 and #35), HTTP handoff contract, Layout suggestions (`POST /solve`), Live execution updates (+4 more)

### Community 95 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

### Community 96 - "furniture_footprint"
Cohesion: 0.20
Nodes (20): front_clearance_zone(), furniture_collision_volumes(), furniture_footprint(), prepare_furniture(), FurnitureItem, Polygon, Transform validated local collision boxes; absent parts mean one solid bbox.…, Return the rotated width/depth rectangle in room X/Z coordinates. Pose is the… (+12 more)

### Community 97 - "test_layout_tools.py"
Cohesion: 0.21
Nodes (23): evaluate(), item(), move(), Any, FurnitureItem, parametrize, RoomScene, Scripted tool calls: validation, shared budget, duplicates and best-draft… (+15 more)

### Community 98 - "SelectedObject"
Cohesion: 0.12
Nodes (12): Path, model_validator, The stored mask for a sighting, unless its box has changed since., The stored raw mesh, unless the mask it was made from has been replaced since., SelectedObject, Sighting, overlap(), _select_views() (+4 more)

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "furniture_search.py"
Cohesion: 0.19
Nodes (22): IkeaSearch, PageReader, ProductOption, _host(), _ikea_options(), _linkup_urls(), _option(), Any (+14 more)

### Community 102 - "objective.py"
Cohesion: 0.11
Nodes (19): _access_not_worse(), beats_original(), _check_comparable(), compare_evaluations(), _door_overlap_area(), is_acceptable_proposal(), LayoutComparison, LayoutMetrics (+11 more)

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "RetailerProduct"
Cohesion: 0.21
Nodes (19): One retailer product, from its page (`url_import`) or a search result…, RetailerProduct, Exception, No search could run (no key, provider down). The message is safe to show., SearchUnavailable, ikea(), Linkup, product() (+11 more)

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "retailer.py"
Cohesion: 0.10
Nodes (28): HTMLParser, _binary_models(), _dimensions(), _first_url(), _is_type(), _metres(), _model_urls(), _nodes() (+20 more)

### Community 124 - "agent.py"
Cohesion: 0.08
Nodes (30): Outcome, AgentLimits, _Budget, _explain_result(), _explore(), _interpret(), _Interpretation, LayoutCancelled (+22 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "catalog.py"
Cohesion: 0.04
Nodes (95): fetch(), main(), prepare(), Fetch a balanced, offline IKEA library using only published retailer meshes.…, Reuse bounded, public-only downloads; keep raw evidence outside the project., Content-addressed store for servable furniture `.glb` files (spec 7.3). A file…, Readers never see a partial file., write_atomic() (+87 more)

### Community 128 - "openings.py"
Cohesion: 0.17
Nodes (15): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+7 more)

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 130 - "PlayLighting.tsx"
Cohesion: 0.19
Nodes (21): LightingPanel(), DoorLightBlockers(), LightingEnvironment, LightSourceInteraction(), PlayLighting(), useEnvironmentSettings(), Button(), inwardNormal() (+13 more)

### Community 131 - "fetch_product"
Cohesion: 0.15
Nodes (16): fetch_product(), guess_category(), Category, Fetch, Classify the head phrase, using its last furniture or accessory noun.…, Download and read one retailer product page. Raises CatalogError. `source`…, IKEA products matching `query`, as `catalog_search` results. A result carries…, search_ikea() (+8 more)

### Community 132 - "FurnitureItem"
Cohesion: 0.07
Nodes (53): FurnitureItem, FengShuiReport, height_overlaps(), Spatial checks independent of HTTP, mesh loading and provider services., _angle_deg(), calculate_feng_shui(), _front(), _occupant() (+45 more)

### Community 133 - "AuditReport"
Cohesion: 0.17
Nodes (19): AuditReport, payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422() (+11 more)

### Community 134 - "reconstruction/main.py"
Cohesion: 0.18
Nodes (13): import_url(), ImportRequest, BaseModel, Editor URL imports through the existing, public-address-only retailer pipeline., furniture_data_dir(), Path, Runtime settings of the reconstruction service., Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served… (+5 more)

### Community 135 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 136 - "test_reconstruction.py"
Cohesion: 0.10
Nodes (34): FailureKind, RuntimeError, asset_router(), APIRouter, Path, `GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`., MeshError, Exception (+26 more)

### Community 137 - "catalog_router"
Cohesion: 0.18
Nodes (13): catalog_router(), APIRouter, Fetch, Path, `fetch` replaces the public downloader (tests)., client(), MonkeyPatch, parametrize (+5 more)

### Community 139 - "editorControls.test.ts"
Cohesion: 0.32
Nodes (8): editorKey(), handleItemKey(), handleSaveKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, initial

### Community 140 - "CatalogError"
Cohesion: 0.11
Nodes (21): _decode(), item_box(), NDArray, uint8, An upright BGR image; transparency becomes white, as in a product shot., Where the product is in its image, and whether that was read off a plain…, CatalogError, _check_public() (+13 more)

### Community 141 - "furniture_proxy"
Cohesion: 0.25
Nodes (8): le, furniture_proxy(), health(), get, gt, Path, Response, Process liveness only; does not probe external providers.

### Community 143 - "footprint"
Cohesion: 0.29
Nodes (11): footprint(), front_zone(), occupied(), BBoxM, CollisionPart, Pose2D, A local rectangle (centre x/z, extents along local X/Z) in room coordinates., The whole `bbox_m` box: what must stay inside the room. (+3 more)

### Community 144 - "rescale_floor"
Cohesion: 0.25
Nodes (9): InvalidScale, ParsedFloor, ValueError, A room of the floor cannot exist at that scale (it would break the contract)., Every room of the floor rescaled; the dimensions now come from the user. Raises…, rescale_floor(), parametrize, PR #59 review: rounding made a door wider than its rescaled wall (the audit… (+1 more)

### Community 145 - "apply_pose_edit"
Cohesion: 0.33
Nodes (7): apply_pose_edit(), InvalidEdit, Exception, `kept` with the edit's poses: what `PUT /scenes/{scene_id}` stores. Raises…, The edit was made against a scene the service no longer has (HTTP 409)., The edit changes something a placement correction may not change (HTTP 422)., StaleEdit

### Community 146 - "_plan_parts"
Cohesion: 0.33
Nodes (6): _plan_parts(), Any, FurnitureItem, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_fixture_scene_has_no_collisions()

### Community 147 - "unpack_model"
Cohesion: 0.50
Nodes (4): Expand retailer Draco geometry and expose WebP sources to the shared reader.…, unpack_model(), Build-only codec checks; application/runtime installs do not need DracoPy., test_unpack_preserves_draco_geometry_and_uvs()

## Knowledge Gaps
- **466 isolated node(s):** `GLB_BBOX_TOLERANCE_M`, `ITEM_ID_PATTERN`, `MAX_COLLISION_PARTS`, `MIN_PART_DIMENSION_M`, `MAX_FLOOR_PLAN_IMAGES` (+461 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `test_scene_cache.py`, `align_debug.py`, `test_real_room.py`, `test_scene_routes.py`, `FurnitureItem`, `test_room_align_vision.py`, `AuditReport`, `test_room_align.py`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `apply_pose_edit`, `propose_layout`, `Pose2D`, `._check_winding`, `DraftSession`, `SpatialInputError`, `test_room_correct.py`, `test_room_parse.py`, `single_room`, `test_contracts.py`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `routes.py`, `spatial_engine/main.py`, `test_room_shell.py`, `ContractModel`, `chat.py`, `score_feng_shui`, `test_demo_cache.py`, `detect_out_of_bounds`, `generate_mock_glbs.py`, `Vec2`, `FurnitureAsset`, `LayoutToolbox`, `audit_scene`, `scene_cache.py`, `calculate_free_floor_ratio`, `detect_collisions`, `test_layout_tools.py`, `objective.py`, `test_demo_assets.py`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `align_debug.py`, `FurnitureItem`, `test_scene_routes.py`, `test_room_align_vision.py`, `RoomScene`, `ContractModel`, `test_reconstruction.py`, `test_room_align.py`, `test_fixture_scene.py`, `test_delivery.py`, `test_demo_cache.py`, `BBoxM`, `Pose2D`, `test_contract_occupancy.py`, `reconstruct_furniture`, `detect_blocked_doors`, `catalog.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `BBoxM` connect `BBoxM` to `test_catalog.py`, `FurnitureItem`, `test_reconstruction.py`, `catalog_router`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `footprint`, `propose_layout`, `Pose2D`, `DraftSession`, `SpatialInputError`, `reconstruct_furniture`, `detect_blocked_doors`, `calculate_brightness_approximation`, `ContractModel`, `score_feng_shui`, `detect_out_of_bounds`, `Vec2`, `FurnitureAsset`, `audit_scene`, `Point`, `calculate_free_floor_ratio`, `detect_collisions`, `furniture_footprint`, `test_layout_tools.py`, `RetailerProduct`, `retailer.py`, `catalog.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 227 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 227 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 80 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 80 INFERRED edges - model-reasoned connections that need verification._
- **Are the 77 inferred relationships involving `Pose2D` (e.g. with `catalog_router()` and `FurnitureAsset`) actually correct?**
  _`Pose2D` has 77 INFERRED edges - model-reasoned connections that need verification._