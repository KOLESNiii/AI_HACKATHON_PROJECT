# SpaceShift — AI Coding Agent Rules & Invariants

1. **Folder Ownership:** Only modify files inside your assigned directory (`services/reconstruction`, `services/spatial_engine`, `services/media_gen`, or `frontend`). Never modify `contracts/` without team sign-off.
2. **Coordinate System Invariant (Strict):**
   - Units are **meters** (`1.0` = 1m).
   - Right-handed 3D: `X` = width, `Y` = vertical height (`Y=0` is floor), `Z` = depth.
   - Every furniture `.glb` mesh MUST have its bounding-box bottom-center normalized to `(0, 0, 0)` and its logical "front" facing `+Z` (`yaw_deg = 0`). The room shell `.glb` is the exception: it is authored in room coordinates (see `contracts/schema.py`).
3. **Optional Compass Rule:**
   - `RoomScene.north_compass_deg` and `WindowOpening.compass_azimuth_deg` are optional (`None` / `null`).
   - Never crash when `north_compass_deg` is `null`. When evaluating glare, fall back to `plan_normal_deg` assuming `-Z` is North (`0°`) and set `AuditReport.glare_orientation_grounded = False`; use `True` for an assessment with grounded orientation. If glare is not assessed, both `glare_alerts` and `glare_orientation_grounded` are `None` / `null`.
4. **fal.ai API Usage:**
   - Use `FAL_KEY` from `.env`.
   - Always enforce exact metric scaling (`bbox_m`) in Three.js and `trimesh` after receiving any `.glb` from `fal-ai/trellis-2` or `fal-ai/sam-3d-objects`—never trust raw generative mesh scale.
5. **FastAPI Standards:**
   - Enable `CORSMiddleware` (`allow_origins=["*"]`) on all Python microservices (`8001`, `8002`, `8003`).
   - All endpoints must accept and return models strictly imported from `contracts/schema.py`.
