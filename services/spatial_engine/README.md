# Spatial engine

Pure checks live in `audit.py`; `report.py` composes them for `POST /audit`.
Geometry comes from shared scene JSON, never from mesh downloads.

## Internal layout comparison (issue #33)

`objective.compare_layouts(original, candidate)` returns baseline/candidate
evaluations, an outcome (`better`, `equal`, `worse`), its `deciding_metric`, and
`skipped_unknown_metrics`. It does not generate poses, run Sonnet, implement a
solver endpoint, or set `AuditReport.overall_score`. Both reports keep that score
null. `evaluate_layout(original, candidate)` exposes the individual measurements.
Pass `baseline=current_best_draft` to compare two drafts while retaining the same
original reference for both movement costs; otherwise the baseline is original.

Comparison uses a priority order, not a weighted public score. Hard feasibility
always comes first, then an explicitly requested placement, then soft priorities
whose order depends on the user's goal (default `balanced`, shown below):

1. Fewer critical issues: overlapping furniture pairs + outside-room items +
   blocked doors. Several items blocking one door count as one blocked door.
2. Smaller critical violation area when counts tie: sum collision areas per pair,
   outside area per offending bbox, and union obstruction area per door. This
   grades invalid intermediate drafts; it is not unique occupied floor area.
3. Smaller missing front-clearance proportion, summed once per target item using
   its nearest blocker. For 0.6 m required/0.2 m available the deficit is 2/3,
   regardless of how many further blockers exist. Existing chair rules apply.
4. More reachable walking area using the existing 50 cm metric.
5. Less movement from the original: total translation plus shortest rotation arc
   at half each item's plan bbox diagonal, expressed in equivalent metres.

`goal` (`objective.LayoutGoal`) reorders only priorities 3-5. Nothing a user asks
for can outrank priorities 1-2, fixed items or locked items.

| Goal | Soft priority order |
| --- | --- |
| `balanced` | front clearance, walking area, least movement |
| `brighter` | window openness, front clearance, walking area, least movement |
| `roomier` | walking area, front clearance, least movement |
| `minimal_changes` | front clearance, least movement, walking area |
| `custom` | front clearance, walking area; movement is not penalised |

`custom` is for a request none of the others express ("a cosy reading corner"). The
user's wording goes to Sonnet, which follows it as closely as the rules allow. Only fit,
doors and access are measured, so a layout is suggested if it is valid, does not make
access worse and moves something. The explanation says the wish itself was not
verified. A new measurable goal such as Feng Shui needs a metric, one table entry in
`objective.py` and a value in `contracts.schema.LayoutGoal`. If the typed request cannot
be read at all, exploration still runs with the default goal, the explanation says the
request was not applied, and `outcome` is `stopped_early`.

The team chose that a requested goal may cost some front access: under `brighter`
or `roomier` a layout can rank better while a wardrobe's access gets worse. The
shortfall stays in the report for the user to judge. `minimal_changes` moves
furniture only to fix a fit or access problem, never just for walking space.

`near_window_item_ids` measures one placement request: "put this item near a
window". For each named item take the plan distance from its bbox footprint to
the nearest window opening, subtract `NEAR_WINDOW_M` (0.5 m) and clamp at zero;
`near_window_shortfall_m` is the sum. Zero means every named item is near a
window. It ranks directly after priorities 1-2 for every goal, and is unknown
(null, skipped) in a room without windows. Other placement relations ("against
the same wall", "facing the door") are not measured.

`compare_evaluations(baseline, candidate, goal)` ranks two existing evaluations
without auditing again; `compare_layouts` evaluates and then calls it.

Counts are exact; floating comparisons use 1e-9 absolute/relative tolerance. Tied
metrics advance to the next priority; no ranking is hidden in the public score.
Any unavailable metric is skipped and reported as such, never replaced by zero.
Known zero walking access differs from unknown entry. `compare_layouts` measures
brightness only for the `brighter` goal. `evaluate_layout(..., measure_brightness=True)`
can measure the proxy without choosing a ranking policy. The 1e-9 tolerance means
a very small gain in the goal metric still wins; no minimum meaningful gain is
applied yet.

Examples: removing a collision beats brighter windows under every goal; under
`balanced`, reducing a wardrobe's access shortfall beats avoiding a move. Moving furniture without improving a
higher-priority metric loses to the original. A smaller collision is progress
but remains infeasible: `passes_critical_checks` explicitly tracks the known
collision/boundary/door checks. It does not certify unknown assessments or that
all access preferences are met. The eventual final-proposal validator must still
reject critical violations; this comparator is not an acceptance gate.

Comparisons must retain the same room, IDs, dimensions, assets and non-pose item
metadata; item order and revision may differ. Fixed poses must remain identical.
Changed/removal/shrinkage attempts and invalid geometry raise `SpatialInputError`.
Request-specific locks are enforced by the draft session described below.
Inputs are not modified; each candidate's movement is measured from the same
original, never from the preceding attempt. Scene geometry is prepared once for
each evaluated layout and reused in its audit/optional brightness calculation.

```bash
uv run --extra spatial pytest tests/spatial_engine/test_objective.py
```

## Layout drafts for proposed moves (issue #33)

`drafts.DraftSession(scene, locked_item_ids)` is a scratchpad for one request. It
copies the submitted scene, audits it as the first draft (`original_draft_id`),
and `apply_moves(base_draft_id, [PoseChange(item_id, x, z, yaw_deg), ...])`
returns a **new** audited `LayoutDraft`, or the existing draft when that exact
arrangement (yaw compared modulo 360) was already evaluated. Stored drafts, the
caller's scene and the move list are never modified. `scene(draft_id)` returns a throwaway `RoomScene`
copy at the base revision, so each draft's report identifies the submitted scene.

Only poses of known, movable items can change. A request is rejected with
`LayoutMoveError` (a `SpatialInputError` with a stable `code`) and stores nothing
when it has no moves (`empty_moves`), names an item twice (`duplicate_item`),
an unknown item (`unknown_item`), a fixed item (`fixed_item`), an item locked by
the user (`locked_item`), a NaN/infinite pose (`non_finite_pose`), or a draft ID
that is not from this session (`unknown_draft`). An unknown locked ID is rejected
when the session is created rather than ignored. One bad entry rejects the whole
request. Messages quote at most 64 characters of any supplied identifier.

A draft with collisions, out-of-room items or a blocked door is **kept**, so
several items can be rearranged across successive drafts (swap two items via an
overlapping intermediate). Check `evaluation.metrics.passes_critical_checks`
before treating a draft as a recommendation. Each draft records brightness
openness as a measurement; ranking it is the comparison policy's decision.

`max_evaluations` is one allowance for the whole request, not per call. Each
attempted evaluation after the original uses one, including an attempt whose
geometry cannot be processed; reusing an existing draft uses none. When it is
spent, `apply_moves` raises `budget_exhausted` and existing drafts stay readable.
`near_window_item_ids` is passed through to every evaluation. Draft IDs are not
secrets; the per-session token only stops an ID from another request being accepted.

```bash
uv run --extra spatial pytest tests/spatial_engine/test_drafts.py
```

## Layout exploration tools (issue #33)

`layout_tools.LayoutToolbox(scene, locked_item_ids=..., preferences=..., max_evaluations=...)`
exposes the draft session to an agent as three tools. `TOOL_DEFINITIONS` holds
their names, descriptions and closed JSON schemas in the Anthropic tool format.
No model is called here; tests drive the tools with scripted calls.

| Tool | Purpose | Uses budget |
| --- | --- | --- |
| `inspect_layout(draft_id)` | Room outline, windows, door keep-clear boxes, each item's size/pose/`movable`, findings, metrics and the user's request | no |
| `evaluate_moves(base_draft_id, moves)` | New audited draft and its ranking against the original and the best so far | one per new arrangement |
| `compare_layouts(first_draft_id, second_draft_id)` | Rank two drafts under the user's goal | no |

`call(name, arguments)` returns a JSON-safe dict and never raises for agent
input. Success is `{"ok": true, ...}`; a rejected call is
`{"ok": false, "error": {"code", "message"}}`. Both include `best_draft_id` and
`evaluations_remaining`. Codes: `unknown_tool`, `invalid_arguments` (wrong types,
missing or extra fields, NaN/infinity, coordinates beyond 1000 m, more than 32
moves), the draft codes above, and `invalid_layout` when geometry cannot be
evaluated. Arguments are validated strictly: `"5"` and `true` are not numbers,
and a move cannot carry extra fields such as a new width.

The server, not the agent, tracks the recommendation. `best_draft_id` starts as
the original and moves only to a draft that may be recommended **and** ranks
better than the current best under `LayoutPreferences` (goal plus near-window
items). `objective.is_acceptable_proposal` decides what may be recommended:
never overlapping furniture or anything outside the room, and no blocked door
swing unless that same door was already blocked in the original. So a fixed
item sitting in a door swing does not stop every suggestion for that room, but
a draft can never block a door that was clear. Each result carries
`can_be_recommended`. A caller must still re-audit the best draft before returning it.

Furniture names are untrusted text: they are truncated to 40 characters and
returned only as data. Nothing in a name or ID changes which items may move.

```bash
uv run --extra spatial pytest tests/spatial_engine/test_layout_tools.py
```

## Brightness approximation for layout comparison

`brightness.calculate_brightness_approximation(scene)` returns a local
`BrightnessApproximation`, without changing `AuditReport` or the HTTP response.
It can be used by the future layout objective/agent tools. Inspect
`openness_ratio` (0..1 or null), `obstruction_depth_m` and per-window `windows`:
each entry has glass area, obstructed area, openness ratio and blocking item IDs.

The proxy is **window openness**, not predicted illumination. Look within a
1 m inward strip across each opening (configurable via `obstruction_depth_m`).
Project occupied furniture parts onto the glass along the wall normal and clip
their shadows to window width and sill/head height. Union overlapping shadows so
two objects covering the same area do not double-count. Weight the room ratio by
window area, not window count. Treat all parts as opaque, including proxies,
chairs and fixed items. No windows means unknown/null, not zero brightness.

Examples: a desk entirely below the sill has no penalty; a tall wardrobe covering
half the glass within the strip gives window openness 0.5. Moving it away from
the window can improve this proxy, but a final layout still needs the ordinary
fit/access checks. The 1 m cutoff is deliberately a heuristic: furniture just
beyond it has no effect. This does not model distance falloff, sunlight, compass,
time, external buildings, glazing, curtains, reflectance or actual lux. A 0.5
ratio must not be presented as "50% room brightness" or a certified daylight score.

Window geometry is authoritative: use its owning wall, offset, width and sill/head
heights. Derived compass/normal labels are not required. Invalid window references,
duplicate IDs, invalid sizes/heights and malformed wall geometry raise
`SpatialInputError`. Supplied request-local prepared geometry can be reused.

```bash
uv run --extra spatial pytest tests/spatial_engine/test_brightness.py
```

## Audit endpoint

Run `bun run dev:spatial` from the repository root (or the equivalent documented
uvicorn command). `POST http://localhost:8002/audit` accepts the shared `RoomScene`
as a JSON body and returns `AuditReport`, without an extra envelope. The frontend
development URL is `/api/spatial_engine/audit`. Swagger is at `/docs`.

Example from PowerShell at the repository root:

```powershell
$sceneJson = Get-Content -Raw contracts/mock_room/mock_scene.json
Invoke-RestMethod -Method Post -Uri http://localhost:8002/audit -ContentType application/json -Body $sceneJson
```

The report includes collisions, out-of-bounds item IDs, blocked doors, front
clearance and reachable walking-area ratio. It echoes `scene_id` and `revision`
as `scene_id` and `scene_revision`; a consumer must discard results that don't
match its current scene. Input is not modified and no provider credentials are
needed. The shared room has a blocked door and a bed-clearance issue; it is not
a universally clean demo layout.

`overall_score`, `glare_alerts` and `feng_shui` return **null**, meaning not assessed.
They must not be rendered as zero, a perfect score or no glare. The shared Python
and TypeScript types were updated together. `glare_orientation_grounded` is also
null until glare is assessed. Later, true denotes grounded orientation and false
denotes an assessment using the plan-normal/-Z fallback. No scoring or solver has
been added. See the recorded contract approval in `docs/decisions.md`.

Malformed JSON/schema and invalid geometry return HTTP 422:

```json
{"detail": [{"loc": ["body"], "msg": "Furniture height must be finite and positive", "type": "value_error"}]}
```

Field errors have more specific `loc` paths. Responses omit raw input and validation
context, including values that cannot safely be JSON-encoded. Known domain errors
use trusted messages; geometry-library/numeric errors use a generic message.
Unexpected programming errors (including TypeError/IndexError) remain structured
500 errors without internal details, never clean audits or disguised input errors.
A missing entry door leaves `walkable_floor_ratio` null in an HTTP 200 report;
other checks still run. Known but unusable doors yield zero. `GET /health` is
unchanged. `POST /solve` is still unimplemented.

## Front clearance

`detect_front_clearance(scene)` returns existing `ClearanceIssue` models. Check a
rectangle across the item's full bbox width, starting at its front face and
extending `requires_front_clear_m` in its rotated +Z direction. Zero disables the
requirement for that item. `actual_m` is the smallest forward distance to each
blocker anywhere across this width, capped to the required distance. This is
conservative access space, not an articulated furniture-door/drawer simulation.

Each blocking item produces at most one issue; a room-boundary obstruction uses
`blocked_by_item_id: null`. Results sort by target ID, boundary first, then blocker
ID. Boundary contact is allowed; area <= 1e-9 m² and deficits <= 1e-9 m are ignored
as numerical noise. Concave boundaries are checked across the whole strip.

Per the shared contract, chairs never block another item's front clearance.
Self is excluded. Other collision parts below the shared 2 m headroom threshold
block access, including low tabletops and fixed fixtures. High parts are ignored;
empty parts fall back to the solid bbox. This standing-headroom rule is a Dev 4
access approximation to review with Dev 3, separate from the shared chair rule.
Do not exempt whole table, bed, storage or fixture categories. More specific
exceptions (e.g. furniture intended to be used together) require explicit
relationships or access geometry that the current contract does not describe.

Product decision: skip chairs' own front-clearance checks as well, even when the
stored requirement is nonzero. A tucked chair should not warn simply because
its desk is in front of it. This additional target exemption was approved by the
Dev 4 operator; it leaves stored data unchanged and should be mirrored by any
frontend access preview. Chairs still participate in collision and free-floor
checks. The shared fixture reports only the bed blocked by the wardrobe (0.25 m
available versus 0.5 m required). Existing fixture tests only establish in-room
clearance endpoints, not obstacle-free access. For other categories, zero required
clearance disables the front-access check.

## Free floor area

`calculate_free_floor_ratio(scene)` returns a number in 0..1:

```text
area(interior floor minus union of blocking part projections) / area(interior floor)
```

A part blocks the floor when `y_min < WALK_HEADROOM_M` (currently 2 m), using
the shared contract. A low tabletop blocks walking beneath it even if a chair
can tuck under it. Parts starting exactly at 2 m do not block the floor. Empty
collision parts fall back to the solid metric bounding box. Fixed items count,
overlaps count once, and projections are clipped to the room. Invalid geometry
or duplicate item IDs raise `ValueError`; the input scene is not modified.

This is free geometric area, including disconnected regions and narrow gaps.
It does not establish reachable circulation or accessibility, and does not reserve
door-swing or furniture-front clearance areas. This metric is not assigned to
`AuditReport.walkable_floor_ratio`; the endpoint uses reachable area instead.

## Reachable walking space

`reachability.calculate_reachable_floor_ratio(scene)` uses the operator-selected
**50 cm passage width**, configurable via `passage_width_m` (default 0.5).
Model a person as an upright circle with a 25 cm radius:

1. Subtract the same blocking part projections as the free-floor calculation.
2. Shrink free space by the person's radius to find valid centre positions.
3. Keep connected regions entered through any suitable door. Test the full
   opening, not just its midpoint; the person must fit between the jambs and
   have the shared 2 m headroom. Use stored door direction to locate the opening.
4. Sweep the person's circle over those regions, clip to free floor, union results,
   and divide by the full usable floor area. Multiple doors never double-count.

An empty enclosed pocket or a region behind a 49 cm passage does not count as
reachable from a door on the other side. An additional door into that region can
make it reachable. At exactly 50 cm, contact is allowed within numerical precision.
An empty square room can be slightly below 100%: a round person cannot cover the
very tips of its corners. This metric is neither raw empty floor nor just the area
of valid centre positions. It must remain distinguishable from free-floor ratio.

No doors means entry is unknown and returns null. Doors too narrow/short, or
entrances entirely obstructed by furniture, contribute no entry; if none reaches
a region the result is zero. Fixed objects and chairs remain walking obstacles.
High parts are excluded by the shared headroom rule. Low doorways are not treated
as crawl-through passages. Inputs, duplicate IDs and geometry are validated.

Door-swing obstruction and walking access answer different questions. A plant
clipping the swing arc still produces `blocked_doors`, but does not make the room
unreachable if the doorway is physically passable. Entry segments and eroded free
floor reject entrances that cannot accommodate the person. We do not simulate
the articulated leaf or infer an achievable opening angle. Circular buffers use 32
segments per quadrant; a 1e-9 m radius reduction handles exact-width contact.
These are geometric approximations, not certified accessibility measurements.
The audit endpoint assigns this result to `AuditReport.walkable_floor_ratio`.
Consumers must use the documented reachable-area meaning.

## Shared geometry and regression cases

The full audit builds item volumes, below-headroom projections, broad-phase bounds
and the free-floor union once per request. All checks use that context; standalone
functions still build their own geometry. Nothing is cached across room edits.

The chair exception is limited to front access; a chair still occupies walking
space. L-shaped/re-entrant rooms are checked over the whole front strip, not a
centre ray; intrusion into one side is intentionally a violation. Wall thickness
is not subtracted twice because `floor_polygon` already follows interior faces.
Tests include independent world-space 90/270-degree examples, 45-degree cases,
clear/obstructed L-shaped rooms, partial reports without doors, nullable/legacy
contracts, blocked-door entry, safe error responses and request-local cache reuse.

Run the focused tests from the repository root:

```bash
uv run --extra spatial pytest tests/spatial_engine/test_free_floor.py
uv run --extra spatial pytest tests/spatial_engine/test_reachability.py
```

## Layout suggestions: `POST /solve` (issues #33, #34)

`POST /solve` accepts `OptimiseRequest` and returns `LayoutProposal`. Sonnet reads
the optional `instruction`, then proposes poses through the tools above; our
code audits every draft. The submitted scene is never modified and nothing is
applied to the editor. Development URL: `/api/spatial_engine/solve`.

Configuration (server-side, root `.env`): `ANTHROPIC_API_KEY`, and optionally
`SPACESHIFT_LAYOUT_MODEL` (default `claude-sonnet-5-5`). Calls cost money.

How a request runs (`agent.propose_layout`):

1. If there is an instruction, one model call turns it into a goal, extra locked
   items, items wanted near a window, and a list of things it cannot express
   ("more storage"). An explicit `goal` wins; the model can add locks but never
   remove the caller's or unlock fixed items; unknown IDs are dropped.
2. A tool loop explores drafts. Tool errors go back to the model as error results.
3. The best draft is rebuilt and audited again from scratch. It is returned only
   if it may be recommended (see the tools section) and still ranks better than
   the original. A door that stays blocked is named in `report` and `explanation`.
   A room where nothing can move is answered at once without a model call.

Limits per request (`AgentLimits`): 8 model calls including the interpretation
call and retries, 24 layout evaluations (or `max_candidates` if lower), 200k
tokens, 90 seconds, 60 furniture items. One retry is allowed for rate limits,
timeouts and server errors. A truncated or declined model turn is never executed.

Read `improved` and `outcome` together:

| `improved` | `outcome` | Meaning |
| --- | --- | --- |
| true | `completed` | Verified better layout in `poses`; `report` audits it |
| true | `stopped_early` | Verified better layout, but a limit or assistant error cut the search short |
| false | `completed` | The assistant finished and found nothing better |
| false | `stopped_early` | A limit was reached before anything better was found |
| false | `assistant_unavailable` | No API key, or the assistant failed; not a verdict on the room |

When `improved` is false, `poses` is empty and `report` audits the unchanged
scene. `report.scene_id`/`scene_revision` always identify the submitted scene.
`explanation` is written by the server from measured results, not by the model,
and lists unhandled parts of the instruction. `goal` is the goal applied.
Bad scenes, unknown `locked_item_ids`, more than 60 items or an instruction over
500 characters return HTTP 422 before any model call. Only outcome, counts and
error kinds are logged; never the key, the prompt or the reply.

Automated tests use scripted replies and the real SDK over a mock HTTP transport;
they make no paid calls. One live run on 2026-11-14 with `claude-sonnet-5-5` on
the shared mock room ("Keep my bed where it is, but move the desk near the
window") took 28.7 s: 3 model calls of 7-11 s each, 9,730 tokens, 1 layout
evaluation. It kept the bed, placed the desk within 0.5 m of the window and
cleared the blocked door and the bed's access issue. Model time dominates; our
geometry takes a few milliseconds per evaluation. This is one run, not a
benchmark.

Two speed-ups followed, and the same request then took 10.2 s (2 calls, 5,070
tokens, again one run). The typed request is read by `claude-haiku-5-5` at low
effort (`SPACESHIFT_INTERPRET_MODEL`), which took 2.1 s instead of 10.2 s. And
`AgentLimits.stop_at_first_valid_draft` (default true) ends the search at the
first draft that is valid and better than the original, skipping the model's
refinement round and closing turn. The cost is that a good first draft is not
improved further; set it to false to restore full exploration. An invalid first
attempt does not stop the loop. Accepting a proposal and re-auditing reproduces `report` apart from
the revision (covered by a test).

```bash
uv run --extra spatial pytest tests/spatial_engine/test_agent.py
```

PR #49 review follow-up: instruction interpretation retries a transient provider error
once within the shared request budget. If interpretation still fails, exploration
continues with explicit caller settings and the explanation says the written request
was not applied. Extra interpreter keys and excess unsupported phrases do not discard
valid locks. Brightness runs only for the brighter goal; its geometry checks allow
5 mm of reconstruction rounding. Provider clients are reused by configuration.

The additive Python/TypeScript contract changes in PR #49 still require explicit
team sign-off, particularly from frontend, before merge (the review by bananadado on 14 November 2026).
This implementation follow-up does not constitute that sign-off.

## Demo home checks (issue #36)

`scripts/check_layout_demo.py` builds each room of the shared three-floor demo
home the way the editor does and audits it. Without arguments it is free and
offline; `--solve ROOM_ID "request"` makes one paid live request.

```bash
uv run --extra spatial --extra reconstruction python scripts/check_layout_demo.py
```

Measured on 2026-11-14 on a developer laptop: all 25 demo rooms audit, median
1.5 ms and at most 3.0 ms per audit. Live requests with the default models:

| Room | Request | Time | Result |
| --- | --- | --- | --- |
| `g-bed2` | Give me more usable walking space. | 10.5 s | 3 items moved; door cleared; reachable floor 0% to 42% |
| `f-bed4` | Make the room feel brighter. | 5.8 s | 1 item moved; door cleared; windows were already unobstructed |
| `g-kitchen` | Improve access without moving much furniture. | 4.9 s | No change proposed; the only problem is a fixed item in a door swing |
| `s-bed8` | Add more storage and keep the bed where it is, but make it roomier. | 15.3 s | 2 items moved; bed kept; "more storage" reported as not handled |

Each row is a single run of 2 model calls and 4,000 to 5,500 tokens. Results
vary between runs. There is no cached or fallback answer: if the assistant is
unavailable the response says so.
