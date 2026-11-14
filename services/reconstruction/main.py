from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.reconstruction.demo_assets import legacy_router
from services.reconstruction.demo_assets import router as demo_router
from services.reconstruction.room.routes import router as floor_plan_router
from services.reconstruction.room.routes import shell_router

app = FastAPI(title="SpaceShift reconstruction", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(floor_plan_router)
app.include_router(shell_router)
app.include_router(demo_router)
app.include_router(legacy_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Process liveness only; does not probe external providers."""
    return {"status": "ok", "service": "reconstruction"}
