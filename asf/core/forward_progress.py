from __future__ import annotations


ALLOWED_WHILE_UNRESOLVED = {
    "documentation",
    "observability",
    "test_contract",
    "dry_run_adapter",
    "operator_experience",
    "policy_hardening",
    "wound_packaging",
    "repair_planner_dry_run",
    "runtime_geometry_validation",
    "repository_hygiene",
    "zero_context_rehydration",
}

BLOCKED_WHILE_UNRESOLVED = {
    "live_enforcement",
    "wound_closure",
    "production_release",
    "memory_promotion",
    "self_healing_mutation",
    "enforce_full",
    "destructive_repair",
    "green_claim",
}


def classify_progress(action: str, *, unresolved: bool = True) -> dict[str, object]:
    if unresolved and action in BLOCKED_WHILE_UNRESOLVED:
        status = "blocked"
    elif action in ALLOWED_WHILE_UNRESOLVED:
        status = "permitted"
    else:
        status = "review"
    return {
        "schema": "ASF-FORWARD-PROGRESS-v0.1",
        "action": action,
        "status": status,
        "allowed_while_unresolved": sorted(ALLOWED_WHILE_UNRESOLVED),
        "blocked_while_unresolved": sorted(BLOCKED_WHILE_UNRESOLVED),
        "non_claim_lock": "Forward progress permission is not wound closure and is not a green claim.",
    }
