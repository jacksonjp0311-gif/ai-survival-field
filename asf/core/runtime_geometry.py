from __future__ import annotations


CANONICAL_GEOMETRY = [
    "ASFLOAD",
    "ROOT-ANCHOR",
    "RHP-REHYDRATE",
    "RCC-ORIENT",
    "POLICY-LOAD",
    "ADAPTER-OBSERVE",
    "GUARD-DECIDE",
    "WOUND-PACKET",
    "LEDGER-RECORD",
    "UI-RENDER",
    "ENFORCEMENT-REPORT",
    "REFLECT",
    "RELEASE-SEAL",
]


def validate_geometry(observed: list[str]) -> dict[str, object]:
    missing = [stage for stage in CANONICAL_GEOMETRY if stage not in observed]
    unexpected = [stage for stage in observed if stage not in CANONICAL_GEOMETRY]
    order_drift = False
    indexes = [observed.index(stage) for stage in CANONICAL_GEOMETRY if stage in observed]
    if indexes != sorted(indexes):
        order_drift = True
    ok = not missing and not unexpected and not order_drift
    return {
        "schema": "ASF-RUNTIME-GEOMETRY-v0.1",
        "canonical": CANONICAL_GEOMETRY,
        "observed": observed,
        "ok": ok,
        "missing_stages": missing,
        "unexpected_stages": unexpected,
        "order_drift": order_drift,
        "geometry_panel": " -> ".join(observed),
        "non_claim_lock": "Runtime geometry validation checks loop shape only. It does not prove truth or production readiness.",
    }
