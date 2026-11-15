"""Editor URL imports through the existing, public-address-only retailer pipeline."""

import os
import sqlite3
import threading

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from services.reconstruction.assets.catalog import CatalogImport, import_catalog_asset
from services.reconstruction.assets.mask_providers import FalSamProvider
from services.reconstruction.assets.mesh_providers import catalog_mesh_providers
from services.reconstruction.assets.retailer import CatalogError
from services.reconstruction.config import furniture_data_dir

router = APIRouter()
# Registry updates are read/modify/write; serialize imports within this process.
_IMPORT_LOCK = threading.Lock()


class ImportRequest(BaseModel):
    url: HttpUrl
    scene_id: str = Field(min_length=1, max_length=190, pattern=r"\S")


@router.post("/catalog/import", response_model=CatalogImport)
def import_url(request: ImportRequest) -> CatalogImport:
    try:
        key = os.environ.get("FAL_KEY", "").strip()
        masks = FalSamProvider(key=key) if key else None
        meshes = catalog_mesh_providers(key, timeout_s=300) if key else None
        with _IMPORT_LOCK:
            result = import_catalog_asset(
                str(request.url),
                request.scene_id,
                data_dir=furniture_data_dir(),
                mask_provider=masks,
                mesh_provider=meshes,
            )
        if not key:
            result.warnings.append(
                "Live fal.ai fallback unavailable: configure FAL_KEY on reconstruction."
            )
        if not result.ok:
            raise HTTPException(422, "The imported asset failed its geometry checks.")
        return result
    except CatalogError as exc:
        raise HTTPException(422, str(exc)) from exc
    except (ValueError, OSError, sqlite3.Error) as exc:
        raise HTTPException(502, "Product import failed. Check the link and try again.") from exc
