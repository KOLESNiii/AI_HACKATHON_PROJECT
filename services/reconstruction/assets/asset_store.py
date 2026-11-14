"""Content-addressed store for servable furniture `.glb` files (spec 7.3).

A file is stored under the SHA-256 of its bytes and never changes, so its URL can be cached
for ever. Dev 1 mounts `asset_router` in the reconstruction app.
"""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

ASSET_URL_BASE = "/api/reconstruction/assets"
"""Browser path of the store. Vite strips `/api/reconstruction` in development, so the service
itself serves `/assets/<sha256>.glb`."""
ASSET_DIR = "assets"
_NAME = re.compile(r"[a-f0-9]{64}\.glb")
IMMUTABLE = {"Cache-Control": "public, max-age=31536000, immutable"}


def write_atomic(path: Path, data: bytes) -> None:
    """Readers never see a partial file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, suffix=".part")
    with os.fdopen(handle, "wb") as file:
        file.write(data)
    os.replace(temporary, path)


def store_asset(data_dir: Path, glb: bytes, *, url_base: str = ASSET_URL_BASE) -> str:
    """Store a finished, profile-conforming `.glb` and return its `glb_url`."""
    name = f"{hashlib.sha256(glb).hexdigest()}.glb"
    path = data_dir / ASSET_DIR / name
    if not path.is_file():  # The name is the content, so an existing file is the same bytes.
        write_atomic(path, glb)
    return f"{url_base.rstrip('/')}/{name}"


def asset_router(data_dir: Path) -> APIRouter:
    """`GET /assets/<sha256>.glb` for the files `store_asset` wrote under `data_dir`."""
    router = APIRouter(prefix="/assets", tags=["furniture assets"])

    @router.get("/{name}", response_class=FileResponse)
    def furniture_asset(name: str) -> FileResponse:
        path = data_dir / ASSET_DIR / name
        if not _NAME.fullmatch(name) or not path.is_file():
            raise HTTPException(404, "unknown furniture asset")
        return FileResponse(path, media_type="model/gltf-binary", headers=IMMUTABLE)

    return router
