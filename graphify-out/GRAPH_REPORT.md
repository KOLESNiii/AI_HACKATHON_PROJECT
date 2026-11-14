# Graph Report - AI_HACKATHON_PROJECT  (2026-11-14)

## Corpus Check
- 57 files · ~65,714 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 962 nodes · 2126 edges · 73 communities (61 shown, 12 thin omitted)
- Extraction: 70% EXTRACTED · 30% INFERRED · 0% AMBIGUOUS · INFERRED: 638 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8a66f958`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]

## God Nodes (most connected - your core abstractions)
1. `ContractModel` - 57 edges
2. `RoomScene` - 57 edges
3. `PlanAnnotations` - 52 edges
4. `ParsedFloorPlan` - 46 edges
5. `Bridge` - 42 edges
6. `RoomLabel` - 39 edges
7. `FloorCaption` - 39 edges
8. `PlanAnnotator` - 39 edges
9. `Raster` - 39 edges
10. `ParsedRoom` - 38 edges

## Surprising Connections (you probably didn't know these)
- `int` --uses--> `RoomScene`  [INFERRED]
  scripts/generate_mock_glbs.py → contracts/schema.py
- `Scene` --uses--> `RoomScene`  [INFERRED]
  scripts/generate_mock_glbs.py → contracts/schema.py
- `EvidenceFrame` --uses--> `ContractModel`  [INFERRED]
  services/reconstruction/assets/models.py → contracts/schema.py
- `EvidenceFrame` --uses--> `BBoxM`  [INFERRED]
  services/reconstruction/assets/models.py → contracts/schema.py
- `EvidenceFrame` --uses--> `CollisionPart`  [INFERRED]
  services/reconstruction/assets/models.py → contracts/schema.py

## Communities (73 total, 12 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.12
Nodes (27): BaseModel, BlockedDoorIssue, ClearanceIssue, CollisionIssue, ContractModel, FengShuiSightline, GlareAlert, OptimiseRequest (+19 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (32): GLB_BBOX_TOLERANCE_M, ITEM_ID_PATTERN, MAX_COLLISION_PARTS, MIN_HEIGHT_OVERLAP_M, MIN_PART_DIMENSION_M, MIN_PLAN_OVERLAP_M2, AuditReport, BBoxM (+24 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (14): Architecture, Workstream ownership, 3D representation and asset handoff, Bootstrap, Decisions, Revised execution plan, 1. The Core Differentiator (Why We Beat Existing Tools), 2. What We Stole (And Improved) From Competitors (+6 more)

### Community 3 - "Community 3"
Cohesion: 0.50
Nodes (3): 1. Aesthetic Direction: "Architectural CAD meets Spatial Glass", 2. Screen Choreography (Zero Clutter), SpaceShift — Figma Design System & Spatial UI Spec

### Community 4 - "Community 4"
Cohesion: 0.18
Nodes (10): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, Dev 1: Room geometry and scene assembly, Dev 2: Furniture extraction and reusable asset pipeline, Dev 3: Interactive editor and aligned render maps (+2 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (24): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+16 more)

### Community 8 - "Community 8"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (17): framer-motion, dependencies, framer-motion, react-dom, @react-three/drei, @react-three/fiber, tailwindcss, @tailwindcss/vite (+9 more)

### Community 10 - "Community 10"
Cohesion: 0.10
Nodes (19): devDependencies, oxlint, prettier, @types/node, @types/react, @types/react-dom, @types/three, typescript (+11 more)

### Community 11 - "Community 11"
Cohesion: 0.17
Nodes (11): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, App(), services, oxc (+3 more)

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (12): assets/README.md, 1. IDs, 2. What Dev 2 returns, 3. Evidence, 4. Mesh references, 5. Normalisation guarantee, 6. Occupied volume, 7. Dimension provenance (+4 more)

### Community 13 - "Community 13"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 14 - "Community 14"
Cohesion: 0.50
Nodes (4): media_gen/main.py, health(), get, Process liveness only; does not probe external providers.

### Community 15 - "Community 15"
Cohesion: 0.50
Nodes (4): reconstruction/main.py, health(), get, Process liveness only; does not probe external providers.

### Community 16 - "Community 16"
Cohesion: 0.50
Nodes (4): spatial_engine/main.py, health(), get, Process liveness only; does not probe external providers.

### Community 19 - "Community 19"
Cohesion: 0.16
Nodes (25): Any, FurnitureItem, parametrize, inputs(), item(), part(), float, str (+17 more)

### Community 27 - "Community 27"
Cohesion: 0.15
Nodes (23): AuditReport, FengShuiReport, LayoutProposal, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., Proposed furniture poses. Only poses change: shell, openings, item IDs and…, RoomScene, Path (+15 more)

### Community 28 - "Community 28"
Cohesion: 0.24
Nodes (8): The one fixture scene: Dev 2's fixture assets placed in the mock room (issues #5, The module-doc collision rule: touching is allowed, overlapping is not., test_chair_seat_clears_the_desktop(), test_evidence_matches_the_agreed_shape(), test_fixture_items_carry_the_agreed_fields(), test_fixture_scene_has_no_collisions(), test_generated_meshes_match_bbox(), test_scene_holds_the_fixture_items_and_the_two_originals()

### Community 29 - "Community 29"
Cohesion: 0.06
Nodes (32): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+24 more)

### Community 30 - "Community 30"
Cohesion: 0.25
Nodes (8): scripts, build, dev, format, format:check, lint, preview, typecheck

### Community 31 - "Community 31"
Cohesion: 0.20
Nodes (9): Asset Handoff Agreement Implementation Plan, Deferred, each under its own issue, Execution notes (2026-11-14), File Structure, Global Constraints, Review Focus, Task 1: Contract additions, Task 2: One fixture scene (+1 more)

### Community 33 - "Community 33"
Cohesion: 0.13
Nodes (78): DoorOpening, DoorOpening, ParsedFloor, ParsedRoom, Vec2, WallSegment, WindowOpening, A hinged door in a wall. `hinge_pos` lies on the wall's interior-face line. The… (+70 more)

### Community 34 - "Community 34"
Cohesion: 0.08
Nodes (76): ParsedFloorPlan, RoomScene, Every floor and room parsed from 1..MAX_FLOOR_PLAN_IMAGES floor-plan images. The, Depends, description, File, MonkeyPatch, ParsedRoom (+68 more)

### Community 35 - "Community 35"
Cohesion: 0.09
Nodes (51): int32, attach(), door_leaf(), EdgeHit, _ink_along(), kind(), Leaf, Bridges → doors and windows on specific room walls.  A bridge is attached to eve (+43 more)

### Community 36 - "Community 36"
Cohesion: 0.05
Nodes (36): 10. How each consumer uses it, 11. Contract changes requested, 12. Order of work, 13. Left to the builder, 1. Intent, 2. Goals, non-goals, anti-goals, 3. Constraints, 4.1 What is the geometric truth? (+28 more)

### Community 37 - "Community 37"
Cohesion: 0.17
Nodes (24): AssetEvidence, FurnitureAsset, What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence., Dev 1 places the asset: add the pose it aligned from the floor plan., BBoxM, CollisionPart, FurnitureItem, RoomCaptureInputs (+16 more)

### Community 38 - "Community 38"
Cohesion: 0.16
Nodes (25): Scene, coloured_box(), convex_vertices(), cross2(), furniture_mesh(), main(), mm_key(), float (+17 more)

### Community 39 - "Community 39"
Cohesion: 0.10
Nodes (20): 1. Core Aesthetic Philosophy, 2. Design Tokens (`tokens.css`), 3. Typography & Bilingual Hierarchy Rules, 4. Paper Grain, Vignette & Ink-Bleed Effects, 5. Signature UI Component Specifications, 6. Three.js & 3D Spatial Viewport Guidelines, 7. AI Agent Implementation Guardrails (Do / Don't), A. Vermilion Chop Seal Button (`.chop-seal`) (+12 more)

### Community 40 - "Community 40"
Cohesion: 0.22
Nodes (18): float64, area(), _drop_collinear(), _fit_edge(), _intersect(), is_simple(), Room region (pixels) → simple, clean polygon of the interior wall faces.  The fr, Outer contour of a room region as a simplified polygon in pixels, wound for the (+10 more)

### Community 41 - "Community 41"
Cohesion: 0.11
Nodes (17): files, code, document, image, paper, video, graphifyignore_patterns, ignored (+9 more)

### Community 42 - "Community 42"
Cohesion: 0.13
Nodes (14): 10. Documentation and handoff, 11. Decision-making priorities, 12. Hackathon-specific guidance, 1. Primary objectives, 2. Repository orientation, 3. Agent collaboration rules, 4. Architecture and design, 5. Implementation standards (+6 more)

### Community 43 - "Community 43"
Cohesion: 0.13
Nodes (14): 10. Room inputs (#5), 1. IDs, 2. What Dev 2 returns, 3. Evidence, 4. Mesh references, 5. Normalisation guarantee, 6. Occupied volume, 7. Dimension provenance (+6 more)

### Community 44 - "Community 44"
Cohesion: 0.13
Nodes (14): Asset Handoff Agreement Implementation Plan, code:bash (git fetch origin), code:python (LEGACY_DESK = {  # the pre-change shape: none of the new fie), code:text (Occupied volume and collision (the editor preview and the au), code:python (ROOT = Path(__file__).resolve().parent.parent), code:bash (git rm services/reconstruction/assets/fixtures/vid-desk-01.g), Deferred, each under its own issue, Execution notes (2026-11-14) (+6 more)

### Community 45 - "Community 45"
Cohesion: 0.19
Nodes (14): Gray, decode(), estimate_wall_px(), flatten_illumination(), rasterise(), Image → binary masks: all ink, and the structural strokes that are walls.  Every, Divide by a smooth estimate of the paper so a photographed printout thresholds e, Thickness of the main walls: the dominant stroke width, weighted towards thick s (+6 more)

### Community 46 - "Community 46"
Cohesion: 0.15
Nodes (12): 1. Ownership and implementation boundaries, 2. Handoffs to agree at kickoff, 3. Execution DAG, 4. Acceptance and scope priorities, 5. Developer focus and ordered task lists, code:text (spaceshift/), code:mermaid (flowchart TD), Dev 1: Room geometry and scene assembly (+4 more)

### Community 47 - "Community 47"
Cohesion: 0.15
Nodes (12): fix-radiator-01, frames, primary_frame_index, vid-chair-01, frames, primary_frame_index, vid-desk-01, frames (+4 more)

### Community 48 - "Community 48"
Cohesion: 0.24
Nodes (8): AnnotationResult, _extract_json(), Plans print labels in capitals ("BEDROOM (4)"); show them in title case., _tidy_name(), bytes, int, str, test_model_output_json_is_extracted()

### Community 49 - "Community 49"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, build, check, dev, dev:media (+3 more)

### Community 50 - "Community 50"
Cohesion: 0.17
Nodes (11): 1. The Core Differentiator (Why We Beat Existing Tools), 2. What We Stole (And Improved) From Competitors, 3. Full Tech Stack, 4. Quickstart (Local Development), **AI & Generative Media (`services/reconstruction` & `services/media_gen`)**, code:bash (bun run setup), code:bash (bun run dev:reconstruction # http://localhost:8001/docs), code:bash (bun run build             # TypeScript check + production fr) (+3 more)

### Community 51 - "Community 51"
Cohesion: 0.18
Nodes (10): doors, floor_polygon, furniture, north_compass_deg, revision, scene_id, shell_glb_url, sun_hour (+2 more)

### Community 52 - "Community 52"
Cohesion: 0.31
Nodes (11): AuditReport, FengShuiReport, LayoutProposal, Pose2D, Floor placement of an item's bounding-box bottom-centre. See module doc for yaw., Proposed furniture poses. Only poses change: shell, openings, item IDs and glb_u, bool, float (+3 more)

### Community 53 - "Community 53"
Cohesion: 0.20
Nodes (9): EvidenceFrame, NormalisedMesh, Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder).  Evidence sta, One video frame an asset was seen in. Optional fields are null for fixtures., Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`., BBoxM, CollisionPart, Canonical metric bounds in the item's local frame: width along X, height along… (+1 more)

### Community 54 - "Community 54"
Cohesion: 0.33
Nodes (4): floor_polygon is clockwise in plan view and every wall has the room on its…, floor_polygon is clockwise in plan view and every wall has the room on its (-dz,, model_validator, ValueError

### Community 55 - "Community 55"
Cohesion: 0.53
Nodes (5): frontend/package.json, name, private, type, version

### Community 56 - "Community 56"
Cohesion: 0.40
Nodes (3): react, react, services

### Community 57 - "Community 57"
Cohesion: 0.33
Nodes (5): code:bash (# API (port 8001): POST images, then fetch the plan or one r), Floor-plan parser (Dev 1), How it works, Status and limits, Use

### Community 58 - "Community 58"
Cohesion: 0.40
Nodes (4): edges, input_tokens, nodes, output_tokens

### Community 59 - "Community 59"
Cohesion: 0.40
Nodes (4): compass, north_bearing_deg, floors, rooms

### Community 60 - "Community 60"
Cohesion: 0.50
Nodes (3): 1. Aesthetic Direction: "Architectural CAD meets Spatial Glass", 2. Screen Choreography (Zero Clutter), SpaceShift — Figma Design System & Spatial UI Spec

### Community 61 - "Community 61"
Cohesion: 0.50
Nodes (3): edges, hyperedges, nodes

### Community 62 - "Community 62"
Cohesion: 0.50
Nodes (3): compass, floors, rooms

### Community 63 - "Community 63"
Cohesion: 0.50
Nodes (3): health(), Process liveness only; does not probe external providers., str

### Community 64 - "Community 64"
Cohesion: 0.50
Nodes (3): health(), Process liveness only; does not probe external providers., str

### Community 65 - "Community 65"
Cohesion: 0.50
Nodes (3): str, health(), Process liveness only; does not probe external providers.

## Knowledge Gaps
- **317 isolated node(s):** `code`, `document`, `paper`, `image`, `video` (+312 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ContractModel` connect `Community 0` to `Community 33`, `Community 34`, `Community 37`, `Community 19`, `Community 52`, `Community 53`, `Community 27`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `RoomScene` connect `Community 34` to `Community 0`, `Community 33`, `Community 37`, `Community 38`, `Community 52`, `Community 54`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `Bridge` connect `Community 33` to `Community 35`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `ContractModel` (e.g. with `AssetEvidence` and `EvidenceFrame`) actually correct?**
  _`ContractModel` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 54 inferred relationships involving `RoomScene` (e.g. with `Depends` and `description`) actually correct?**
  _`RoomScene` has 54 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `PlanAnnotations` (e.g. with `EdgeHit` and `FloorCaption`) actually correct?**
  _`PlanAnnotations` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `ParsedFloorPlan` (e.g. with `Depends` and `description`) actually correct?**
  _`ParsedFloorPlan` has 43 INFERRED edges - model-reasoned connections that need verification._