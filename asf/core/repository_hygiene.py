from __future__ import annotations

from pathlib import Path


WARNING_LIMIT_BYTES = 10_000_000
HARD_LIMIT_BYTES = 95_000_000
TRACKED_SURFACES = ["README.md", "docs", "docs/releases", "schemas", "policies", "examples", "examples/traces"]


def scan_repository(root: str | Path = ".") -> dict[str, object]:
    base = Path(root)
    warnings: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    checked: list[dict[str, object]] = []
    for surface in TRACKED_SURFACES:
        path = base / surface
        if not path.exists():
            continue
        files = [path] if path.is_file() else [item for item in path.rglob("*") if item.is_file()]
        for file_path in files:
            size = file_path.stat().st_size
            record = {"path": str(file_path.relative_to(base)), "size_bytes": size}
            checked.append(record)
            if size >= HARD_LIMIT_BYTES:
                errors.append(record)
            elif size >= WARNING_LIMIT_BYTES:
                warnings.append(record)
    return {
        "schema": "ASF-REPOSITORY-HYGIENE-v0.1",
        "ok": not errors,
        "warning_limit_bytes": WARNING_LIMIT_BYTES,
        "hard_limit_bytes": HARD_LIMIT_BYTES,
        "checked_files": checked,
        "warnings": warnings,
        "errors": errors,
        "non_claim_lock": "Repository hygiene keeps governance surfaces parseable. It is not a production quality claim.",
    }
