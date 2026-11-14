# Spatial engine

Pure checks live in `audit.py`; `report.py` composes them for `POST /audit`.
Geometry comes from shared scene JSON, never from mesh downloads.

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
and TypeScript types were updated together. `glare_orientation_grounded` remains
false until a grounded glare calculation is implemented. No scoring or solver
has been added.

Malformed JSON/schema and invalid geometry return HTTP 422:

```json
{"detail": [{"loc": ["body"], "msg": "Reachability needs at least one door as an entry point", "type": "value_error"}]}
```

Field errors have more specific `loc` paths. Responses omit raw input and validation
context, including values that cannot safely be JSON-encoded. A missing entry door
is invalid for this endpoint; a valid room whose doors cannot be traversed returns
a reachable ratio of zero. Unexpected faults remain server errors, never clean
audits. `GET /health` is unchanged. `POST /solve` is still unimplemented.

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

No doors means entry is unknown and raises `ValueError`. Doors too narrow/short,
or entrances entirely obstructed by furniture, contribute no entry; if none reaches
a region the result is zero. Fixed objects and chairs remain walking obstacles.
High parts are excluded by the shared headroom rule. Low doorways are not treated
as crawl-through passages. Inputs, duplicate IDs and geometry are validated.

The walking calculation assumes door openings are available for passage. A blocked
door leaf remains a separate finding; this metric does not simulate opening a door
or infer a passable opening from its current leaf angle. Circular buffers use 32
segments per quadrant; a 1e-9 m radius reduction handles exact-width contact.
These are geometric approximations, not certified accessibility measurements.
The audit endpoint assigns this result to `AuditReport.walkable_floor_ratio`.
Consumers must use the documented reachable-area meaning.

Run the focused tests from the repository root:

```bash
uv run --extra spatial pytest tests/spatial_engine/test_free_floor.py
uv run --extra spatial pytest tests/spatial_engine/test_reachability.py
```
