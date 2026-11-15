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
