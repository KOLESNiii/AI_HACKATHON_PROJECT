# Dev 4 implementation and integration plan

This is a proposed implementation sequence for the existing Dev 4 workstream.
It does not change shared contracts or approve API decisions on behalf of the team.
At the time of writing, the spatial service implements only `GET /health`.

Baseline: branch Dev 4's work from Dev 3's `feat/dev3-contract-conventions`,
including commit `2f91f01` (or a descendant). This plan uses that commit's shared
models and conventions; do not recreate them or use the older contracts from main.
Python `contracts/schema.py` is authoritative and TypeScript mirrors it. Branching
from Dev 3 includes their commit in your history; coordinate its integration into
main once rather than independently reproducing the contract changes. This plan
does not create a branch or commit. The plan file is currently untracked and must
be included explicitly when the human requests the first documentation commit.

## 1. What you own

Dev 4 answers two questions: **What is wrong with this layout?** and **Can we find
a better arrangement of the same furniture?**

| Feature | User-visible result | Priority |
| --- | --- | --- |
| Furniture overlap | Identify the two items and their overlapping floor area | P0 |
| Room containment | Detect furniture extending outside the usable floor polygon | P0 |
| Door swing | Identify furniture obstructing a door's opening sector | P0 |
| Free floor area | Report the fraction of floor not occupied by furniture | P0 |
| Front clearance | Check space in front of desks, wardrobes and other items | P1 |
| Reachable circulation | Detect disconnected areas and passages too narrow for the agreed clearance | P1 |
| Layout optimisation | Propose better positions/rotations, then validate them | P1 |
| Solar glare | Warn about screen exposure using the agreed sun/orientation approximation | P2 |
| Feng Shui/sightlines | Explain heuristic door visibility/alignment findings | P2 |

P0 is the first integrated audit; P1 is the completed core layout demonstration.
P2 follows a working core. Geometry checks are based on dimensioned footprints,
not photoreal mesh surfaces. This is a conservative floor-layout model; it does
not support stacked furniture, under-table nesting or arbitrary 3D collisions.

### How the other developers relate to collision checks

| Developer | Responsibility | What Dev 4 receives or supplies |
| --- | --- | --- |
| Dev 1 | Room geometry, scale and initial furniture placement | Supplies assembled `RoomScene`; agrees wall/door semantics |
| Dev 2 | Furniture extraction, catalog search, metric mesh normalisation | Supplies reliable `bbox_m` and logical front; uncertain dimensions need correction |
| Dev 3 | Rendering, selection, movement, optional immediate collision preview | Submits current scene, displays your findings and previews/applies your proposals |
| Dev 4 | Authoritative spatial audit and layout search | Returns findings and proposed poses using those same dimensions/transforms |

You detect overlap and search for arrangements that avoid it. Whether dragging
through an overlap is allowed, warned about or blocked is a UI policy to agree
with Dev 3. The backend must still check every submitted layout. Dev 2 does not
decide whether furniture fits into a particular arrangement.

## 2. What a good outcome looks like

The demo starts with a cached scene and needs no provider credentials. Moving a
desk into a bed shows a collision naming both objects. Moving it into a door swing
shows a blocked-door finding. Moving it away clears those findings. A layout
proposal improves a deliberately bad but solvable example; the user previews,
accepts and re-audits it. IDs, dimensions, furniture count, mesh URLs and room
geometry remain unchanged. No feasible improvement is also an honest result.

First integration uses the shared fixture. M1 additionally uses Dev 1's scene
assembled from real inputs. Do not wait for reconstruction to start development.

Do not promise that every room can be made valid, that an approximate clearance
model establishes accessibility compliance, or that generated imagery proves fit.

## 3. Agree the small shared surface first

Send these proposals to Devs 1 and 3 before implementing HTTP callers. Independent
geometry functions and tests can proceed while answers are pending.

### Adopt Dev 3's geometry conventions

1. Metres; X/Z floor; Y up; pose at mesh bottom-centre; front +Z at zero yaw.
   Use Three.js positive Y rotation: front = `(sin(yaw), cos(yaw))` in X/Z,
   so 90 degrees faces +X. Transform local points with
   `x_world = pose.x + x_local*cos(yaw) + z_local*sin(yaw)` and
   `z_world = pose.z - x_local*sin(yaw) + z_local*cos(yaw)` (convert degrees to
   radians). Test an asymmetric rectangle and its front-clearance strip.
2. The floor polygon is the usable interior boundary. Wall start/end are on the
   interior face and thickness extends outward. Test a wall-flush item without double-subtracting wall
   thickness. Handle concave rooms; reject invalid/self-intersecting polygons.
3. Use `swing_clockwise` (clockwise in plan view) and `swings_into_room` to
   derive which wall-parallel closed leaf rotates toward the selected side.
   Determine the room side from the floor polygon, not assumed wall winding.
   The schema's example has room on +Z and clockwise inward opening: the closed
   leaf points +X and opens toward +Z. Cover outward opening, reversed wall
   direction, both swing signs and hinge ends. Do not invent a closed-angle field.
4. Agree length and area tolerances separately. Proposed contact policy: touching
   furniture edges are allowed; positive intersection area above a small documented
   numerical tolerance is overlap. Clearance is a separate check.
5. Define whether `walkable_floor_ratio` initially means unoccupied floor or
   connected reachable area. Do not change its meaning silently between releases.
   Agree a person-clearance value separately from per-item front clearance.

Plan bearings are different from furniture yaw: clockwise from -Z, direction
`(sin(b), -cos(b))` in X/Z. Convert with `bearing = (180 - yaw) mod 360`.
True compass azimuth is `(plan_bearing - north_compass_deg) mod 360`.
Missing compass means -Z is North and glare orientation is ungrounded.
Stable item IDs, `is_proxy`, `dimension_source`, and `needs_correction` already
exist. Preserve them; inferred dimensions do not become exact because an audit passes.

### Proposed API with Dev 3

| Operation | Proposed service route | Body | Success response |
| --- | --- | --- | --- |
| Audit | `POST /audit` | Existing `RoomScene` | Existing `AuditReport` |
| Optimise | `POST /solve` | Existing `OptimiseRequest` | Existing `LayoutProposal` |

These paths and signatures are proposals, not existing endpoints. Browser paths
would be `/api/spatial_engine/audit` and `/api/spatial_engine/solve`, through the
existing Vite proxy. Model shapes are defined on Dev 3's branch; route paths and
error semantics still need confirmation. Import models from `contracts.schema`.

- Audit must echo submitted `scene_id` and `revision` as `scene_id` and
  `scene_revision` in every `AuditReport`.
- `OptimiseRequest` contains `scene`, `locked_item_ids` (default empty) and
  `max_candidates` (default 200, minimum 1). Validate locked IDs against the scene,
  cap service work defensively, and preserve locked poses exactly.
- `LayoutProposal` contains `proposal_id`, `poses` (item ID to `Pose2D`), `report`
  and `improved`. Unlisted items keep their original pose. Report the candidate
  layout using the base scene's ID and revision, without incrementing it.
- If no candidate improves the objective, return `improved=false`, an empty pose
  map and the baseline report. Confirm that convention with Dev 3; do not signal
  an ordinary no-improvement outcome as an HTTP error.
- Dev 3 checks scene ID and exact revision equality before displaying/applying
  results. On acceptance, copy poses onto matching items, increment the editor's
  revision and request a fresh audit. Preview does not mutate the live scene.

Use 422 for schema/domain-invalid input with an agreed actionable error shape.
Service/network failures must appear as unavailable, never as a clean audit.
Keep `/health`, its response, and CORS behaviour unchanged.

### Contract gaps that require an explicit team decision

- Room-boundary and front-clearance findings are already supported: populate
  `out_of_bounds_item_ids` and `clearance_issues`. `ClearanceIssue` includes
  `item_id`, `required_m`, `actual_m`, and an optional `blocked_by_item_id`
  (null for a wall/boundary). Agree how `actual_m` is measured across the item's
  front width. Do not disguise a wall as a furniture ID in `collisions`.
  There is still no explicit disconnected-region/narrow-passage finding; agree
  its transport before promising actionable reachability findings in the UI.
- `feng_shui` is required. Empty sightlines and an invented perfect score would
  falsely suggest an assessment. Agree a documented unassessed convention with
  the UI, or a coordinated assessment-status contract change. The same issue
  applies to empty glare alerts while glare checks are unavailable.
- Agree what contributes to `overall_score`. Label partial audits as partial in
  the UI; do not count unimplemented checks as passes. Score is a summary, not
  proof that a layout is valid.
- `RoomScene.revision` and report revision echoes already address stale results.
  Verify consumers use exact scene ID/revision equality, including proposals;
  a report from a different scene with the same revision is also stale.

Record settled choices with small shared documentation/contract changes owned by
one contributor. Do not hold all independent geometry work behind API agreement.

## 4. Files and ownership

Keep implementation under `services/spatial_engine/`. A sufficient initial layout:

```text
services/spatial_engine/
  main.py             # existing app, thin HTTP adapters
  geometry.py         # footprints, transforms, validation, door sectors
  audit.py            # individual checks and report assembly
  scoring.py          # documented objective, added when needed
  solver.py           # bounded candidate search, added after audit
  README.md           # settled semantics, API examples, limitations
tests/spatial_engine/
  conftest.py         # private scene builders; copies of shared fixture
  test_geometry.py
  test_audit.py
  test_api.py
  test_solver.py
```

The root pytest configuration discovers `tests/`; a dedicated subdirectory avoids
changing discovery or editing another contributor's tests. Coordinate this test
directory ownership with the operator. Add modules only when a step needs them.
The spatial extra already contains Shapely, NumPy and SciPy; no new dependency is
needed for the initial implementation. Never download meshes to perform an audit:
`bbox_m`, `pose`, and room geometry are sufficient.

## 5. Small implementation steps and suggested commit boundaries

Each row is an independently reviewable change with its own tests and handoff.
The messages below are suggestions; do not create commits or branches unless the
human explicitly requests them. Do not combine unfinished features into one commit.

| Step | Suggested commit | Work and acceptance |
| --- | --- | --- |
| 0 | `docs(spatial): adopt dev3 contracts and agree remaining API semantics` | Confirm the branch contains `2f91f01`, adopt its models/conventions, and settle only remaining route, tolerance, scoring and assessment questions. Publish examples. |
| 1 | `feat(spatial): validate scenes and build rotated footprints` | Pure functions create metric X/Z rectangles and transform them around bottom-centre. Validate finite values, positive dimensions, unique IDs, references, polygon validity, nonzero walls and sensible openings. Test 0/90/45-degree rotations and invalid inputs. No network or mutation. |
| 2 | `feat(spatial): detect furniture overlaps and boundary violations` | Pairwise intersection reports each colliding pair once with square-metre area; containment uses the actual polygon. Populate `out_of_bounds_item_ids`. Test touching edges, known overlap area, rotated items, concave rooms and partly outside items. |
| 3 | `feat(spatial): detect blocked door swings` | Build sectors using the agreed closed-door direction and swing rules. Test both hinges/signs, reversed walls, inside/outside sectors and near-edge tolerance. Approximate arcs with a documented resolution; do not require provider input. |
| 4 | `feat(spatial): assemble basic audit and expose audit endpoint` | Compute agreed floor ratio using the union of footprints clipped to the floor, avoiding double-counted overlap. Return `AuditReport` with scene ID/revision echoes and agreed assessment conventions/scoring. Add endpoint and error tests; preserve health. Dev 3 integrates now. |
| 5 | `test(spatial): cover editor and reconstructed-scene handoffs` | Replay fixed scene snapshots for collision, blocked door and corrected layout through the API. Verify M1 with Devs 1 and 3; record actual integration results. Fix semantic disagreements before optimisation. |
| 6 | `feat(spatial): evaluate front clearance and circulation` | Add rotated front strips and populate existing `ClearanceIssue` fields using agreed distance semantics. Check furniture and room boundary. Separate geometric free area from reachability; test narrow corridors and disconnected areas. Agree transport for reachability findings before exposing them. |
| 7 | `feat(spatial): define layout objective and candidate evaluation` | Reuse audit geometry. Rank hard violations ahead of clearance/preferences/movement cost. Document weights or lexicographic ordering and test that soft improvements cannot outweigh newly introduced hard violations. |
| 8 | `feat(spatial): search bounded layout improvements` | Search deterministic translations and 90-degree rotations, optionally wall-aligned. Include the original layout, honour `locked_item_ids` and `max_candidates`, cap execution time, and only return improvements under the same objective. Test solvable, already-valid, impossible, all-locked and budget-exhausted cases. |
| 9 | `feat(spatial): expose layout proposals and document acceptance` | Add the agreed solve route using `OptimiseRequest` and `LayoutProposal`. Revalidate the final candidate; echo the base revision in its report. Test locked/unknown IDs, serialization, immutable inputs and unchanged non-pose fields. Dev 3 integrates preview/apply/re-audit and discards stale results. |
| 10 | `test(spatial): verify demo cases and service failure handling` | Profile representative scene sizes, record environment/latency, run full checks, and freeze reproducible cached bad/good scenes outside the locked fixture. Verify provider-independent operation and UI behaviour when spatial service is down. |

Implementing steps 1–3 before exposing step 4 avoids publishing silently incomplete
collision/door results. If an earlier partial endpoint is needed, explicitly agree
its assessed checks and UI wording first. Integrate at step 4 rather than waiting
for the solver or advanced features.

### Solver details worth getting right

- Prefer a simple bounded search before simulated annealing. More sophisticated
  search is justified only if the demo cases require it.
- Reject non-finite geometry and never silently repair geometry in a way that
  changes the interpreted room. Keep candidate generation within reasonable bounds.
- Evaluate out-of-room area, item overlaps and door violations before softer
  preferences. Door access and reachability remain distinct checks.
- `wall_flush_preferred` is a preference, not permission to intersect a wall.
  `requires_front_clear_m` refers to an oriented front area, not an all-around buffer.
- Copy the input scene; change only furniture poses. Do not remove, shrink or rename
  furniture, alter `bbox_m`, or modify windows/doors to achieve a better score.
- Run the same audit on the final returned candidate, even after a timeout. Never
  claim an unfinished search proved that no feasible solution exists.
- Honour `OptimiseRequest.locked_item_ids` even when rotating or snapping.
  Reject unknown lock IDs explicitly. Test that every proposed pose key is a
  known, unlocked item and that applying the map reproduces the candidate audit.

## 6. Integration checkpoints with other developers

| Checkpoint | Participants | Concrete evidence |
| --- | --- | --- |
| Before API work | Devs 1, 3, 4; Dev 2 for front/bounds | One numeric rotated-item example, one door example, agreed input/output/error examples |
| First audit endpoint | Devs 3 and 4 | Same fixture posted directly to port 8002 and through Vite; collision appears and clears after moving an item |
| M1 | Devs 1–4 | Real assembled scene; bounds match rendering; stable IDs locate highlighted items; doors interpreted consistently |
| Before solver integration | Devs 3 and 4 | Agreed no-improvement behaviour; baseline/candidate audit comparison; stale proposal cannot overwrite current edits |
| M2 | Devs 1–4 | Preview/apply/re-audit works; shell and assets preserved; cached scene works without providers |

Dev 3 owns frontend edits. Supply JSON examples and backend tests rather than
editing their state store or UI without coordination. Dev 1 owns reconstruction
fixes; report malformed geometry rather than adding hidden compensation rules.
Dev 2 owns measured/estimated dimension quality; auditing cannot recover true
dimensions from a wrong bounding box. All furniture sources use the same audit.

Suggested message to send manually at kickoff:

> I am branching from Dev 3's contract-conventions work and adopting its geometry,
> revision echoes, OptimiseRequest and LayoutProposal. Please confirm POST /audit
> and POST /solve paths, errors, floor-ratio/clearance semantics, tolerances and
> how unimplemented assessments are labelled. I will preserve locked items and
> return proposals tied to the base scene revision. I will leave shared contracts,
> frontend and root manifests untouched unless we coordinate a specific change.

## 7. Verification and commit discipline

For each behaviour change, run the focused tests, format/lint the affected files,
and check types. Example commands from the repository root, once those files exist:

```bash
uv run --extra spatial pytest tests/spatial_engine tests/test_contracts.py tests/test_health.py
uv run ruff format services/spatial_engine tests/spatial_engine
uv run ruff check services/spatial_engine tests/spatial_engine
uv run mypy services/spatial_engine
```

Before handoff, run `bun run check` and inspect `git diff --check` and the diff.
The root test/type checks may expose other contributors' work; report ownership
and failures accurately rather than changing unrelated files. Do not claim checks
ran if dependencies or tools prevented execution. The original sub-30ms audit
target is a profiling goal, not an established guarantee; record scene size and
actual timings before choosing a UI request rate.

When the human authorises commits, stage only the intended files or hunks. A
commit includes a coherent behaviour, its tests and relevant documentation; it
does not need to contain the entire audit. Keep each agreed shared-contract change
in a separate coordinated commit, update Python/TypeScript together, and have
consumers integrate that change first. Never use destructive Git cleanup or commit
another contributor's work incidentally. Branch/PR creation requires a request.

## 8. Instructions to give an AI coding agent

Use one step at a time; substitute its number and accepted interface decisions:

> Implement step N from docs/dev4-plan.md. Read AGENTS.md, README.md,
> docs/architecture.md, docs/decisions.md, ARCHITECTURE_DAG.md, CLAUDE.md and the
> current shared schemas first. Inspect status/history and report intended files.
> Verify the branch includes Dev 3's commit 2f91f01; use its yaw/door conventions,
> revision echoes, finding types, OptimiseRequest and LayoutProposal. Do not
> implement the obsolete full-RoomScene solver response or recreate these models.
> Own only services/spatial_engine/ and tests/spatial_engine/; coordinate any other
> edit. Reuse existing dependencies and contracts. Do not invent missing shared
> fields, API semantics or assessment results. Implement the smallest complete
> behaviour for this step with meaningful deterministic tests. Keep HTTP adapters
> thin and domain logic testable without network access. Preserve input scenes,
> health behaviour and other contributors' changes. Run focused checks, inspect
> the diff, and report results, limitations, pending decisions and a suggested
> commit message. Do not commit, branch, push or open a PR unless requested.

For a substantial unresolved interface decision, continue independent work and
ask for that decision before implementing the dependent portion. Avoid several
agents editing the same geometry/audit modules simultaneously. Parallel human
work across the existing developer boundaries is enough to start.

## 9. Stretch features after core acceptance

For glare, agree the sun model, height assumptions and orientation convention
before returning rays. Use the existing missing-compass rule and set
`glare_orientation_grounded` honestly; hour alone does not define accurate solar
position without further assumptions. Test null compass, no windows, screen/no
screen and deterministic orientations. This is a declared approximation.

For Feng Shui, implement explainable sightline heuristics and documented scoring,
not universal wellbeing claims. Test front/back orientation, occlusion and door
alignment. These checks should not displace collision/door correctness or make
unsafe candidates look preferable. Dev 3 owns their visual overlays and shaders.
