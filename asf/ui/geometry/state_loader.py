from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_latest_pointer(root: str | Path = ".") -> dict[str, Any]:
    return load_json(Path(root) / "docs" / "context" / "latest-asf.json")


def load_release_seal(root: str | Path = ".", pointer: dict[str, Any] | None = None) -> dict[str, Any]:
    root_path = Path(root)
    pointer_data = pointer or load_latest_pointer(root_path)
    seal_path = pointer_data.get("latest_release_seal", "")
    if not seal_path:
        return {}
    return load_json(root_path / seal_path)


def latest_run_summary(root: str | Path = ".") -> dict[str, Any]:
    run_root = Path(root) / ".asf_loop_runs"
    if not run_root.exists():
        return {}
    summaries = sorted(run_root.glob("*/summary.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    return load_json(summaries[0]) if summaries else {}
