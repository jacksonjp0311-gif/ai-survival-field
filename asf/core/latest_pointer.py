from __future__ import annotations

import json
from pathlib import Path


def load_latest_pointer(path: str | Path = "docs/context/latest-asf.json") -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_latest_pointer(pointer: dict, *, observed_commit: str | None = None) -> dict[str, object]:
    failures: list[str] = []
    latest_commit = pointer.get("latest_commit", "")
    if not latest_commit or latest_commit == "pending":
        failures.append("LATEST_COMMIT_PENDING")
    if observed_commit and latest_commit != observed_commit:
        failures.append("LATEST_COMMIT_DRIFT")
    if pointer.get("mutation_enabled") is not False:
        failures.append("MUTATION_ENABLED_DRIFT")
    if pointer.get("self_healing_mutation_enabled") is not False:
        failures.append("SELF_HEALING_MUTATION_DRIFT")
    if "enforce_full" not in pointer.get("forbidden_modes", []):
        failures.append("ENFORCE_FULL_NOT_FORBIDDEN")
    return {
        "schema": "ASF-LATEST-POINTER-ALIGNMENT-v0.1",
        "ok": not failures,
        "latest_commit": latest_commit,
        "observed_commit": observed_commit,
        "failures": failures,
        "non_claim_lock": "Latest pointer alignment verifies rehydration continuity only. It grants no authority.",
    }
