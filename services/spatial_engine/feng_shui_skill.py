"""Load the same Form School skill for assessment and layout optimisation."""

from pathlib import Path
from typing import Literal

SKILL_PATH = Path(__file__).with_name("skills") / "feng-shui" / "SKILL.md"


def load_feng_shui_skill(mode: Literal["assessment", "layout_optimisation"]) -> str:
    source = SKILL_PATH.read_text(encoding="utf-8")
    parts = source.split("---", 2)
    body = parts[2].strip() if source.startswith("---\n") and len(parts) == 3 else source.strip()
    common, assessment_header, protocols = body.partition("\n## Assessment mode\n")
    assessment, optimisation_header, optimisation = protocols.partition(
        "\n## Layout optimisation mode\n"
    )
    if not common.strip() or not assessment_header or not optimisation_header:
        raise ValueError("The Feng Shui skill is missing its mode protocols")
    selected = assessment if mode == "assessment" else optimisation
    if not selected.strip():
        raise ValueError("The selected Feng Shui protocol is empty")
    return f"Mode: {mode}\n\n{common.strip()}\n\n{selected.strip()}"
