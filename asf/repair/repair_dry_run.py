from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from asf.core.hashing import stable_hash
from asf.repair.repair_plan import RepairPlan


@dataclass
class RepairDryRun:
    schema: str
    repair_plan_hash: str
    mutation_performed: bool
    repair_performed: bool
    wound_closed: bool
    simulated_actions: list[str]
    expected_new_evidence: list[str]
    authorization_requested: bool
    ui_status: str
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def dry_run(plan: RepairPlan) -> RepairDryRun:
    plan_data = plan.as_dict()
    expected_new_evidence = [action.split(":", 1)[1] for action in plan.proposed_actions if action.startswith("name_required_evidence:")]
    return RepairDryRun(
        schema="ASF-REPAIR-DRY-RUN-v0.1",
        repair_plan_hash=stable_hash(plan_data),
        mutation_performed=False,
        repair_performed=False,
        wound_closed=False,
        simulated_actions=plan.proposed_actions,
        expected_new_evidence=expected_new_evidence,
        authorization_requested=plan.requires_authorization,
        ui_status="repair planned, not repaired",
        non_claim_lock="Dry-run may reveal the shape of repair. Dry-run may not perform repair.",
    )
