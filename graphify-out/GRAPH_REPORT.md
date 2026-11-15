# Graph Report - hackathon-project  (2026-11-15)

## Corpus Check
- 278 files · ~418,318 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4120 nodes · 12215 edges · 147 communities (126 shown, 21 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1378 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fbe84fcc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_catalog.py
- test_scene_cache.py
- SceneFurniture
- test_real_room.py
- test_scene_routes.py
- audio.test.ts
- import_product
- footprint.py
- test_segmentation.py
- align_debug.py
- test_room_align.py
- calculate_reachable_floor_ratio
- test_delivery.py
- Registry
- BBoxM
- test_selection.py
- App.tsx
- propose_layout
- test_room_routes.py
- Pose2D
- DraftSession
- regions.py
- RoomScene
- test_room_correct.py
- test_room_parse.py
- reconstruct_items.py
- AuditReport
- detect_blocked_doors
- schema.ts
- parse.py
- calculate_brightness_approximation
- test_demo_cache_room.py
- walk.ts
- spatial_engine/main.py
- SpaceShift 3D representation and asset handoff — design
- demo_assets.py
- test_room_shell.py
- test_feng_shui_optimisation.py
- detect_front_clearance
- Vec2
- ContractModel
- scenes.py
- score_feng_shui
- compilerOptions
- test_demo_cache.py
- .to_item
- Sidebar.tsx
- scene_cache.py
- CatalogError
- generate_mock_glbs.py
- geometry.py
- test_contract_occupancy.py
- FurnitureItem
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- test_room_align_vision.py
- Decisions
- LayoutToolbox
- audit_scene
- routes.py
- compilerOptions
- Video frame selection and furniture identity — issue #14
- shell.py
- Dev 2 → Dev 1 asset handoff
- dependencies
- devDependencies
- raster.py
- polygon.py
- Architecture
- Dev 4 implementation and integration plan
- RoomView.tsx
- Agent Instructions
- calculate_free_floor_ratio
- test_fixture_scene.py
- agent.ts
- Implementation plan: issue #14
- Spatial engine
- report.py
- store.ts
- scripts
- scene_cache/README.md
- SpaceShift — System Architecture & 4-Developer Execution DAG
- Asset Handoff Agreement Implementation Plan
- Review Focus
- Review Focus
- Floor-plan parser (Dev 1)
- Furniture masks and placement evidence — issue #15
- furniture_search.py
- detect_collisions
- generate-landscapes.ts
- Individual furniture meshes with proxy fallback — issue #16
- Furniture asset delivery and checks (#18, Dev 2.6)
- Retailer asset import (#19, Dev 2.7)
- scripts
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- Spatial findings: Dev 3 / Dev 4 handoff
- Furniture mesh normalisation — issue #17
- layoutProgress.test.tsx
- test_layout_tools.py
- model_validator
- README.md
- frontend/package.json
- test_furniture_search.py
- FixedAnnotator
- health
- .prettierrc.json
- tsconfig.json
- test_service_health_and_cors
- CLAUDE.md
- @react-three/drei
- rescale_floor
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- tests/conftest.py
- spaceshift
- SKILL.md
- manifest.json
- retailer.py
- _Budget
- test_demo_assets.py
- vite
- FurnitureAsset
- openings.py
- Validated, cached demo assets (#20, Dev 2.8)
- Extractions
- Protocol
- objective.py
- test_api.py
- _FengShuiModel
- plugins
- chat.py
- catalog_router
- demo_cache/README.md
- ParsedFloorPlan
- gt
- furniture_proxy
- LayoutMetrics
- demoHome.ts
- check_layout_demo.py
- fetch_product
- place_item

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 220 edges
2. `useStore` - 95 edges
3. `FurnitureAsset` - 88 edges
4. `BBoxM` - 83 edges
5. `Pose2D` - 80 edges
6. `FurnitureItem` - 80 edges
7. `SpatialInputError` - 74 edges
8. `Registry` - 69 edges
9. `propose_layout()` - 64 edges
10. `audit_scene()` - 63 edges

## Surprising Connections (you probably didn't know these)
- `test_parsed_room_contract()` --calls--> `ParsedRoom`  [INFERRED]
  tests/test_room_routes.py → contracts/schema.py
- `test_field_docstrings_reach_openapi()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_scene_rules_are_validated()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py
- `test_all_home_furniture_urls_have_canonical_models()` --uses--> `RoomScene`  [INFERRED]
  tests/test_demo_assets.py → contracts/schema.py
- `test_dev1_consumes_fixtures_through_the_asset_interface()` --uses--> `FurnitureAsset`  [INFERRED]
  tests/test_fixture_scene.py → services/reconstruction/assets/models.py

## Import Cycles
- None detected.

## Communities (147 total, 21 thin omitted)

### Community 0 - "test_catalog.py"
Cohesion: 0.11
Nodes (45): catalog_id(), catalog_scene(), import_catalog_asset(), Category, Import the product on a retailer page: read the page, then `import_product`.…, The registry key of a scene's retailer products, apart from its video…, One product URL is one item ID, so importing it again updates the same item., bounds() (+37 more)

### Community 1 - "test_scene_cache.py"
Cohesion: 0.09
Nodes (41): Serve a published plan (`scene_cache.py`, #12) as if it had been uploaded and…, restore_plan(), Serve every plan published in `cache_dir` (`routes.restore_plan`); a plan…, restore_published(), _audit(), auditor(), _blockers(), client() (+33 more)

### Community 2 - "SceneFurniture"
Cohesion: 0.07
Nodes (47): MonkeyPatch, Runner, RoomScene, What a furniture source supplies for one room., SceneFurniture, ExtractionError, ExtractionJob, Extractions (+39 more)

### Community 3 - "test_real_room.py"
Cohesion: 0.08
Nodes (75): Collection, proxy_warning(), still_extracting(), _audit(), auditor(), _clear(), client(), _collides() (+67 more)

### Community 4 - "test_scene_routes.py"
Cohesion: 0.16
Nodes (31): _audit(), auditor(), client(), _door(), _leaf_end(), DoorOpening, parametrize, RoomScene (+23 more)

### Community 5 - "audio.test.ts"
Cohesion: 0.05
Nodes (27): listeners, onSoundCue(), PartialTone, playCue(), renderCue(), SoundCue, tones, AudioEngine (+19 more)

### Community 6 - "import_product"
Cohesion: 0.07
Nodes (43): FailureKind, CatalogImport, import_product(), imported_assets(), computed_field, Path, One imported product: the placed-ready asset, its checks, and where it all came…, The delivered asset passed every check. A proxy or a requested correction is… (+35 more)

### Community 7 - "footprint.py"
Cohesion: 0.06
Nodes (61): any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach() (+53 more)

### Community 8 - "test_segmentation.py"
Cohesion: 0.09
Nodes (74): Rect, _fetch(), MaskError, Safe user-facing provider diagnostic; never reflects credentials or raw HTTP…, main(), Path, Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads…, Review images plus the two machine-readable handoffs: the result and the… (+66 more)

### Community 9 - "align_debug.py"
Cohesion: 0.08
Nodes (29): AlignmentRecord, AlignmentResult, _Capture, pose_error(), FrameSource, FurnitureItem, RoomScene, Debug CLI for furniture alignment: place assets in a room and draw the result.… (+21 more)

### Community 10 - "test_room_align.py"
Cohesion: 0.09
Nodes (65): align_assets(), FrameSource, Place every asset in the room. Deterministic for a given scene, assets and…, FixedObserver, NullObserver, PlacementHint, PlacementHints, BaseModel (+57 more)

### Community 11 - "calculate_reachable_floor_ratio"
Cohesion: 0.17
Nodes (29): calculate_reachable_floor_ratio(), RoomScene, Fraction of room floor coverable by a person entering through any door. Model…, divided_room(), obstacle(), FurnitureItem, parametrize, RoomScene (+21 more)

### Community 12 - "test_delivery.py"
Cohesion: 0.09
Nodes (62): check_placed(), deliver_furniture(), Path, RoomScene, A scene's furniture for Dev 1 to place: per item, its checked mesh or its…, Faults in how a scene carries delivered assets; empty when every asset appears…, RawMesh, choose_view() (+54 more)

### Community 13 - "Registry"
Cohesion: 0.06
Nodes (41): Connection, box_pixels(), fal_media_url(), GrabCutProvider, Any, NDArray, uint8, Instance masks from item boxes (#15): local GrabCut offline, fal SAM 3 when… (+33 more)

### Community 14 - "BBoxM"
Cohesion: 0.11
Nodes (53): BBoxM, Canonical metric bounds in the item's local frame: width along X, height along…, Front, BBoxM, CollisionPart, The category's parts inside `bbox`, or `[]` (one solid box) for solid…, template_parts(), _bounds() (+45 more)

### Community 15 - "test_selection.py"
Cohesion: 0.08
Nodes (83): DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery(), Exception, Path, Protocol (+75 more)

### Community 16 - "App.tsx"
Cohesion: 0.06
Nodes (43): App(), ORDER, screenVariants, FloorPlanScreen(), Openings(), PlanRoom(), plural(), points() (+35 more)

### Community 17 - "propose_layout"
Cohesion: 0.11
Nodes (67): OptimiseRequest, AgentLimits, propose_layout(), ProviderError, LayoutProposal, Explore within the request's limits and return a re-audited proposal or an…, One allowance per request. Retries and the interpretation call spend the same…, A failed model call. `kind` is safe to log; no key or payload is kept. (+59 more)

### Community 18 - "test_room_routes.py"
Cohesion: 0.21
Nodes (16): _png(), client(), _plan_file(), fixture, TestClient, Floor-plan routes on the reconstruction service, and the ParsedFloorPlan…, Uploads in tmp_path; extraction jobs recorded, never run against fal., test_errors() (+8 more)

### Community 19 - "Pose2D"
Cohesion: 0.14
Nodes (49): Pose2D, WindowOpening, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., compare_layouts(), evaluate_layout(), Measure a candidate against the immutable original, without modifying either.…, Compare to baseline (default original); movement always references original.…, test_full_scoring_is_opt_in_and_the_comparator_requires_it() (+41 more)

### Community 20 - "DraftSession"
Cohesion: 0.11
Nodes (36): _arrangement(), DraftSession, _echo(), LayoutMoveError, PoseChange, RoomScene, Request-local immutable layout drafts: pose-only edits audited against one…, A fresh scene at the base revision, so its audit identifies the submitted scene. (+28 more)

### Community 21 - "regions.py"
Cohesion: 0.12
Nodes (34): int32, Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction() (+26 more)

### Community 22 - "RoomScene"
Cohesion: 0.08
Nodes (75): ChatRequest, RoomScene, POST /chat and /chat/stream., add_item(), chat(), _percent(), ChatRequest, FurnitureItem (+67 more)

### Community 23 - "test_room_correct.py"
Cohesion: 0.10
Nodes (45): apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, InvalidScale, _perimeter(), _point() (+37 more)

### Community 24 - "test_room_parse.py"
Cohesion: 0.10
Nodes (52): ParsedFloorPlan, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images.…, ParsedRoom, _extract_json(), NullAnnotator, PlanAnnotations, No labels: the parser falls back to estimated scale and generic names., bay_room() (+44 more)

### Community 25 - "reconstruct_items.py"
Cohesion: 0.18
Nodes (15): main(), Path, Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback…, write_report(), Delivery, computed_field, Every delivered asset passed its checks. Proxies are allowed; they are listed., load_dimensions() (+7 more)

### Community 26 - "AuditReport"
Cohesion: 0.14
Nodes (22): AuditReport, FengShuiReport, load_generator(), load_mock(), parametrize, RoomScene, plan_normal_deg is derived from the wall's outward normal (dz, -dx)., True when the point lies inside one of the mesh's boxes (all mock parts are… (+14 more)

### Community 27 - "detect_blocked_doors"
Cohesion: 0.18
Nodes (32): BlockedDoorIssue, CollisionPart, One box of an item's occupied volume, in the item's local frame (the .glb…, detect_blocked_doors(), Report furniture intersecting door sweeps, sorted by door and item ID. Tests…, item(), FurnitureItem, parametrize (+24 more)

### Community 28 - "schema.ts"
Cohesion: 0.04
Nodes (62): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutProgressStage, MAX_COLLISION_PARTS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M, MIN_PLAN_OVERLAP_M2, AuditReport (+54 more)

### Community 29 - "parse.py"
Cohesion: 0.09
Nodes (46): Compass, FloorCaption, BaseModel, What computer vision cannot read off a floor plan: room labels with their…, Plans print labels in capitals ("BEDROOM (4)"); show them in title case., RoomLabel, _tidy_name(), _assign_labels() (+38 more)

### Community 30 - "calculate_brightness_approximation"
Cohesion: 0.13
Nodes (35): BrightnessApproximation, calculate_brightness_approximation(), RoomScene, A window-openness proxy for layout comparison, not a lighting simulation., Ratios describe geometric openness, never percentage brightness or lux., Project nearby occupied parts onto each window and union their shadows. The…, WindowOpenness, item() (+27 more)

### Community 31 - "test_demo_cache_room.py"
Cohesion: 0.09
Nodes (44): NoFurniture, The room alone: what parsed rooms get until #16 produces furniture assets., broken_cache(), from_demo_cache(), geometry_mismatch(), geometry_warning(), RoomScene, Video furniture for a real plan room (#10): Dev 2's extracted items, placed… (+36 more)

### Community 32 - "walk.ts"
Cohesion: 0.07
Nodes (41): WALK_HEADROOM_M, editorKey(), handleItemKey(), handleSaveKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys (+33 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.04
Nodes (80): exception_handler, FengShuiResult, JSONResponse, Outcome, RequestValidationError, _explain_result(), _explore(), _interpret() (+72 more)

### Community 34 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "demo_assets.py"
Cohesion: 0.11
Nodes (29): FileResponse, HTTPException, demo_room_scenes(), Each demo room with the furniture standing in it, as the editor builds them., demo_floors(), demo_room_scene(), demo_rooms(), demo_shell() (+21 more)

### Community 36 - "test_room_shell.py"
Cohesion: 0.10
Nodes (46): build_shell(), Scene, The room shell as a trimesh Scene with nodes `floor`, `ceiling`, `wall_<id>`., shell_glb(), corner_probes(), _inside(), invalid_footprints(), _l_door() (+38 more)

### Community 37 - "test_feng_shui_optimisation.py"
Cohesion: 0.13
Nodes (26): ModelReply, Any, ToolCall, assess_feng_shui(), FengShuiRequest, LayoutPreferences, What the user asked for, already validated by the server., Any (+18 more)

### Community 38 - "detect_front_clearance"
Cohesion: 0.25
Nodes (27): ClearanceIssue, detect_front_clearance(), Check full-width front access strips, returning one issue per blocker. actual_m…, item(), obstacle(), FurnitureItem, parametrize, RoomScene (+19 more)

### Community 39 - "Vec2"
Cohesion: 0.19
Nodes (27): Vec2, A point on the floor plan (Y omitted)., detect_out_of_bounds(), Return sorted item IDs whose rectangular footprint leaves the interior floor.…, Build the usable interior floor, accepting either winding and a closed ring.…, room_floor_polygon(), item(), FurnitureItem (+19 more)

### Community 40 - "ContractModel"
Cohesion: 0.10
Nodes (31): ChatErrorEvent, ChatProgressEvent, ChatReplyEvent, ContractModel, LayoutErrorEvent, LayoutProgressEvent, LayoutResultEvent, BaseModel (+23 more)

### Community 41 - "scenes.py"
Cohesion: 0.05
Nodes (61): ge, gt, Protocol, put, Query, demo_cache_dir(), furniture_data_dir(), Path (+53 more)

### Community 42 - "score_feng_shui"
Cohesion: 0.10
Nodes (65): FengShuiRequest, POST /feng-shui and /feng-shui/score., FengShuiSightline, RuleScore, AuditReport, FengShuiRequest, Shared validation for the assessment and the score; returns the audit and…, validate_feng_shui_request() (+57 more)

### Community 43 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "test_demo_cache.py"
Cohesion: 0.08
Nodes (79): _declared_bounds(), _declared_bounds_problems(), _gltf_problems(), inspect_asset(), ndarray, The bounds the file declares: the union of its `POSITION` accessors' min/max.…, Re-read an asset's stored file and check it against the furniture profile and…, Scene-graph rules of the furniture profile, read from the file's JSON chunk. (+71 more)

### Community 45 - ".to_item"
Cohesion: 0.33
Nodes (4): FurnitureItem, model_validator, Pose2D, Dev 1 places the asset: add the pose it aligned from the floor plan.

### Community 46 - "Sidebar.tsx"
Cohesion: 0.07
Nodes (30): ChatStreamEvent, LayoutStreamEvent, MAX_FLOOR_PLAN_IMAGES, MAX_ROOM_VIDEOS, CatalogPreview(), FengShuiScoreCard(), AuditDiff(), AuditStats() (+22 more)

### Community 47 - "scene_cache.py"
Cohesion: 0.07
Nodes (51): FalVisionAnnotator, PlanAnnotator, Path, Protocol, Reads labels with a vision LLM on fal.ai (`FAL_KEY`). The endpoint and model…, plan_id_for(), _annotator(), _assemble() (+43 more)

### Community 48 - "CatalogError"
Cohesion: 0.13
Nodes (16): CatalogError, _check_public(), fetch_public(), ValueError, The product cannot be imported at all. The message is safe to show., Refuse anything but http(s) to a public address: an imported URL is untrusted…, Download a public URL with a size cap, re-checking every redirect hop., _read_page() (+8 more)

### Community 49 - "generate_mock_glbs.py"
Cohesion: 0.17
Nodes (23): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), ndarray, Scene (+15 more)

### Community 50 - "geometry.py"
Cohesion: 0.15
Nodes (26): DoorOpening, WallSegment, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The…, door_center(), door_entry_segment(), _door_frame(), door_opening_frame(), door_swing_sector() (+18 more)

### Community 51 - "test_contract_occupancy.py"
Cohesion: 0.15
Nodes (22): RoomCaptureInputs, inputs(), item(), part(), Any, BaseModel, FurnitureItem, parametrize (+14 more)

### Community 52 - "FurnitureItem"
Cohesion: 0.08
Nodes (38): FurnitureItem, model_validator, floor_polygon is clockwise in plan view and every wall has the room on its…, Correction, Facing, _access(), _Choice, _extents() (+30 more)

### Community 53 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "test_room_align_vision.py"
Cohesion: 0.05
Nodes (78): FurnitureAsset, Image, MaskSource, EvidenceFrame, One video frame an asset was seen in. Optional fields are null for fixtures., main(), assets_of(), A scene's furniture as pose-less assets with placeholder evidence (no source… (+70 more)

### Community 55 - "Decisions"
Cohesion: 0.06
Nodes (35): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+27 more)

### Community 56 - "LayoutToolbox"
Cohesion: 0.16
Nodes (17): LayoutDraft, _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, LayoutToolbox, _metrics() (+9 more)

### Community 57 - "audit_scene"
Cohesion: 0.22
Nodes (23): audit_scene(), AuditReport, RoomScene, Audit without network access or mutation; unavailable assessments stay null.…, piece(), FurnitureItem, parametrize, RoomScene (+15 more)

### Community 58 - "routes.py"
Cohesion: 0.07
Nodes (45): BinaryIO, File, ParsedFloorPlan, PlanAnnotator, clear_corrections(), get_annotator(), get_extractions(), get_plan() (+37 more)

### Community 59 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "shell.py"
Cohesion: 0.10
Nodes (38): int64, _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key(), _miter() (+30 more)

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
Cohesion: 0.23
Nodes (15): _drop_collinear(), _fit_edge(), _intersect(), is_simple(), float64, Mask, NDArray, Point (+7 more)

### Community 67 - "Architecture"
Cohesion: 0.07
Nodes (28): Architecture, Backend-provided demo models, Bundled retailer library, Chat additions and application, Corrections (#11), Demo scene cache (#12), Editor Feng Shui score integration, Editor layout review and live Stats (+20 more)

### Community 68 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "RoomView.tsx"
Cohesion: 0.10
Nodes (38): floorPlane, Furniture, MeshBoundary, ProxyBox(), FurnitureMesh(), categoryWash, disposeInk(), inkify() (+30 more)

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 71 - "calculate_free_floor_ratio"
Cohesion: 0.23
Nodes (24): calculate_free_floor_ratio(), RoomScene, Return the usable floor fraction not blocked under the shared headroom rule.…, item(), FurnitureItem, parametrize, RoomScene, Free floor area is distinct from reachable walking space. (+16 more)

### Community 72 - "test_fixture_scene.py"
Cohesion: 0.14
Nodes (9): _plan_parts(), Any, FurnitureItem, The one fixture scene: Dev 2's fixture assets placed in the mock room (issues…, Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates., The module-doc collision rule: touching is allowed, overlapping is not., test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape() (+1 more)

### Community 73 - "agent.ts"
Cohesion: 0.07
Nodes (55): LayoutGoal, MAX_LAYOUT_INSTRUCTION_CHARS, LayoutProposalCard(), poseText(), ScoreComparison, useProposalScores(), isLibraryAsset(), AgentReply (+47 more)

### Community 74 - "Implementation plan: issue #14"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Spatial engine"
Cohesion: 0.11
Nodes (19): Audit endpoint, Brightness approximation for layout comparison, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng Shui placement metric (rule-based, in `/audit`), Feng shui score, Free floor area, Front clearance (+11 more)

### Community 76 - "report.py"
Cohesion: 0.11
Nodes (24): FengShuiReport, Spatial checks independent of HTTP, mesh loading and provider services., _angle_deg(), calculate_feng_shui(), _front(), _occupant(), FurnitureItem, RoomScene (+16 more)

### Community 77 - "store.ts"
Cohesion: 0.07
Nodes (48): EditorScreen(), clock(), ExtractionProgress(), Sidebar(), useLiveAudit(), VersionTree(), VersionTreeView(), PlayOverlay() (+40 more)

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

### Community 86 - "furniture_search.py"
Cohesion: 0.17
Nodes (24): IkeaSearch, PageReader, ProductOption, _host(), _ikea_options(), linkup_client(), _linkup_urls(), _option() (+16 more)

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
Cohesion: 0.17
Nodes (12): Bot additions restricted to mesh Library assets, Completion and follow-up, Consuming the findings, Deterministic Feng Shui score in the editor, Editor integration status (issues #32 and #35), HTTP handoff contract, Layout suggestions (`POST /solve`), Live execution updates (+4 more)

### Community 95 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

### Community 96 - "layoutProgress.test.tsx"
Cohesion: 0.14
Nodes (15): HarnessProgress(), HarnessStatus(), proposalSummary(), initial, proposal(), propose(), report(), response() (+7 more)

### Community 97 - "test_layout_tools.py"
Cohesion: 0.21
Nodes (23): evaluate(), item(), move(), Any, FurnitureItem, parametrize, RoomScene, Scripted tool calls: validation, shared budget, duplicates and best-draft… (+15 more)

### Community 98 - "model_validator"
Cohesion: 0.16
Nodes (3): model_validator, The stored mask for a sighting, unless its box has changed since., The stored raw mesh, unless the mask it was made from has been replaced since.

### Community 100 - "frontend/package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 101 - "test_furniture_search.py"
Cohesion: 0.23
Nodes (17): Exception, No search could run (no key, provider down). The message is safe to show., SearchUnavailable, ikea(), Linkup, product(), Any, Exception (+9 more)

### Community 102 - "FixedAnnotator"
Cohesion: 0.12
Nodes (16): AnnotationResult, FixedAnnotator, Returns pre-recorded annotations (tests, the debug CLI, cached demo plans)., main(), ndarray, ParsedFloor, Debug CLI: parse floor-plan images and write the JSON plus an overlay per…, Draw the contract geometry exactly as returned (metres), not the source image:… (+8 more)

### Community 103 - "health"
Cohesion: 0.50
Nodes (3): health(), get, Process liveness only; does not probe external providers.

### Community 109 - "rescale_floor"
Cohesion: 0.29
Nodes (7): ParsedFloor, ParsedRoom, One room parsed from a floor plan. `scene` uses its floor's shared frame (see…, One storey. Every room's coordinates share this floor's frame: metres, origin…, ParsedFloor, Every room of the floor rescaled; the dimensions now come from the user. Raises…, rescale_floor()

### Community 122 - "manifest.json"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 123 - "retailer.py"
Cohesion: 0.10
Nodes (28): HTMLParser, _binary_models(), _dimensions(), _first_url(), _is_type(), _metres(), _model_urls(), _nodes() (+20 more)

### Community 125 - "test_demo_assets.py"
Cohesion: 0.21
Nodes (10): MonkeyPatch, parametrize, Path, Demo GLBs are backend-provided; the browser needs no copied asset directory., test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory() (+2 more)

### Community 127 - "FurnitureAsset"
Cohesion: 0.04
Nodes (95): RuntimeError, fetch(), main(), prepare(), Fetch a balanced, offline IKEA library using only published retailer meshes.…, Reuse bounded, public-only downloads; keep raw evidence outside the project., Expand retailer Draco geometry and expose WebP sources to the shared reader.…, unpack_model() (+87 more)

### Community 128 - "openings.py"
Cohesion: 0.22
Nodes (11): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Mask, Point (+3 more)

### Community 129 - "Validated, cached demo assets (#20, Dev 2.8)"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

### Community 132 - "objective.py"
Cohesion: 0.16
Nodes (19): _access_not_worse(), beats_original(), _check_comparable(), compare_evaluations(), _door_overlap_area(), is_acceptable_proposal(), LayoutComparison, LayoutEvaluation (+11 more)

### Community 133 - "test_api.py"
Cohesion: 0.20
Nodes (16): payload(), Any, Exception, MonkeyPatch, parametrize, HTTP integration for the audit contract and shared frontend handoff cases., test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422() (+8 more)

### Community 134 - "_FengShuiModel"
Cohesion: 0.33
Nodes (6): _FengShuiModel, FengShuiActivityAnchor, FengShuiMirror, FengShuiRuleScore, FengShuiScore, POST /feng-shui/score: deterministic Form School score, no model call.

### Community 135 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 136 - "chat.py"
Cohesion: 0.11
Nodes (22): ChatReply, POST /chat response, and the data of /chat/stream's terminal `reply` event., AddItemArguments, place(), PlaceRequest, AuditReport, BaseModel, ChatReply (+14 more)

### Community 137 - "catalog_router"
Cohesion: 0.18
Nodes (13): catalog_router(), APIRouter, Fetch, Path, `fetch` replaces the public downloader (tests)., client(), MonkeyPatch, parametrize (+5 more)

### Community 141 - "furniture_proxy"
Cohesion: 0.15
Nodes (12): le, furniture_proxy(), health(), get, gt, Path, Response, Process liveness only; does not probe external providers. (+4 more)

### Community 150 - "demoHome.ts"
Cohesion: 0.17
Nodes (20): area(), DEFAULT_ROOM_ID, DemoFloor, demoFloors, demoRooms, edgeDistance(), findRoom(), floor() (+12 more)

### Community 153 - "check_layout_demo.py"
Cohesion: 0.11
Nodes (19): profile(), Any, RoomScene, Check the spatial engine against the shared demo home. Free (no network): audit…, solve(), Timed, AnthropicLayoutModel, Claude through the official SDK. The loop above owns retries, so the SDK makes… (+11 more)

### Community 154 - "fetch_product"
Cohesion: 0.15
Nodes (16): fetch_product(), guess_category(), Category, Fetch, Classify the head phrase, using its last furniture or accessory noun.…, Download and read one retailer product page. Raises CatalogError. `source`…, IKEA products matching `query`, as `catalog_search` results. A result carries…, search_ikea() (+8 more)

### Community 157 - "place_item"
Cohesion: 0.09
Nodes (49): height_overlaps(), CollisionVolume, front_clearance_zone(), furniture_collision_volumes(), furniture_footprint(), prepare_furniture(), FurnitureItem, Polygon (+41 more)

## Knowledge Gaps
- **488 isolated node(s):** `ORDER`, `screenVariants`, `PROVERBS`, `rise`, `DemoFloor` (+483 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `RoomScene` to `test_scene_cache.py`, `test_real_room.py`, `objective.py`, `test_api.py`, `test_scene_routes.py`, `chat.py`, `align_debug.py`, `test_room_align.py`, `calculate_reachable_floor_ratio`, `test_delivery.py`, `propose_layout`, `Pose2D`, `DraftSession`, `test_room_correct.py`, `test_room_parse.py`, `check_layout_demo.py`, `AuditReport`, `detect_blocked_doors`, `parse.py`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `place_item`, `spatial_engine/main.py`, `demo_assets.py`, `test_room_shell.py`, `detect_front_clearance`, `Vec2`, `ContractModel`, `score_feng_shui`, `scene_cache.py`, `generate_mock_glbs.py`, `geometry.py`, `FurnitureItem`, `test_room_align_vision.py`, `LayoutToolbox`, `audit_scene`, `shell.py`, `calculate_free_floor_ratio`, `report.py`, `detect_collisions`, `test_layout_tools.py`, `test_demo_assets.py`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `FurnitureAsset` connect `FurnitureAsset` to `test_scene_routes.py`, `import_product`, `align_debug.py`, `test_room_align.py`, `test_delivery.py`, `BBoxM`, `test_selection.py`, `Pose2D`, `reconstruct_items.py`, `detect_blocked_doors`, `test_demo_cache_room.py`, `demo_assets.py`, `ContractModel`, `test_demo_cache.py`, `.to_item`, `test_contract_occupancy.py`, `FurnitureItem`, `test_room_align_vision.py`, `test_fixture_scene.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `FurnitureItem` connect `FurnitureItem` to `test_real_room.py`, `footprint.py`, `chat.py`, `catalog_router`, `test_room_align.py`, `align_debug.py`, `calculate_reachable_floor_ratio`, `BBoxM`, `propose_layout`, `Pose2D`, `DraftSession`, `RoomScene`, `test_room_correct.py`, `detect_blocked_doors`, `place_item`, `calculate_brightness_approximation`, `test_demo_cache_room.py`, `detect_front_clearance`, `Vec2`, `ContractModel`, `score_feng_shui`, `geometry.py`, `test_contract_occupancy.py`, `audit_scene`, `calculate_free_floor_ratio`, `test_fixture_scene.py`, `report.py`, `detect_collisions`, `test_layout_tools.py`, `FurnitureAsset`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 217 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 217 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 80 inferred relationships involving `BBoxM` (e.g. with `_along_mesh()` and `template_parts()`) actually correct?**
  _`BBoxM` has 80 INFERRED edges - model-reasoned connections that need verification._
- **Are the 77 inferred relationships involving `Pose2D` (e.g. with `catalog_router()` and `FurnitureAsset`) actually correct?**
  _`Pose2D` has 77 INFERRED edges - model-reasoned connections that need verification._