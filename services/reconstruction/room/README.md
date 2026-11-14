# Floor-plan parser (Dev 1)

Turns floor-plan images into contract geometry: every floor and every room, each room as a
`RoomScene` (`furniture == []`) inside a `ParsedFloorPlan` (`contracts/schema.py`).

## How it works

Hybrid: OpenCV does all the geometry; a vision LLM only reads text.

| Step | Module | What it does |
|---|---|---|
| 1 | `raster.py` | Resample to 2000 px, flatten lighting (photographed printouts), threshold. Keep strokes of wall thickness; drop text, hatching, door leaves, glazing and furniture symbols. |
| 2 | `annotate.py` | Vision LLM on fal.ai reads room labels with printed metric dimensions, floor captions and the compass. Returns JSON only; never geometry. |
| 3 | `regions.py` | Doors and windows are gaps in the walls. Wall ends cast rays along their wall (or pair up across bay corners) to bridge each gap. Long bridges count only if glazing lines run along them. Rooms = enclosed free space; floors = connected wall masses. |
| 4 | `parse.py` | Scale per floor from labelled rooms whose two printed dimensions agree (median); second gap pass with metric door/window limits; merge slivers (stair treads, wardrobes, partitions); assign captions to floors. |
| 5 | `polygon.py` | Room contour → straightened polygon (snapped to 45° multiples), contract winding. |
| 6 | `openings.py` | Bridges → walls. Glazed exterior gap = window; anything else = door. Hinge and swing side come from the drawn leaf. |

Each floor has its own frame: metres, origin at the floor's top-left wall bound, +X right,
+Z down the image. All rooms on a floor share it.

## Use

```bash
# API (port 8001): POST images, then fetch the plan or one room
curl -F files=@examples/one_floor.jpg localhost:8001/floor-plans
curl localhost:8001/floor-plans/<plan_id>
curl localhost:8001/floor-plans/<plan_id>/rooms/<room_id>     # -> RoomScene

# Debug CLI: plan.json plus a render of the returned geometry per floor
uv run python -m services.reconstruction.room examples/three_floor.png --out /tmp/plan \
    --annotations services/reconstruction/room/fixtures/three_floor.annotations.json
```

Plans are cached in memory by `plan_id`, which is a hash of the image bytes.

Configuration: `FAL_KEY` (required for labels). Optional: `FAL_VISION_ENDPOINT` (default
`fal-ai/any-llm/vision`) and `FAL_VISION_MODEL` (default `google/gemini-2.5-flash`). Without
a key, or if the call fails, rooms are still traced. Scale is then estimated from door widths
and every room carries `dimension_source = "estimated"` and `"dimensions"` in
`correction_needed`.

## Status and limits

- **The fal call has not been run live yet** (no key during development). Its request and
  response shape follows fal's any-llm vision API and is unverified. The fixtures in
  `fixtures/` are hand-transcribed from the two example plans, not recorded model output.
- `shell_glb_url` points to `/api/reconstruction/shells/<scene_id>.glb`. The shell generator
  that serves it is the next step.
- Open archways wider than a door, with no glazing, are not split, so both rooms come out as
  one region (named `A / B`, with a warning). Stairs and landings can fragment.
- Photographed printouts are not perspective-corrected; mild keystone costs a few percent.
- Door hinge and swing are inferred from the drawn leaf. When no leaf is found, the room gets
  `"openings"` in `correction_needed`.
