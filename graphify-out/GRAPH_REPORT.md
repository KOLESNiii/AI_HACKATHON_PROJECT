# Graph Report - AI_HACKATHON_PROJECT  (2026-11-14)

## Corpus Check
- 143 files · ~123,138 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 102 file(s) not represented in the graph (top: .glb 93, (none) 5, .lock 2)
- WARNING: 102 of 254 files seen (40%) have no supported extractor and are missing from this graph entirely. It may look complete while representing only part of the codebase.

## Summary
- 1989 nodes · 5314 edges · 128 communities (67 shown, 61 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 536 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d72c6d5b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- pytest
- schema.ts
- Dev 2 → Dev 1 asset handoff
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- SpaceShift — System Architecture & 4-Developer Execution DAG
- CLAUDE.md
- test_api.py
- compilerOptions
- compilerOptions
- frontend/package.json
- devDependencies
- .oxlintrc.json
- detect_collisions
- scripts
- parse_floor_plan
- segment_furniture
- spatial_engine/main.py
- .prettierrc.json
- tsconfig.json
- single_room
- spaceshift
- test_demo_assets.py
- fixtures/README.md
- test_contracts.py
- test_segmentation.py
- SpaceShift 3D representation and asset handoff — design
- scripts
- annotate.py
- parse.py
- geometry.py
- test_room_parse.py
- ._check_winding
- test_doors.py
- test_drafts.py
- shell_scene
- test_clearance.py
- polygon.py
- test_containment.py
- math
- geometry.py
- demo_assets.py
- useStore
- Vec2
- invalid_request
- walk.ts
- Agent Instructions
- spatial_engine/main.py
- schema.py
- openings.py
- CollisionPart
- test_room_routes.py
- test_objective.py
- test_drafts.py
- test_agent.py
- fastapi_testclient
- FurnitureItem
- Floor-plan parser (Dev 1)
- store.ts
- assets/__init__.py
- ValueError
- _bridge_sides
- BBoxM
- test_service_health_and_cors
- @react-three/drei
- vite
- agent.py
- test_room_routes.py
- Registry
- test_shared_handoff_case
- FloorPlanScreen.tsx
- object_evidence
- test_fixture_scene.py
- generate_mock_glbs.py
- ProviderError
- LayoutModel
- furniture_model
- MaskRecord
- Spatial engine
- test_mask_download_enforces_the_byte_cap_before_reading_the_entire_body
- mock_room/README.md

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 83 edges
2. `SpatialInputError` - 46 edges
3. `Registry` - 46 edges
4. `useStore` - 41 edges
5. `segment_furniture()` - 41 edges
6. `room()` - 39 edges
7. `detect_collisions()` - 38 edges
8. `detect_blocked_doors()` - 38 edges
9. `item()` - 37 edges
10. `propose_layout()` - 36 edges

## Surprising Connections (you probably didn't know these)
- `Furniture evidence selection (#14)` --references--> `AssetEvidence`  [INFERRED]
  docs/architecture.md → services/reconstruction/assets/models.py
- `Furniture evidence selection (#14)` --references--> `SelectionResult`  [INFERRED]
  docs/architecture.md → services/reconstruction/assets/selection_models.py
- `Furniture evidence selection (#14)` --references--> `object_evidence()`  [INFERRED]
  docs/architecture.md → services/reconstruction/assets/selection.py
- `Furniture masks and placement evidence (#15)` --references--> `SegmentationResult`  [INFERRED]
  docs/architecture.md → services/reconstruction/assets/selection_models.py
- `test_field_docstrings_reach_openapi()` --uses--> `RoomScene`  [INFERRED]
  tests/test_contracts.py → contracts/schema.py

## Import Cycles
- None detected.

## Communities (128 total, 61 thin omitted)

### Community 0 - "pytest"
Cohesion: 0.10
Nodes (42): CollisionPart, calculate_free_floor_ratio(), calculate_reachable_floor_ratio(), item(), room(), test_concave_room_uses_actual_floor_area(), test_disconnected_free_regions_are_both_counted(), test_does_not_mutate_scene_and_order_does_not_matter() (+34 more)

### Community 1 - "schema.ts"
Cohesion: 0.07
Nodes (36): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, LayoutGoal, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_LAYOUT_INSTRUCTION_CHARS, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M (+28 more)

### Community 2 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.04
Nodes (42): Architecture, Backend-provided demo models, Editor play mode, Furniture evidence selection (#14), Layout suggestion API, Spatial audit API, Workstream ownership, 3D representation and asset handoff (+34 more)

### Community 3 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.12
Nodes (29): FloorCaption, RoomLabel, _assign_labels(), _bearing(), _bridge_sides(), _build_scene(), _caption_distance(), _consensus() (+21 more)

### Community 4 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 6 - "test_api.py"
Cohesion: 0.09
Nodes (56): DiscoveryError, DiscoveryProvider, FalVisionProvider, OfflineProvider, parse_discovery(), RecordedProvider, Implemented: frame selection and identity (#14), main() (+48 more)

### Community 7 - "compilerOptions"
Cohesion: 0.08
Nodes (25): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+17 more)

### Community 8 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 9 - "frontend/package.json"
Cohesion: 0.12
Nodes (17): framer-motion, dependencies, framer-motion, react, react-dom, @react-three/fiber, tailwindcss, @tailwindcss/vite (+9 more)

### Community 10 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, oxlint, prettier, @types/node, @types/react, @types/react-dom, @types/three, typescript (+9 more)

### Community 11 - ".oxlintrc.json"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 12 - "detect_collisions"
Cohesion: 0.07
Nodes (38): detect_collisions(), _height_overlaps(), CollisionVolume, furniture_collision_volumes(), furniture_footprint(), item(), part(), test_disjoint_intersections_are_summed() (+30 more)

### Community 13 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 15 - "segment_furniture"
Cohesion: 0.08
Nodes (20): box_pixels(), FalSamProvider, _fetch(), GrabCutProvider, MaskError, MaskProvider, Segment, main() (+12 more)

### Community 16 - "spatial_engine/main.py"
Cohesion: 0.22
Nodes (18): detect_out_of_bounds(), item(), room(), test_clockwise_floor_and_explicit_closure_are_accepted(), test_concave_floor_checks_entire_edges_not_just_corners(), test_containment_rejects_floor_corrupted_after_validation(), test_duplicate_ids_rejected(), test_empty_furniture_in_valid_room() (+10 more)

### Community 19 - "single_room"
Cohesion: 0.15
Nodes (15): inputs(), item(), part(), test_fixture_category_must_be_fixed(), test_furniture_asset_mirrors_item_without_pose(), test_item_id_pattern(), test_legacy_item_still_validates(), test_new_literals() (+7 more)

### Community 24 - "test_demo_assets.py"
Cohesion: 0.15
Nodes (6): test_all_home_furniture_urls_have_canonical_models(), test_each_demo_room_shell_preserves_geometry_and_nodes(), test_legacy_models_live_in_the_backend(), test_shell_is_generated_once_per_room_and_cached_in_memory(), test_symlinks_cannot_escape_the_asset_directory(), test_unknown_assets_and_path_traversal_return_404()

### Community 27 - "test_contracts.py"
Cohesion: 0.09
Nodes (22): ContractModel, BlockedDoorIssue, ClearanceIssue, CollisionIssue, DoorOpening, FengShuiReport, FengShuiSightline, FurnitureItem (+14 more)

### Community 28 - "test_segmentation.py"
Cohesion: 0.10
Nodes (47): Sighting, box_mask(), FakeProvider, iou(), loose_box(), make_scene(), add(), make_scene_frame_dict() (+39 more)

### Community 29 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 30 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, format, format:check, lint, preview, typecheck

### Community 31 - "annotate.py"
Cohesion: 0.20
Nodes (9): Asset Handoff Agreement Implementation Plan, Deferred, each under its own issue, Execution notes (2026-11-14), File Structure, Global Constraints, Review Focus, Task 1: Contract additions, Task 2: One fixture scene (+1 more)

### Community 32 - "parse.py"
Cohesion: 0.20
Nodes (24): detect_blocked_doors(), item(), scene(), test_bbox_overlap_but_parts_clear_door(), test_boundary_contact_and_outside_radius_are_clear(), test_concave_room_wall(), test_door_uses_stored_head_height(), test_duplicate_ids_rejected() (+16 more)

### Community 33 - "geometry.py"
Cohesion: 0.09
Nodes (17): _door_frame(), door_swing_sector(), _DoorFrame, front_clearance_zone(), FurnitureGeometry, prepare_furniture(), prepare_scene(), room_floor_polygon() (+9 more)

### Community 34 - "test_room_parse.py"
Cohesion: 0.12
Nodes (33): ParsedFloorPlan, _extract_json(), PlanAnnotations, bay_room(), _canvas(), _close(), _example(), _has_vertex() (+25 more)

### Community 35 - "._check_winding"
Cohesion: 0.12
Nodes (19): _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point(), find_bridges() (+11 more)

### Community 36 - "test_doors.py"
Cohesion: 0.11
Nodes (18): 1. Source identity and local frame processing, 2. Frame choice has two independent purposes, 3. Discovery and conservative association, 4. Durable per-scene registry, 5. Camera recovery and placement against the room design, 6. Preserve materials as well as meshes, 7. Fixed handoff compatibility and multiple videos, 8. Provider boundaries, configuration and failures (+10 more)

### Community 37 - "test_drafts.py"
Cohesion: 0.05
Nodes (46): RoomScene, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+38 more)

### Community 38 - "shell_scene"
Cohesion: 0.22
Nodes (6): convex_vertices(), cross2(), mm_key(), shell_scene(), slab(), triangulate()

### Community 39 - "test_clearance.py"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 40 - "polygon.py"
Cohesion: 0.22
Nodes (8): area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), region_polygon(), _segments_cross(), shoelace()

### Community 41 - "test_containment.py"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 42 - "math"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 43 - "geometry.py"
Cohesion: 0.15
Nodes (12): Execution record, Follow-on issue gates (planned here, implemented separately), Implementation plan: issue #14, Library-first implementation, Scope and constraints, Task 1: Internal selection records and durable registry, Task 2: Timestamped upright extraction and quality selection, Task 3: Bounded fal discovery with offline substitution (+4 more)

### Community 44 - "demo_assets.py"
Cohesion: 0.14
Nodes (4): demo_rooms(), demo_shell(), room_shell(), health()

### Community 46 - "useStore"
Cohesion: 0.12
Nodes (32): App(), EditorScreen(), AuditStats(), ChatTab(), LibraryTab(), Metric(), Row(), Sidebar() (+24 more)

### Community 47 - "Vec2"
Cohesion: 0.25
Nodes (21): detect_front_clearance(), item(), obstacle(), room(), test_blocker_overlapping_front_edge_has_zero_clearance(), test_cardinal_front_direction_in_fixed_world_coordinates(), test_chair_has_no_own_clearance_zone_but_still_occupies_space(), test_chair_is_ignored_but_not_other_categories() (+13 more)

### Community 48 - "invalid_request"
Cohesion: 0.06
Nodes (19): AnnotationResult, Compass, FalVisionAnnotator, FixedAnnotator, NullAnnotator, PlanAnnotator, _tidy_name(), main() (+11 more)

### Community 49 - "walk.ts"
Cohesion: 0.12
Nodes (28): captureEditorView(), EditorOrbit, EditorView, floor, pointOnFloor(), resizePlayCamera(), restoreEditorView(), Human() (+20 more)

### Community 50 - "Agent Instructions"
Cohesion: 0.40
Nodes (4): Floor-plan parser (Dev 1), How it works, Status and limits, Use

### Community 51 - "spatial_engine/main.py"
Cohesion: 0.10
Nodes (8): AnthropicLayoutModel, audit(), get_interpreter_model(), get_layout_model(), health(), _input_errors(), solve(), test_missing_api_key_means_no_model()

### Community 52 - "schema.py"
Cohesion: 0.11
Nodes (16): load_generator(), load_mock(), solid_at(), test_audit_report_must_echo_scene(), test_field_docstrings_reach_openapi(), test_layout_proposal_round_trips(), test_mock_glbs_follow_contract(), test_mock_scene_lists_every_field() (+8 more)

### Community 53 - "openings.py"
Cohesion: 0.17
Nodes (25): DoorSwings(), bounds(), clampToFloor(), doorSwing(), fitsRoom(), fitYaw(), footprint(), inwardNormal() (+17 more)

### Community 54 - "CollisionPart"
Cohesion: 0.14
Nodes (19): floorPlane, Furniture, Mesh(), MeshBoundary, OverlapGlow(), ProxyBox(), categoryWash, disposeInk() (+11 more)

### Community 55 - "test_room_routes.py"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 56 - "test_objective.py"
Cohesion: 0.06
Nodes (71): Pose2D, calculate_brightness_approximation(), WindowOpenness, LayoutPreferences, compare_layouts(), evaluate_layout(), LayoutMetrics, item() (+63 more)

### Community 57 - "test_drafts.py"
Cohesion: 0.09
Nodes (28): _arrangement(), DraftSession, _echo(), LayoutMoveError, PoseChange, _findings(), LayoutToolbox, _metrics() (+20 more)

### Community 58 - "test_agent.py"
Cohesion: 0.17
Nodes (26): OptimiseRequest, AgentLimits, ModelReply, propose_layout(), ToolCall, Layout suggestions: `POST /solve` (issues #33, #34), interpret(), item() (+18 more)

### Community 59 - "fastapi_testclient"
Cohesion: 0.17
Nodes (7): decode(), estimate_wall_px(), flatten_illumination(), rasterise(), structural_strokes(), UnreadableImage, test_empty_or_corrupt_image_is_unreadable()

### Community 60 - "FurnitureItem"
Cohesion: 0.20
Nodes (9): Execution record, Furniture Segmentation Implementation Plan, Global Constraints, Review Focus, Task 1: Mask records, Task 2: Pipeline with the offline provider, Task 3: Evidence handoff, Task 4: Live SAM 3 provider (+1 more)

### Community 61 - "Floor-plan parser (Dev 1)"
Cohesion: 0.22
Nodes (8): Approaches, Design, Furniture masks and placement evidence — issue #15, Intent, Left to the builder, Live probe (2026-11-14, approved by the operator: at most 20 requests), Live result (2026-11-14), Needs coordination

### Community 62 - "store.ts"
Cohesion: 0.13
Nodes (16): editorKey(), handleItemKey(), panCamera(), rotationDegrees, KeyboardControls(), panKeys, CatalogItem, bump() (+8 more)

### Community 63 - "assets/__init__.py"
Cohesion: 0.24
Nodes (6): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf

### Community 65 - "_bridge_sides"
Cohesion: 0.18
Nodes (13): AuditReport, audit_scene(), payload(), test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422(), test_no_doors_keeps_independent_findings_available(), test_nonfinite_values_do_not_break_error_serialization(), test_report_contains_clearance_findings_and_does_not_mutate_input() (+5 more)

### Community 66 - "BBoxM"
Cohesion: 0.13
Nodes (7): BBoxM, AssetEvidence, EvidenceFrame, FurnitureAsset, NormalisedMesh, 3. Evidence, 8. Functions and failure contract

### Community 70 - "agent.py"
Cohesion: 0.12
Nodes (13): _explain_result(), _percent(), LayoutDraft, _Arguments, _CompareArguments, _EvaluateArguments, _InspectArguments, _Move (+5 more)

### Community 71 - "test_room_routes.py"
Cohesion: 0.31
Nodes (6): _png(), client(), test_errors(), test_parsed_room_contract(), test_same_upload_returns_the_same_plan_id(), test_upload_then_fetch_plan_and_room()

### Community 77 - "Registry"
Cohesion: 0.14
Nodes (4): RequestBudget, Registry, Box, test_boxes_validate_external_coordinates()

### Community 79 - "FloorPlanScreen.tsx"
Cohesion: 0.14
Nodes (21): FloorPlanScreen(), Openings(), PlanRoom(), plural(), points(), px(), Chip(), area() (+13 more)

### Community 80 - "object_evidence"
Cohesion: 0.29
Nodes (3): Furniture masks and placement evidence (#15), object_evidence(), test_primary_evidence_frame_avoids_a_low_confidence_mask()

### Community 81 - "test_fixture_scene.py"
Cohesion: 0.15
Nodes (4): _plan_parts(), test_fixture_scene_has_no_collisions(), test_front_clearances_stay_inside_the_room(), test_generated_meshes_match_bbox()

### Community 82 - "generate_mock_glbs.py"
Cohesion: 0.27
Nodes (6): coloured_box(), furniture_mesh(), main(), rotate_y(), wall_mesh(), wall_piece()

### Community 83 - "ProviderError"
Cohesion: 0.16
Nodes (5): ProviderError, sdk_model(), test_sdk_adapter_maps_http_failures_without_leaking_the_key(), test_sdk_adapter_maps_timeouts(), handler()

### Community 84 - "LayoutModel"
Cohesion: 0.21
Nodes (5): _Budget, _explore(), _interpret(), _Interpretation, LayoutModel

### Community 85 - "furniture_model"
Cohesion: 0.36
Nodes (3): furniture_model(), legacy_model(), _model_file()

### Community 86 - "MaskRecord"
Cohesion: 0.29
Nodes (4): Implemented: masks and placement evidence (#15), MaskRecord, record(), test_mask_is_not_current_after_its_sighting_box_changes()

### Community 87 - "Spatial engine"
Cohesion: 0.18
Nodes (10): BrightnessApproximation, Audit endpoint, Brightness approximation for layout comparison, Free floor area, Front clearance, Internal layout comparison (issue #33), Layout exploration tools (issue #33), Reachable walking space (+2 more)

## Knowledge Gaps
- **29 isolated node(s):** `spaceshift`, `oxlint`, `prettier`, `@types/node`, `@types/react` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 737 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **61 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `test_drafts.py` to `pytest`, `Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill`, `detect_collisions`, `spatial_engine/main.py`, `test_demo_assets.py`, `test_contracts.py`, `parse.py`, `geometry.py`, `test_room_parse.py`, `demo_assets.py`, `Vec2`, `invalid_request`, `spatial_engine/main.py`, `schema.py`, `test_objective.py`, `test_drafts.py`, `test_agent.py`, `_bridge_sides`, `agent.py`, `test_room_routes.py`, `test_shared_handoff_case`, `generate_mock_glbs.py`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Are the 74 inferred relationships involving `RoomScene` (e.g. with `main()` and `demo_rooms()`) actually correct?**
  _`RoomScene` has 74 INFERRED edges - model-reasoned connections that need verification._
- **What connects `spaceshift`, `oxlint`, `prettier` to the rest of the system?**
  _29 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `pytest` be split into smaller, more focused modules?**
  _Cohesion score 0.10064935064935066 - nodes in this community are weakly interconnected._
- **Why does `_build_scene()` connect `Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill` to `._check_winding`, `test_drafts.py`, `invalid_request`, `test_contracts.py`, `assets/__init__.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `SpatialInputError` (e.g. with `DraftSession` and `LayoutToolbox`) actually correct?**
  _`SpatialInputError` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `schema.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.06543385490753911 - nodes in this community are weakly interconnected._