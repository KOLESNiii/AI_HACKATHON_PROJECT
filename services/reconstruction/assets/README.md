# Dev 2 → Dev 1 asset handoff

The agreement for issues #13 (Dev 2.1) and #5 (Dev 1.1). The reasoning behind each decision
is in `docs/superpowers/specs/2026-11-14-3d-representation-design.md`; section numbers below
refer to it. The contract types are in `contracts/schema.py`.

Dev 2 produces individual, normalised furniture assets. Dev 1 consumes them, decides where
each stands, and assembles the `RoomScene`.

## 1. IDs

- `FurnitureItem.id` matches `^[a-z0-9][a-z0-9_-]{0,63}$` (`ITEM_ID_PATTERN`) and is unique
  within a scene.
- IDs are opaque. No code reads the category or source out of an ID; those are fields.
- Dev 2 generates IDs as `{source}-{category}-{nn}`, for example `vid-desk-01`. That is a
  naming habit, not a format anyone may rely on.
- An ID identifies one physical object for the life of a scene. Stability comes from a
  persisted per-scene registry that maps each ID to its evidence (arrives with #14), not from
  the naming scheme, because a re-run may detect objects in a different order.

## 2. What Dev 2 returns

An asset: every `FurnitureItem` field except `pose`, plus evidence (section 3). Dev 2 does
not know where an object stands. Dev 1 aligns the asset to the floor plan and adds the
`pose`, which makes it a `FurnitureItem` (spec 9.1).

## 3. Evidence

Evidence ties an asset to the frames it was seen in, so Dev 1 can align it.

```json
{
  "vid-desk-01": {
    "frames": [
      {
        "frame_index": 412,
        "timestamp_s": 13.73,
        "image_size_px": [1920, 1080],
        "mask_url": "…/mask.png",
        "bbox_px": [x, y, w, h],
        "provider_pose": { }
      }
    ],
    "primary_frame_index": 412
  }
}
```

- At least one frame per asset; `primary_frame_index` names one of them.
- `image_size_px`, `mask_url`, `bbox_px` and `provider_pose` may be `null`. Fixtures have no
  source video, so all four are `null` there and Dev 1's alignment must tolerate that.
- For video items, `mask_url` is a reference relative to the asset data directory, read with
  `segmentation.read_mask(data_dir, mask_url)`. It is not a browser URL (see #15 below).
- `provider_pose` carries the raw per-object rotation, translation, scale and camera pose
  that `fal-ai/sam-3/3d-objects` returns. The verified SAM 3D shape is documented under #16 below.
- Evidence stays inside the reconstruction service. It is never placed in `RoomScene`, which
  the editor sends to the audit on every move. Its types are `EvidenceFrame` and
  `AssetEvidence` in `models.py`.

## 4. Mesh references

- `glb_url` is an absolute URL or a site-root path that the browser can fetch as written.
  It is never a filesystem path and never a raw provider URL: fal.ai output is downloaded,
  normalised and re-hosted.
- The file behind a `glb_url` never changes. The item `id` is permanent. Replacing a proxy
  with a real mesh, or a mesh with a better one, puts a new `glb_url` on the same `id`.
- `bbox_m` is authoritative and the mesh is fitted to it, so swapping a mesh never
  invalidates an audit or a proposed layout (spec 7.3).

## 5. Normalisation guarantee

Every furniture `.glb` Dev 2 hands over meets this profile (spec 7.1):

| Property | Requirement |
|---|---|
| Format | glTF 2.0 binary, one self-contained file, textures embedded. |
| Frame | Metres, +Y up, front +Z, bounding-box bottom-centre at the origin. |
| Bounds | Equal to `bbox_m` within 1 mm on every axis (`GLB_BBOX_TOLERANCE_M`). |
| Scene graph | Transforms baked into vertices; no skins, animations, cameras or lights. |
| Geometry | At most 30,000 triangles (target 15,000). |
| Material | Standard metallic-roughness; base colour texture at most 1024 px. |
| Size | At most 3 MB (target 1.5 MB). |
| Proxy | A plain box of `bbox_m`, with `is_proxy: true` on the item. |

Dev 1 applies `pose` on top without rescaling.

## 6. Occupied volume

- `collision_parts` lists boxes inside `bbox_m`, in the mesh's own frame, so that furniture
  can nest: a chair under a desk, a table over a radiator. An empty list means one solid box.
  The collision rule is in the `contracts/schema.py` module docstring.
- Dev 2 fills the parts in: first from a category template fitted to `bbox_m` (which also
  works for proxies), later refined from the mesh. `collision_source` records which. The templates are
  `collision_templates.template_parts(category, bbox_m)`; proxies and normalised meshes both
  use them (#17).
- Template parts are guesses. A nested fit that relies on them is an estimate.
- `is_fixed: true` marks an item that is part of the room, such as a radiator. It is checked
  like any other item but is never moved.

## 7. Dimension provenance

`dimension_source` says where `bbox_m` came from:

| Value | Meaning |
|---|---|
| `measured` | Derived from a known scale reference in the capture. |
| `catalog` | Retailer-published dimensions. |
| `user_corrected` | Entered or confirmed by the user. |
| `estimated` | Inferred from category priors or generator output. |

All but `estimated` are trusted. There is no "unknown" value: an unknown size is `estimated`
with `"dimensions"` in `correction_needed`, so it surfaces as a request to the user and never
as a silent default.

## 8. Functions and failure contract

Agreed signatures; the issue that implements each is noted. Dev 1 wires them into the
reconstruction routes (#9). The types they use are in `models.py`.

```python
async def extract_furniture(video_path: Path, scene_id: str) -> list[FurnitureAsset]   # #14–#16
def import_catalog_asset(product_url: str, scene_id: str, *, data_dir: Path,
                         ...) -> CatalogImport                                         # #19, implemented
def normalise_mesh(raw_glb: Path, *, category: str, target_bbox: BBoxM | None,
                   data_dir: Path, front: Front | None = None,
                   url_base: str = ASSET_URL_BASE) -> NormalisedMesh                    # #17, implemented
def deliver_furniture(scene_id: str, *, data_dir: Path, ...) -> Delivery               # #18, implemented
```

`FurnitureAsset` is the pose-less asset from section 2; Dev 1 places one with
`asset.to_item(pose)`, which also applies every `FurnitureItem` rule. `NormalisedMesh` carries `glb_url`,
`bbox_m`, `collision_parts`, `collision_source` and `correction_needed`. Video and catalog
assets go through the same `normalise_mesh`; there is no second normaliser.

A provider failure never raises across this boundary and never drops an item. It returns a
labelled proxy box: `is_proxy: true`, `dimension_source: "estimated"`, and `"dimensions"` in
`correction_needed`.

## 9. Fixtures

The fixture assets are in the shared fixture scene, `contracts/mock_room/mock_scene.json`:
a desk with a tucked chair and a table over a fixed radiator. See `fixtures/README.md`.

## 10. Room inputs (#5)

`RoomCaptureInputs` in `contracts/schema.py`:

- 1 to 5 floor-plan images (`MAX_FLOOR_PLAN_IMAGES`) and 1 to 5 walkthrough videos
  (`MAX_ROOM_VIDEOS`) per room. URLs follow the `glb_url` rules.
- Scale comes from the dimension labels printed on the floor plan. Labelled lengths are read
  directly and the remaining walls are scaled from them; geometry sized this way is
  `dimension_source: "measured"`. A plan without readable labels gives `estimated` sizes with
  `"dimensions"` in `correction_needed`.

## Still open

- The collision check itself and shared collision test vectors are Dev 4's (#29–#30).

## Implemented: frame selection and identity (#14)

`selection.select_furniture_frames(videos, scene_id, *, data_dir, provider=None, options=None)`
returns an internal `SelectionResult`, not a finished mesh or `FurnitureAsset`. The agreed
`extract_furniture(Path, scene_id)` façade remains for #16. Neither the shared contracts
nor the existing evidence types change.

Requirements: the reconstruction Python extra and FFmpeg/FFprobe on `PATH` (verified with
FFmpeg 8). Tests generate small VFR/rotation clips and need a build supporting
`-display_rotation` and `-fps_mode` (both verified with FFmpeg 8). No additional Python dependencies, database server or ORM are needed.
The standard-library SQLite registry and frame images live under `data_dir`; keep that
directory between retries. Removing it loses ID history. The default CLI data directory is
`artifacts/furniture`, already ignored by Git.

Offline sampling (no network or credentials):

```bash
uv run --extra reconstruction python -m services.reconstruction.assets.select_frames \
  examples/three_floor_3.mp4 --scene-id opening-room --start 0 --end 6 --max-frames 8 \
  --data-dir artifacts/furniture --out /tmp/furniture-report
```

The report includes upright frame contact sheets, per-item labelled views, full original
image references, actual source frame ordinals/PTS, and JSON evidence. Exit codes: `0` for
complete reviewed sampled discovery, `2` for incomplete/review-required discovery (report
still written), `1` for invalid options/media/storage. Completeness concerns requested sampled
frames, not an exhaustive inventory of a house.

For live proposals, add `--live` and supply `FAL_KEY` server-side. For example, add
`--env-file .env` to `uv run`. Configuration reuses `FAL_VISION_ENDPOINT` (default
`fal-ai/any-llm/vision`) and `FAL_VISION_MODEL` (default `google/gemini-2.5-flash`). Individual
full-resolution images and reference crops are uploaded only in live mode. Source PNGs are
retained without relighting or texture edits for later material reconstruction.

Live testing exposed missed/merged objects and chair-part splitting in vision proposals,
including a stronger model. **AI proposals always carry a review warning and return code 2.**
They are not certified furniture identities. Inspect `selection.json`/the labelled images,
correct a `Discovery` JSON recording, and use `--recorded <file>` for reviewed results. A
recording groups sightings of one physical item, with full source frame keys and normalised
upright boxes; `RecordedProvider` maps the group across batches. Use a separate scene ID
for the reviewed inventory when replacing a faulty initial proposal: this issue never
silently deletes existing IDs. Editing/merging established identities remains explicit work.

Reproducible reviewed acceptance case, without provider calls:

```bash
uv run --extra reconstruction python -m services.reconstruction.assets.select_frames \
  examples/three_floor_3.mp4 --scene-id reviewed-opening-room --start 0 --end 6 --max-frames 8 \
  --data-dir artifacts/furniture --out /tmp/reviewed-furniture \
  --recorded tests/reconstruction/assets/fixtures/opening_room.reviewed.json
```

The coding agent visually reviewed the supplied **coarse visible boxes**; they are not
independently human-verified, SAM masks, or raw provider output. They cover four target items
in six frames: two separate sofas, a table
and one office chair. Automated tests repeat the run with reordered observations and require
the same IDs and evidence. No private images or generated assets are added by this issue.

`--batch-size` is 1–8, `--max-frames` caps sampling per video, and `--max-requests` bounds
new inference submission attempts per run. Cached results, saved-handle recovery and recorded
replays are free, so repeated runs advance past previously completed batches. A zero budget
still allows those free operations. Capped sampling/budget exhaustion is explicit.
Provider handles/results are cached by scene, ordered frame keys, model and prompt. A retry
recovers a saved request instead of resubmitting. A local wait deadline leaves the remote job
running so a later run can collect its result; it does not cancel the handle it saves.
Preparation/encoding/upload failures release their reservation and retry normally. Only a
failure after submission starts is uncertain and blocked to avoid duplicate charges.
`--refresh <new-label>` deliberately starts a new detection cache and can
incur new charges. Failed/partial outputs do not erase known inventory. Runtime errors are
sanitised; keys/provider HTTP bodies are not included in reports.

Review issues are scoped to source frames: successfully reprocessing a batch replaces those
frames' issues and preserves issues on other frames. Recognised reflections are excluded
with an informational warning and do not prevent completion. Existing unscoped registry
issues migrate conservatively onto their stored frames and clear as those frames are reviewed.
This clears diagnostics, not established IDs or unwanted initial proposal objects.

New live requests choose at most 16 nearby references from a larger registry and report any
omitted context; cache hits/recovery retain the original reference mapping. Additional
sightings do not silently overwrite established names, categories or appearance. Conflicting
categories require review; metadata corrections remain explicit work.

For multiple videos, source hashes distinguish equal frame ordinals. Each provider batch
belongs to one source. Cross-video reference matching requires `--room-key` identifying a
caller-confirmed physical room; filenames never establish storey/room identity. Unregistered
camera groups are not compared. Choose one continuous room segment for the first integration;
automatic room/storey assignment and long-occlusion re-identification are not established.

`selection.object_evidence(result, object_id, source_id=...)` adapts one source's sightings to
the existing `AssetEvidence`, with real ordinals/timestamps and pixel `(x,y,w,h)` boxes.
Multi-source items require explicit `source_id`; `provider_pose` remains null for #16 to
populate, and masks are filled by #15 (below). `geometry_frame_keys` is an ordered subset of original wide frames for
later camera estimation, not a grounded camera solution. Dev 1's #8 owns metric plan fitting
and final poses; no route or multi-video extraction façade is wired here.

## Implemented: masks and placement evidence (#15)

`segmentation.segment_furniture(scene_id, *, data_dir, provider=None, object_ids=None,
replace=False, max_requests=16)` gives every selected view (at most four per item) of every
registered item an instance mask and a cut-out, and returns a `SegmentationResult`. It reads
the #14 registry, so run frame selection first. Contracts, `models.py` and dependencies do
not change; no route is added.

Per item and view, stored under `data_dir` and recorded on the item in the registry
(`SelectedObject.masks`, a `MaskRecord` each):

| Field | Meaning |
|---|---|
| `frame_key` | The source frame: source hash, stream and decoded frame ordinal. |
| `mask_path` | 8-bit PNG, 255 = item, the size of the upright source frame. |
| `crop_path` | RGBA cut-out of the untouched source pixels, cropped to `bbox_px`. |
| `bbox_px` | Tight `(x, y, w, h)` of the mask in upright source-frame pixels. |
| `area_px`, `method`, `score` | Mask area; `sam3` or `grabcut`; SAM's confidence, `null` for GrabCut. |
| `box` | The #14 sighting box used as the prompt. If the sighting box later changes, the mask is stale and is redone. |

File names contain a digest of the mask, so a file never changes once written. A missing
mask or cut-out triggers regeneration. Successful replacement removes the superseded pair
after the registry update; failed replacements keep the previous files.

**Handoff to Dev 1.** `selection.object_evidence(result, object_id)` accepts the
`SegmentationResult` and now fills `EvidenceFrame.mask_url` and the mask's tight `bbox_px` for
masked views; other sightings keep their coarse box and a `null` mask. `primary_frame_index`
prefers a view whose mask is not low-confidence. `mask_url` is the `mask_path` above: resolve
it with `segmentation.read_mask(data_dir, mask_url)`, which returns a boolean array and
refuses paths outside `data_dir`. Serving masks over HTTP, if the editor ever needs it, is a
route decision for #9.

```bash
uv run --extra reconstruction python -m services.reconstruction.assets.segment_items \
  --scene-id reviewed-opening-room --data-dir artifacts/furniture --out /tmp/furniture-masks
```

The report has `segmentation.json`, `evidence.json` (the section 3 shape, keyed by item ID),
one mask overlay and one cut-out per view, and `report.md`. Exit codes: `0` every selected
view has a mask, `2` some are missing (report still written), `1` unknown scene/item, invalid
storage or missing key. `--object-id` limits the run; `--replace` segments stored masks again.
Stored SAM 3 masks require `--live` for replacement or repair: offline runs refuse to
overwrite them with approximate GrabCut masks, before doing any segmentation.

**Providers.** The default is local OpenCV GrabCut inside each sighting box: no network, no
key, deterministic, and approximate (it can keep floor under a table or an object in front).
Every GrabCut run carries a warning. `--live` uses fal.ai `fal-ai/sam-3/image` with `FAL_KEY`:
it uploads each needed frame and sends all of that frame's item boxes as box prompts in one
request, so the cost is one request per frame. `--max-requests` bounds new submissions per
run. Requests are saved in the registry: a rerun, or `--replace`, re-reads the saved result
without a new charge; an interrupted submission is never repeated blindly; `--refresh
<label>` deliberately pays again. Masks are streamed over HTTPS from `fal.media` hosts only,
with a 20 MB cap enforced while reading. For duplicate prompt indices, the first usable
mask (highest score first) is kept; unmatched items are reported as missing. A live failure
is reported per item and never falls back to GrabCut silently.

**What is checked.** A mask must be frame-sized, non-empty and agree with its item's box
(bounding-box IoU of at least 0.3), which also rejects a mask returned for the wrong item.
This is a coarse association check: a mask can pass while most of its pixels lie outside
the prompt box. Inspect overlays for floor or neighbouring-item leakage even at high scores.
Rejected or failed masks are listed under `missing` with a reason; they never remove an item
or a stored mask. Warnings, which do not change the exit code, name masks of different items
that overlap by more than 20 % in one frame and SAM masks scoring below 0.8. Quality and
GrabCut warnings use current masks only, excluding records with changed sighting boxes.

**Live result (2026-11-14).** The reviewed opening room (four items, six frames) took six
SAM 3 requests and gave 14 of 14 masks. Inspected overlays: the table, the rear sofa and the
wide views of the right sofa and chair are clean and separate (scores 0.92–0.98). Blurred
close-ups are worse: three masks scored 0.57–0.71 and are flagged, and one 0.94 mask of the
right sofa includes a hand at the frame edge without a flag. Masks are machine-generated
evidence, not verified outlines. Not covered: masks for non-selected sightings, tracking
between frames, depth or floor contact, and any metric size or room position.

## Implemented: individual raw meshes and proxy fallback (#16)

`reconstruction.reconstruct_furniture(scene_id, *, data_dir, provider=None, object_ids=None,
dimensions=None, replace=False, max_requests=8, concurrency=4)` reads the #14/#15 registry.
Each item returns a current `MeshRecord` or an explicit `MeshFailure`, plus a labelled,
dimensioned `FurnitureAsset` proxy. Failed replacements also return the previous current
mesh. `complete` means every requested item has a mesh and no attempt failed this run.

The live provider is `FalSam3dProvider(key=...)`, endpoint `fal-ai/sam-3/3d-objects`: it uploads
one upright frame and one instance mask per item. Requests run concurrently (four workers
by default) against a shared submission budget. View selection prefers confident masks,
then an unclipped view at least half the largest mask's area, then the largest mask. Clipped
and low-confidence views carry warnings. Without an explicit provider there is no network:
stored meshes are reused and other items return `not_attempted` or `no_view` with proxies.

```bash
uv run --extra reconstruction --env-file .env python \
  -m services.reconstruction.assets.reconstruct_items \
  --scene-id reviewed-opening-room --data-dir artifacts/furniture \
  --out /tmp/furniture-meshes --live --max-requests 4
```

Omit `--live` for offline proxies. The CLI writes `reconstruction.json` (raw mesh records,
failures, warnings), `assets.json` (an array of servable proxy `FurnitureAsset`s), and
`report.md`. Exit 0 means complete, 2 means partial/proxies, 1 means invalid input or storage.
Use repeated `--object-id` arguments to select items. `--dimensions file.json` accepts known
sizes keyed by item ID, for example:

```json
{"vid-000001": {"bbox_m": {"width": 1.2, "height": 0.7, "depth": 0.6}, "source": "measured"}}
```

Allowed sources are `measured`, `catalog`, `user_corrected`. Without known dimensions,
category defaults are explicitly `estimated` and request a `dimensions` correction. Every
proxy keeps the item's ID/name, has its bottom-centre at the origin, +Y up and a dark front
marker at +Z. Fixtures remain fixed; desk, table and chair proxies use category-template
collision parts. Other categories use one solid bounding box.

**Storage and retries.** Raw GLBs live under `meshes/<scene digest>/<item ID>/` and retain
provider units/orientation. They must pass binary glTF 2.0, declared-length, 20 MB, triangle
and finite non-zero extent checks. They are not served or represented as normalised assets:
metric scaling, canonical orientation and the final mesh profile are #17. A missing file or
changed mask triggers reconstruction. Successful replacements attach transactionally only
if their mask is still current; failed replacements keep existing records/files.

A rerun reuses stored meshes. `--replace` re-reads a saved fal request without submitting;
`--refresh label --replace` deliberately starts a paid regeneration. Submitted request IDs
survive timeouts (420 seconds by default); retry collects the remote result. Uncertain
submissions are never repeated automatically. Budget-deferred submissions remain retryable.
Terminal remote errors, disallowed URLs and invalid/oversized GLBs mark the saved request
failed: reruns stop before polling or downloading again and instruct the operator to use
`--refresh` with a new namespace for a paid retry. Transient network/download failures keep
the saved handle recoverable without another inference charge.
Failure kinds are `not_attempted`, `no_view`, `budget`, `timeout`, `provider`, `invalid_mesh`.
Downloads permit HTTPS `fal.media` hosts only, without redirects, and enforce the cap while
streaming. Credentials and raw provider error bodies are excluded from diagnostics.

`selection.object_evidence` / `evidence_for` now fill `provider_pose` on the mesh's frame:
raw `object_index`, `scale`, `rotation` (x/y/z/w quaternion), `translation`, `camera_pose`.
Scale and translation are nested arrays; their relationship to room metres is unverified.
The live single-object response uses `model_glb` and `metadata[0]`.

**Dev 1 handoff ([#52](https://github.com/KOLESNiii/AI_HACKATHON_PROJECT/issues/52)).**
Mount `asset_store.asset_router(data_dir)` in the reconstruction app to serve `/assets/<sha256>.glb` with immutable caching. Proxy browser URLs already use
`/api/reconstruction/assets/<sha256>.glb`, matching Vite's existing prefix stripping.
Raw meshes remain private runtime files. No main entry point, shared contract, dependency
manifest or room-placement interface changes in this issue.

**Live verification (2026-11-14).** Four new requests returned four separate usable raw GLBs.
Together with six mask requests and the earlier probe this used 11 of the 15 authorised
requests. An offline rerun reused all four stored meshes. No private input, masks, meshes or
provider URLs are committed.

| Item | Triangles | Bytes | Source frame |
|---|---:|---:|---:|
| Coffee table | 10,806 | 1,257,384 | 59 |
| Rear sofa | 9,804 | 1,095,880 | 30 |
| Right sofa | 10,098 | 1,157,744 | 105 |
| Office chair | 17,978 | 1,409,988 | 105 |

Geometry projections were compared with source crops: table/sofas are recognisable, but the
item labelled office chair reconstructs as an upholstered armchair. Frame 105 clips the
right sofa and chair, both warned. Hidden geometry is inferred; passing structural checks
is not a visual-accuracy claim. Textures, metric scaling and canonical orientation were not
visually verified. Raw meshes become servable only through #17's normalisation (below).

## Implemented: mesh normalisation (#17)

`normalisation.normalise_mesh(raw_glb, *, category, target_bbox, data_dir, front=None,
url_base=...)` is the one path from any raw glTF 2.0 binary to the section 5 profile. It
returns a `NormalisedMesh` whose `glb_url` is stored in the content-addressed asset store.
`data_dir` (where to store) and `front` are additions to the signature agreed in section 8.

| Step | Behaviour |
|---|---|
| Load | Node transforms are baked into the vertices and unused vertices are removed; the output has identity nodes, no skins, animations, cameras or lights. The raw file is taken to be +Y up, as glTF requires. |
| Front | `front` (`"+z"`, `"+x"`, `"-z"`, `"-x"`) names the raw mesh's front, which is turned to +Z. `None` keeps the mesh as given and adds `"orientation"` to `correction_needed`. |
| Size, known | With a `target_bbox` each axis is scaled to match it exactly. If that stretches one axis over 15 % more than another (`MAX_DISTORTION`), `"dimensions"` is requested: the shape disagrees with the stated size. |
| Size, unknown | Without one the mesh is scaled uniformly so its height is the category's typical height (`CATEGORY_SIZE_M`), `bbox_m` is read off the result (rounded to 1 mm) and `"dimensions"` is always requested. Any estimated side over 3 times its corresponding category size is refused; the item keeps its proxy until dimensions are supplied. |
| Origin | The bounding-box bottom-centre is moved to the origin. |
| Profile | Textures above 1024 px are downscaled; a file still over 3 MB is written again at 768 px, then 512 px, before it is refused (#19). The written file is re-read: its bounds must equal `bbox_m` within `GLB_BBOX_TOLERANCE_M`. |
| Parts | `collision_parts` come from the category template fitted to `bbox_m`; `collision_source` is `"template"`. |

**Measured against estimated.** `normalise_mesh` never calls a size it derived a measurement.
`reconstruct_furniture` sets `dimension_source` from the caller's `dimensions[id].source`
(`measured`, `catalog`, `user_corrected`) only when dimensions were given; otherwise the asset
is `estimated` with `"dimensions"` in `correction_needed`. The provider's own `scale` metadata
is not used: on the four live meshes it gave a 0.86 m two-seat sofa and a 0.55 m armchair.

**Refusals.** `NormalisationError` (a `ValueError`) when the file cannot be read, has no
triangles or no extent, a side would be under 1 cm, or it exceeds 30,000 triangles, 4
primitives or 3 MB, or an estimated side exceeds 3 times its category size. This size limit
does not apply to caller-supplied dimensions. There is no decimator among the dependencies,
so an over-budget mesh is refused, not reduced: providers are asked for a budget instead.
Nothing is stored on refusal.

**In the pipeline.** `ItemReconstruction.asset` is the item's normalised `FurnitureAsset`
(`is_proxy: false`, same ID and evidence as the proxy) when its current raw mesh normalises,
else `None` with a warning; `proxy` is always present. `complete` now also requires every
item to have an `asset`. The CLI's `assets.json` holds each item's `asset`, or its `proxy`
when there is none, and `report.md` lists the normalised size and outstanding corrections.
SAM 3D meshes are passed `front="+z"` (`PROVIDER_FRONT`). A provider missing from this map
keeps its mesh orientation and requests `"orientation"`. Proxies now carry the same category
template parts, so a desk or table proxy can nest a chair.

**Dependency.** Pillow joins the `reconstruction` extra: without it `trimesh` silently drops
textures on load.

**Verification (2026-11-15).** The four stored raw SAM 3D meshes of the reviewed opening room
were normalised offline (no provider request). Orthographic projections of the raw meshes
showed all four +Y up and axis-aligned, with both sofas and the armchair facing +Z; the table
is symmetric. Re-reading each stored output:

| Item | `bbox_m` W × H × D (m) | Source | Bounds error | Triangles | Bytes |
|---|---|---|---:|---:|---:|
| Coffee table | 1.1 × 0.45 × 0.65 | `user_corrected` (test value) | < 0.001 mm | 10,806 | 1,257,480 |
| Rear sofa | 1.82 × 0.85 × 0.818 | `estimated` | < 0.001 mm | 9,804 | 1,095,976 |
| Right sofa | 1.9 × 0.85 × 0.859 | `estimated` | < 0.001 mm | 10,098 | 1,157,840 |
| Office chair | 1.015 × 0.95 × 0.741 | `estimated` | < 0.001 mm | 17,978 | 1,410,088 |

All four kept their 1024 px base-colour texture and have their bottom-centre at the origin.
The table's supplied size was an invented test value that stretches the mesh 17 %, so it
correctly asked for `"dimensions"`. Not verified: how the textured results look in the
editor, the front direction of other SAM 3D outputs, and `trellis-2` output. Estimated sizes
are category guesses: the "office chair" mesh is an armchair and comes out 1.0 m wide.

## Implemented: delivery to Dev 1 and its checks (#18)

`delivery.deliver_furniture(scene_id, *, data_dir, dimensions=None, object_ids=None,
url_base=...)` is what Dev 1 places. Per item it returns the normalised mesh when the stored
file passes its checks, otherwise the labelled proxy, with the same ID either way. It is
offline (stored results only, no provider request) and returns a `Delivery`: `assets` (one
`FurnitureAsset` per item, in item-ID order), a matching `AssetCheck` per asset, `warnings`
and `ok`. Unknown scenes and items raise `ValueError`, as `reconstruct_furniture` does.

| Check (`inspect_asset`) | Fault reported |
|---|---|
| Store | `glb_url` is not under the asset URL base, is not a `<sha256>.glb` name, the file is missing, or its bytes do not hash to its name. |
| Scene graph | Not binary glTF 2.0; has skins, animations or cameras; a node transform is not baked. |
| Budget | Over 30,000 triangles or 3 MB. |
| Bounds | Stored bounds differ from `bbox_m` by `GLB_BBOX_TOLERANCE_M` or more on any axis. Passing also fixes the bottom-centre at the origin. |
| Item rules | The asset no longer validates as a `FurnitureItem` (collision parts, fixtures). |
| Provenance | An `estimated` size without `"dimensions"` in `correction_needed`. |

**Fallback.** An item with no mesh, a mesh that could not be normalised, or a mesh that fails
a check is delivered as its proxy; `AssetCheck.fallback_reason` and `warnings` say why. A mesh
is never delivered with a known fault. A proxy is delivered even if its own file is faulty
(the item is never dropped), and then `ok` is false. A proxy with stated dimensions keeps
them and their provenance.

`delivery.check_placed(scene, assets)` lists what an assembled `RoomScene` changed: every
asset must appear exactly once with every field equal except `pose`, and `correction_needed`
may only grow (alignment adds `placement` and `orientation`).

```bash
uv run --extra reconstruction python -m services.reconstruction.assets.check_delivery \
  --scene-id reviewed-opening-room --data-dir artifacts/furniture --out /tmp/furniture-delivery
```

Prints a one-line JSON summary and, with `--out`, writes `delivery.json`, `assets.json` (the
delivered assets) and `report.md`. Exit 0: every delivered asset passed and there are at
least `--min-items` (default 2); 2: a check failed or too few items; 1: unknown scene or
item, or unusable input or storage. `--dimensions` and `--object-id` work as in
`reconstruct_items`.

**Dev 1 handoff.** Run delivery as offline batch preparation with the CLI above and
`--out`, after reconstruction or changes to masks, selected items or dimensions. Check
`delivery.json`'s `ok` and warnings before publishing its prepared `assets.json`.
`RealRoomFurniture` (PR #55) should load that list with `FurnitureAsset.model_validate`,
then place those assets. Never call `deliver_furniture` during scene assembly: every call
re-normalises and inspects every mesh. The integrator must regenerate and atomically
publish the list when inputs change; retain the proxy path until that integration exists.
IDs and evidence are unchanged; the asset route serves both meshes and proxies.

**Verification (2026-11-15), stored data, no provider request.** The check CLI on the four
reviewed opening-room items: four meshes delivered, all checks pass, bounds error under
0.0001 mm each. The same assets were assembled into the demo reception room through
`assemble_scene` with the #8 reviewed hints: `check_placed` clean, each `glb_url` served 200
with immutable caching from `asset_router` and re-measured equal to `bbox_m`. Moving the
table onto the rear sofa left the other three items identical and the audit reported that
collision; moving it back cleared it. The editor's store (`frontend/src/store.ts`), loaded
with that scene, selected and moved the table and the chair separately with all IDs, bounds
and mesh URLs unchanged. Not verified: the meshes drawn in a browser. The editor has no
backend scene loader yet (#22, #25), so nothing was looked at on screen.

## Implemented: retailer import (#19)

`catalog.import_catalog_asset(product_url, scene_id, *, data_dir, category=None,
source="url_import", dimensions=None, mask_provider=None, mesh_provider=None, ...)` reads a
retailer product page and returns a `CatalogImport`: the `FurnitureAsset`, its `AssetCheck`,
and the provenance (`product`, `image`, `mesh_source`, `warnings`). It is synchronous and
takes `data_dir`, like the other implemented functions; the section 8 signature is updated.
`catalog.import_product(product, scene_id, ...)` does the same for a `RetailerProduct` that
is already in hand (a search result). `catalog.imported_assets(scene_id, data_dir=...)`
lists a scene's stored imports offline. Contracts, routes and dependencies do not change.

**One pipeline.** A product is registered in the #14 registry as an item with one view, its
product image, under the scene key `catalog:<scene_id>`. It then takes the existing steps:
`segment_furniture` (#15), `reconstruct_furniture` (#16), `normalise_mesh` (#17) and the
`deliver_furniture` checks (#18). There is no second generator, normaliser or checker.
The separate scene key keeps catalog items out of a video delivery; their IDs are
`cat-<12 hex of the product URL's SHA-256>`, so importing a URL again updates the same item
and reuses its stored mask and mesh.

**Geometry, first that works.**

| Source | When | `mesh_source` |
|---|---|---|
| The retailer's own 3D model | The page publishes a binary glTF: schema.org `3DModel` (IKEA) or a `<model-viewer src>` tag. Free. It enters as the raw mesh through `RetailerModelProvider`, a `MeshProvider` (`MeshRecord.provider: "retailer"`). | `retailer_model` |
| A mesh generated from the product image | No usable published model and the caller passed `mesh_provider` (SAM 3D, paid). | `generated` |
| A labelled proxy box | Neither. Also after any failed download, mask, mesh or check. | `proxy` |

A retailer usually publishes several qualities of one model. They are tried best first and
the first that meets the furniture profile is kept: over 30,000 triangles, or over 3 MB
after normalisation, moves on to the next. Draco-compressed files are tried last and cannot
be read (there is no Draco decoder among the dependencies).

**Provenance kept.**

| What | Where |
|---|---|
| Source URL and how it was found | `asset.product_url`; `asset.source` is `url_import` or `catalog_search`. |
| Price | `asset.price_gbp`, only when published in GBP. |
| Image | `CatalogImport.image`: URL, SHA-256 of the served bytes, stored PNG path, size. The image is the item's evidence frame, with its mask. |
| Model | `asset.evidence.frames[0].provider_pose.model_url`: the file the mesh was made from. |
| Dimensions | `product.dimensions`: the size in metres, `found_in` (`structured_data`, `page_text`) and `text`, the published words it was read from. |

**Dimensions.** A complete published size makes `dimension_source: "catalog"` and the mesh
is fitted to it. Read, in order: schema.org `width`/`height`/`depth` (with units, or
`QuantitativeValue`, or `additionalProperty`); then, only for sides that leaves out,
labelled page text (`Width: 120 cm`, `W120 x D60 x H75 cm`). A label must open its line, so
`Armrest width` and `Seat height` are not the item's size. Unlabelled triples
(`120 x 60 x 75 cm`), sides without a unit, and sides outside 1 cm to 5 m are not used.
**A missing or unusable size is never invented:** the asset is `estimated` from its
category with `"dimensions"` in `correction_needed`, and the CLI exits 2. Passing
`dimensions=KnownDimensions(..., source="user_corrected")` settles it.

Retailers name a desk's or table's long side "depth" or "length" whichever way it faces
(IKEA: width 60, depth 140 for a desk). The published width and depth are therefore
assigned to the delivered shape's own X and Z: the mesh's proportions, or for a proxy the
category's usual ones. An exchange is reported in `warnings`; `product.dimensions` keeps
what was published as written. A user's own size is never turned.

**Failures.** `CatalogError` (a `ValueError`) only when there is no product to import: the
URL is not a public http(s) address, the page cannot be fetched, or it names no product.
After that nothing raises and the item is never dropped; it is delivered as a proxy with the
reason in `warnings`. Downloads refuse non-public addresses on every redirect hop and are
size-capped (page 3 MB, image 15 MB, model 20 MB).

```bash
uv run --extra reconstruction python -m services.reconstruction.assets.import_product \
  --url https://www.ikea.com/gb/en/p/micke-desk-white-80213074/ \
  --scene-id demo-room --data-dir artifacts/furniture --out /tmp/furniture-import
uv run --extra reconstruction python -m services.reconstruction.assets.import_product \
  --search "office desk"                      # list IKEA results; add --pick N --scene-id … to import one
```

`--out` writes `import.json`, `assets.json` and `report.md`. `--category` overrides the
category read from the product's name; `--dimensions W H D` (metres) is a user correction;
`--product file.json` imports a stored `RetailerProduct`. `--live` adds fal.ai (`FAL_KEY`):
SAM 3 masks, and a SAM 3D mesh when no published model is usable. Exit 0: checks pass and no
correction is asked; 2: a check failed or a correction is asked; 1: nothing to import.

**Search.** `retailer.search_ikea(query, limit=5, market="gb/en")` returns `catalog_search`
results (URL, name, image, GBP price). It calls the search endpoint the IKEA website itself
uses: no key, but not a documented API, and it may change. A result has no dimensions or
model; importing its URL reads both from the product page. `LINKUP_API_KEY` and
`TAVILY_API_KEY` are not used: any search that yields a product URL can feed
`import_catalog_asset(url, ..., source="catalog_search")`.

**Dev 1 handoff.** Place `CatalogImport.asset` with `asset.to_item(pose)` like any other
asset; the asset route already serves its file. A catalog item has no position in the room:
its evidence is a product photo, so the pose comes from the user or the layout search, not
from alignment. A route (`POST` a URL, return the item) needs a request model in
`contracts/schema.py`, which needs team sign-off and is not added here.

**Live verification (2026-11-15), IKEA GB, no fal.ai request.** Eight product pages:

| Product | Delivered | W × H × D (m) | Size from | Triangles | Bytes |
|---|---|---|---|---:|---:|
| MICKE desk | IKEA model | 1.05 × 0.75 × 0.5 | `catalog`, structured data | 12,166 | 1,294,244 |
| BILLY bookcase | IKEA model | 0.8 × 2.02 × 0.28 | `catalog`, structured data | 19,274 | 1,621,388 |
| BRIMNES wardrobe | IKEA model | 1.17 × 1.9 × 0.5 | `catalog`, structured data | 7,560 | 2,009,472 |
| MALM bed frame | IKEA model, second quality (the first has 34,161 triangles) | 1.5 × 1 × 1.99 | `catalog`, structured data | 22,592 | 2,477,520 |
| SKOGSTA dining table | IKEA model, textures reduced to fit 3 MB | 2.35 × 0.74 × 1 (published as width 100, depth 235) | `catalog`, structured data | 13,222 | 2,448,352 |
| SALTSJÖBADEN 2-seat sofa | proxy: the only published model is Draco | 1.64 × 0.9 × 0.88 | `catalog`, height from page text | | |
| POÄNG armchair | proxy: no model published | 0.68 × 1 × 0.82 | `catalog`, structured data | | |
| LAGKAPTEN / ALEX desk | proxy: no model published | 1.4 × 0.73 × 0.6 (published as width 60, depth 140) | `catalog`, structured data | | |

All eight pass `inspect_asset` (bounds error under 0.0001 mm) and are delivered together by
`deliver_furniture("catalog:demo")`. IKEA's plain GLBs are in metres and within 1 % of the
published size (MICKE: 1.049 × 0.754 × 0.500 against 105 × 75 × 50 cm), so fitting them
barely changes their shape. Orientation was measured on the stored files, not looked at:
the MICKE drawers, the BILLY opening and the foot of the MALM bed are at +Z; the wardrobe
was inconclusive. A re-import reused the stored mesh, and `http://localhost:8001/health`
was refused. **Not verified:** the image → SAM 3 → SAM 3D path on a live product (tested
with provider doubles only; no paid request was made), any retailer other than IKEA, the
`<model-viewer>` path on a live page, and how the meshes look in the editor. Offline masks
are GrabCut and approximate; they matter only when a mesh is generated from the image.

## Implemented: validation and demo cache (#20)

**Demo cache.** `demo_cache.py` publishes a scene's delivered assets as a generation folder,
`g-<hex>` named by its manifest's hash: `manifest.json` (the `FurnitureAsset`s exactly as
delivered, and every file they reference with its SHA-256 and size) plus those files, at the
paths they have in the data directory. The scene folder's `CURRENT` file names the published
generation. A publish writes a complete generation, then switches `CURRENT` with one atomic
replace: readers see the old cache or the new one, never none. A reader resolves `CURRENT` once
and reads only that generation, which is never changed. The generation just replaced is kept
for readers still using it; older ones are removed. Run one publisher at a time. Installing
a cache copies the files into a data directory, so each `glb_url` is served by the existing
asset route and each evidence `mask_url` resolves with `segmentation.read_mask`. The delivery
checks (`inspect_asset`) then run again on the installed files. Nothing is regenerated and no
provider, key or network is used. Contracts, routes and dependencies do not change.

| Function | Does |
|---|---|
| `publish_video_scene(scene_id, *, data_dir, cache_dir, ...)` | `deliver_furniture` (#18), which must be `ok`, then publish. A delivered proxy stays a proxy. |
| `publish_catalog_scene(scene_id, *, data_dir, cache_dir)` | `imported_assets` (#19), each `ok`, published under `catalog:<scene_id>` with its retailer provenance. |
| `publish_demo_cache(scene_id, assets, ...)` | The common step. Refuses (`CacheError`, the earlier cache untouched) on too few items, a repeated ID, a failed check or a missing file. Written as a new generation, then switched to. The manifest is deterministic, so republishing the same assets reuses their generation. |
| `read_demo_cache(scene_id, *, cache_dir, url_base=...)` | `None` when nothing is published. Otherwise the verified manifest: `CacheError` for a bad `CURRENT`, a bad manifest, another scene's, an asset outside `url_base`, a path leaving the folder, or a missing or altered file. |
| `install_demo_cache(scene_id, *, cache_dir, data_dir, url_base=...)` | Read, copy what is missing or damaged from that one generation, check every asset again. |

`url_base` is the asset store's URL prefix (default `/api/reconstruction/assets`). Publish, read
and install a cache with the same one.

```bash
uv run --extra reconstruction python -m services.reconstruction.assets.demo_cache publish \
  --scene-id reviewed-opening-room --data-dir artifacts/furniture
uv run --extra reconstruction python -m services.reconstruction.assets.demo_cache verify \
  --scene-id reviewed-opening-room
# Catalog imports: --scene-id demo --catalog (publishes catalog:demo)
```

The default cache directory is `$FURNITURE_DEMO_CACHE_DIR`, else
`services/reconstruction/assets/fixtures/demo_cache` (`config.demo_cache_dir()`). Exit codes:
0 published or verified; 2 refused, missing or broken; 1 unusable input or storage.

**Committed cache.** `fixtures/demo_cache/` holds `reviewed-opening-room`: the four normalised
SAM 3D meshes of the opening room and their 15 SAM 3 masks, 4.97 MB, delivered from registry
revision 13. They are derived from the committed `examples/three_floor_3.mp4`. All four sizes
are `estimated` and ask for `"dimensions"`. Retailer models are not committed (third-party
files): publish a catalog scene into a local cache directory instead. See
`fixtures/demo_cache/README.md`.

**Use in the real-input room (Dev 1).** `RealRoomFurniture` takes `cache_dir`, and
`get_furniture_source` passes `demo_cache_dir()`. When the data directory has no registry data
for the bound video, the room installs that video's cache and warns that it did. Pipeline data,
when present, always wins, so running the pipeline still takes effect on the next request. A
broken cache gives the old empty room with `NOT_EXTRACTED` plus the reason, and is asked again.
`tests/conftest.py` points `FURNITURE_DEMO_CACHE_DIR` at an empty directory, so other tests are
unaffected. The plan's labels are still read with fal vision (`FAL_KEY`). Without them the room's
geometry does not match its binding and gets no furniture. Recorded labels for a key-free demo are
Dev 1's #12.

**Bounds agreement (Devs 1, 3, 4).** One size, three readers:

| Reader | What it uses | Checked by |
|---|---|---|
| Delivery (Dev 2) | Vertex bounds of the stored file equal `bbox_m`, bottom-centre at the origin | `inspect_asset` |
| Editor (Dev 3) | `Box3.setFromObject` in `Furniture.tsx`. GLTFLoader builds it from the `POSITION` accessors' declared min/max, not from the vertices | `inspect_asset` now compares the declared bounds with `bbox_m` too |
| Auditor (Dev 4) | `furniture_footprint(item)`: the width × depth box at the pose | `tests/test_demo_cache_room.py` |
| Placement (Dev 1) | `check_placed`: only the pose changes, corrections only grow | same |

`tests/test_demo_cache_room.py` blocks every socket and loads the real-input room from an
empty data directory with the committed cache. Four meshes are served by content hash and
`check_placed` is clean. For every item, the editor's scale is 1 and its offset 0. Mesh
vertices placed with the editor's transform (at yaw 0°, 90° and 37°) lie inside the auditor's
footprint and reach each of its sides. Two solid sofas 5 mm apart are clear to the auditor, and
5 mm overlapping they collide. Moving one item changes only that item, and the audit follows
it. The same checks pass for a catalog import published, installed and placed.

**Verification (2026-11-15), no fal.ai request.**

- The committed cache verifies offline: four meshes, bounds error under 0.001 mm, and a
  republish gives an identical manifest.
- A real uvicorn server ran with `FAL_KEY` unset, an empty `FURNITURE_DATA_DIR` and the
  recorded plan labels. `GET /scenes/plan-83a12322e933-floor-0-room-3` returned the four meshes
  with the cache warning, and each `glb_url` was served 200 with bytes matching its hash. The live
  spatial service accepted the scene.
- Live IKEA GB imports of MICKE and BILLY (retailer models, `catalog` sizes) were published,
  verified in a fresh directory and passed the editor/auditor agreement at four yaws.

**Not verified:** the meshes drawn in a browser. The editor has no backend scene loader yet
(#22, #25).

**Changed baseline for Devs 3 and 4.** The meshes' estimated sizes are larger than the proxies
of the #10 runbook, so the first audit of the real-input room differs from the one documented
in `docs/architecture.md`:

- `door0` is blocked by `vid-000003` (right sofa) and `vid-000004` (chair).
- The table is 0.12 m in front of the rear sofa; it needs 0.6 m.
- The right sofa is 0.37 m from the rear sofa.

There are no collisions. All are estimates flagged for correction.

## Provider configuration and dependencies

Every key is server-side, read from `.env` by `bun run dev:*` (`--env-file .env`) or
`uv run --env-file .env`. Never expose one through a `VITE_` variable.

| Variable | Used by | Default |
|---|---|---|
| `FAL_KEY` | `--live` on `select_frames`, `segment_items`, `reconstruct_items` and `import_product`; plan labels and the vision observer in `room/` | none: offline paths only |
| `FAL_VISION_ENDPOINT`, `FAL_VISION_MODEL` | Live frame selection and plan reading | `fal-ai/any-llm/vision`, `google/gemini-2.5-flash` |
| `FURNITURE_DATA_DIR` | The service's registry, masks, meshes and asset store | `artifacts/furniture` (Git-ignored) |
| `FURNITURE_DEMO_CACHE_DIR` | Published demo caches | `services/reconstruction/assets/fixtures/demo_cache` |

Leave unused variables out of `.env` instead of setting them empty: an empty
`FAL_VISION_ENDPOINT` replaces the default with an empty string.

| fal.ai endpoint | Step | Cost control |
|---|---|---|
| `fal-ai/any-llm/vision` | Frame selection proposals (#14) | `--max-requests`; cached by scene, frames, model and prompt |
| `fal-ai/sam-3/image` | Masks (#15), one request per frame | `--max-requests`; saved results are re-read free |
| `fal-ai/sam-3/3d-objects` | Raw meshes (#16), one request per item | `--max-requests`, `--concurrency`; uncertain submissions are never repeated |

IKEA search and product pages need no key. The search endpoint is undocumented and may change.
`LINKUP_API_KEY` and `TAVILY_API_KEY` are not used by Dev 2's code.

**Dependencies.** No change in #20. The `reconstruction` extra (`opencv-python-headless`,
`trimesh`, `fal-client`, `pillow`) covers every furniture CLI, the demo cache and the service.
The service already starts with it (`bun run dev:reconstruction`). The bounds-agreement test
also needs the `spatial` extra (`shapely`) and is skipped without it. Frame selection needs
FFmpeg and FFprobe 8 on `PATH`; the demo cache, delivery and catalog import do not.
`bun run setup` installs every extra.
