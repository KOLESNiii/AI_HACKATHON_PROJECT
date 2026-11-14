# Furniture Segmentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every furniture ID a stored instance mask and cut-out for each selected view,
linked to its source frame and exposed through the existing evidence handoff.

**Architecture:** A provider boundary returns one mask per item box per frame. A pipeline
validates and stores masks under the runtime data directory and records them on the item in
the #14 SQLite registry. `object_evidence` and a CLI expose them.

**Tech Stack:** Python 3.11, Pydantic, OpenCV/NumPy, fal-client, HTTPX, stdlib SQLite, pytest.

**Spec:** `docs/superpowers/specs/2026-11-14-furniture-segmentation-design.md`

## Execution record

All five tasks were implemented test-first in the session that wrote this plan. Added during
execution, after inspecting the live masks: `MaskRecord.score`, the low-confidence warning and
the primary-frame preference (Task 5). Live use: 2 probe requests and 6 acceptance requests.

## Global Constraints

- Only `services/reconstruction/assets/`, `tests/reconstruction/assets/` and docs change.
- `contracts/`, `assets/models.py`, `pyproject.toml`, `uv.lock` and routes do not change.
- No network unless a live provider is passed explicitly; tests run offline.
- At most 20 live SAM 3 requests in total for this issue (operator approval).
- No private imagery, masks or provider URLs in Git.
- `ruff check`, `ruff format --check` and `mypy` (strict) stay clean.

## Review Focus

- A frame whose image file is missing: its masks are reported missing; other frames continue.
- A provider that returns a mask for the wrong item: rejected by the box check, not stored.
- A sighting box that changed after its mask was stored: the mask is redone, not reused.
- `mask_url` containing `..`: `read_mask` refuses to read outside the data directory.
- A crash between submission and storing a live result: the retry re-reads the saved request.

---

### Task 1: Mask records

**Files:** modify `services/reconstruction/assets/selection_models.py`; test
`tests/reconstruction/assets/test_segmentation.py`.

**Produces:** `MaskRecord(frame_key, box: Box, method: Literal["sam3","grabcut"], mask_path,
crop_path, bbox_px: tuple[int,int,int,int], area_px)`; `SelectedObject.masks: list[MaskRecord]`
and `SelectedObject.mask_for(frame_key) -> MaskRecord | None` (current masks only);
`MissingMask(object_id, frame_key, reason)`; `SegmentationResult(scene_id, registry_revision,
frames, objects, missing, warnings, complete)`.

- [x] Test: a mask for a frame without a sighting, or two masks for one frame, is rejected;
  `mask_for` returns `None` once the sighting box differs; a snapshot without `masks` loads.
- [x] Implement, run, commit.

### Task 2: Pipeline with the offline provider

**Files:** create `mask_providers.py` (`MaskError`, `MaskProvider`, `GrabCutProvider`) and
`segmentation.py` (`segment_furniture`, `read_mask`); test as above.

**Produces:** `segment_furniture(scene_id, *, data_dir, provider=None, object_ids=None,
replace=False, max_requests=16) -> SegmentationResult`; `read_mask(data_dir, mask_url) ->
NDArray[np.bool_]`.

- [x] Tests: two coloured items in one synthetic frame get separate masks matching their true
  rectangles (IoU ≥ 0.9), cut-outs whose alpha equals the mask, and persisted records.
- [x] Tests: rerun makes no provider call; `replace`, a changed box and a deleted file do.
- [x] Tests: `None`, empty, wrong-size, wrong-place masks, `MaskError` and a missing frame
  image are reported in `missing`, store nothing and keep the items; overlapping masks warn.
- [x] Tests: unknown scene, unknown object ID and `read_mask("../…")` raise `ValueError`.
- [x] Implement, run, commit.

### Task 3: Evidence handoff

**Files:** modify `selection.py` (`object_evidence`); test as above.

- [x] Test: with a current mask, `mask_url == record.mask_path` and `bbox_px == record.bbox_px`
  and `read_mask` returns it; without one, the #14 behaviour is unchanged.
- [x] Implement, run, commit.

### Task 4: Live SAM 3 provider

**Files:** modify `mask_providers.py` (`FalSamProvider(key, endpoint="fal-ai/sam-3/image",
timeout_s=120, refresh="", fetch=None)`); test with a mocked client and injected `fetch`.

- [x] Tests: box prompts are integer pixels with `object_id` i+1; masks returned in score
  order are mapped back through `metadata.index`; a missing index gives `None`.
- [x] Tests: a second call re-reads the saved request without submitting; an exhausted budget
  submits nothing and stays retryable; a non-`fal.media` or non-HTTPS URL is refused.
- [x] Implement, run, commit.

### Task 5: CLI, real-room check, docs

**Files:** create `segment_items.py`; modify `assets/README.md`, `docs/architecture.md`,
`docs/decisions.md`, `README.md`.

- [x] Tests: CLI writes `segmentation.json`, `evidence.json` (validates as `AssetEvidence`),
  overlays and cut-outs; exit 0 complete, 2 incomplete, 1 unknown scene.
- [x] Test: the reviewed opening room (recorded #14 inventory) gets a mask for every selected
  view of all four items offline, and a rerun is stable.
- [x] Live: segment the reviewed opening room with `--live`, inspect overlays, record request
  count and limits in the PR.
- [x] Full suite, ruff, mypy, diff review, commit.
