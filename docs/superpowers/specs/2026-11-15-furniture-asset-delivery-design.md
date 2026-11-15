# Furniture asset delivery and checks (#18, Dev 2.6)

## Intent

M1 needs two video furniture items that load through Dev 1's scene, move independently and
keep their IDs and bounds. #16 and #17 produce, per item, a labelled proxy and (when the raw
mesh normalises) a mesh asset. Nothing yet decides which of the two Dev 1 receives, and
nothing re-checks a file before it is handed over. This issue adds that step and its checks.

## Goals

- One call that gives Dev 1 a scene's furniture: the normalised mesh where it passes its
  checks, otherwise the labelled proxy. Same ID either way; no item is ever dropped.
- Checks that run on what is actually stored: normalisation (bounds, origin, profile budgets)
  and failure fallback (a proxy is labelled, sized and honest about its provenance).
- A check that a scene assembled by Dev 1 still carries each asset's ID, bounds and mesh.
- A CLI that runs the checks on pipeline data and fails loudly, for the PR record and for #20.

## Non-goals

- No provider request. Delivery is offline: it reuses what the pipeline stored.
- No change to `contracts/`, the app entry point, `room/` or the frontend. Dev 1's
  `RealRoomFurniture` (PR #55) loads prepared `assets.json` from the offline delivery CLI;
  never run delivery during scene assembly. Regenerate the list after input changes. The editor already draws non-proxy items from `glb_url`
  fitted to `bbox_m` and falls back to a labelled box when a file fails to load.
- No mesh-quality work (#19) and no persistent cache (#12, #20).

## Approaches

1. **Deliver inside `reconstruct_furniture`** (make `asset` the only output). Rejected: it
   removes the proxy that callers and the CLI report use, and mixes paid reconstruction with
   a read-only handoff.
2. **Leave the choice to Dev 1** (`item.asset or item.proxy` in `room/`). Rejected: the
   fallback rule and the checks would live outside the asset pipeline, and each consumer
   (video now, catalog in #19) would repeat them.
3. **A delivery module in `assets/`** (chosen). `delivery.py` wraps the offline
   `reconstruct_furniture`, checks each candidate file and returns the assets with a check
   record per item. Dev 1 and the CLI both call it.

## Design

`services/reconstruction/assets/delivery.py`:

- `inspect_asset(asset, *, data_dir, url_base) -> AssetCheck` re-reads the stored file and
  lists problems:
  - the URL is in the asset store, the file exists and its bytes hash to its name;
  - binary glTF with no skins, animations or cameras and identity node transforms;
  - at most `MAX_TRIANGLES` and `MAX_BYTES`;
  - bounds equal `bbox_m` within `GLB_BBOX_TOLERANCE_M`, which also fixes the bottom-centre
    at the origin;
  - the asset still satisfies the `FurnitureItem` rules;
  - an `estimated` size asks for `"dimensions"`.
- `deliver_furniture(scene_id, *, data_dir, dimensions=None, object_ids=None, url_base=...)
  -> Delivery`. Per item: the mesh asset if it has no problems, else the proxy with a
  `fallback_reason` and a warning. A delivered proxy must be `is_proxy`. `Delivery.ok` is
  true when no delivered asset has a problem and IDs are unique. Unknown scenes raise
  `ValueError`, as `reconstruct_furniture` does.
- `check_placed(scene, assets) -> list[str]`: every asset appears exactly once in the scene
  with every field unchanged except `pose`; `correction_needed` may only grow.

`check_delivery.py` (CLI): prints a JSON summary, optionally writes `assets.json`,
`delivery.json` and `report.md`. Exit 0: all checks pass and at least `--min-items` (default
2) items; 2: a check failed or too few items; 1: invalid input.

## Tests

`tests/reconstruction/assets/test_delivery.py`: meshes are delivered and pass; a failed or
unnormalisable mesh delivers its proxy while the other item keeps its mesh; each check
detects its fault (wrong bounds, missing file, altered bytes, unflagged estimate); a mesh
that fails its checks falls back; two delivered items go through `GET /scenes`, are fetched
from the asset route, keep IDs and bounds, move independently and are accepted by the audit;
CLI exit codes.
