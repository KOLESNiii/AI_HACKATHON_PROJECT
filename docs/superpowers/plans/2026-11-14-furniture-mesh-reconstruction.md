# Furniture Mesh Reconstruction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Give every furniture ID its own raw provider mesh, or an explicit failure, and always
a labelled dimensioned proxy asset.

**Architecture:** A provider boundary returns one raw mesh per item from a frame and its #15
mask. A pipeline runs the providers concurrently, validates and stores meshes under the
runtime data directory and records them on the item in the #14 SQLite registry. A proxy
builder and a content-addressed asset store produce a servable `FurnitureAsset` per item.

**Tech Stack:** Python 3.11, Pydantic, trimesh, OpenCV/NumPy, fal-client, HTTPX, FastAPI,
stdlib SQLite and threads, pytest.

**Spec:** `docs/superpowers/specs/2026-11-14-furniture-mesh-reconstruction-design.md`

## Global Constraints

- Only `services/reconstruction/assets/`, `tests/reconstruction/assets/` and docs change.
- `contracts/`, `assets/models.py`, `services/reconstruction/main.py`, `pyproject.toml` and
  `uv.lock` do not change.
- No network unless a live provider is passed explicitly; tests run offline.
- At most 15 live requests in total for this issue (operator approval); 7 used by the mask
  rebuild and the probe.
- No private imagery, masks, meshes or provider URLs in Git.
- `ruff check`, `ruff format --check` and `mypy` (strict) stay clean.

## Review Focus

- A provider failure or timeout: the item is still returned, with its kind and a proxy.
- A mask replaced after its mesh was stored: the mesh is stale and is redone, not reused.
- A mesh URL outside `fal.media`, or over the size cap: refused before it is stored.
- A crash between submission and storing a live result: the retry re-reads the saved request.
- Guessed proxy sizes: always `estimated` with `"dimensions"` in `correction_needed`.
- An asset name that is not a SHA-256: the route answers 404 and reads nothing.

---

### Task 1: Mesh records

**Files:** modify `selection_models.py`; test `tests/reconstruction/assets/test_reconstruction.py`.

**Produces:** `MeshRecord`; `SelectedObject.mesh` and `current_mesh()`; `MeshFailure(kind,
reason)`; `ItemReconstruction(object_id, mesh, failure, proxy)`; `ReconstructionResult`.

- [x] Test: a mesh for a frame without a sighting is rejected; `current_mesh()` is `None` once
  the frame's mask differs; a snapshot without `mesh` loads; an item needs a `mesh` or `failure`; a failed replacement may retain both.
- [x] Implement, run, commit.

### Task 2: Proxy assets and the asset store

**Files:** create `asset_store.py` (`store_asset`, `asset_router`) and `proxies.py`
(`CATEGORY_SIZE_M`, `KnownDimensions`, `proxy_glb`, `proxy_asset`); test as above.

- [x] Tests: proxy bounds equal `bbox_m` within 1 mm with the bottom-centre at the origin;
  bytes are deterministic; a default-sized proxy is `estimated` with `"dimensions"`; known
  dimensions keep their provenance and need no correction; a `fixture` proxy is fixed.
- [x] Tests: `store_asset` is idempotent and returns a URL matching `GLB_URL_PATTERN`; the
  router serves the bytes with an immutable cache header and answers 404 for other names.
- [x] Implement, run, commit.

### Task 3: Pipeline with a test provider

**Files:** create `mesh_providers.py` (`MeshError`, `RawMesh`, `MeshProvider`) and
`reconstruction.py` (`reconstruct_furniture`); modify `selection.py` (`evidence_for`,
`provider_pose`) and `providers.py` (thread-safe `RequestBudget`); test as above.

- [x] Tests: two items get separate stored meshes and records; a rerun makes no provider call;
  `replace` and a replaced mask do; `provider_pose` appears on the mesh's evidence frame.
- [x] Tests: no provider, no mask, `MeshError` of each kind, an unexpected exception, a
  non-glTF, truncated or empty mesh each give a failure with its kind, a proxy, and no record;
  the other item still succeeds; a failed replacement keeps the stored mesh.
- [x] Tests: view choice (confident, unclipped, largest) and its warnings; unknown scene or
  item raises `ValueError`.
- [x] Implement, run, commit.

### Task 4: Live SAM 3D provider

**Files:** modify `mesh_providers.py` (`FalSam3dProvider(key, endpoint="fal-ai/sam-3/3d-objects",
timeout_s=420, refresh="", fetch=None)`) and `mask_providers.py` (shared bounded download and
host check); test with a mocked client and injected `fetch`.

- [x] Tests: the frame and the mask are uploaded and sent as `image_url` and `mask_urls`; the
  mesh and the pose come back; a second call re-reads the saved request without submitting.
- [x] Tests: an exhausted budget submits nothing and stays retryable (`budget`); a deadline is
  `timeout` and keeps the request; a result without `model_glb` is `invalid_mesh`; a
  non-`fal.media` or non-HTTPS URL is refused.
- [x] Implement, run, commit.

### Task 5: CLI, real-room check, docs

**Files:** create `reconstruct_items.py`; modify `assets/README.md`, `docs/architecture.md`,
`docs/decisions.md`.

- [x] Tests: the CLI writes `reconstruction.json`, `assets.json` (each validates as
  `FurnitureAsset`) and `report.md`; exit 0 all meshes, 2 proxies only, 1 unknown scene.
- [x] Live: reconstruct the reviewed opening room with `--live`, inspect the meshes, record
  the request count and limits in the PR.
- [x] Full suite, ruff, mypy, diff review, commit.

## Completed verification

- Full offline Python suite: 525 passed; ruff lint/format and strict mypy pass.
- Live opening room: four separate meshes, then a successful offline cache rerun.
  Total issue spend: 11/15 approved inference requests, including the earlier masks/probe.
- Inspected geometry projections against crops; the office-chair label produced an armchair
  shape. Two clipped views warned. Quality limitations are recorded in the asset README.
- Failed replacements retain the previous current mesh alongside the explicit failure.
  This is the deliberate refinement of Task 1's initial mutually exclusive outcome model.
