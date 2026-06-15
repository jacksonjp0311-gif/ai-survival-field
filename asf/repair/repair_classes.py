REPAIR_CLASSES = [
    "documentation_alignment",
    "missing_gate_evidence",
    "policy_mismatch",
    "runtime_geometry_drift",
    "ui_decision_drift",
    "ledger_hash_drift",
    "adapter_mode_violation",
    "zero_context_pointer_stale",
    "repository_hygiene_warning",
    "repository_hygiene_error",
    "authorization_missing",
    "capability_token_invalid",
]


def classify_wound(wound: dict) -> str:
    wound_class = wound.get("wound_class", "")
    blocked_reason = wound.get("blocked_reason", "")
    if "MISSING_GATE" in blocked_reason or wound_class == "missing_gate_failed":
        return "missing_gate_evidence"
    if "AUTHORIZATION" in blocked_reason or wound_class == "authorization_failed":
        return "authorization_missing"
    if "POLICY" in blocked_reason:
        return "policy_mismatch"
    if "geometry" in wound_class:
        return "runtime_geometry_drift"
    return "documentation_alignment"
