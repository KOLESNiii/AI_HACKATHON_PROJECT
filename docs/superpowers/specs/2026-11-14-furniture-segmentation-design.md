# Furniture masks and placement evidence — issue #15

Status: implemented; design, live probe findings and the live result below. Builds on the #14 selector
(`2026-11-14-video-frame-selection-design.md`). Branch:
`feat/dev2-segment-furniture-and-retain-placement-evidence`.

## Intent

#14 gives every physical furniture item a permanent ID, its sightings (coarse boxes in upright
source frames) and up to four selected views. Dev 1's room alignment (#8) and mesh
reconstruction (#16) need more than a box: which pixels are the item. #15 produces, for every
selected view of every item, an instance mask and a cut-out crop, stored durably and linked to
the item ID and the exact source frame.

Goals: one mask and crop per item per selected view; mask pixels in upright source-frame
coordinates; masks reachable through the existing `AssetEvidence` handoff; reruns free.
Non-goals: meshes, proxies and `extract_furniture` (#16), metric size (#17), plan fitting and
poses (#8), HTTP routes (Dev 1), temporal mask propagation, masks for non-selected sightings.
Anti-goals: a mask attributed to the wrong ID; a rerun that pays again for a stored mask; a
provider failure that loses an item or raises past the pipeline.

## Live probe (2026-11-14, approved by the operator: at most 20 requests)

Two `fal-ai/sam-3/image` requests on source frame 0 of the reviewed opening room (480 × 848
upright PNG), `apply_mask=false`, `prompt=""`:

| Check | Observed |
| --- | --- |
| One box prompt | One mask, 2.0 s, score 0.957 |
| Four box prompts, `object_id` 1–4, `return_multiple_masks=true` | Four masks, 2.4 s |
| Mask format | Single-channel 8-bit PNG, values 0/255, exactly frame-sized, on `*.fal.media` |
| Mapping | `masks` are ordered by score; `metadata[i].index` is the 0-based prompt-box position. All four masks matched their own box |
| Box prompt units | Integer pixels `x_min, y_min, x_max, y_max` |
| `boxes` output | `null` even with `include_boxes=true`; compute the box from the mask |
| Quality | Rear sofa excludes the table in front of it; table, right sofa and chair are separate instances |

A good mask can extend past its coarse reviewed box (rear sofa by 18 px, chair by 9 px), so
acceptance compares the mask's own bounding box with the prompt box instead of clipping to it.
Local GrabCut inside the same boxes runs offline but includes floor under the table and the
table in front of the sofa: usable as a labelled fallback, not as the primary source.

## Approaches

| Approach | Trade-off |
| --- | --- |
| **SAM 3 image, all of a frame's item boxes in one request (chosen)** | Clean instance masks; one request per frame; needs `FAL_KEY` and uploads frames |
| SAM 3 text-prompted video masks | Probed in #14: merges both sofas and has no object IDs. Rejected |
| GrabCut inside each box (kept as offline default) | No network or cost; approximate. Never the silent substitute for a failed live call |
| `fal-ai/sam-3/3d-objects` box prompts directly in #16 | Skips this stage but leaves Dev 1 without mask evidence and gives no review step |

## Design

- **Provider boundary.** `MaskProvider.segment(frame, image, boxes, registry, budget=)` returns
  one boolean frame-sized mask (or `None`) per box, in order. `GrabCutProvider` (`method
  "grabcut"`) is the offline default; `FalSamProvider` (`method "sam3"`) is explicit opt-in.
  A provider raises only `MaskError`, with a message safe to show.
- **Acceptance of a mask.** Frame-sized, at least 16 px, and the IoU of its tight bounding box
  with the prompt box is at least 0.3 (probe: 0.61–0.76 for correct masks, 0.22 between the
  chair and the right sofa). A rejected mask is reported and never stored.
- **Storage.** `masks/<sha256(scene_id)[:16]>/<item id>/<source[:12]>-<stream>-<ordinal>-<digest[:10]>.png`
  under the runtime data directory, plus `….crop.png` (RGBA cut-out of the original pixels,
  cropped to the mask's bounding box). Names contain the content digest, so a file never
  changes; files are written atomically.
- **Record.** `SelectedObject.masks: list[MaskRecord]` in the existing SQLite registry
  snapshot: `frame_key`, the prompt `box`, `method`, `mask_path`, `crop_path`, `bbox_px`
  `(x, y, w, h)`, `area_px` and the provider's `score` when it reports one. A record whose `box` differs from the current sighting box, or
  whose file is gone, is stale and is redone. Old snapshots load with no masks.
- **Pipeline.** `segment_furniture(scene_id, *, data_dir, provider=None, object_ids=None,
  replace=False, max_requests=16) -> SegmentationResult`. Work is grouped by frame; provider
  calls run outside the registry transaction; each frame's records are attached in one
  transaction that re-checks the item and its box. `complete` means every requested view has
  a stored mask. Overlapping masks of different items in one frame (> 20 % of the smaller),
  SAM scores below 0.8 and GrabCut provenance are warnings.
- **Live requests.** One request per frame, cached and recoverable through the registry's
  request table exactly like #14: only the reservation winner submits, the request ID is
  saved, a retry or `replace` re-reads the saved request for free, an uncertain submission is
  never repeated, `refresh` deliberately pays again. Masks are downloaded at once over HTTPS
  from `fal.media` hosts only, size-bounded, and validated before they count as evidence.
- **Handoff.** `object_evidence` fills `EvidenceFrame.mask_url` and uses the mask's tight
  `bbox_px` when a current mask exists, and prefers a view without a low-confidence mask as
  the primary frame. `mask_url` is a reference relative to the asset data
  directory, read with `segmentation.read_mask(data_dir, mask_url)`; it is not browser-facing.
  `contracts/` and `assets/models.py` do not change.
- **CLI.** `python -m services.reconstruction.assets.segment_items --scene-id … --data-dir …
  --out …` writes `segmentation.json`, `evidence.json` (README section 3 shape), mask overlays
  and cut-outs. Offline by default; `--live` uploads. Exit 0 complete, 2 incomplete, 1 invalid.

## Live result (2026-11-14)

Six further requests (eight of the approved 20 in total) segmented the reviewed opening room:
14 of 14 selected views of the four items, no rejected masks, no overlaps above the threshold.
A rerun with `--replace --max-requests 0` re-read all six saved requests without submitting.
Overlays were inspected by the coding agent, not independently verified. Wide and medium views
are clean (scores 0.92–0.98). Three blurred close-ups scored 0.57–0.71 and are ragged; this
motivated storing `score` and the low-confidence warning. One close-up of the right sofa
scored 0.94 but includes a hand at the frame edge, so a high score is not proof of a clean
mask. Images, masks and provider URLs stay local; none are committed.

## Left to the builder

Internal helper names, report layout, and test fixtures. No dependency, manifest, contract or
route changes; anything that would need one stops for coordination.

## Needs coordination

Dev 1 (#8/#9): the `mask_url` resolution rule above, and whether selected views (at most four
per item) are enough evidence for alignment.
