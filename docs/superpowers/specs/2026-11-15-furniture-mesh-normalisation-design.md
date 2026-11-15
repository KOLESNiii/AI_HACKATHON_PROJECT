# Furniture mesh normalisation — issue #17

Status: implemented; verification is recorded in the asset README and the PR. Builds on the
#16 raw meshes (`2026-11-14-furniture-mesh-reconstruction-design.md`) and implements spec 8.3
of `2026-11-14-3d-representation-design.md`. Branch:
`feat/dev2-normalise-furniture-meshes-to-metric-bounds-17`.

## Intent

#16 stores one raw provider mesh per item: unit-scaled, centred on the origin, not servable.
#17 is the single path that turns any raw mesh into a furniture asset the editor and the
audit can trust: metres, bottom-centre at the origin, front +Z, bounds equal to `bbox_m`.

Goals: one `normalise_mesh` for video and (later) catalog meshes; bounds within 1 mm of the
recorded `bbox_m`; a size nobody stated is `estimated` and asks for `"dimensions"`; an
unknown front asks for `"orientation"`; the video pipeline returns the normalised asset.
Non-goals: mesh-derived collision parts, decimation and compression; the `extract_furniture`
façade and M1 delivery (#18); catalog import (#19); poses and routes (Dev 1).
Anti-goals: a guessed size that reads as measured; a raw mesh served unnormalised; a mesh
whose bounds disagree with its `bbox_m`; an item dropped because its mesh failed the profile.

## What the stored meshes showed (2026-11-15, no provider requests)

The four raw SAM 3D meshes of the reviewed opening room each have one node, one primitive,
9,804–17,978 triangles and one 1024 px PNG texture. Orthographic projections show all four
+Y up and axis-aligned, with the sofas' and the armchair's fronts at +Z. The provider's
`scale` metadata is not a usable size: it makes the two-seat sofa 0.86 m and the armchair
0.55 m wide. `trimesh` without Pillow drops textures on load.

## Approaches

| Approach | Trade-off |
| --- | --- |
| **`trimesh` load → transform → export, with Pillow (chosen)** | Short, handles any scene graph and bakes transforms. Re-encodes textures and adds Pillow to the `reconstruction` extra (approved by the operator). |
| Edit the GLB buffers directly | No new dependency and textures stay byte-identical, but hand-written accessor handling that must refuse sparse, quantised or shared accessors. |
| Scale in the editor only | No backend work, but the file would break the section 5 guarantee and the audit could not rely on it. |

## Design

- **Front.** The caller states the raw mesh's front (`"+z"`, `"+x"`, `"-z"`, `"-x"`); `None`
  keeps the mesh and requests `"orientation"`. The pipeline passes `"+z"` for SAM 3D, from
  the observation above. Detecting the front from geometry is not attempted.
- **Scale.** Known `target_bbox`: per-axis, exact, with `"dimensions"` requested above 15 %
  distortion. Unknown: uniform from the category's typical height (spec 8.3), `bbox_m`
  rounded to 1 mm, `"dimensions"` always requested. PR #54 review follow-up: refuse an
  estimate if any side exceeds 3 times its corresponding category size, keeping the proxy
  until dimensions are supplied. This avoids inflating flat/partial meshes by their height.
- **Provenance** stays with the caller: `dimension_source` is the stated source or
  `estimated`. `NormalisedMesh` is unchanged.
- **Budgets.** Over 30,000 triangles, 4 primitives or 3 MB is refused with
  `NormalisationError`; textures are capped at 1024 px. No decimator is added.
- **Collision parts.** The spec 6.4 category templates, shared with proxies.
- **Pipeline.** `ItemReconstruction.asset` holds the normalised asset or `None` plus a
  warning; the proxy always remains.

## Calls made by the author, open to correction

- `normalise_mesh` gained `data_dir`, `front` and `url_base` over the agreed signature.
- SAM 3D's front is taken as +Z without an `"orientation"` request, on three asymmetric
  examples.
- A normalisation failure makes `ReconstructionResult.complete` false.
- Proxies now carry template collision parts.
