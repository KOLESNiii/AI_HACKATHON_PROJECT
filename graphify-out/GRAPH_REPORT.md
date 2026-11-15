# Graph Report - AI_HACKATHON_PROJECT  (2026-11-15)

## Corpus Check
- 248 files · ~257,091 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 110 file(s) not represented in the graph (top: .glb 97, (none) 7, .css 3)
- WARNING: 110 of 388 files seen (28%) have no supported extractor and are missing from this graph entirely. It may look complete while representing only part of the codebase.

## Summary
- 3744 nodes · 11364 edges · 167 communities (100 shown, 67 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1315 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `594a223d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- catalog.py
- detect_blocked_doors
- observe_vision.py
- TestClient
- calculate_free_floor_ratio
- test_room_align.py
- correct.py
- Registry
- useStore
- test_reconstruction.py
- test_room_align_vision.py
- calculate_reachable_floor_ratio
- test_objective.py
- useStore
- test_room_parse.py
- ContractModel
- test_chat.py
- propose_layout
- FurnitureAsset
- detect_collisions
- BBoxM
- reconstruction.py
- test_chat.py
- scenes.py
- SpatialInputError
- calculate_free_floor_ratio
- agent.py
- SpaceShift 3D representation and asset handoff — design
- proxies.py
- audio.test.ts
- propose_layout
- test_demo_cache_room.py
- geometry.ts
- spatial_engine/main.py
- walk.ts
- RoomView.tsx
- Furniture.tsx
- store.ts
- generate_mock_glbs.py
- delivery.py
- move
- schema.py
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- audit_scene
- routes.py
- store.ts
- feng_shui_score.py
- App.tsx
- Video frame selection and furniture identity — issue #14
- SpatialInputError
- devDependencies
- proxies.py
- polygon.py
- roomVersions.test.tsx
- Dev 4 implementation and integration plan
- Sidebar.tsx
- video_furniture.py
- .apply_moves
- store.ts
- FurnitureAsset
- Furniture.tsx
- Implementation plan: issue #14
- Architecture
- SoundControls.tsx
- scripts
- openings.py
- test_demo_assets.py
- SpaceShift — System Architecture & 4-Developer Execution DAG
- streaming.py
- Agent Instructions
- Registry
- conform_openings
- test_room_align_vision.py
- Asset Handoff Agreement Implementation Plan
- Review Focus
- plugins
- store.ts
- invalid_request
- plugins
- generate-landscapes.ts
- scenes.py
- video_furniture.py
- Individual furniture meshes with proxy fallback — issue #16
- Exception
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- detect_collisions
- ProviderError
- RealRoomFurniture
- spatial_engine/main.py
- test_fixture_scene.py
- frontend/package.json
- SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin
- feng_shui
- Furniture mesh normalisation — issue #17
- object_evidence
- test_service_health_and_cors
- CLAUDE.md
- single_room
- shan-shui/README.md
- fixtures/README.md
- mock_room/README.md
- vite.config.ts
- spaceshift
- services/__init__.py
- assets/__init__.py
- data_dir
- spatial_engine/__init__.py
- spaceshift
- SKILL.md
- client
- streaming.py
- agent.py
- AnthropicLayoutModel
- reconstruction/main.py
- FurnitureItem
- ._check_winding
- report.py
- model_validator

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 221 edges
2. `FurnitureAsset` - 87 edges
3. `BBoxM` - 79 edges
4. `useStore` - 79 edges
5. `Pose2D` - 74 edges
6. `FurnitureItem` - 71 edges
7. `SpatialInputError` - 69 edges
8. `Registry` - 67 edges
9. `propose_layout()` - 64 edges
10. `scene()` - 59 edges

## Surprising Connections (you probably didn't know these)
- `Editor integration status (issues #32 and #35)` --references--> `toServiceScene()`  [INFERRED]
  docs/dev3-spatial-handoff.md → frontend/src/lib/spatial.ts
- `Chat additions and application` --references--> `add_item()`  [INFERRED]
  docs/architecture.md → services/spatial_engine/chat.py
- `Library-only chat additions` --references--> `add_item()`  [INFERRED]
  docs/architecture.md → services/spatial_engine/chat.py
- `Backend-provided demo models` --references--> `roomScene()`  [INFERRED]
  docs/architecture.md → frontend/src/data/demoHome.ts
- `Corrections (#11)` --references--> `nearest_fit()`  [INFERRED]
  docs/architecture.md → services/reconstruction/room/align.py

## Import Cycles
- None detected.

## Communities (167 total, 67 thin omitted)

### Community 0 - "catalog.py"
Cohesion: 0.05
Nodes (50): catalog_id(), _binary_models(), CatalogError, _check_public(), _dimensions(), fetch_product(), fetch_public(), _first_url() (+42 more)

### Community 1 - "detect_blocked_doors"
Cohesion: 0.07
Nodes (23): PlanAnnotator, main(), render_floor(), render_shell_section(), _clean(), _clip(), _cross(), _door_span() (+15 more)

### Community 2 - "observe_vision.py"
Cohesion: 0.07
Nodes (18): build_prompt(), _distance_to_wall(), _draw_marks(), _encode(), _facing(), FalVisionObserver, hints_from_reply(), _Mark (+10 more)

### Community 3 - "TestClient"
Cohesion: 0.09
Nodes (45): _audit(), auditor(), _clear(), client(), _collides(), data_dir(), _findings(), _get_in_thread() (+37 more)

### Community 4 - "calculate_free_floor_ratio"
Cohesion: 0.16
Nodes (20): RoomScene, FurnitureSource, NoFurniture, _audit(), auditor(), _leaf_end(), _scene(), _served() (+12 more)

### Community 5 - "test_room_align.py"
Cohesion: 0.05
Nodes (27): listeners, onSoundCue(), PartialTone, playCue(), renderCue(), SoundCue, tones, AudioEngine (+19 more)

### Community 6 - "correct.py"
Cohesion: 0.06
Nodes (25): _along_mesh(), catalog_scene(), CatalogImport, _decode(), ImageProvenance, import_catalog_asset(), import_product(), imported_assets() (+17 more)

### Community 7 - "Registry"
Cohesion: 0.07
Nodes (29): any_overlap(), boundary_distance(), _bounds_apart(), clip_convex(), closed_leaf(), covered_by(), _crosses_interior(), door_approach() (+21 more)

### Community 8 - "useStore"
Cohesion: 0.12
Nodes (47): segment_furniture(), Sighting, test_mesh_record_belongs_to_a_sighting_and_goes_stale_with_its_mask(), box_mask(), FakeProvider, iou(), loose_box(), make_scene() (+39 more)

### Community 9 - "test_reconstruction.py"
Cohesion: 0.08
Nodes (11): FurnitureAsset, AlignmentRecord, _Capture, assemble_scene(), Assembly, assets_of(), PlacementHint, PlacementHints (+3 more)

### Community 10 - "test_room_align_vision.py"
Cohesion: 0.12
Nodes (43): align_assets(), FixedObserver, NullObserver, _asset(), _box(), _collisions(), _emptied(), _error() (+35 more)

### Community 11 - "calculate_reachable_floor_ratio"
Cohesion: 0.07
Nodes (53): calculate_free_floor_ratio(), calculate_reachable_floor_ratio(), payload(), test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422(), test_no_doors_keeps_independent_findings_available(), test_nonfinite_values_do_not_break_error_serialization(), test_report_contains_clearance_findings_and_does_not_mutate_input() (+45 more)

### Community 12 - "test_objective.py"
Cohesion: 0.10
Nodes (32): main(), write_report(), check_placed(), _declared_bounds(), _declared_bounds_problems(), deliver_furniture(), Delivery, audit() (+24 more)

### Community 13 - "useStore"
Cohesion: 0.08
Nodes (20): ArtifactTooLarge, box_pixels(), FalSamProvider, _fetch(), GrabCutProvider, MaskError, MaskProvider, Segment (+12 more)

### Community 14 - "test_room_parse.py"
Cohesion: 0.13
Nodes (32): BBoxM, template_parts(), NormalisedMesh, NormalisationError, normalise_mesh(), test_oversized_textures_are_reduced_before_a_mesh_is_refused(), assert_fits(), chair_like() (+24 more)

### Community 15 - "ContractModel"
Cohesion: 0.13
Nodes (38): DiscoveryError, FalVisionProvider, RecordedProvider, main(), write_report(), Discovery, RegistryState, SelectionOptions (+30 more)

### Community 16 - "test_chat.py"
Cohesion: 0.11
Nodes (27): App(), ORDER, screenVariants, EditorScreen(), RoomView(), VersionTree(), VersionTreeView(), HomeScreen() (+19 more)

### Community 17 - "propose_layout"
Cohesion: 0.08
Nodes (65): OptimiseRequest, AgentLimits, prepare_layout(), propose_layout(), ProviderError, solve(), Layout suggestions: `POST /solve` (issues #33, #34), solve_events() (+57 more)

### Community 18 - "FurnitureAsset"
Cohesion: 0.08
Nodes (18): _access(), _Choice, _extents(), _front(), _nearby(), nearest_fit(), _place_default(), _place_hinted() (+10 more)

### Community 19 - "detect_collisions"
Cohesion: 0.11
Nodes (48): Pose2D, _access_not_worse(), beats_original(), compare_evaluations(), compare_layouts(), evaluate_layout(), is_acceptable_proposal(), LayoutEvaluation (+40 more)

### Community 20 - "BBoxM"
Cohesion: 0.18
Nodes (19): DraftSession, LayoutMoveError, PoseChange, item(), room(), session(), test_draft_scene_preserves_everything_except_poses_and_echoes_the_base_revision(), test_error_messages_truncate_untrusted_identifiers() (+11 more)

### Community 21 - "reconstruction.py"
Cohesion: 0.12
Nodes (21): Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point() (+13 more)

### Community 22 - "test_chat.py"
Cohesion: 0.06
Nodes (47): add_item(), AddItemArguments, chat(), ChatReply, ChatRequest, _percent(), _rejections(), _reply_text() (+39 more)

### Community 23 - "scenes.py"
Cohesion: 0.10
Nodes (25): apply_pose_edit(), carry_furniture(), corrected_shell_url(), geometry_digest(), InvalidEdit, InvalidScale, _perimeter(), _point() (+17 more)

### Community 24 - "SpatialInputError"
Cohesion: 0.06
Nodes (47): ParsedFloorPlan, AnnotationResult, _extract_json(), FalVisionAnnotator, FixedAnnotator, NullAnnotator, PlanAnnotations, _tidy_name() (+39 more)

### Community 25 - "calculate_free_floor_ratio"
Cohesion: 0.07
Nodes (37): Individual furniture meshes and proxies (#16), fal_media_url(), fetch_bounded(), FalSam3dProvider, _fetch(), inspect_mesh(), MeshError, MeshProvider (+29 more)

### Community 26 - "agent.py"
Cohesion: 0.17
Nodes (11): LayoutDraft, _Arguments, _CompareArguments, _EvaluateArguments, _findings(), _InspectArguments, LayoutToolbox, _metrics() (+3 more)

### Community 27 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.08
Nodes (45): BlockedDoorIssue, CollisionPart, detect_blocked_doors(), detect_out_of_bounds(), item(), room(), test_clockwise_floor_and_explicit_closure_are_accepted(), test_concave_floor_checks_entire_edges_not_just_corners() (+37 more)

### Community 28 - "proxies.py"
Cohesion: 0.06
Nodes (41): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, LayoutProgressStage, LayoutStreamEvent, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS (+33 more)

### Community 29 - "audio.test.ts"
Cohesion: 0.10
Nodes (31): Compass, FloorCaption, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance() (+23 more)

### Community 30 - "propose_layout"
Cohesion: 0.08
Nodes (27): demo_room_scenes(), BrightnessApproximation, calculate_brightness_approximation(), WindowOpenness, Brightness approximation for layout comparison, item(), room(), test_behind_wall_beyond_depth_and_side_contact_are_clear() (+19 more)

### Community 31 - "test_demo_cache_room.py"
Cohesion: 0.05
Nodes (36): Real-input room (#10), Scene assembly route (#9), demo_cache_dir(), furniture_data_dir(), health(), SceneFurniture, broken_cache(), default_bindings() (+28 more)

### Community 32 - "geometry.ts"
Cohesion: 0.08
Nodes (30): WALK_HEADROOM_M, captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera(), restoreEditorView() (+22 more)

### Community 33 - "spatial_engine/main.py"
Cohesion: 0.06
Nodes (13): profile(), solve(), Timed, AnthropicLayoutModel, FengShuiScore, _cached_model(), furniture_proxy(), get_interpreter_model() (+5 more)

### Community 34 - "walk.ts"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 35 - "RoomView.tsx"
Cohesion: 0.08
Nodes (48): Editor play mode, Play lighting, DoorSwings(), floorPlane, flaggedFor(), Navigation(), RotationRing(), SelectionTools() (+40 more)

### Community 36 - "Furniture.tsx"
Cohesion: 0.10
Nodes (26): build_shell(), shell_glb(), corner_probes(), _inside(), invalid_footprints(), _l_door(), make_scene(), rect() (+18 more)

### Community 38 - "store.ts"
Cohesion: 0.05
Nodes (17): clear_corrections(), find_parsed_scene(), get_annotator(), get_plan(), get_room(), get_shell(), parse_plan(), prepare_floor_scale() (+9 more)

### Community 39 - "generate_mock_glbs.py"
Cohesion: 0.21
Nodes (16): evaluate(), item(), move(), room(), test_custom_draft_cannot_trade_circulation_for_clearance(), test_disallowed_calls_report_their_code_and_cost_nothing(), test_duplicates_are_free_and_the_budget_is_shared_across_calls(), test_goal_and_near_window_request_decide_the_best_draft() (+8 more)

### Community 40 - "delivery.py"
Cohesion: 0.25
Nodes (21): detect_front_clearance(), item(), obstacle(), room(), test_blocker_overlapping_front_edge_has_zero_clearance(), test_cardinal_front_direction_in_fixed_world_coordinates(), test_chair_has_no_own_clearance_zone_but_still_occupies_space(), test_chair_is_ignored_but_not_other_categories() (+13 more)

### Community 41 - "move"
Cohesion: 0.14
Nodes (10): demo_floors(), demo_room_scene(), demo_rooms(), demo_shell(), furniture_model(), legacy_model(), _model_file(), room_shell() (+2 more)

### Community 42 - "schema.py"
Cohesion: 0.07
Nodes (29): ContractModel, LayoutErrorEvent, LayoutProgressEvent, LayoutResultEvent, AuditReport, ClearanceIssue, CollisionIssue, DoorOpening (+21 more)

### Community 43 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 44 - "audit_scene"
Cohesion: 0.08
Nodes (43): _gltf_problems(), inspect_asset(), cache_folder(), CachedFile, CacheError, current_generation(), DemoCache, _inside() (+35 more)

### Community 45 - "routes.py"
Cohesion: 0.09
Nodes (26): DiscoveryProvider, OfflineProvider, parse_discovery(), choose_view(), _clipped(), _Job, _diagnostic(), evidence_for() (+18 more)

### Community 46 - "store.ts"
Cohesion: 0.06
Nodes (69): AuditDiff(), LayoutProposalCard(), PlanDiff(), poseText(), ScoreComparison, useProposalScores(), useLiveAudit(), CatalogItem (+61 more)

### Community 47 - "feng_shui_score.py"
Cohesion: 0.12
Nodes (44): FengShuiRequest, _add(), _angle_deg(), _backing(), _balance(), _bed_side_access(), _clamp(), _command_rules() (+36 more)

### Community 48 - "App.tsx"
Cohesion: 0.17
Nodes (20): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), Panel(), area() (+12 more)

### Community 49 - "Video frame selection and furniture identity — issue #14"
Cohesion: 0.17
Nodes (12): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), rotate_y(), shell_scene() (+4 more)

### Community 50 - "SpatialInputError"
Cohesion: 0.06
Nodes (29): _angle_deg(), calculate_feng_shui(), _front(), _occupant(), _wording(), door_center(), _door_frame(), door_swing_sector() (+21 more)

### Community 51 - "devDependencies"
Cohesion: 0.16
Nodes (14): inputs(), item(), part(), test_fixture_category_must_be_fixed(), test_item_id_pattern(), test_legacy_item_still_validates(), test_new_literals(), test_part_height_range() (+6 more)

### Community 52 - "proxies.py"
Cohesion: 0.08
Nodes (13): asset_router(), store_asset(), write_atomic(), _bounds(), _cap_textures(), _load(), proxy_asset(), proxy_glb() (+5 more)

### Community 53 - "polygon.py"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 54 - "roomVersions.test.tsx"
Cohesion: 0.12
Nodes (21): catalog, catalogCategories, demoFloors, proposalSummary(), editRoomLayout(), historyForScene(), initialRoomHistory(), recordRoomVersion() (+13 more)

### Community 55 - "Dev 4 implementation and integration plan"
Cohesion: 0.06
Nodes (31): 3D representation and asset handoff, Acceptable layout proposals, Agent-driven layout recommendations, Agent furniture additions, Backend-owned mock meshes, Bootstrap, Calm editor audio, Corrections (#11) (+23 more)

### Community 56 - "Sidebar.tsx"
Cohesion: 0.12
Nodes (27): FengShuiScoreCard(), AuditStats(), ChatTab(), FengShuiSection(), HarnessProgress(), HarnessStatus(), LibraryTab(), Metric() (+19 more)

### Community 57 - "video_furniture.py"
Cohesion: 0.26
Nodes (14): piece(), room(), test_a_bed_whose_foot_points_straight_at_the_door_is_in_coffin_position(), test_a_bed_with_its_head_toward_the_door_cannot_see_it(), test_a_bed_with_the_door_off_to_the_side_is_in_command(), test_a_desk_facing_the_door_side_of_the_room_is_in_command(), test_a_desk_with_the_door_behind_the_sitter_is_back_to_door(), test_desk_directly_aligned_with_door_is_not_in_command() (+6 more)

### Community 59 - "store.ts"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 60 - "FurnitureAsset"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 61 - "Furniture.tsx"
Cohesion: 0.22
Nodes (14): CatalogPreview(), Furniture, MeshBoundary, OverlapGlow(), ProxyBox(), FurnitureMesh(), categoryWash, disposeInk() (+6 more)

### Community 62 - "Implementation plan: issue #14"
Cohesion: 0.10
Nodes (20): 10. Room inputs (#5), 1. IDs, 2. What Dev 2 returns, 3. Evidence, 4. Mesh references, 5. Normalisation guarantee, 6. Occupied volume, 7. Dimension provenance (+12 more)

### Community 63 - "Architecture"
Cohesion: 0.12
Nodes (17): framer-motion, dependencies, framer-motion, react, react-dom, @react-three/fiber, tailwindcss, @tailwindcss/vite (+9 more)

### Community 64 - "SoundControls.tsx"
Cohesion: 0.12
Nodes (17): devDependencies, oxlint, prettier, @types/node, @types/react, @types/react-dom, @types/three, typescript (+9 more)

### Community 65 - "scripts"
Cohesion: 0.17
Nodes (7): decode(), estimate_wall_px(), flatten_illumination(), rasterise(), structural_strokes(), UnreadableImage, test_empty_or_corrupt_image_is_unreadable()

### Community 66 - "openings.py"
Cohesion: 0.22
Nodes (8): area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), region_polygon(), _segments_cross(), shoelace()

### Community 67 - "test_demo_assets.py"
Cohesion: 0.14
Nodes (14): Architecture, Backend-provided demo models, Chat additions and application, Corrections (#11), Editor layout review and live Stats, Frontend audio, Furniture normalisation (#17, PR #54 review), Home screen and intake presentation (+6 more)

### Community 68 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 69 - "streaming.py"
Cohesion: 0.18
Nodes (6): LayoutCancelled, chat_events(), execution_events(), progress(), publish(), work()

### Community 70 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 72 - "conform_openings"
Cohesion: 0.21
Nodes (7): conform_openings(), test_every_example_room_is_rescaled_validly_or_refused(), _door(), test_conform_leaves_a_valid_room_unchanged(), test_conform_leaves_large_errors_and_reports_them(), test_conform_pulls_an_overshooting_leaf_back_onto_the_wall(), test_conform_puts_an_off_line_hinge_on_its_wall()

### Community 73 - "test_room_align_vision.py"
Cohesion: 0.08
Nodes (31): EvidenceFrame, main(), _no_frames(), directory_frames(), selection_frames(), selection_masks(), _by_index(), _decode() (+23 more)

### Community 74 - "Asset Handoff Agreement Implementation Plan"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 75 - "Review Focus"
Cohesion: 0.14
Nodes (14): Audit endpoint, Demo home checks (issue #36), Feng shui assessment (AI-written, `POST /feng-shui`), Feng shui score, Free floor area, Front clearance, Layout drafts for proposed moves (issue #33), Library-only additions (+6 more)

### Community 76 - "plugins"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 77 - "store.ts"
Cohesion: 0.31
Nodes (8): editorKey(), handleItemKey(), handleSaveKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, initial

### Community 78 - "invalid_request"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 79 - "plugins"
Cohesion: 0.24
Nodes (6): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf

### Community 80 - "generate-landscapes.ts"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 81 - "scenes.py"
Cohesion: 0.20
Nodes (9): Asset Handoff Agreement Implementation Plan, Deferred, each under its own issue, Execution notes (2026-11-14), File Structure, Global Constraints, Review Focus, Task 1: Contract additions, Task 2: One fixture scene (+1 more)

### Community 82 - "video_furniture.py"
Cohesion: 0.20
Nodes (9): Completed verification, Furniture Mesh Reconstruction Implementation Plan, Global Constraints, Review Focus, Task 1: Mesh records, Task 2: Proxy assets and the asset store, Task 3: Pipeline with a test provider, Task 4: Live SAM 3D provider (+1 more)

### Community 83 - "Individual furniture meshes with proxy fallback — issue #16"
Cohesion: 0.20
Nodes (9): Execution record, Furniture Segmentation Implementation Plan, Global Constraints, Review Focus, Task 1: Mask records, Task 2: Pipeline with the offline provider, Task 3: Evidence handoff, Task 4: Live SAM 3 provider (+1 more)

### Community 84 - "Exception"
Cohesion: 0.20
Nodes (8): Corrections (#11), Floor-plan parser (Dev 1), Furniture alignment (#8), How it works, Real-input room (#10), Scene assembly (#9), Status and limits, Use

### Community 85 - "SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin"
Cohesion: 0.22
Nodes (8): Approaches, Design, Furniture masks and placement evidence — issue #15, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 20 requests), Live result (2026-11-14), Needs coordination

### Community 87 - "detect_collisions"
Cohesion: 0.08
Nodes (38): detect_collisions(), _height_overlaps(), CollisionVolume, furniture_collision_volumes(), furniture_footprint(), item(), part(), test_disjoint_intersections_are_summed() (+30 more)

### Community 88 - "ProviderError"
Cohesion: 0.22
Nodes (7): file, outDir, page, root, SEEDS, tmp, vendor

### Community 89 - "RealRoomFurniture"
Cohesion: 0.25
Nodes (7): Approaches, Design, Individual furniture meshes with proxy fallback — issue #16, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 15 requests for this issue), Needs coordination

### Community 90 - "spatial_engine/main.py"
Cohesion: 0.25
Nodes (7): Approaches, Design, Furniture asset delivery and checks (#18, Dev 2.6), Goals, Intent, Non-goals, Tests

### Community 91 - "test_fixture_scene.py"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Left open, Non-goals, Retailer asset import (#19, Dev 2.7)

### Community 92 - "frontend/package.json"
Cohesion: 0.25
Nodes (8): scripts, build, dev, format, format:check, lint, preview, typecheck

### Community 93 - "SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin"
Cohesion: 0.25
Nodes (8): 1. The Core Differentiator (Why We Beat Existing Tools), 2. What We Stole (And Improved) From Competitors, 3. Full Tech Stack, 4. Quickstart (Local Development), **AI & Generative Media (`services/reconstruction` & `services/media_gen`)**, **Design & Frontend (`frontend/`)**, SpaceShift — Spatial Audit, Auto-Reconfiguration & Photoreal Room Twin, **Spatial Audit & Solver Engine (`services/spatial_engine`)**

### Community 94 - "feng_shui"
Cohesion: 0.13
Nodes (17): Editor Feng Shui score integration, Main integration: chat additions and streaming, Skill-guided Feng Shui optimisation, Spatial audit API, Bot additions restricted to mesh Library assets, Completion and follow-up, Consuming the findings, Deterministic Feng Shui score in the editor (+9 more)

### Community 95 - "Furniture mesh normalisation — issue #17"
Cohesion: 0.29
Nodes (6): Approaches, Calls made by the author, open to correction, Design, Furniture mesh normalisation — issue #17, Intent, What the stored meshes showed (2026-11-15, no provider requests)

### Community 97 - "object_evidence"
Cohesion: 0.32
Nodes (5): Furniture evidence selection (#14), Furniture masks and placement evidence (#15), write_report(), SegmentationResult, object_evidence()

### Community 100 - "CLAUDE.md"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 102 - "single_room"
Cohesion: 0.14
Nodes (14): load_generator(), load_mock(), solid_at(), test_assessed_audit_fields_remain_backwards_compatible(), test_audit_report_must_echo_scene(), test_field_docstrings_reach_openapi(), test_mock_glbs_follow_contract(), test_mock_scene_lists_every_field() (+6 more)

### Community 122 - "client"
Cohesion: 0.29
Nodes (6): assets, files, format, registry_revision, scene_id, source

### Community 124 - "agent.py"
Cohesion: 0.06
Nodes (34): _Budget, _explain_result(), _explore(), _interpret(), _Interpretation, LayoutModel, ModelReply, _percent() (+26 more)

### Community 125 - "AnthropicLayoutModel"
Cohesion: 0.21
Nodes (6): test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory(), test_symlinks_cannot_escape_the_asset_directory(), test_unknown_assets_and_path_traversal_return_404()

### Community 127 - "FurnitureItem"
Cohesion: 0.16
Nodes (5): FurnitureItem, AlignmentResult, pose_error(), _report(), test_furniture_asset_mirrors_item_without_pose()

### Community 129 - "report.py"
Cohesion: 0.25
Nodes (7): Approaches, Design, Goals, Intent, Non-goals, Tests, Validated, cached demo assets (#20, Dev 2.8)

## Knowledge Gaps
- **29 isolated node(s):** `@react-three/drei`, `spaceshift`, `vite`, `oxc`, `typescript` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1317 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **67 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `calculate_free_floor_ratio` to `detect_blocked_doors`, `observe_vision.py`, `TestClient`, `test_reconstruction.py`, `test_room_align_vision.py`, `calculate_reachable_floor_ratio`, `test_objective.py`, `propose_layout`, `FurnitureAsset`, `detect_collisions`, `BBoxM`, `test_chat.py`, `scenes.py`, `SpatialInputError`, `agent.py`, `SpaceShift 3D representation and asset handoff — design`, `audio.test.ts`, `propose_layout`, `test_demo_cache_room.py`, `spatial_engine/main.py`, `Furniture.tsx`, `store.ts`, `generate_mock_glbs.py`, `delivery.py`, `move`, `schema.py`, `feng_shui_score.py`, `Video frame selection and furniture identity — issue #14`, `SpatialInputError`, `video_furniture.py`, `.apply_moves`, `conform_openings`, `test_room_align_vision.py`, `detect_collisions`, `single_room`, `AnthropicLayoutModel`, `FurnitureItem`?**
  _High betweenness centrality (0.167) - this node is a cross-community bridge._
- **Are the 212 inferred relationships involving `RoomScene` (e.g. with `demo_room_scenes()` and `profile()`) actually correct?**
  _`RoomScene` has 212 INFERRED edges - model-reasoned connections that need verification._
- **What connects `@react-three/drei`, `spaceshift`, `vite` to the rest of the system?**
  _29 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `catalog.py` be split into smaller, more focused modules?**
  _Cohesion score 0.052941176470588235 - nodes in this community are weakly interconnected._
- **Why does `BBoxM` connect `test_room_parse.py` to `catalog.py`, `correct.py`, `Registry`, `test_reconstruction.py`, `calculate_reachable_floor_ratio`, `test_objective.py`, `propose_layout`, `FurnitureAsset`, `detect_collisions`, `BBoxM`, `test_chat.py`, `calculate_free_floor_ratio`, `SpaceShift 3D representation and asset handoff — design`, `propose_layout`, `generate_mock_glbs.py`, `delivery.py`, `schema.py`, `feng_shui_score.py`, `proxies.py`, `video_furniture.py`, `detect_collisions`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 52 inferred relationships involving `FurnitureAsset` (e.g. with `CatalogImport` and `_relabel()`) actually correct?**
  _`FurnitureAsset` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Should `detect_blocked_doors` be split into smaller, more focused modules?**
  _Cohesion score 0.07205387205387205 - nodes in this community are weakly interconnected._