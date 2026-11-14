# Spatial findings: Dev 3 / Dev 4 handoff

Status: Dev 4's integration contract and reusable examples for issue #29.
Record Dev 1/3 acknowledgement in the issue or PR. `POST /audit` is implemented;
`POST /solve` remains a future implementation target.
The authoritative wire models remain `contracts/schema.py` and `schema.ts`.

## HTTP handoff contract

Use JSON request/response bodies (`Content-Type: application/json`) and existing
models directly, without an additional `data` envelope:

| Operation | Service route on port 8002 | Browser route through Vite | Request | HTTP 200 response |
| --- | --- | --- | --- | --- |
| Audit | `POST /audit` | `/api/spatial_engine/audit` | `RoomScene` | `AuditReport` |
| Layout suggestion | `POST /solve` | `/api/spatial_engine/solve` | `OptimiseRequest` | `LayoutProposal` |

Audit is read-only. Solve returns a suggestion without mutating the editor's scene.
Existing contracts define scene/revision echoes and proposal application below.
No better layout is a successful response with `improved: false`, `poses: {}`,
and the unchanged layout's report. Unknown locked item IDs are invalid input;
fixed and explicitly locked items must never be moved.

Invalid schema or geometry returns HTTP 422 using FastAPI's `detail` list shape.
The UI should use each entry's `msg` for display and `loc` for field context,
without depending on Pydantic-specific wording or `type` values. Domain errors
use `loc: ["body"]` when no narrower field location is available. Other non-2xx
responses, network errors and malformed success bodies mean assessment unavailable;
none must be converted into a clean report. Internal error details stay server-side.

The audit response uses the shared models with these nullable fields:
`overall_score: number | null`, `glare_alerts: GlareAlert[] | null`, and
`feng_shui: FengShuiReport | null`. All three currently return null: display
"not checked", never zero/perfect scores or "no glare". Python and TypeScript
schemas changed together; use this revision when wiring the frontend. A future
assessed empty glare list means no alerts, whereas null means not checked.
`glare_orientation_grounded` is also nullable: null = not assessed, true = grounded
assessment, false = assessment using the orientation fallback. Do not infer that a
compass is absent merely because glare was not assessed.

`walkable_floor_ratio` now means reachable walking area for a 50 cm person, unioned
across all suitable door entries, divided by usable floor area. It is not raw free
area. With no known doors, the response remains HTTP 200, its walking ratio is
null, and collision/boundary/clearance findings are retained. Known but unusable
entries give zero; doors listed in `blocked_doors` cannot seed walking access.
Both nullable-field changes are mirrored in the shared schemas: merge this
contract revision when updating frontend consumers.

## Load the same examples in the editor and backend

Use `services/spatial_engine/fixtures/audit_cases.json`. It references the existing
`contracts/mock_room/mock_scene.json`; there is no second copy of the room.
For each case:

1. Load a fresh copy of the base scene. Do not apply cases cumulatively.
2. Replace the poses of matching furniture IDs with `pose_overrides`.
3. Set `scene.revision` to the case's `revision`; retain the base `scene_id`.
4. Load that scene into the editor, and compare the three finding lists with
   `expected`. Frontend tooling can read/import these repository files in tests;
   they are not automatically exposed as public browser URLs by Vite.

| Case | Expected behaviour |
| --- | --- |
| `blocked-door` | Original room. Highlight the wardrobe and door. Nested chair/desk and table/radiator do not collide. |
| `clear-layout` | Wardrobe moved away; no collisions, boundary violations or door obstruction. This does not establish clearance/glare/Feng Shui results. |
| `furniture-overlap` | Highlight bed and wardrobe; one collision with approximately 0.6 m² overlap. |
| `outside-room` | Highlight the wardrobe as outside the floor. No furniture collision or door obstruction. |

The test `tests/spatial_engine/test_handoff_cases.py` runs these examples through
the actual spatial functions. Compare overlap areas with numerical tolerance
(absolute 1e-9 m² in these examples), rather than exact decimal equality.

Dev 4 owns these expected results and backend regression tests. Dev 3 reuses the
same cases for finding-display tests; Dev 1 confirms the base room and override
poses are interpreted the same way. IDs and expected findings must not be changed
independently to make one consumer pass. Coordinate intentional changes in one
reviewed update. This fixture pack adds no shared room-model fields.

## Consuming the findings

`expected` contains only the implemented subset of `AuditReport` findings:
`collisions`, `out_of_bounds_item_ids`, and `blocked_doors`. It is deliberately
not a complete `AuditReport`; do not cast it to that type or invent scores,
walkable ratios, glare assessments or Feng Shui assessments to fill required fields.
Dev 3 can render these three lists in isolation; the live `/audit` response is now
a complete shared report with nulls for unavailable assessments.

Findings reference stable furniture and door IDs. Use those IDs to locate and
highlight the actual scene objects; never parse category/source out of an ID.
Both members of a collision should be identifiable. A failed request is an
unavailable assessment, not an empty list of issues.

Once the endpoint exists, its report must echo the submitted `scene_id` and
`revision` as `scene_id` and `scene_revision`. Display it only when both match the
current editor scene exactly. For example, a delayed revision-0 blocked-door
report must not replace revision-1 clear-layout feedback.

For solver proposals, the existing `LayoutProposal.report` identifies the base
scene ID/revision while evaluating its proposed poses. Reject stale proposals.
Preview separately; on acceptance apply poses by item ID, increment revision,
then re-audit. Preserve fixed items and respect `locked_item_ids`.

## Completion and follow-up

- For #29: Devs 1 and 3 acknowledge the HTTP handoff and shared cases above;
  record agreement and verification in the issue/PR. This is not a requirement
  to implement the solver or live editor integration as part of #29.
- Dev 3 adds frontend checks using the same expected results during editor work.
- The endpoint now uses the 50 cm reachability and full-width front-clearance
  definitions in the spatial README. Chairs are excluded as clearance targets
  and blockers, but still block walking and participate in collisions. Review
  these behaviours when adding frontend previews. Scoring is deferred, with
  unavailable assessments explicitly null.

Dev 3 is the direct UI consumer of `AuditReport`. Dev 1's floor/wall/opening/pose
geometry and Dev 2's bounds/collision parts are upstream integration dependencies.
The future solver also relies on these audit rules. Valid JSON alone does not
prove those geometric interpretations agree; these shared cases help check them.

Verification from the repository root:

```bash
uv run --extra spatial pytest tests/spatial_engine/test_handoff_cases.py
```
