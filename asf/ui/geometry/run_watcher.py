from __future__ import annotations

from pathlib import Path

from asf.ui.geometry.state_loader import latest_run_summary


def current_run_summary(root: str | Path = ".") -> dict:
    return latest_run_summary(root)
