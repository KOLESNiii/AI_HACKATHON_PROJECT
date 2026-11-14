# Legacy demo room meshes

These GLBs belong to `contracts/mock_room/mock_scene.json`. They moved here from
the frontend's public directory and are served by the reconstruction backend at
`/mock_room/<name>.glb` (`/api/reconstruction/mock_room/<name>.glb` in the browser).

Regenerate them from the repository root with:

```bash
uv run --extra reconstruction python scripts/generate_mock_glbs.py
```

The three-floor home's furniture is served directly from the existing
`contracts/mock_room/assets/` fixtures. Its room shells are generated in memory
on request; neither needs a second set of files in the frontend.
