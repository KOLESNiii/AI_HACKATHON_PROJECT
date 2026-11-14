# Dev 2 — Asset handoff (DRAFT, pending Dev 1 sign-off)

Tracks issue #13 (Dev 2.1), parent #2. **Nothing here is agreed yet** — this file is
the proposal Dev 1 reviews on the PR. Update it in place as the agreement settles.

## Scope of the agreement

Dev 2 produces individual, normalised furniture assets. Dev 1 consumes them and owns
alignment and final room poses. This file fixes the five things that cross that boundary:
object IDs, source-frame/mask evidence, mesh references, dimension provenance, and the
asset function interface.

## 1. Stable object IDs

`FurnitureItem.id` format: `{source_tag}-{category}-{ordinal}` — e.g. `vid-desk-01`,
`cat-chair-02`. `source_tag` is `vid` (`extracted_video`), `cat` (`catalog_search`),
or `url` (`url_import`).

Stability rule: an ID identifies one physical object across re-runs, re-segmentation and
mesh regeneration. Deduplicating two views of the same object keeps the lower ordinal.
Dev 2 never reassigns an ID once handed over; a re-extraction that genuinely finds a new
object gets a new ordinal.

## 2. Source-frame / mask evidence

**Not in `contracts/schema.py` today.** `FurnitureItem` has no evidence field, and
`contracts/` needs team sign-off (CLAUDE.md rule 1), so this is the open question for
Dev 1 on this PR. Proposal — a sidecar keyed by object ID rather than a contract change:

```json
{
  "vid-desk-01": {
    "frames": [{"frame_index": 412, "timestamp_s": 13.73, "mask_url": "...png", "bbox_px": [x, y, w, h]}],
    "primary_frame_index": 412
  }
}
```

Dev 1 needs: the object ID, at least one frame identity, and the mask for that frame.
Decision needed: sidecar (`assets/<scene_id>/evidence.json`) vs. an added contract field.

## 3. Mesh references

`FurnitureItem.glb_url` is the only mesh reference. It points at a normalised `.glb`
(see §4). Dev 2 guarantees the URL is stable for the life of a scene and that the mesh
behind it is never swapped for a differently-normalised one without a new ID.

## 4. Normalisation guarantee (CLAUDE.md rule 2)

Every `.glb` Dev 2 hands over has bounding-box bottom-centre at `(0, 0, 0)`, logical
front facing `+Z` (`yaw_deg = 0`), units in metres. `bbox_m` is the post-normalisation
measurement, not the generator's raw scale. Dev 1 applies `pose` on top without rescaling.

## 5. Dimension provenance

**Also absent from the contract.** Measured dimensions must stay distinguishable from
estimates (issue #2, task 5). Proposed values, carried in the same sidecar as §2:

| value | meaning |
|---|---|
| `measured` | derived from a known in-frame scale reference |
| `estimated` | inferred from category priors / generator output |
| `catalog` | taken from retailer-published dimensions |
| `unknown` | needs correction before the layout is trusted |

`unknown` must surface as a correction request, not a silent default.

## 6. Asset function interface

Dev 2 supplies functions; Dev 1 wires them into reconstruction routes (`docs/architecture.md`).
Proposed signatures, all returning contract types from `contracts/schema.py`:

- `extract_furniture(video_path, scene_id) -> list[FurnitureItem]`
- `import_catalog_asset(product_url, scene_id) -> FurnitureItem`
- `normalise_mesh(glb_path) -> tuple[str, BBoxM]`  (same path for both sources — no second normaliser)

Failure contract: provider failure yields a labelled, dimensioned proxy box with
provenance `estimated`, never an exception across the boundary and never a missing item.

## 7. Fixture assets

Two fixtures live in `fixtures/` so Dev 1 can integrate before real extraction works.
See `fixtures/README.md` for what is and is not present.
