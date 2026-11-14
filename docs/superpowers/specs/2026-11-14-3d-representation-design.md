# SpaceShift 3D representation and asset handoff — design

Status: **approved**. Implemented for the contract and fixtures by
`docs/superpowers/plans/2026-11-14-asset-handoff-and-collision-parts.md`.
Naming note: PR #38 replaced the `needs_correction` flag with a `correction_needed` list
(`dimensions`, `placement`, `orientation`) and named the 1 mm tolerance
`GLB_BBOX_TOLERANCE_M`. Where this document says `needs_correction`, read it as an entry in
`correction_needed`.
Covers issues #5 (Dev 1.1) and #13 (Dev 2.1), and sets the amendments requested on PR #38.

## 1. Intent

SpaceShift turns a floor plan and a walkthrough video into an editable room, audits the
layout, and proposes better ones. Four developers build against one shared scene contract.
This document fixes how 3D geometry is represented so that:

- the editor, the audit, the layout solver and the photoreal step all describe the same room;
- generated meshes of unknown quality cannot corrupt spatial results;
- furniture that nests (a chair under a desk, a table over a radiator) is handled correctly;
- the result is light enough for the web today and for VR later.

## 2. Goals, non-goals, anti-goals

**Goals**

- One geometric truth that every consumer reads.
- Concave occupancy as a first-class concept: nesting is allowed when it physically fits and
  reported when it does not.
- Furniture is independently movable, identified by a permanent ID.
- Works with fal.ai output without trusting its scale, orientation or cleanliness.
- Editing and auditing keep working when mesh generation is slow or fails.
- Small, backward-compatible contract changes on top of PR #38.

**Non-goals (for now)**

- Multi-room plans and interior walls shared by two rooms.
- Items that are not on the floor (wall shelves, a monitor as a separate item).
- Curved or polygonal collision shapes, level-of-detail variants, Gaussian splats.
- A VR mode. The representation must not block it, but no VR code is planned here.

**Anti-goals**

- The audit must never read a `.glb`. If it does, mesh quality decides audit results.
- No second mesh normaliser or generator for catalog items.
- No exact-looking numbers that are really guesses. Estimated shapes stay labelled.

## 3. Constraints

- `CLAUDE.md` rules: metres, right-handed Y-up, floor at Y=0, furniture mesh bottom-centre at
  the origin with front facing +Z, metric scale always enforced, contracts need team sign-off.
- PR #38 (open) already pins yaw, plan bearings, wall and door rules, and adds `revision`,
  `is_proxy`, `dimension_source`, `needs_correction`, `LayoutProposal` and `RenderBundle`.
  This design builds on it and assumes it merges with the amendments in section 11.
- Folder ownership: Dev 1 owns `services/reconstruction/room/` and the reconstruction app
  and routes; Dev 2 owns `services/reconstruction/assets/`; Dev 3 owns `frontend/`; Dev 4
  owns `services/spatial_engine/`.
- Frontend stack is fixed: Three.js, React Three Fiber, Drei. `three-mesh-bvh` and
  `meshoptimizer` are already installed as Drei dependencies.
- Python reads meshes with `trimesh` 4.x, which supports Draco but not meshopt compression.

## 4. Approaches considered

### 4.1 What is the geometric truth?

| | Approach | Outcome |
|---|---|---|
| A | **Mesh-first.** The audit, solver and sun rays compute against triangles. | Rejected. Generated meshes have arbitrary scale and invented undersides; the solver needs thousands of cheap evaluations; a failed mesh would mean no audit; the backend cannot read web-compressed meshes. |
| B | **Parametric-first, mesh as skin.** The scene JSON is the truth; `.glb` files are derived visuals fitted to it. | **Chosen.** It is what the contract already nearly is. |
| C | **One glTF scene graph** with an asset table and instances. | Rejected for now. It breaks the contract three developers build on, and a vision model cannot emit it. Two ideas are kept: content-addressed asset URLs, and a single-file scene export later. |

### 4.2 How is a concave item's occupied volume described?

| | Approach | Outcome |
|---|---|---|
| 1 | **Box parts.** A short list of boxes per item, each a floor rectangle with a height range. | **Chosen.** Identical, trivial maths in the browser and in Python; drawable and user-correctable; works for proxies with no mesh. |
| 2 | **Occupancy grid** computed from the mesh. | Rejected as the representation: accuracy is limited to cell size, thin legs vanish, and users cannot correct it. Kept as the method for *deriving* box parts from a mesh (section 6.4). |
| 3 | **Mesh collision** (triangles or convex hulls). | Rejected. It is approach A again, and single-image reconstruction is least reliable on the underside, which is the part nesting depends on. |

The user delegated this choice; B with box parts is the builder's call, made for the factors
the user listed (rendering, rasterisation, ray casting, web weight, VR, generation, fal.ai).

## 5. The three layers

| Layer | What it is | Who reads it | Where it lives |
|---|---|---|---|
| **Truth** | `RoomScene` JSON: walls, openings, and per item `bbox_m`, `collision_parts`, `pose`. | Everyone. The audit and solver read only this. | `contracts/schema.py`, mirrored in `schema.ts` |
| **Visual** | Immutable `.glb` files: one shell, one per furniture asset. Derived from, and fitted to, the truth layer. | The editor only. | Served by the reconstruction service |
| **Evidence** | Source frames, masks and provider metadata that tie an asset to the video. | Dev 1's alignment code only. | Typed models inside `services/reconstruction/assets/` |

Rules that follow:

- `bbox_m` is authoritative. A mesh is scaled per axis to fit it, never the reverse.
- A proxy box and a reconstructed mesh with the same `bbox_m` and parts audit identically.
- Replacing a mesh changes `glb_url` only. It never invalidates an audit or a proposal.
- The shell `.glb` is derived from `floor_polygon`, `walls`, `windows` and `doors`.

## 6. Truth layer: item occupancy

### 6.1 The new type

```python
class CollisionPart(ContractModel):
    """One box of an item's occupied volume, in the item's local frame (the .glb frame):
    origin at the bounding-box bottom-centre, +Y up, front facing +Z."""
    x: float       # centre along X
    z: float       # centre along Z
    width: float   # extent along X
    depth: float   # extent along Z
    y_min: float   # bottom, metres above the floor
    y_max: float   # top
```

New `FurnitureItem` fields, all defaulted so existing JSON still validates:

| Field | Default | Meaning |
|---|---|---|
| `collision_parts: List[CollisionPart]` | `[]` | Occupied volume. **Empty means one solid box filling `bbox_m`.** |
| `collision_source: Literal["template", "mesh", "user_corrected"]` | `"template"` | Where the parts came from. Ignored when the list is empty. |
| `is_fixed: bool` | `False` | The item is part of the room (a radiator). The editor does not drag it and the solver does not move it. |

`category` gains `"table"` and `"fixture"`.

### 6.2 Invariants (validated in the contract)

- Every part lies inside `bbox_m` within 1 mm: `|x| + width/2 <= bbox.width/2`, the same for
  `z` and depth, and `0 <= y_min < y_max <= bbox.height`.
- At most 12 parts per item; no part dimension under 1 cm.
- Parts rotate with the item's yaw. Because items only rotate about Y, every part stays a
  vertical prism: a rotated rectangle in plan with a height range.

### 6.3 Shared semantics

These definitions go in the contract module docstring so the browser preview and the Python
audit cannot drift.

- **Collision.** Items A and B collide when some part of A and some part of B overlap in plan
  by more than 1 cm² *and* their height ranges overlap by more than 5 mm. Touching is not a
  collision, so an item flush against a wall or another item passes.
- **Broad phase.** `bbox_m` footprints are tested first; parts are only compared when the
  bounding boxes overlap.
- **`CollisionIssue.overlap_area_m2`.** The plan area of the union of overlapping part pairs.
- **Walkable floor.** A floor cell is blocked by any part whose `y_min` is below 2.0 m. A desk
  therefore blocks walking even though a chair fits beneath it.
- **Door swing.** The leaf sweeps from the floor to the door head, so it tests against every
  part in that height range.
- **Sun rays.** A ray is blocked by any part box it passes through. Light passes under a desk.
- **Fixed items** take part in every check but are never moved.
- **Front clearance.** Chairs do not block another item's `requires_front_clear_m` zone,
  because a chair at a desk is the intended use. This is a proposed rule for Dev 4.

Shared test vectors keep both implementations honest: `contracts/mock_room/collision_cases.json`
lists small scenes with the expected colliding pairs. `pytest` loads it for the audit and
`bun test` loads it for the browser preview. The frontend has no test script yet, so Dev 3
adds one.

### 6.4 Where parts come from

In order of preference; a later source replaces an earlier one and updates `collision_source`.

1. **Category template**, fitted to `bbox_m`. Always available, deterministic, and works for
   proxies. With width `w`, height `h`, depth `d`:

   | Category | Parts |
   |---|---|
   | `desk` | Top slab 4 cm thick over the full footprint; two side panels 4 cm wide at the X extremes, full depth, from the floor to the slab. |
   | `table` | Top slab 4 cm thick; four 6 cm square legs at the corners from the floor to the slab. |
   | `chair` | Seat block over the front 85% of the depth, floor to `0.5 h`; back over the rear 15%, floor to `h`. |
   | `bed`, `wardrobe`, `sofa`, `storage`, `fixture`, `other` | Empty list (solid). |

2. **Mesh-derived**, when a real mesh exists. Voxelise the normalised mesh at about 2.5 cm,
   merge occupied cells greedily into at most 12 boxes, and accept the result only if every
   box lies inside `bbox_m` and the boxes cover at least 98% of occupied cells. Boxes may
   over-cover, never under-cover, so a reconstruction that fills in an underside makes the
   item more solid. That errs towards reporting a collision rather than a false fit.
3. **User correction** in the editor.

Whether a table clears a radiator comes down to centimetres. Template parts are guesses, so
the editor labels any nested fit that relies on `collision_source == "template"` as estimated.

## 7. Visual layer

### 7.1 Furniture `.glb` profile

| Property | Requirement |
|---|---|
| Format | glTF 2.0 binary, one self-contained file, textures embedded. |
| Frame | Metres, +Y up, front +Z, bounding-box bottom-centre at the origin. |
| Bounds | Equal to `bbox_m` within 1 mm on every axis. |
| Scene graph | All transforms baked into vertices; root nodes are identity. No skins, animations, cameras or lights. |
| Geometry | At most 30,000 triangles (target 15,000); at most 4 primitives. |
| Material | Standard metallic-roughness. Base colour texture at most 1024 px; normal and occlusion-roughness-metal maps optional. |
| Size | At most 3 MB (target 1.5 MB). |
| Compression | None at first. Later, optional meshopt geometry and WebP textures; Drei decodes both with no configuration. No Draco, which needs a separately hosted decoder. |
| Proxy | A plain box of `bbox_m`, with `is_proxy: true` on the item. |

Twelve items at the target give roughly 180,000 triangles, which is a workable budget for a
standalone headset. fal.ai `trellis-2` defaults to 500,000 vertices and 2048 px textures, so
requests set `decimation_target` to about 10,000 and `texture_size` to `1024`.

The editor still fits each loaded mesh to `bbox_m` (`CLAUDE.md` rule 4). For a conforming file
this changes nothing. It also draws a `bbox_m` box while a mesh loads or if loading fails, so
loading, missing and proxy states share one code path.

### 7.2 Shell `.glb` profile

- Authored in room coordinates with identity transforms. The floor's top surface is at Y=0.
  It is exempt from the furniture origin rule.
- Named nodes: `floor`, `ceiling`, and one `wall_<wall_id>` per wall with its openings cut.
  Names use only letters, digits, `_` and `-`, because Three's loader strips `:`, `.` and `/`.
- Generated deterministically from the parametric fields by Dev 1, for any simple polygon,
  including L-shaped rooms.
- The ceiling is hidden in the orbit view. It exists so that sunlight enters only through
  windows and so that a first-person or VR view is enclosed.

### 7.3 Asset storage and URLs

- A file is stored under the hash of its bytes and never modified. `glb_url` is
  `/api/reconstruction/assets/<hash>.glb` and is served with a one-year immutable cache
  header. The base path comes from configuration. In development Vite strips
  `/api/reconstruction`, so the service itself serves `/assets/<hash>.glb`.
- `glb_url` is always something the browser can fetch as written: an absolute URL or a
  site-root path. It is never a filesystem path and never a raw provider URL. fal.ai output
  is downloaded, normalised and re-hosted.
- The item `id` is permanent. Upgrading a proxy to a real mesh, or to a better mesh, puts a
  new `glb_url` on the same `id`. This replaces the rule in the PR #37 draft.
- Two items with the same `glb_url` download once and share geometry on the GPU.
- Dev 2 supplies the store functions; Dev 1 mounts the route in the reconstruction app.

## 8. Generation

### 8.1 Room

Floor plan image → vision model → `floor_polygon`, `walls`, `windows`, `doors`, optional
compass → Dev 1's deterministic shell generator → shell `.glb`. The model emits JSON only.

### 8.2 Furniture

```text
video → keyframes → detect and deduplicate objects → mask per object per frame
      → fal.ai mesh (trellis-2 on the crop, or fal-ai/sam-3/3d-objects on frame + masks)
      → download raw .glb → normalise → store → FurnitureAsset
      (any provider failure → proxy box with the same ID)
```

`fal-ai/sam-3/3d-objects` returns per-object rotation, translation, scale and camera pose
metadata. That is placement evidence for Dev 1, so it is carried in the evidence layer.

### 8.3 Normalisation (one path for video and catalog)

1. Load the raw file, bake transforms, merge into the profile's scene graph.
2. Orient: Y up, then choose which of the four horizontal directions is the front. If that
   cannot be decided confidently, keep the best guess and set `needs_correction`.
3. Scale:
   - A target `bbox_m` is known (catalog, measured or user-corrected): scale each axis to
     match it exactly. If the axis ratios differ from uniform by more than 15%, set
     `needs_correction`, because the mesh shape disagrees with the stated dimensions.
   - No target is known: scale uniformly from the estimated height, then set `bbox_m` from
     the result and `dimension_source` to `"estimated"`.
4. Translate the bounding-box bottom-centre to the origin.
5. Check the profile (bounds, triangle count, size). Reduce if over budget.
6. Build `collision_parts` (section 6.4).
7. Store and return the `glb_url`.

### 8.4 Photoreal

The editor renders RGB, depth and object masks from one camera and revision
(`RenderBundle` in PR #38). The lossless linear depth is the interchange format; the
photoreal adapter converts it to whatever the chosen fal.ai model expects.

## 9. Handoff: Dev 2 → Dev 1 (#5 and #13)

### 9.1 Types

Internal Pydantic models in `services/reconstruction/assets/types.py`. They are typed and
validated but are not contract types, because they never cross an HTTP boundary.

```python
class FrameObservation(BaseModel):
    frame_index: int
    timestamp_s: float
    image_size_px: tuple[int, int] | None
    mask_url: str | None             # None on fixtures
    bbox_px: tuple[int, int, int, int] | None
    provider_pose: dict | None       # raw SAM 3D metadata[0]; shape verified in #16

class AssetEvidence(BaseModel):
    frames: list[FrameObservation]   # at least one
    primary_frame_index: int

class FurnitureAsset(BaseModel):
    """Every FurnitureItem field except `pose`, plus evidence."""
    ...
    evidence: AssetEvidence | None   # None for catalog imports
    def place(self, pose: Pose2D) -> FurnitureItem: ...
```

Dev 2 does not know where an object stands, so it returns a `FurnitureAsset` with no pose.
Dev 1 aligns it and calls `place`. Evidence never enters `RoomScene`, which the editor sends
to the audit on every move.

### 9.2 Functions

```python
async def extract_furniture(video_path: Path, scene_id: str) -> list[FurnitureAsset]
async def import_catalog_asset(product_url: str, scene_id: str) -> FurnitureAsset
def normalise_mesh(raw_glb: Path, *, category: str, target_bbox: BBoxM | None) -> NormalisedMesh
def proxy_asset(asset_id: str, category: str, bbox: BBoxM, ...) -> FurnitureAsset
```

`NormalisedMesh` carries `glb_url`, `bbox_m`, `collision_parts`, `collision_source` and
`needs_correction`.

Provider failures never raise across this boundary and never drop an item. They return a
proxy with `is_proxy: true`, `dimension_source: "estimated"` and `needs_correction: true`.

### 9.3 IDs

- Pattern `^[a-z0-9][a-z0-9_-]{0,63}$`, unique within a scene, and opaque: no code parses
  meaning out of an ID. Category and source are fields.
- Dev 2 may generate IDs as `{source}-{category}-{nn}`, as in the PR #37 draft.
- Stability comes from a persisted per-scene registry that maps each ID to its evidence, not
  from the naming scheme, since a re-run may detect objects in a different order.

### 9.4 Dimension provenance

`dimension_source` is `measured`, `catalog`, `estimated` or `user_corrected`. The first,
second and fourth are trusted. "Unknown" is expressed as `estimated` with `needs_correction`.

### 9.5 Fixtures

One fixture scene replaces the two current sets (`contracts/mock_room/` and
`services/reconstruction/assets/fixtures/`):

- It includes Dev 2's desk and chair, produced through `proxy_asset` and `place`, with
  `is_proxy: true`, template parts, agreed IDs and browser-fetchable URLs.
- The chair is tucked under the desk, which must audit as no collision.
- A fixed radiator sits under a table that straddles it, which must also pass.
- `collision_cases.json` adds the failing variants: the chair pushed until its back meets the
  desk top, and a table too narrow to straddle the radiator.

Still needed for #5 and not solvable in code: the team must choose the real floor plan and
matching video, and record the known scale reference.

## 10. How each consumer uses it

| Consumer | Uses | Notes |
|---|---|---|
| Editor rendering (Dev 3) | Shell and furniture `.glb`, `pose` | One group per item at `(x, 0, z)` with `rotation.y = yaw`. Meshes cached by URL and cloned per item. |
| Selection and drag (Dev 3) | `collision_parts` or `bbox_m` | Pick against invisible part boxes. This is fast enough for VR controller rays. |
| Client collision preview (Dev 3) | `collision_parts`, `pose` | Same rules as section 6.3, checked against the shared vectors. |
| Render maps (Dev 3) | Scene graph | One object per item ID gives the mask index; the shell is index 1. |
| Audit and solver (Dev 4) | Truth layer only | Rotated rectangles with height ranges; no mesh loading. |
| Sun and glare (Dev 4) | Windows, parts, walls | Analytic rays through window rectangles against part boxes. |
| Mesh-accurate rays (later) | Furniture `.glb` | `three-mesh-bvh` in the browser, for path-traced lighting or precise picking. |
| VR (later) | Everything above | Units, axes and floor height already match WebXR. A single-file scene export can be produced with Three's glTF exporter. |

## 11. Contract changes requested

All additive and defaulted. Items 1 and 4–7 are already raised as review comments on PR #38.

1. `dimension_source` gains `"catalog"`.
2. `CollisionPart`; `FurnitureItem.collision_parts`, `collision_source`, `is_fixed`.
3. `category` gains `"table"` and `"fixture"`.
4. Documented: shell frame and node names; `CLAUDE.md` rule 2 reworded to "furniture `.glb`".
5. Documented: `floor_polygon` is a simple polygon with one fixed winding.
6. Documented: `glb_url` resolution, immutability, `bbox_m` authority and the 1 mm tolerance.
7. Optional: `needs_correction` as a list of reasons; a door head height.
8. Documented: the collision semantics in section 6.3.

## 12. Order of work

| Phase | Content | Owner |
|---|---|---|
| 0 | Agree this document; amend PR #38; choose the real plan and video. | All |
| 1 (M1) | Contract fields; category templates; unified fixture scene and shared vectors; proxies; basic normaliser; asset store and route; shell with named nodes; editor loading; parts-based collision. | Devs 1–4 in their folders |
| 2 (M2) | Mesh-derived parts; compression pass; catalog import through the same normaliser; parts overlay and correction in the editor. | Devs 2 and 3 |
| 3 (later) | VR mode, single-file export, detail levels, polygon footprints, elevated items. | Unassigned |

## 13. Left to the builder

- Verify the axis convention and scale of `trellis-2` output before freezing the orient
  step. SAM 3D metadata shape, latency and file sizes were verified live in #16 (see
  `2026-11-14-furniture-mesh-reconstruction-design.md`); metric scale and axes still need
  interpretation.
- How the front direction is chosen in normalisation step 2.
- How a finished mesh reaches an open editor after the scene was first returned with a
  proxy (re-fetching the scene, polling, or a push). Dev 1 owns the routes. Because a mesh
  swap does not change `bbox_m` or the parts, it needs no re-audit.
- The exact box-merging algorithm for mesh-derived parts, within the acceptance rule given.
- Whether the compression pass runs through `gltf-transform` under Bun or another tool.
- Tuning the thresholds marked below.

**Calls made by the author, open to correction:** the 1 cm² and 5 mm collision thresholds,
2.0 m headroom, the 12-part limit, template dimensions, the triangle and size budgets, the
15% distortion threshold, treating a radiator as a fixed item rather than a wall fixture, and
the rule that chairs do not block front clearance.
