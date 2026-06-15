from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from asf.repair.repair_plan import FORBIDDEN_REPAIR_ACTIONS, RepairPlan


@dataclass
class RepairValidation:
    schema: str
    valid: bool
    failures: list[str]
    wound_closed: bool
    mutation_performed: bool
    replay_required: bool
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def validate_plan(plan: RepairPlan) -> RepairValidation:
    failures: list[str] = []
    if not plan.wound_id:
        failures.append("WOUND_ID_MISSING")
    if not plan.source_decision_hash:
        failures.append("SOURCE_DECISION_HASH_MISSING")
    if not plan.source_policy_hash:
        failures.append("SOURCE_POLICY_HASH_MISSING")
    if plan.mutation_mode != "dry_run":
        failures.append("MUTATION_MODE_NOT_DRY_RUN")
    forbidden = set(plan.proposed_actions).intersection(FORBIDDEN_REPAIR_ACTIONS)
    if forbidden:
        failures.append("FORBIDDEN_ACTION_PROPOSED")
    if plan.authority_granted:
        failures.append("REPAIR_CANNOT_GRANT_AUTHORITY")
    if plan.enforce_full_enabled:
        failures.append("REPAIR_CANNOT_ENABLE_ENFORCE_FULL")
    if plan.repair_performed:
        failures.append("REPAIR_ALREADY_PERFORMED")
    if plan.wound_closed:
        failures.append("WOUND_CLOSED_BY_VALIDATION")
    return RepairValidation(
        schema="ASF-REPAIR-VALIDATION-v0.1",
        valid=not failures,
        failures=failures,
        wound_closed=False,
        mutation_performed=False,
        replay_required=True,
        non_claim_lock="A valid repair plan is not wound closure. It only proves that the repair path is coherent.",
    )
