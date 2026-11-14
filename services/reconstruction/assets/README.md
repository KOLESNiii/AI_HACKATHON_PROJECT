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
- `provider_pose` carries the raw per-object rotation, translation, scale and camera pose
  that fal.ai `sam-3d-objects` returns. Its exact shape is unverified until one live call.
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
  works for proxies), later refined from the mesh. `collision_source` records which.
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

Agreed signatures. None is implemented yet; the issue that implements each is noted. Dev 1
wires them into the reconstruction routes (#9). The types they use are in `models.py`.

```python
async def extract_furniture(video_path: Path, scene_id: str) -> list[FurnitureAsset]   # #14–#16
async def import_catalog_asset(product_url: str, scene_id: str) -> FurnitureAsset      # #19
def normalise_mesh(raw_glb: Path, *, category: str, target_bbox: BBoxM | None) -> NormalisedMesh  # #17
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
`extract_furniture(Path, scene_id)` façade remains for #15–#16. Neither the shared contracts
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
Multi-source items require explicit `source_id`; `provider_pose` and masks remain null for
#15/#16 to populate. `geometry_frame_keys` is an ordered subset of original wide frames for
later camera estimation, not a grounded camera solution. Dev 1's #8 owns metric plan fitting
and final poses; no route or multi-video extraction façade is wired here.
