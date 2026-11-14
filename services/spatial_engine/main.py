from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from shapely.errors import GEOSException  # type: ignore[import-untyped]

from contracts.schema import AuditReport, RoomScene
from services.spatial_engine.report import audit_scene

app = FastAPI(title="SpaceShift spatial_engine", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Process liveness only; does not probe external providers."""
    return {"status": "ok", "service": "spatial_engine"}


@app.exception_handler(RequestValidationError)
async def invalid_request(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """Keep standard actionable error keys without echoing input or non-JSON values."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
                for error in exc.errors()
            ]
        },
    )


@app.post("/audit", response_model=AuditReport)
def audit(scene: RoomScene) -> AuditReport:
    """Return current spatial findings; scoring, glare and Feng Shui are not assessed."""
    try:
        return audit_scene(scene)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=[
                {"loc": ["body", *error["loc"]], "msg": error["msg"], "type": error["type"]}
                for error in exc.errors(include_input=False, include_context=False)
            ],
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail=[{"loc": ["body"], "msg": str(exc), "type": "value_error"}]
        ) from exc
    except GEOSException as exc:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["body"],
                    "msg": "Room geometry could not be processed",
                    "type": "value_error",
                }
            ],
        ) from exc
