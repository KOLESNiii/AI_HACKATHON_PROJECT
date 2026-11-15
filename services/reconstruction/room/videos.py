"""Walkthrough videos uploaded with a floor plan, kept for furniture extraction.

`POST /floor-plans` accepts up to MAX_ROOM_VIDEOS videos beside the plan images. Each is saved,
content-addressed, as `<upload_dir>/<plan_id>/videos/<sha256[:16]><ext>`, and the route then
starts extracting their furniture in the background (`video_jobs.py`). Saving them calls no
provider.

Videos are staged first (size and type checked while streaming to disk), and kept only once
the plan has parsed, so a rejected upload leaves nothing behind.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

MAX_VIDEO_BYTES = 500 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024

_SUFFIX_BY_TYPE = {
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "video/x-m4v": ".m4v",
    "video/webm": ".webm",
    "video/x-matroska": ".mkv",
    "video/x-msvideo": ".avi",
}
_KNOWN_SUFFIXES = frozenset(_SUFFIX_BY_TYPE.values())

EXTRACTING_NOTE = (
    "{count} received: extracting their furniture with fal.ai in the background. It appears "
    "in the room you build once ready (a few minutes)."
)


class VideoRejected(ValueError):
    """The upload is not a usable video; `status_code` is the HTTP status to answer with."""

    def __init__(self, message: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class StagedVideo:
    path: Path
    sha256: str
    suffix: str
    size_bytes: int


def _suffix(filename: str | None, content_type: str | None) -> str:
    by_type = _SUFFIX_BY_TYPE.get((content_type or "").lower())
    if by_type:
        return by_type
    by_name = Path(filename or "").suffix.lower()
    return by_name if by_name in _KNOWN_SUFFIXES else ".video"


def stage_video(
    src: BinaryIO,
    filename: str | None,
    content_type: str | None,
    staging: Path,
    max_bytes: int = MAX_VIDEO_BYTES,
) -> StagedVideo:
    """Stream one uploaded video into `staging`, hashing it on the way.

    Raises `VideoRejected` for a non-video content type (415), an empty file (422) or one larger
    than `max_bytes` (413).
    """
    name = filename or "video"
    suffix = _suffix(filename, content_type)
    if not (content_type or "").lower().startswith("video/") and suffix == ".video":
        raise VideoRejected(f"{name} is not a video", 415)
    digest = hashlib.sha256()
    size = 0
    fd, tmp = tempfile.mkstemp(dir=staging, suffix=suffix)
    with os.fdopen(fd, "wb") as out:
        while chunk := src.read(CHUNK_BYTES):
            size += len(chunk)
            if size > max_bytes:
                raise VideoRejected(f"{name} is larger than {max_bytes} bytes", 413)
            digest.update(chunk)
            out.write(chunk)
    if size == 0:
        raise VideoRejected(f"{name} is empty")
    return StagedVideo(Path(tmp), digest.hexdigest(), suffix, size)


def new_staging(root: Path) -> Path:
    """A private staging directory under `root`; the caller removes it (`discard_staging`)."""
    root.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(dir=root, prefix=".staging-"))


def discard_staging(staging: Path) -> None:
    shutil.rmtree(staging, ignore_errors=True)


def keep_videos(staged: list[StagedVideo], plan_id: str, root: Path) -> list[Path]:
    """Move staged videos into the plan's video folder. Re-uploading a video is a no-op."""
    dest = root / plan_id / "videos"
    dest.mkdir(parents=True, exist_ok=True)
    kept: list[Path] = []
    for video in staged:
        target = dest / f"{video.sha256[:16]}{video.suffix}"
        if target.exists():
            video.path.unlink(missing_ok=True)
        else:
            os.replace(video.path, target)
        kept.append(target)
    return kept


def videos_note(count: int) -> str:
    noun = "1 walkthrough video" if count == 1 else f"{count} walkthrough videos"
    return EXTRACTING_NOTE.format(count=noun)
