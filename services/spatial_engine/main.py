import os
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import ValidationError
from shapely.errors import ShapelyError  # type: ignore[import-untyped]

from contracts.schema import AuditReport, LayoutProposal, OptimiseRequest, RoomScene
from services.spatial_engine.agent import (
    DEFAULT_INTERPRET_MODEL,
    DEFAULT_MODEL,
    AnthropicLayoutModel,
    LayoutModel,
    propose_layout,
)
from services.spatial_engine.chat import ChatReply, ChatRequest, chat
from services.spatial_engine.feng_shui import (
    FengShuiRequest,
    FengShuiResult,
    assess_feng_shui,
)
from services.spatial_engine.geometry import SpatialInputError
from services.spatial_engine.proxy import proxy_glb
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


@contextmanager
def _input_errors() -> Iterator[None]:
    """Report bad scenes and geometry as 422 without echoing input; other errors stay 500s."""
    try:
        yield
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=[
                {"loc": ["body", *error["loc"]], "msg": error["msg"], "type": error["type"]}
                for error in exc.errors(include_input=False, include_context=False)
            ],
        ) from exc
    except SpatialInputError as exc:
        raise HTTPException(
            status_code=422, detail=[{"loc": ["body"], "msg": str(exc), "type": "value_error"}]
        ) from exc
    except (ShapelyError, ArithmeticError) as exc:
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


@app.post("/audit", response_model=AuditReport)
def audit(scene: RoomScene) -> AuditReport:
    """Return current spatial findings; scoring, glare and Feng Shui are not assessed."""
    with _input_errors():
        return audit_scene(scene)


@lru_cache(maxsize=8)
def _cached_model(api_key: str, model: str, effort: str = "medium") -> AnthropicLayoutModel:
    return AnthropicLayoutModel(api_key, model, effort=effort)


def get_layout_model() -> LayoutModel | None:
    """The configured assistant, or None when no API key is set. The key is never logged."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return None
    model = os.environ.get("SPACESHIFT_LAYOUT_MODEL", "").strip() or DEFAULT_MODEL
    return _cached_model(api_key, model)


def get_interpreter_model(request: OptimiseRequest) -> LayoutModel | None:
    """The faster model that reads the typed request; None falls back to the main model."""
    if not (request.instruction or "").strip():
        return None
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return None
    model = os.environ.get("SPACESHIFT_INTERPRET_MODEL", "").strip() or DEFAULT_INTERPRET_MODEL
    return _cached_model(api_key, model, effort="low")


@app.post("/solve", response_model=LayoutProposal)
def solve(
    request: OptimiseRequest,
    model: LayoutModel | None = Depends(get_layout_model),
    interpreter: LayoutModel | None = Depends(get_interpreter_model),
) -> LayoutProposal:
    """Suggest furniture poses for the request; never modifies the submitted scene.

    Always inspect `improved` and `outcome`: assistant failures and limits are reported
    in a 200 response, not as a clean or successful proposal.
    """
    with _input_errors():
        return propose_layout(request, model, interpreter=interpreter)


@app.exception_handler(Exception)
async def unexpected_failure(_request: Request, _exc: Exception) -> JSONResponse:
    """Programming errors remain 500s; return structured output without leaking internals."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": [
                {
                    "loc": ["body"],
                    "msg": "Spatial audit failed unexpectedly",
                    "type": "internal_error",
                }
            ]
        },
    )


@app.post("/feng-shui", response_model=FengShuiResult)
def feng_shui(
    request: FengShuiRequest,
    model: LayoutModel | None = Depends(get_layout_model),
) -> FengShuiResult:
    """Assess traditional layout preferences without changing the scene or audit score."""
    with _input_errors():
        return assess_feng_shui(request, model)


@app.post("/chat", response_model=ChatReply)
def room_chat(
    request: ChatRequest,
    model: LayoutModel | None = Depends(get_layout_model),
) -> ChatReply:
    """Return an audited proposal for explicit application by the editor."""
    with _input_errors():
        return chat(request, model)


@app.get("/proxies/{width}/{height}/{depth}.glb")
def furniture_proxy(
    width: Annotated[float, Path(gt=0.01, le=20)],
    height: Annotated[float, Path(gt=0.01, le=10)],
    depth: Annotated[float, Path(gt=0.01, le=20)],
) -> Response:
    return Response(
        proxy_glb(width, height, depth),
        media_type="model/gltf-binary",
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
