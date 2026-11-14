# Dev 2 fixture furniture

The fixture assets live in the shared fixture scene, `contracts/mock_room/mock_scene.json`,
so Devs 1, 3 and 4 integrate against one room:

| item | what it shows |
|---|---|
| `vid-desk-01`, `vid-chair-01` | a chair tucked under a desk without colliding |
| `vid-table-01`, `fix-radiator-01` | a table standing over a fixed radiator |

All four are labelled proxy boxes (`is_proxy: true`) with template collision parts, not
reconstructed meshes. Their `.glb` files are generated from the scene by
`scripts/generate_mock_glbs.py` into `services/reconstruction/fixtures/mock_room/`.
The reconstruction API serves them at `/mock_room/<name>.glb`; browser URLs use
the `/api/reconstruction` proxy prefix.

`evidence.json` here is their source evidence in the agreed shape (see `../README.md`).
There is no source video for a fixture, so `mask_url`, `bbox_px` and the other optional
fields are `null`. Dev 1's alignment must tolerate that.
