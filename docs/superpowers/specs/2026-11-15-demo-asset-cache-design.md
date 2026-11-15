# Validated, cached demo assets (#20, Dev 2.8)

## Intent

M2 needs a reproducible demo. The real-input room (#10) gets its furniture from Dev 2's
pipeline data directory (`artifacts/furniture`), which Git ignores and which only exists on a
machine that ran the pipeline with `FAL_KEY`. A fresh clone shows an empty room. Nothing
checks that the assets Dev 2 delivers agree with what the editor (Dev 3) draws and what the
auditor (Dev 4) measures. Provider setup is spread over five README sections.

## Goals

- A published, hash-verified demo cache: the delivered assets of one scene (video or catalog)
  and every file they reference, loadable with no provider, key or network.
- The real-input room uses that cache when the pipeline has no data for its video, so a fresh
  clone shows the four real meshes.
- Checks that an asset's bounds agree across the three readers: the delivered `bbox_m`, the
  editor's fit (three.js reads the glTF's declared `POSITION` min/max), and the auditor's
  footprint (`spatial_engine.geometry.furniture_footprint`).
- One place that documents provider configuration, costs and dependency requirements.

## Non-goals

- No contract, route or dependency change. No provider request in tests or at runtime.
- No frontend change: the editor has no backend scene loader yet (#22, #25).
- Retailer models are not committed (third-party files); the cache supports catalog scenes,
  published locally.
- No cache of `/solve` answers (operator decision: requests are always live).

## Approaches

1. **Commit the pipeline data directory.** Rejected: SQLite registry, raw provider meshes and
   frames are runtime state, and every scene request would re-normalise from raw meshes.
2. **Commit the delivery CLI's `assets.json` and copy GLBs to `contracts/`.** Rejected: no
   integrity check and a second asset location the asset route does not serve.
3. **A published cache folder per scene, installed into the asset store** (chosen). A manifest
   lists the delivered assets and each referenced file with its SHA-256. Installing copies the
   files into the data directory under the same relative paths, so every `glb_url` and
   `mask_url` stays valid and the existing asset route serves them, then re-runs the delivery
   checks on the installed files.

## Design

`services/reconstruction/assets/demo_cache.py`:

- `DemoCache` manifest: `format`, `scene_id` (registry key), `source` (`video`, `catalog`),
  `registry_revision`, `assets`, `files` (`path`, `sha256`, `size_bytes`).
- `publish_demo_cache(scene_id, assets, ...)`: every asset passes `inspect_asset`, IDs are
  unique, every `glb_url` and evidence mask exists. Written to a temporary folder and swapped
  in, so a failed publish keeps the previous cache. The manifest is deterministic.
- `publish_video_scene` (via `deliver_furniture`, which must be `ok`) and
  `publish_catalog_scene` (via `imported_assets`, each `ok`).
- `read_demo_cache` returns `None` when absent; `CacheError` for a bad manifest, a path outside
  the folder, or a missing or altered file. `install_demo_cache` copies into the data directory
  and re-inspects every asset there.
- CLI: `publish` and `verify` subcommands; exit 0 / 2 / 1 as the other furniture CLIs.

`delivery.inspect_asset` also compares the declared `POSITION` bounds with `bbox_m`, because
three.js fits the mesh from those, not from the vertices.

`config.demo_cache_dir()` (`$FURNITURE_DEMO_CACHE_DIR`, else
`services/reconstruction/assets/fixtures/demo_cache`). `RealRoomFurniture` takes an optional
`cache_dir`: when the pipeline has no data for the bound video it installs that scene's cache,
with a warning that names it. Pipeline data, when present, still wins, so running the pipeline
keeps taking effect on the next request. A broken cache degrades to the old empty-room warning.

The committed cache holds `reviewed-opening-room`: four normalised SAM 3D meshes and their
SAM 3 masks, derived from the committed `examples/three_floor_3.mp4`, all sizes `estimated`.

## Tests

- Cache: round trip, deterministic manifest, refused publish keeps the old cache, republish
  removes stale files, tampered or missing file, escaping path, absent cache.
- Committed cache: four meshes with the binding's IDs pass every check after install.
- Real room from a fresh data directory with sockets blocked: the four meshes are served,
  `check_placed` is clean, the audit accepts the scene and follows a move. For every item, mesh
  vertices placed with the editor's transform lie inside the auditor's footprint and span it.
- A catalog import (retailer double) cached, installed and placed passes the same checks.
- `inspect_asset` reports declared bounds that disagree with the vertices.
