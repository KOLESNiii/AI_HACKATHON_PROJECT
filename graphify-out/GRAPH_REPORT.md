# Graph Report - AI_HACKATHON_PROJECT  (2026-11-14)

## Corpus Check
- 93 files · ~63,427 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: .glb 7, (none) 5, .lock 2)

## Summary
- 1264 nodes · 3402 edges · 66 communities (49 shown, 17 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 315 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9879b942`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- pytest
- schema.ts
- Spatial engine
- Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill
- SpaceShift — System Architecture & 4-Developer Execution DAG
- CLAUDE.md
- test_api.py
- compilerOptions
- compilerOptions
- frontend/package.json
- devDependencies
- .oxlintrc.json
- Dev 2 → Dev 1 asset handoff
- scripts
- parse_floor_plan
- test_room_shell.py
- spatial_engine/main.py
- .prettierrc.json
- tsconfig.json
- single_room
- test_objective.py
- spaceshift
- detect_collisions
- fixtures/README.md
- test_contracts.py
- test_fixture_scene.py
- SpaceShift 3D representation and asset handoff — design
- scripts
- annotate.py
- parse.py
- parse_floor_plan
- test_room_parse.py
- test_doors.py
- test_drafts.py
- generate_mock_glbs.py
- test_clearance.py
- polygon.py
- test_containment.py
- math
- geometry.py
- cv2
- Asset Handoff Agreement Implementation Plan
- Vec2
- invalid_request
- Dev 4 implementation and integration plan
- Agent Instructions
- FixedAnnotator
- schema.py
- openings.py
- CollisionPart
- test_room_routes.py
- App.tsx
- FloorPlanScreen.tsx
- BBoxM
- fastapi_testclient
- FurnitureItem
- Floor-plan parser (Dev 1)
- store.ts
- _bridge_sides

## God Nodes (most connected - your core abstractions)
1. `RoomScene` - 69 edges
2. `detect_collisions()` - 37 edges
3. `detect_blocked_doors()` - 37 edges
4. `SpatialInputError` - 33 edges
5. `ContractModel` - 33 edges
6. `FurnitureItem` - 31 edges
7. `room()` - 31 edges
8. `calculate_free_floor_ratio()` - 31 edges
9. `parse_floor_plan()` - 30 edges
10. `detect_front_clearance()` - 30 edges

## Surprising Connections (you probably didn't know these)
- `Deferred, each under its own issue` --references--> `FurnitureAsset`  [INFERRED]
  docs/superpowers/plans/2026-11-14-asset-handoff-and-collision-parts.md → services/reconstruction/assets/models.py
- `9.1 Types` --references--> `FurnitureAsset`  [INFERRED]
  docs/superpowers/specs/2026-11-14-3d-representation-design.md → services/reconstruction/assets/models.py
- `Task 1: Contract additions` --references--> `ContractModel`  [INFERRED]
  docs/superpowers/plans/2026-11-14-asset-handoff-and-collision-parts.md → contracts/schema.py
- `9.2 Functions` --references--> `NormalisedMesh`  [INFERRED]
  docs/superpowers/specs/2026-11-14-3d-representation-design.md → services/reconstruction/assets/models.py
- `Internal layout comparison (issue #33)` --references--> `SpatialInputError`  [INFERRED]
  services/spatial_engine/README.md → services/spatial_engine/geometry.py

## Import Cycles
- None detected.

## Communities (66 total, 17 thin omitted)

### Community 0 - "pytest"
Cohesion: 0.08
Nodes (55): calculate_free_floor_ratio(), calculate_reachable_floor_ratio(), item(), room(), test_concave_room_uses_actual_floor_area(), test_disconnected_free_regions_are_both_counted(), test_does_not_mutate_scene_and_order_does_not_matter(), test_duplicate_ids_rejected() (+47 more)

### Community 1 - "schema.ts"
Cohesion: 0.06
Nodes (34): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MAX_FLOOR_PLAN_IMAGES, MAX_ROOM_VIDEOS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M, MIN_PLAN_OVERLAP_M2 (+26 more)

### Community 2 - "Spatial engine"
Cohesion: 0.06
Nodes (29): Architecture, Spatial audit API, Workstream ownership, 3D representation and asset handoff, Bootstrap, Decisions, PR #44 review follow-up, Revised execution plan (+21 more)

### Community 3 - "Xuan Ink & Scroll (*Shuǐmò*) Design System & AI Skill"
Cohesion: 0.09
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 4 - "SpaceShift — System Architecture & 4-Developer Execution DAG"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 6 - "test_api.py"
Cohesion: 0.16
Nodes (13): audit_scene(), payload(), test_geometry_library_errors_are_safe_422(), test_invalid_scenes_return_actionable_422(), test_no_doors_keeps_independent_findings_available(), test_nonfinite_values_do_not_break_error_serialization(), test_report_contains_clearance_findings_and_does_not_mutate_input(), test_revision_echo_does_not_reuse_previous_report() (+5 more)

### Community 7 - "compilerOptions"
Cohesion: 0.09
Nodes (21): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+13 more)

### Community 8 - "compilerOptions"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 9 - "frontend/package.json"
Cohesion: 0.13
Nodes (21): dependencies, framer-motion@^14.14.0, react-dom@^19.3.1, @react-three/drei@^10.7.9, @react-three/fiber@^9.8.2, tailwindcss@^4.3.5, @tailwindcss/vite@^4.3.5, three@^0.187.0 (+13 more)

### Community 10 - "devDependencies"
Cohesion: 0.10
Nodes (19): devDependencies, oxlint@^1.90.0, prettier@^3.10.1, @types/node@^24.19.2, @types/react@^19.3.0, @types/react-dom@^19.3.0, @types/three@^0.187.0, typescript@~7.0.2 (+11 more)

### Community 11 - ".oxlintrc.json"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 12 - "Dev 2 → Dev 1 asset handoff"
Cohesion: 0.18
Nodes (10): 10. Room inputs (#5), 1. IDs, 2. What Dev 2 returns, 4. Mesh references, 5. Normalisation guarantee, 6. Occupied volume, 7. Dimension provenance, 9. Fixtures (+2 more)

### Community 13 - "scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 14 - "parse_floor_plan"
Cohesion: 0.16
Nodes (7): FalVisionAnnotator, PlanAnnotator, main(), parse_floor_plan(), _unique_names(), get_annotator(), test_fal_annotator_without_key_warns_and_returns_nothing()

### Community 15 - "test_room_shell.py"
Cohesion: 0.05
Nodes (46): RoomScene, build_shell(), _clean(), _clip(), _cross(), _door_span(), _is_simple_quad(), _key() (+38 more)

### Community 16 - "spatial_engine/main.py"
Cohesion: 0.11
Nodes (4): health(), health(), audit(), health()

### Community 19 - "single_room"
Cohesion: 0.33
Nodes (6): bay_room(), _canvas(), l_room(), single_room(), two_rooms(), _wall()

### Community 20 - "test_objective.py"
Cohesion: 0.15
Nodes (31): WindowOpening, compare_layouts(), evaluate_layout(), LayoutComparison, LayoutMetrics, item(), room(), test_better_clearance_never_outweighs_leaving_the_room() (+23 more)

### Community 25 - "detect_collisions"
Cohesion: 0.10
Nodes (38): detect_collisions(), _height_overlaps(), CollisionVolume, furniture_collision_volumes(), furniture_footprint(), item(), part(), test_disjoint_intersections_are_summed() (+30 more)

### Community 27 - "test_contracts.py"
Cohesion: 0.13
Nodes (15): AuditReport, load_generator(), load_mock(), solid_at(), test_assessed_audit_fields_remain_backwards_compatible(), test_audit_report_must_echo_scene(), test_field_docstrings_reach_openapi(), test_layout_proposal_round_trips() (+7 more)

### Community 28 - "test_fixture_scene.py"
Cohesion: 0.13
Nodes (8): AssetEvidence, EvidenceFrame, 3. Evidence, test_dev1_consumes_fixtures_through_the_asset_interface(), test_evidence_matches_the_agreed_shape(), test_fixture_scene_has_no_collisions(), test_front_clearances_stay_inside_the_room(), test_generated_meshes_match_bbox()

### Community 29 - "SpaceShift 3D representation and asset handoff — design"
Cohesion: 0.07
Nodes (26): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+18 more)

### Community 30 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, format, format:check, lint, preview, typecheck

### Community 31 - "annotate.py"
Cohesion: 0.16
Nodes (6): AnnotationResult, Compass, _extract_json(), NullAnnotator, _tidy_name(), test_model_output_json_is_extracted()

### Community 32 - "parse.py"
Cohesion: 0.14
Nodes (22): FloorCaption, RoomLabel, _assign_labels(), _caption_distance(), _consensus(), _fallback_scale(), _floor_order(), _floor_scales() (+14 more)

### Community 33 - "parse_floor_plan"
Cohesion: 0.10
Nodes (9): plan_id_for(), decode(), UnreadableImage, _find_scene(), get_plan(), get_room(), get_shell(), parse_plan() (+1 more)

### Community 34 - "test_room_parse.py"
Cohesion: 0.20
Nodes (23): ParsedFloorPlan, PlanAnnotations, _close(), _example(), _has_vertex(), _label(), _parse(), _rect_sides() (+15 more)

### Community 36 - "test_doors.py"
Cohesion: 0.18
Nodes (26): BlockedDoorIssue, detect_blocked_doors(), item(), scene(), test_bbox_overlap_but_parts_clear_door(), test_boundary_contact_and_outside_radius_are_clear(), test_concave_room_wall(), test_door_uses_stored_head_height() (+18 more)

### Community 37 - "test_drafts.py"
Cohesion: 0.11
Nodes (21): DraftSession, _echo(), LayoutDraft, LayoutMoveError, PoseChange, LayoutEvaluation, Layout drafts for proposed moves (issue #33), item() (+13 more)

### Community 38 - "generate_mock_glbs.py"
Cohesion: 0.15
Nodes (12): coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), rotate_y(), shell_scene() (+4 more)

### Community 39 - "test_clearance.py"
Cohesion: 0.18
Nodes (24): detect_front_clearance(), item(), obstacle(), room(), test_blocker_overlapping_front_edge_has_zero_clearance(), test_cardinal_front_direction_in_fixed_world_coordinates(), test_chair_has_no_own_clearance_zone_but_still_occupies_space(), test_chair_is_ignored_but_not_other_categories() (+16 more)

### Community 40 - "polygon.py"
Cohesion: 0.21
Nodes (8): area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), region_polygon(), _segments_cross(), shoelace()

### Community 41 - "test_containment.py"
Cohesion: 0.26
Nodes (18): detect_out_of_bounds(), item(), room(), test_clockwise_floor_and_explicit_closure_are_accepted(), test_concave_floor_checks_entire_edges_not_just_corners(), test_containment_rejects_floor_corrupted_after_validation(), test_duplicate_ids_rejected(), test_empty_furniture_in_valid_room() (+10 more)

### Community 42 - "math"
Cohesion: 0.14
Nodes (21): Raster, _accept(), Bridge, _cast(), _dedupe(), draw_bridges(), _end_direction(), _exit_point() (+13 more)

### Community 43 - "geometry.py"
Cohesion: 0.07
Nodes (34): BrightnessApproximation, calculate_brightness_approximation(), WindowOpenness, _door_frame(), door_swing_sector(), _DoorFrame, front_clearance_zone(), FurnitureGeometry (+26 more)

### Community 45 - "cv2"
Cohesion: 0.14
Nodes (6): render_floor(), render_shell_section(), estimate_wall_px(), flatten_illumination(), rasterise(), structural_strokes()

### Community 46 - "Asset Handoff Agreement Implementation Plan"
Cohesion: 0.14
Nodes (12): Asset Handoff Agreement Implementation Plan, Deferred, each under its own issue, Execution notes (2026-11-14), File Structure, Global Constraints, Review Focus, Task 1: Contract additions, Task 2: One fixture scene (+4 more)

### Community 47 - "Vec2"
Cohesion: 0.22
Nodes (5): DoorOpening, Vec2, WallSegment, to_m(), door_entry_segment()

### Community 49 - "Dev 4 implementation and integration plan"
Cohesion: 0.12
Nodes (15): 1. What you own, 2. What a good outcome looks like, 3. Agree the small shared surface first, 4. Files and ownership, 5. Small implementation steps and suggested commit boundaries, 6. Integration checkpoints with other developers, 7. Verification and commit discipline, 8. Instructions to give an AI coding agent (+7 more)

### Community 50 - "Agent Instructions"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 51 - "FixedAnnotator"
Cohesion: 0.25
Nodes (3): FixedAnnotator, client(), test_shell_route_serves_the_scene_url()

### Community 52 - "schema.py"
Cohesion: 0.14
Nodes (14): ContractModel, ClearanceIssue, CollisionIssue, FengShuiReport, FengShuiSightline, GlareAlert, LayoutProposal, OptimiseRequest (+6 more)

### Community 53 - "openings.py"
Cohesion: 0.16
Nodes (9): attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, _bearing(), _build_scene() (+1 more)

### Community 55 - "test_room_routes.py"
Cohesion: 0.26
Nodes (6): _png(), client(), test_errors(), test_parsed_room_contract(), test_same_upload_returns_the_same_plan_id(), test_upload_then_fetch_plan_and_room()

### Community 56 - "App.tsx"
Cohesion: 0.27
Nodes (14): react@^19.3.1, App(), FloorPlanScreen(), ProgressScreen(), DropZone(), UploadScreen(), Button(), ButtonProps (+6 more)

### Community 57 - "FloorPlanScreen.tsx"
Cohesion: 0.31
Nodes (6): PlanRoom(), mockScene, mockPlanDoors, mockPlanWindows, mockSegments, RoomSegment

### Community 58 - "BBoxM"
Cohesion: 0.18
Nodes (9): BBoxM, 9.1 Types, 9.2 Functions, 9.3 IDs, 9.4 Dimension provenance, 9.5 Fixtures, 9. Handoff: Dev 2 → Dev 1 (#5 and #13), NormalisedMesh (+1 more)

### Community 60 - "FurnitureItem"
Cohesion: 0.27
Nodes (4): FurnitureItem, Pose2D, FurnitureAsset, test_furniture_asset_mirrors_item_without_pose()

### Community 61 - "Floor-plan parser (Dev 1)"
Cohesion: 0.40
Nodes (4): Floor-plan parser (Dev 1), How it works, Status and limits, Use

## Knowledge Gaps
- **1 isolated node(s):** `spaceshift`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 475 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RoomScene` connect `test_room_shell.py` to `pytest`, `parse_floor_plan`, `test_room_parse.py`, `._check_winding`, `test_doors.py`, `test_drafts.py`, `generate_mock_glbs.py`, `test_clearance.py`, `test_api.py`, `test_containment.py`, `geometry.py`, `spatial_engine/main.py`, `schema.py`, `openings.py`, `test_objective.py`, `test_room_routes.py`, `detect_collisions`, `test_contracts.py`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 60 inferred relationships involving `RoomScene` (e.g. with `main()` and `_build_scene()`) actually correct?**
  _`RoomScene` has 60 INFERRED edges - model-reasoned connections that need verification._
- **What connects `spaceshift` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `pytest` be split into smaller, more focused modules?**
  _Cohesion score 0.08145131432802666 - nodes in this community are weakly interconnected._
- **Why does `react` connect `App.tsx` to `frontend/package.json`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `detect_collisions()` (e.g. with `CollisionIssue` and `FurnitureItem`) actually correct?**
  _`detect_collisions()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `schema.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._