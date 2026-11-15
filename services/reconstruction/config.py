"""Runtime settings of the reconstruction service."""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FURNITURE_DATA_DIR_ENV = "FURNITURE_DATA_DIR"


def furniture_data_dir() -> Path:
    """Where Dev 2's furniture pipeline keeps its registry, masks, meshes and served proxies.

    `$FURNITURE_DATA_DIR`, else `artifacts/furniture` in the repository: the furniture CLIs'
    default, resolved from the repository root so the server's working directory does not
    matter. The directory need not exist yet.
    """
    configured = os.environ.get(FURNITURE_DATA_DIR_ENV)
    return Path(configured).resolve() if configured else REPO_ROOT / "artifacts" / "furniture"


FURNITURE_DEMO_CACHE_DIR_ENV = "FURNITURE_DEMO_CACHE_DIR"


def demo_cache_dir() -> Path:
    """Where published demo furniture is read from when the pipeline has none (#20).

    `$FURNITURE_DEMO_CACHE_DIR`, else the cache committed with Dev 2's assets. Each scene's
    cache is a folder with a hash-verified manifest (`assets/demo_cache.py`); loading one
    needs no provider, key or network.
    """
    configured = os.environ.get(FURNITURE_DEMO_CACHE_DIR_ENV)
    if configured:
        return Path(configured).resolve()
    return REPO_ROOT / "services" / "reconstruction" / "assets" / "fixtures" / "demo_cache"
