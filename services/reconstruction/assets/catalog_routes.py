"""HTTP import of one retailer product (#19): a searched or pasted product page -> an item.

The product goes through `catalog.import_catalog_asset`, the same pipeline as video furniture:
IKEA's own published 3D model when there is one, else a mesh generated from the product image
when `FAL_KEY` is set (TRELLIS.2, then SAM 3D), else a labelled proxy box. The returned item is
unplaced (pose at the origin): the editor asks the spatial engine's `/place` for a spot.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from contracts.schema import FurnitureItem, Pose2D

from .catalog import import_catalog_asset
from .mask_providers import FalSamProvider, MaskProvider
from .mesh_providers import MeshProvider, catalog_mesh_providers
from .retailer import CatalogError, Fetch
from .selection_models import Category

logger = logging.getLogger(__name__)

WARNINGS_HEADER = "X-Reconstruction-Warnings"
GENERATION_TIMEOUT_S = 300
"""Per mesh provider. A request still running after it is collected by the next import."""


class CatalogImportRequest(BaseModel):
    product_url: str = Field(pattern=r"^https?://\S+$", max_length=2000)
    scene_id: str = Field(min_length=1, max_length=64)
    category: Category | None = None
    source: Literal["url_import", "catalog_search"] = "catalog_search"


def catalog_router(data_dir: Path, *, fetch: Fetch | None = None) -> APIRouter:
    """`fetch` replaces the public downloader (tests)."""
    router = APIRouter(prefix="/catalog", tags=["catalog import"])

    @router.post("/imports", response_model=FurnitureItem)
    def import_item(request: CatalogImportRequest, response: Response) -> FurnitureItem:
        """Import a product page and return the delivered item, unplaced. Slow: it downloads
        the page and model, and may generate a mesh. Warnings go in the response header."""
        key = os.environ.get("FAL_KEY", "").strip()
        # Bounded so the editor's Add button gives up in minutes. TRELLIS.2 took 216 s live.
        masks: MaskProvider | None = FalSamProvider(key=key, timeout_s=60) if key else None
        meshes: list[MeshProvider] | None = (
            catalog_mesh_providers(key, timeout_s=GENERATION_TIMEOUT_S) if key else None
        )
        try:
            result = import_catalog_asset(
                request.product_url,
                request.scene_id,
                data_dir=data_dir,
                category=request.category,
                source=request.source,
                mask_provider=masks,
                mesh_provider=meshes,
                fetch=fetch,
            )
        except CatalogError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except (ValueError, OSError, sqlite3.Error) as exc:
            logger.warning("catalog import failed: %s", type(exc).__name__)
            raise HTTPException(
                status_code=422, detail="the product could not be imported"
            ) from exc
        response.headers[WARNINGS_HEADER] = json.dumps(result.warnings[:8])
        return result.asset.to_item(Pose2D(x=0, z=0, yaw_deg=0))

    return router
