import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.reconstruction.assets.asset_store import asset_router
from services.reconstruction.catalog_routes import router as catalog_router
from services.reconstruction.config import furniture_data_dir, scene_cache_dir
from services.reconstruction.demo_assets import legacy_router
from services.reconstruction.demo_assets import router as demo_router
from services.reconstruction.room.routes import router as floor_plan_router
from services.reconstruction.room.routes import shell_router
from services.reconstruction.room.scene_cache import restore_published
from services.reconstruction.room.video_jobs import PENDING_HEADER, PROGRESS_HEADER
from services.reconstruction.scenes import WARNINGS_HEADER
from services.reconstruction.scenes import router as scene_router

app = FastAPI(title="SpaceShift reconstruction", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[WARNINGS_HEADER, PENDING_HEADER, PROGRESS_HEADER],
)
app.include_router(floor_plan_router)
app.include_router(shell_router)
app.include_router(scene_router)
app.include_router(catalog_router)
# Dev 2's content-addressed furniture files (proxies now, normalised meshes after #17).
app.include_router(asset_router(furniture_data_dir()))
app.include_router(demo_router)
app.include_router(legacy_router)
# Published demo plans (#12) are served from startup: no upload, provider or key. A cache
# that cannot be used is skipped and said so; its rooms are then unknown until uploaded.
for _problem in restore_published(scene_cache_dir()):
    logging.getLogger(__name__).warning("scene cache skipped: %s", _problem)


@app.get("/health")
def health() -> dict[str, str]:
    """Process liveness only; does not probe external providers."""
    return {"status": "ok", "service": "reconstruction"}
