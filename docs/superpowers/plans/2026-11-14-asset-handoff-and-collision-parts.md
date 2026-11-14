# Asset Handoff Agreement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Record the Dev 1 ↔ Dev 2 agreement for #13 and #5: the contract additions, the written handoff, and one fixture scene. No pipeline code.

**Architecture:** The scene JSON is the only geometric truth; each `FurnitureItem` gains a list of box parts describing its occupied volume. The agreement lives in three places: `contracts/` (types and rules), `services/reconstruction/assets/README.md` (the handoff), and `contracts/mock_room/` (the fixture scene everyone builds against).

**Tech Stack:** Python 3.11, Pydantic v2, pytest; TypeScript mirror in `contracts/schema.ts`; trimesh only inside PR #38's existing mock generator.

**Spec:** `docs/superpowers/specs/2026-11-14-3d-representation-design.md`

## Execution notes (2026-11-14)

Executed as written, with these deviations:

- PR #38 had moved on by the time of the merge: it already added `"catalog"`, the 1 mm
  tolerance as `GLB_BBOX_TOLERANCE_M`, and a `correction_needed` list in place of the
  `needs_correction` flag. The code uses those names; where the tasks below say
  `BBOX_TOLERANCE_M` or `needs_correction: false`, read `GLB_BBOX_TOLERANCE_M` and
  `correction_needed: []`.
- `tests/test_dev2_fixture_assets.py` was deleted in Task 1, not Task 2, because the merged
  `glb_url` pattern made it fail.
- The TypeScript check needs `--ignoreConfig` on TypeScript 7.
- Review added one rule the tasks did not list: collision part values must be finite.
- A decision-log entry was added to `docs/decisions.md`.

## Global Constraints

- Units are metres; right-handed, Y-up; floor at Y=0; furniture `.glb` bottom-centre at the origin, front facing +Z.
- `bbox_m` is authoritative. Mesh bounds equal `bbox_m` within 1 mm.
- Every contract addition is defaulted, so existing `RoomScene` JSON still validates.
- An empty `collision_parts` list means one solid box filling `bbox_m`.
- Collision: plan overlap greater than 1 cm² (`0.0001` m²) and height overlap greater than 5 mm (`0.005` m). Touching is not a collision.
- At most 12 parts per item; no part dimension under 1 cm.
- Item IDs match `^[a-z0-9][a-z0-9_-]{0,63}$` and are opaque.
- `contracts/` changes need team sign-off: the PR stays draft until Devs 3 and 4 confirm.
- Files touched: `contracts/`, `services/reconstruction/assets/`, `tests/`, `docs/`, and generated files in `frontend/public/mock_room/`. Nothing else.
- No new Python modules under `services/`. This plan adds types, data and documentation only.

## Review Focus

1. **Float error at the bounding box edge.** A part that exceeds `bbox_m` by less than 1 mm must validate (Task 1).
2. **Old scene JSON.** A `FurnitureItem` written before this change, with none of the new fields, must still validate (Task 1).
3. **IDs with unsafe characters.** Uppercase, spaces, colons and empty strings must be rejected (Task 1).
4. **Fixture without a mask.** Fixture evidence has no mask or pixel box; the agreed evidence shape must allow that (Task 2).
5. **Mesh and `bbox_m` drifting apart.** Each generated fixture mesh must match its item's `bbox_m` (Task 2).

## Deferred, each under its own issue

| Work | Where it belongs |
|---|---|
| Category templates that generate parts; `FurnitureAsset` and evidence as Python types; asset store; proxy generation; normaliser; fal.ai calls | Dev 2, #14–#17 |
| Parts-based collision check and shared collision test vectors | Dev 4, #29–#30 (proposed on PR #38) |
| Editor loading and client collision preview | Dev 3, #22–#23 |
| Shell generator with named nodes; asset route | Dev 1, #7 and #9 |
| `CLAUDE.md` rule 2 rewording and the documentation items raised in review | PR #38 |

## File Structure

| File | Change |
|---|---|
| `contracts/schema.py`, `contracts/schema.ts` | Modify: `CollisionPart`, new `FurnitureItem` fields, literals, constants, rules in the docstring. |
| `contracts/mock_room/mock_scene.json` | Modify: becomes the one fixture scene. |
| `services/reconstruction/assets/README.md` | Rewrite: the agreed handoff. |
| `services/reconstruction/assets/fixtures/evidence.json`, `README.md` | Modify: agreed evidence shape; point at the fixture scene. |
| `services/reconstruction/assets/fixtures/*.glb`, `manifest.json`, `make_fixtures.py` | Delete: superseded by the fixture scene and PR #38's generator. |
| `tests/test_contract_occupancy.py`, `tests/test_fixture_scene.py` | Create. |
| `tests/test_dev2_fixture_assets.py` | Delete: superseded. |
| `tests/test_contracts.py` | Modify one assertion (comes from PR #38). |

---

### Task 1: Contract additions

**Files:**
- Modify: `contracts/schema.py`, `contracts/schema.ts`, `contracts/mock_room/mock_scene.json`
- Test: `tests/test_contract_occupancy.py`

**Interfaces:**
- Consumes: PR #38's `ContractModel`, `BBoxM`, `FurnitureItem`.
- Produces, all importable from `contracts.schema`:
  - Constants: `BBOX_TOLERANCE_M = 0.001`, `MAX_COLLISION_PARTS = 12`, `MIN_PART_DIMENSION_M = 0.01`, `MIN_PLAN_OVERLAP_M2 = 0.0001`, `MIN_HEIGHT_OVERLAP_M = 0.005`, `WALK_HEADROOM_M = 2.0`, `ITEM_ID_PATTERN = r"^[a-z0-9][a-z0-9_-]{0,63}$"`.
  - `class CollisionPart(ContractModel)` with float fields `x`, `z`, `width`, `depth`, `y_min`, `y_max`.
  - `FurnitureItem` gains `collision_parts: List[CollisionPart] = []`, `collision_source: Literal["template", "mesh", "user_corrected"] = "template"`, `is_fixed: bool = False`.
  - `FurnitureItem.id` is constrained by `ITEM_ID_PATTERN`. `category` gains `"table"` and `"fixture"`. `dimension_source` gains `"catalog"`.
  - A `FurnitureItem` model validator enforces: every part inside `bbox_m` within `BBOX_TOLERANCE_M`; `0 <= y_min < y_max <= bbox.height`; at most `MAX_COLLISION_PARTS`; no part dimension under `MIN_PART_DIMENSION_M`.

- [ ] **Step 1: Base the branch on PR #38**

```bash
git fetch origin
git merge origin/feat/dev3-contract-conventions
uv run pytest -q
```

Expected: the merge succeeds and every test passes. If PR #38 has already added `"catalog"`, skip that part of Step 4.

- [ ] **Step 2: Write the failing tests**

```python
LEGACY_DESK = {  # the pre-change shape: none of the new fields
    "id": "item_desk", "name": "Work Desk", "category": "desk", "source": "extracted_video",
    "glb_url": "/mock_room/desk.glb", "bbox_m": {"width": 1.4, "height": 0.75, "depth": 0.7},
    "pose": {"x": 2.1, "z": 2.6, "yaw_deg": 0},
}

def item(**over): return FurnitureItem.model_validate({**LEGACY_DESK, **over})
def part(**over): return {"x": 0, "z": 0, "width": 0.1, "depth": 0.1, "y_min": 0, "y_max": 0.1, **over}

def test_legacy_item_still_validates():
    it = item()
    assert (it.collision_parts, it.collision_source, it.is_fixed) == ([], "template", False)

def test_constants():
    assert (BBOX_TOLERANCE_M, MAX_COLLISION_PARTS, MIN_PART_DIMENSION_M) == (0.001, 12, 0.01)
    assert (MIN_PLAN_OVERLAP_M2, MIN_HEIGHT_OVERLAP_M, WALK_HEADROOM_M) == (0.0001, 0.005, 2.0)

def test_part_must_lie_inside_bbox():
    item(collision_parts=[part(x=0.68, width=0.04)])              # reaches 0.70: allowed
    item(collision_parts=[part(x=0.6805, width=0.04)])            # 0.5 mm over: within tolerance
    with pytest.raises(ValidationError):
        item(collision_parts=[part(x=0.70, width=0.04)])          # 2 cm over
    with pytest.raises(ValidationError):
        item(collision_parts=[part(z=0.35, depth=0.1)])

@pytest.mark.parametrize("bad", [dict(y_max=0.76), dict(y_min=-0.01), dict(y_min=0.1, y_max=0.1)])
def test_part_height_range(bad):
    with pytest.raises(ValidationError):
        item(collision_parts=[part(**bad)])

def test_part_limits():
    item(collision_parts=[part()] * 12)
    with pytest.raises(ValidationError):
        item(collision_parts=[part()] * 13)
    with pytest.raises(ValidationError):
        item(collision_parts=[part(width=0.005)])

@pytest.mark.parametrize("bad_id", ["Desk 01", "-desk", "", "a" * 65, "desk:1"])
def test_item_id_pattern(bad_id):
    with pytest.raises(ValidationError):
        item(id=bad_id)

def test_new_literals():
    assert item(id="vid-table-01", category="table").category == "table"
    assert item(category="fixture", is_fixed=True).is_fixed
    assert item(dimension_source="catalog").dimension_source == "catalog"
    assert item(collision_source="mesh").collision_source == "mesh"
```

- [ ] **Step 3: Run to confirm failure** — `uv run pytest tests/test_contract_occupancy.py -q`; Expected: import errors or failures.

- [ ] **Step 4: Implement in `contracts/schema.py`** as listed under Interfaces, and append this section to the module docstring, verbatim:

```text
Occupied volume and collision (the editor preview and the audit MUST agree on these):

- `FurnitureItem.collision_parts` lists boxes in the item's local frame. An empty list means
  one solid box filling `bbox_m`. Every part lies inside `bbox_m` (tolerance BBOX_TOLERANCE_M).
- Parts rotate with the item's yaw, so each stays a vertical prism: a rotated rectangle in
  plan with a height range [y_min, y_max].
- Two items collide when some part of one and some part of the other overlap in plan by more
  than MIN_PLAN_OVERLAP_M2 and in height by more than MIN_HEIGHT_OVERLAP_M. Touching is not a
  collision. Test `bbox_m` footprints first as a broad phase.
- `CollisionIssue.overlap_area_m2` is the plan area of the union of overlapping part pairs.
- Walkable floor is blocked by any part whose y_min is below WALK_HEADROOM_M.
- A door leaf and a sun ray test against the parts in their height range.
- `is_fixed` items take part in every check but are never moved by the editor or the solver.
```

- [ ] **Step 5: Mirror in `contracts/schema.ts`** — `export const` for the seven constants, `export interface CollisionPart`, the three new `FurnitureItem` fields (non-optional, with default comments in PR #38's style), the new literals, and the same rules as a block comment.

- [ ] **Step 6: List the new fields in the mock.** PR #38's `test_mock_scene_lists_every_field` requires every defaulted field to be present. Add `"collision_parts": [], "collision_source": "template", "is_fixed": false` to each of the three existing items in `mock_scene.json`.

- [ ] **Step 7: Verify**

Run: `uv run pytest -q` — Expected: all pass.
Run: `cd frontend && bun x tsc --noEmit --strict ../contracts/schema.ts` — Expected: no output.
Run: `uv run ruff check tests && uv run mypy` — Expected: clean.

- [ ] **Step 8: Commit** — `git add contracts tests/test_contract_occupancy.py && git commit -m "contracts: add box collision parts, fixed items and catalog provenance"`. Keep it as one self-contained commit so it can be moved onto PR #38 if the team prefers.

---

### Task 2: One fixture scene

**Files:**
- Modify: `contracts/mock_room/mock_scene.json`, `tests/test_contracts.py`, `services/reconstruction/assets/fixtures/evidence.json`, `services/reconstruction/assets/fixtures/README.md`
- Delete: `services/reconstruction/assets/fixtures/vid-desk-01.glb`, `vid-chair-01.glb`, `manifest.json`, `make_fixtures.py`; `tests/test_dev2_fixture_assets.py`; `frontend/public/mock_room/desk.glb`
- Regenerate: `frontend/public/mock_room/*.glb`
- Test: `tests/test_fixture_scene.py`

**Interfaces:**
- Consumes: Task 1's contract.
- Produces: `mock_scene.json` with furniture `item_bed`, `item_wardrobe` (unchanged) and four fixture items; `evidence.json` keyed by item ID.

Fixture items. All have `source: "extracted_video"`, `is_proxy: true`, `dimension_source: "estimated"`, `needs_correction: false`, `collision_source: "template"`, and `glb_url: "/mock_room/<id>.glb"`. `item_desk` is removed; `vid-desk-01` takes its pose.

| `id` | `name` | category | w / h / d | pose x, z, yaw | `has_screen` | `requires_front_clear_m` | `wall_flush_preferred` | `is_fixed` |
|---|---|---|---|---|---|---|---|---|
| `vid-desk-01` | Work Desk + Monitor (proxy) | desk | 1.4 / 0.75 / 0.7 | 2.1, 2.6, 0 | true | 0.75 | false | false |
| `vid-chair-01` | Desk Chair (proxy) | chair | 0.52 / 0.95 / 0.55 | 2.1, 2.8, 180 | false | 0.6 | false | false |
| `vid-table-01` | Side Table (proxy) | table | 1.2 / 0.75 / 0.6 | 0.3, 2.3, 90 | false | 0.6 | true | false |
| `fix-radiator-01` | Radiator (proxy) | fixture | 1.0 / 0.6 / 0.1 | 0.05, 2.3, 90 | false | 0.0 | true | true |

`collision_parts`, as `[x, z, width, depth, y_min, y_max]`:

| Item | Parts |
|---|---|
| `vid-desk-01` | top `[0, 0, 1.4, 0.7, 0.71, 0.75]`; panels `[-0.68, 0, 0.04, 0.7, 0, 0.71]` and `[0.68, 0, 0.04, 0.7, 0, 0.71]` |
| `vid-chair-01` | seat `[0, 0.04125, 0.52, 0.4675, 0, 0.475]`; back `[0, -0.23375, 0.52, 0.0825, 0, 0.95]` |
| `vid-table-01` | top `[0, 0, 1.2, 0.6, 0.71, 0.75]`; legs `[±0.57, ±0.27, 0.06, 0.06, 0, 0.71]` (four) |
| `fix-radiator-01` | none (solid) |

With these numbers the chair tucks under the desk and the table straddles the radiator without any part overlapping. That was checked while writing this plan; the scene is meant as Dev 4's "clear layout" case.

`evidence.json`: one entry for each of the four fixture IDs, of the form `{"frames": [{"frame_index": 0, "timestamp_s": 0.0, "image_size_px": null, "mask_url": null, "bbox_px": null, "provider_pose": null}], "primary_frame_index": 0}`. Remove `dimension_provenance` and `is_proxy`, which are now contract fields, and the `_comment` key.

- [ ] **Step 1: Write the failing tests**

```python
ROOT = Path(__file__).resolve().parent.parent
SCENE = RoomScene.model_validate(json.loads((ROOT / "contracts/mock_room/mock_scene.json").read_text()))
BY_ID = {i.id: i for i in SCENE.furniture}
EVIDENCE = json.loads((ROOT / "services/reconstruction/assets/fixtures/evidence.json").read_text())
FIXTURE_IDS = {"vid-desk-01", "vid-chair-01", "vid-table-01", "fix-radiator-01"}

def test_scene_holds_the_fixture_items_and_the_two_originals():
    assert set(BY_ID) == FIXTURE_IDS | {"item_bed", "item_wardrobe"}

def test_fixture_items_carry_the_agreed_fields():
    for fid in FIXTURE_IDS:
        it = BY_ID[fid]
        assert it.is_proxy and it.dimension_source == "estimated" and it.collision_source == "template"
        assert it.glb_url == f"/mock_room/{fid}.glb"
    assert [len(BY_ID[f].collision_parts) for f in sorted(FIXTURE_IDS)] == [0, 2, 3, 5]
    assert [BY_ID[f].is_fixed for f in sorted(FIXTURE_IDS)] == [True, False, False, False]
    desk, chair = BY_ID["vid-desk-01"], BY_ID["vid-chair-01"]
    assert max(p.y_max for p in chair.collision_parts if p.z > 0) < min(
        p.y_min for p in desk.collision_parts if p.width > 1)   # seat clears the desktop

def test_evidence_matches_the_agreed_shape():
    assert set(EVIDENCE) == FIXTURE_IDS
    keys = {"frame_index", "timestamp_s", "image_size_px", "mask_url", "bbox_px", "provider_pose"}
    for record in EVIDENCE.values():
        assert set(record) == {"frames", "primary_frame_index"} and record["frames"]
        assert all(set(f) == keys for f in record["frames"])
        assert record["primary_frame_index"] in {f["frame_index"] for f in record["frames"]}
        assert record["frames"][0]["mask_url"] is None      # fixtures have no source video

def test_generated_meshes_match_bbox():
    trimesh = pytest.importorskip("trimesh")
    for it in SCENE.furniture:
        path = ROOT / "frontend/public" / it.glb_url.lstrip("/")
        if not path.exists():
            pytest.skip("run scripts/generate_mock_glbs.py first")
        lo, hi = trimesh.load(path, force="mesh").bounds
        b = it.bbox_m
        assert hi - lo == pytest.approx([b.width, b.height, b.depth], abs=BBOX_TOLERANCE_M)
        assert lo[1] == pytest.approx(0.0, abs=BBOX_TOLERANCE_M)
```

- [ ] **Step 2: Run to confirm failure** — `uv run pytest tests/test_fixture_scene.py -q`; Expected: the first test fails on the ID set.
- [ ] **Step 3: Edit `mock_scene.json` and `evidence.json`** from the tables above.
- [ ] **Step 4: Update PR #38's test.** In `tests/test_contracts.py::test_mock_scene_validates_with_defaults`, replace the per-item `is_proxy is False` assertion with `assert {i.id for i in scene.furniture if i.is_proxy} == {"vid-desk-01", "vid-chair-01", "vid-table-01", "fix-radiator-01"}`. Keep the other assertions.
- [ ] **Step 5: Remove superseded files and regenerate meshes**

```bash
git rm services/reconstruction/assets/fixtures/vid-desk-01.glb services/reconstruction/assets/fixtures/vid-chair-01.glb \
       services/reconstruction/assets/fixtures/manifest.json services/reconstruction/assets/fixtures/make_fixtures.py \
       tests/test_dev2_fixture_assets.py frontend/public/mock_room/desk.glb
uv run --extra reconstruction python scripts/generate_mock_glbs.py
```

Expected: `frontend/public/mock_room/` holds `shell.glb`, `bed.glb`, `wardrobe.glb` and the four fixture files.

- [ ] **Step 6: Rewrite `fixtures/README.md`** in a few lines: the fixture assets now live in `contracts/mock_room/mock_scene.json`; their meshes are generated by `scripts/generate_mock_glbs.py`; `evidence.json` here is their evidence in the agreed shape, with no masks because there is no source video.
- [ ] **Step 7: Verify** — `uv run pytest -q` all pass, with no skips in `test_fixture_scene.py`.
- [ ] **Step 8: Commit** — `git add -A contracts services/reconstruction/assets tests frontend/public/mock_room && git commit -m "feat(dev2): one fixture scene with nested desk, chair, table and radiator"`

---

### Task 3: Written handoff and PR

**Files:**
- Rewrite: `services/reconstruction/assets/README.md`

- [ ] **Step 1: Rewrite `README.md`** as the agreed handoff, replacing the draft and its "pending sign-off" wording. Sections and the decision each records, linking to the spec for detail:
  1. **IDs** — the pattern; opaque; stability comes from a persisted registry, not the naming scheme (spec 9.3).
  2. **What Dev 2 returns** — an asset with every `FurnitureItem` field except `pose`, plus evidence; Dev 1 adds the pose (spec 9.1).
  3. **Evidence** — the agreed shape, as in `fixtures/evidence.json`; held inside the reconstruction service and never placed in `RoomScene`; masks may be null on fixtures.
  4. **Mesh references** — permanent `id`; immutable `glb_url` the browser can fetch as written; upgrading a proxy changes the URL, not the ID (spec 7.3).
  5. **Normalisation guarantee** — the furniture `.glb` profile table (spec 7.1).
  6. **Occupied volume** — collision parts, where they come from, and `collision_source` (spec 6).
  7. **Dimension provenance** — the four values; "unknown" is `estimated` plus `needs_correction`.
  8. **Functions and failure contract** — the three signatures from spec 9.2, marked as agreed but not yet implemented, with the issue that will implement each; provider failures return a proxy and never raise.
  9. **Fixtures** — where they are and what they contain.
- [ ] **Step 2: Full check** — `bun run check`; Expected: every stage passes.
- [ ] **Step 3: Commit, including the spec and this plan** — `git add services/reconstruction/assets/README.md docs/superpowers && git commit -m "docs(dev2): agreed asset handoff"`
- [ ] **Step 4: Update draft PR #37.** Push the branch. Edit the description to state: it is stacked on PR #38; it adds contract fields that need sign-off from Devs 3 and 4; it closes #13; for #5 it delivers the handoff and the fixture scene, and the real floor plan, video and scale reference are still to be chosen by the team. Paste the output of `uv run pytest -q` and `bun run check` under Verification. Leave the PR as draft.
