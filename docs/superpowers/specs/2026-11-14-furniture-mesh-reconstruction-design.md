# Individual furniture meshes with proxy fallback — issue #16

Status: implemented, with verification recorded in the asset README and PR. Builds on the #14 selector and the #15
masks (`2026-11-14-furniture-segmentation-design.md`). Branch:
`feat/dev2-reconstruct-individual-meshes-with-proxy-fallback-16`.

## Intent

#15 says which pixels of which frame are each furniture ID. #16 turns each ID into its own
mesh through one provider, and guarantees that an item whose mesh fails still comes back: as
a labelled box with stated dimensions and an explicit reason.

Goals: one raw mesh per item, stored durably and linked to its ID, frame and mask; every
failure and timeout reported per item with its kind; a servable labelled proxy for every item;
provider pose kept as placement evidence for Dev 1; reruns free.
Non-goals: metric scale, bottom-centre origin, front +Z and the triangle/size profile (#17);
collision templates (#17/#18); the `extract_furniture` façade and M1 delivery (#18); poses
(#8); mounting routes (Dev 1); catalog imports (#19).
Anti-goals: an item dropped because its mesh failed; a failure that looks like a success; a
proxy whose guessed size reads as measured; a rerun that pays again for a stored mesh; a raw
provider mesh served as if it met the furniture profile.

## Live probe (2026-11-14, approved by the operator: at most 15 requests for this issue)

One `fal-ai/sam-3/3d-objects` request: source frame 59 of the reviewed opening room (480 × 848
upright PNG) and the coffee table's #15 SAM 3 mask as `mask_urls`, `export_textured_glb=true`,
`seed=0`. Six further `fal-ai/sam-3/image` requests rebuilt the #15 masks, whose local data
directory no longer existed.

| Check | Observed |
| --- | --- |
| Latency | 170 s for one object. Slow enough that items must not run one after another |
| `model_glb` | glTF 2.0 binary, 1.3 MB, `model/gltf-binary`, on `*.fal.media`; one node, one mesh |
| Geometry | 6,857 vertices, 10,828 triangles; UVs, one PNG base-colour texture, metallic-roughness |
| Frame and scale | Centred on the origin, longest side ≈ 1 unit (0.996 × 0.476 × 0.602): not metres |
| `metadata[0]` | `object_index`, `scale` `[[s, s, s]]` (0.69), `rotation` `[[x, y, z, w]]`, `translation` `[[x, y, z]]`, `camera_pose: null` |
| `individual_glbs` | Absent for a single object. `gaussian_splat` (16 MB) and `artifacts_zip` (15 MB) are also returned and are not needed |

So the mesh is a unit-scaled shape; the provider's own size estimate is only in the metadata.
`scale × extents` would make the table about 0.69 × 0.33 × 0.42 m, which is plausible, but the
axis convention and accuracy are unverified: interpreting it is #17's job. #16 records it.

## Approaches

| Approach | Trade-off |
| --- | --- |
| **SAM 3D Objects, frame + the item's mask, one request per item (chosen by the operator)** | Uses the #15 mask directly; returns the pose the handoff already reserves as `provider_pose`; failures stay isolated per item. Needs `FAL_KEY`, ~3 min per item |
| SAM 3D Objects, all of a frame's masks in one request | Fewer requests, but each item's best view is often a different frame, the `individual_glbs` mapping is unverified, and one failure loses several items |
| TRELLIS 2 on the cut-out | Likely cleaner hidden sides, no pose evidence; not selected. The provider boundary allows adding it later |
| Proxy boxes only | No spend, but no meshes: kept as the offline default and the fallback, not the result |

## Design

- **Provider boundary.** `MeshProvider.reconstruct(frame, image, mask, registry, budget=)`
  returns `RawMesh(glb, pose)` or raises `MeshError(message, kind=)`. `FalSam3dProvider`
  (`name "sam3d"`) is explicit opt-in. There is no offline mesh generator: with no provider
  every item is reported as `not_attempted`. Failure kinds: `not_attempted`, `no_view`,
  `budget`, `timeout`, `provider`, `invalid_mesh`.
- **View.** One attempt per item per run, on one of its current #15 masks: masks at or above
  the low-confidence score are preferred; among those the largest, unless a view not clipped
  by the frame edge has at least half that area. A clipped or low-confidence view is a warning.
- **Checks on a returned mesh.** glTF 2.0 binary whose declared length matches, at most 20 MB,
  parseable, at least one triangle, finite non-zero extents. Anything else is `invalid_mesh`.
- **Storage.** Raw mesh at `meshes/<sha256(scene_id)[:16]>/<item id>/<sha256[:16]>.raw.glb`
  under the runtime data directory, written atomically, never served. `SelectedObject.mesh`
  (a `MeshRecord`) in the registry: `frame_key`, the `mask_path` sent, `provider`, `mesh_path`,
  `size_bytes`, `triangles`, raw `extents`, raw `pose`. A mesh is current while its mask is
  still the item's current mask for that frame and the file exists. Old snapshots load.
- **Pipeline.** `reconstruct_furniture(scene_id, *, data_dir, provider=None, object_ids=None,
  dimensions=None, replace=False, max_requests=8, concurrency=4, url_base=…) ->
  ReconstructionResult`. Provider calls run concurrently, outside the registry transaction;
  storing and attaching run one at a time and re-check the item and its mask. Each item of the
  result has `mesh` or `failure` and always a `proxy`; a failed replacement retains both
  its current stored mesh and the failed attempt. `complete` means every requested item
  has a current raw mesh and no attempt failed in this run.
- **Live requests.** Cached and recoverable through the registry's request table as in #15:
  only the reservation winner submits, the request ID is saved, a retry or `replace` re-reads
  the saved request for free, an uncertain submission is never repeated, `refresh`
  deliberately pays again. A local deadline (default 420 s) is a `timeout`: the remote request
  keeps running and the next run collects it. The mesh is streamed over HTTPS from `fal.media`
  hosts only, size-bounded. The request budget becomes thread-safe.
- **Proxy.** `proxy_asset(...) -> FurnitureAsset`: a box of `bbox_m` with a dark strip on the
  top-front edge inside the bounds, bottom-centre at the origin, front +Z, `is_proxy: true`,
  `source: "extracted_video"`, no collision parts (one solid box). Dimensions are the caller's
  `dimensions[id]` (`bbox_m` plus `measured`, `catalog` or `user_corrected`) when given;
  otherwise a category default with `dimension_source: "estimated"` and `"dimensions"` in
  `correction_needed`. The provider's scale is not used as a dimension here.
- **Asset store.** `store_asset(data_dir, glb) -> glb_url` writes `assets/<sha256>.glb` once and
  returns `/api/reconstruction/assets/<sha256>.glb` (spec 7.3). `asset_router(data_dir)` serves
  `/assets/<sha256>.glb` with a one-year immutable cache header. Dev 1 mounts it; this issue
  does not touch `main.py`.
- **Handoff.** `object_evidence` fills `EvidenceFrame.provider_pose` with the raw metadata on
  the frame the mesh was made from. `contracts/` and `assets/models.py` do not change.
- **CLI.** `python -m services.reconstruction.assets.reconstruct_items --scene-id … --data-dir …
  --out …` writes `reconstruction.json`, `assets.json` and `report.md`. Offline by default;
  `--live` uploads. Exit 0 every item has a mesh, 2 some only have a proxy, 1 invalid.

## Left to the builder

Internal helper names, report layout, category default sizes (rounded from the shared
fixtures) and test fixtures. No dependency, manifest or contract changes.

## Needs coordination

Dev 1 (#8/#9): mounting `asset_router`; the verified `provider_pose` shape; whether proxies for
every item are wanted in the scene before #17 delivers normalised meshes.
