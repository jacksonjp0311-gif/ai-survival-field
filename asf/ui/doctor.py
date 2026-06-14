from __future__ import annotations

from pathlib import Path
from typing import Any


REQUIRED_PATHS = [
    "README.md",
    "pyproject.toml",
    "asf/runtime.py",
    "asf/core/validator.py",
    "asf/core/invariants.py",
    "asf/core/alignment_auditor.py",
    "asf/ledger/replay.py",
    "asf/adapters/safety.py",
    "policies/default.yaml",
    "schemas/asf_artifact.schema.json",
    "schemas/asf_decision.schema.json",
    "schemas/asf_wound.schema.json",
    "docs/non_claim_lock.md",
]


def run_doctor(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root)
    checks = {path: (root_path / path).exists() for path in REQUIRED_PATHS}
    readme_path = root_path / "README.md"
    readme = readme_path.read_text(encoding="utf-8", errors="replace") if readme_path.exists() else ""
    checks["non_claim_lock_in_readme"] = "does not prove truth" in readme.lower()
    return {
        "schema": "ASF-OPERATOR-DOCTOR-v0.1",
        "ok": all(checks.values()),
        "checks": checks,
        "failures": [key for key, value in checks.items() if not value],
        "non_claim_lock": "Doctor checks scaffold health. It grants no action authority.",
    }

