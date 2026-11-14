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
  the editor sends to the audit on every move. It becomes typed Python models with #15.

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
wires them into the reconstruction routes (#9).

```python
async def extract_furniture(video_path: Path, scene_id: str) -> list[FurnitureAsset]   # #14–#16
async def import_catalog_asset(product_url: str, scene_id: str) -> FurnitureAsset      # #19
def normalise_mesh(raw_glb: Path, *, category: str, target_bbox: BBoxM | None) -> NormalisedMesh  # #17
```

`FurnitureAsset` is the pose-less asset from section 2. `NormalisedMesh` carries `glb_url`,
`bbox_m`, `collision_parts`, `collision_source` and `correction_needed`. Video and catalog
assets go through the same `normalise_mesh`; there is no second normaliser.

A provider failure never raises across this boundary and never drops an item. It returns a
labelled proxy box: `is_proxy: true`, `dimension_source: "estimated"`, and `"dimensions"` in
`correction_needed`.

## 9. Fixtures

The fixture assets are in the shared fixture scene, `contracts/mock_room/mock_scene.json`:
a desk with a tucked chair and a table over a fixed radiator. See `fixtures/README.md`.

## Still open

- The team has not yet chosen the real floor plan and matching video, or recorded the known
  scale reference (#5).
- The collision check itself and shared collision test vectors are Dev 4's (#29–#30).
