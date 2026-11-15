from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.reconstruction.assets.asset_store import asset_router
from services.reconstruction.catalog_routes import router as catalog_router
from services.reconstruction.config import furniture_data_dir
from services.reconstruction.demo_assets import legacy_router
from services.reconstruction.demo_assets import router as demo_router
from services.reconstruction.room.routes import router as floor_plan_router
from services.reconstruction.room.routes import shell_router
from services.reconstruction.scenes import WARNINGS_HEADER
from services.reconstruction.scenes import router as scene_router

app = FastAPI(title="SpaceShift reconstruction", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[WARNINGS_HEADER],
)
app.include_router(floor_plan_router)
app.include_router(shell_router)
app.include_router(scene_router)
app.include_router(catalog_router)
# Dev 2's content-addressed furniture files (proxies now, normalised meshes after #17).
app.include_router(asset_router(furniture_data_dir()))
app.include_router(demo_router)
app.include_router(legacy_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Process liveness only; does not probe external providers."""
    return {"status": "ok", "service": "reconstruction"}
