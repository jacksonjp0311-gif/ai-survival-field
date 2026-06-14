from __future__ import annotations

from typing import Any


def audit_runtime_result(result: dict[str, Any], *, readme_text: str = "") -> dict[str, Any]:
    failures: list[str] = []
    decision = result.get("decision") or {}
    wound = result.get("wound")
    ledger = result.get("ledger") or {}
    route = result.get("route") or {}
    rehydration = result.get("rehydration") or {}
    ui = result.get("ui") or ""

    status = decision.get("status")
    if status and f"Status:         {status}" not in ui:
        failures.append("UI_DECISION_DRIFT")
    if status != "pass" and not wound:
        failures.append("WOUND_DECISION_DRIFT")
    if status == "pass" and wound:
        failures.append("WOUND_DECISION_DRIFT")
    if wound and wound.get("subject_artifact") != decision.get("artifact_id"):
        failures.append("WOUND_DECISION_DRIFT")
    if ledger.get("decision_hash") != decision.get("decision_hash"):
        failures.append("LEDGER_HASH_DRIFT")
    if ledger.get("rcc_route_hash") != route.get("route_hash"):
        failures.append("RCC_ROUTE_DRIFT")
    if ledger.get("rhp_state_hash") != rehydration.get("proof_state_hash"):
        failures.append("REHYDRATION_STATE_DRIFT")
    for surface in [decision, rehydration] + ([wound] if wound else []):
        if not surface.get("non_claim_lock"):
            failures.append("NON_CLAIM_LOCK_MISSING")
            break
    if not ledger.get("non_claim_lock"):
        failures.append("NON_CLAIM_LOCK_MISSING")
    if readme_text and "v0.1" not in readme_text and "v0.1.1" not in readme_text:
        failures.append("README_STATE_DRIFT")

    return {
        "schema": "ASF-RUNTIME-ALIGNMENT-AUDIT-v0.1",
        "ok": not failures,
        "failures": failures,
        "checked_surfaces": ["decision", "wound", "ledger", "route", "rehydration", "ui", "readme"],
        "non_claim_lock": "Alignment audit checks surface coherence. It does not prove truth.",
    }

