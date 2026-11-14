"""FFmpeg handles decoding and display rotation; FFprobe supplies original ordinals/PTS."""

from __future__ import annotations

import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray

from .selection_models import Box, Frame, SelectionOptions, SourceVideo


def read_image(data_dir: Path, frame: Frame) -> NDArray[np.uint8]:
    root = data_dir.resolve()
    path = (root / frame.image_path).resolve()
    if not path.is_relative_to(root):
        raise ValueError("frame artifact is outside the data directory")
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"frame artifact unavailable: {frame.key}")
    return image.astype(np.uint8, copy=False)


def crop(image: NDArray[np.uint8], box: Box) -> NDArray[np.uint8]:
    h, w = image.shape[:2]
    x0, y0 = min(w - 1, int(box.x * w)), min(h - 1, int(box.y * h))
    x1 = min(w, max(x0 + 1, round((box.x + box.width) * w)))
    y1 = min(h, max(y0 + 1, round((box.y + box.height) * h)))
    return image[y0:y1, x0:x1]


def image_quality(image: NDArray[np.uint8]) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sharpness = min(1.0, float(cv2.Laplacian(gray, cv2.CV_64F).var()) / 300)
    exposure = float(np.mean((gray > 15) & (gray < 240)))
    return 0.65 * sharpness + 0.35 * exposure


def _run(args: list[str], *, timeout: float = 120) -> str:
    try:
        return subprocess.run(
            args, check=True, capture_output=True, text=True, timeout=timeout
        ).stdout
    except FileNotFoundError as exc:
        raise ValueError("FFmpeg and FFprobe must be installed") from exc
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f"video processing failed ({type(exc).__name__})") from exc


def _transform(w: int, h: int, rotation: int) -> list[list[float]]:
    # Pixel-centre coordinates; FFmpeg's display rotation is counter-clockwise.
    matrix = {
        0: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        90: [[0, 1, 0], [-1, 0, w - 1], [0, 0, 1]],
        180: [[-1, 0, w - 1], [0, -1, h - 1], [0, 0, 1]],
        270: [[0, -1, h - 1], [1, 0, 0], [0, 0, 1]],
    }[rotation]
    return [[float(value) for value in row] for row in matrix]


def sample_video(
    path: Path, data_dir: Path, options: SelectionOptions
) -> tuple[SourceVideo, list[Frame], list[str]]:
    path = path.resolve(strict=True)
    if not path.is_file():
        raise ValueError("video input must be a local file")
    with path.open("rb") as file:
        source_id = hashlib.file_digest(file, "sha256").hexdigest()
    metadata: dict[str, Any] = json.loads(
        _run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_streams",
                "-show_frames",
                "-show_entries",
                "stream=index,width,height,time_base:stream_side_data=rotation:"
                "frame=best_effort_timestamp",
                "-of",
                "json",
                str(path),
            ]
        )
    )
    streams = metadata.get("streams", [])
    if not streams:
        raise ValueError("input has no video stream")
    stream = streams[0]
    w, h = int(stream["width"]), int(stream["height"])
    if w <= 0 or h <= 0 or w * h > 40_000_000:
        raise ValueError("unsupported video dimensions")
    rotation = (
        float(next((s["rotation"] for s in stream.get("side_data_list", []) if "rotation" in s), 0))
        % 360
    )
    if rotation not in (0, 90, 180, 270):
        raise ValueError("only right-angle display rotation is supported")
    time_base = Fraction(stream["time_base"])
    rows = metadata.get("frames", [])
    if not rows or any("best_effort_timestamp" not in row for row in rows):
        raise ValueError("video needs decoded presentation timestamps")
    pts = [int(row["best_effort_timestamp"]) for row in rows]
    times = np.array([float((value - pts[0]) * time_base) for value in pts])
    if np.any(np.diff(times) < 0):
        raise ValueError("video presentation timestamps are not monotonic")
    upright = (h, w) if rotation in (90, 270) else (w, h)
    source = SourceVideo(
        source_id=source_id,
        name=path.name,
        stream_index=stream["index"],
        encoded_size=(w, h),
        upright_size=upright,
        rotation_deg=int(rotation),
        encoded_to_upright=_transform(w, h, int(rotation)),
        time_base=str(time_base),
    )
    end = min(options.end_s, float(times[-1]) + 1e-6) if options.end_s else times[-1] + 1e-6
    valid = np.flatnonzero((times >= options.start_s) & (times < end))
    if not len(valid):
        raise ValueError("requested range contains no decoded video frames")
    # Decode two candidates per sampling interval; choose the sharper crop-independent frame.
    targets = np.arange(options.start_s, end, options.sample_interval_s / 2)
    warnings: list[str] = []
    limit = options.max_frames_per_video * 2
    if len(targets) > limit:
        targets = np.linspace(options.start_s, end, limit, endpoint=False)
        warnings.append(f"{source_id[:12]}: sampling cap widened the interval; coverage incomplete")
    indices = sorted({int(valid[np.argmin(np.abs(times[valid] - target))]) for target in targets})
    folder = data_dir / "frames" / source_id
    folder.mkdir(parents=True, exist_ok=True)
    missing = [i for i in indices if not (folder / f"{i}.png").exists()]
    if missing:
        # A bounded (at most 240 terms) select expression preserves decoder frame ordinals.
        expression = "+".join(f"eq(n\\,{i})" for i in missing)
        # No input seek: n must refer to the full source's decoded ordinal, including VFR.
        prefix = folder / "decode-"
        import tempfile

        with tempfile.TemporaryDirectory(prefix=str(prefix)) as temporary:
            _run(
                [
                    "ffmpeg",
                    "-nostdin",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    str(path),
                    "-map",
                    "0:v:0",
                    "-vf",
                    f"select={expression}",
                    "-fps_mode",
                    "passthrough",
                    "-frames:v",
                    str(len(missing)),
                    str(Path(temporary) / "%06d.png"),
                ]
            )
            for number, ordinal in enumerate(missing, 1):
                decoded = Path(temporary) / f"{number:06d}.png"
                if not decoded.exists():
                    raise ValueError("decoder returned fewer frames than requested")
                decoded.replace(folder / f"{ordinal}.png")
    candidates: list[Frame] = []
    for ordinal in indices:
        relative = f"frames/{source_id}/{ordinal}.png"
        frame = Frame(
            key=f"{source_id}:{source.stream_index}:{ordinal}",
            source_id=source_id,
            frame_index=ordinal,
            pts=pts[ordinal],
            timestamp_s=float(times[ordinal]),
            image_size_px=upright,
            image_path=relative,
            quality=0,
        )
        image = read_image(data_dir, frame)
        if (image.shape[1], image.shape[0]) != upright:
            raise ValueError("decoded display dimensions disagree with rotation metadata")
        frame.quality = image_quality(image)
        candidates.append(frame)
    # Adjacent candidate pairs give each interval a sharp alternative without extra inference.
    frames = [
        max(candidates[i : i + 2], key=lambda f: (f.quality, -f.frame_index))
        for i in range(0, len(candidates), 2)
    ]
    return source, frames, warnings
