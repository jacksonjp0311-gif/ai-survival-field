from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


ALLOWED_WITH_UNRESOLVED = {
    "observe",
    "diagnostic",
    "known_wound_repair",
    "governance_kernel_update",
    "documentation_only",
    "policy_hardening",
    "adapter_dry_run",
    "controlled_block_enforcement",
    "repair_planner_dry_run",
    "repair_validation",
    "residue_cleanup",
}

BLOCKED_WITH_UNRESOLVED = {
    "release",
    "promotion",
    "live_enforcement",
    "enforce_full",
    "self_healing_mutation",
    "wound_closure",
    "destructive_repair",
    "production_claim",
}


@dataclass
class EvolutionReadiness:
    schema: str
    requested_operation: str
    ready: bool
    blocked_reasons: list[str]
    permitted_lanes: list[str]
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def evaluate(
    *,
    test_status: str,
    open_wounds: list[str] | None,
    integration_closed: bool,
    worktree_clean: bool,
    requested_operation: str,
    current_release_seal: str,
    current_enforcement_mode: str,
) -> EvolutionReadiness:
    wounds = open_wounds or []
    reasons: list[str] = []
    unresolved = bool(wounds) or test_status in {"unknown", "failed"} or not integration_closed
    if requested_operation in BLOCKED_WITH_UNRESOLVED and unresolved:
        reasons.append("UNRESOLVED_STATE_BLOCKS_OPERATION")
    if test_status == "unknown" and requested_operation in BLOCKED_WITH_UNRESOLVED:
        reasons.append("UNKNOWN_TEST_STATE")
    if not worktree_clean and requested_operation in {"release", "promotion", "wound_closure", "production_claim"}:
        reasons.append("WORKTREE_NOT_CLEAN")
    if current_enforcement_mode == "enforce_full":
        reasons.append("ENFORCE_FULL_FORBIDDEN")
    if not current_release_seal:
        reasons.append("RELEASE_SEAL_MISSING")
    if requested_operation not in ALLOWED_WITH_UNRESOLVED and requested_operation not in BLOCKED_WITH_UNRESOLVED:
        reasons.append("UNKNOWN_OPERATION_CLASS")
    return EvolutionReadiness(
        schema="ASF-EVOLUTION-READINESS-v0.1",
        requested_operation=requested_operation,
        ready=not reasons,
        blocked_reasons=reasons,
        permitted_lanes=sorted(ALLOWED_WITH_UNRESOLVED),
        non_claim_lock="Evolution readiness classifies legal continuation only. It is not a production or truth claim.",
    )
