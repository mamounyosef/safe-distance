"""Helpers shared by every detection benchmark."""

from __future__ import annotations

import platform
import subprocess
from datetime import datetime, timezone

import torch
import ultralytics


def iou(a: tuple, b: tuple) -> float:
    """IoU (Intersection over Union) of two (x1, y1, x2, y2) boxes."""
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def provenance() -> dict:
    """Everything needed to reproduce a set of numbers."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        ).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = "unknown", None
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": commit,
        "git_uncommitted_changes": dirty,
        "python": platform.python_version(),
        "torch": torch.__version__,
        "ultralytics": ultralytics.__version__,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none",
    }


def md_table(header: list[str], rows: list[list]) -> list[str]:
    """Render a Markdown table as a list of lines, followed by a blank line."""
    lines = ["| " + " | ".join(header) + " |", "|" + " --- |" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return lines + [""]


def pct(x: float) -> str:
    return f"{x:.0%}"


def best_row(label: str, values: list, higher_is_better: bool, fmt) -> list:
    """A comparison-table row with the best value in bold. None renders as '-'."""
    known = [v for v in values if v is not None]
    best = (max if higher_is_better else min)(known) if known else None
    cells = [
        "-" if v is None else (f"**{fmt(v)}**" if v == best and len(values) > 1 else fmt(v))
        for v in values
    ]
    return [label, *cells]
