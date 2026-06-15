from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from asf.core.hashing import stable_hash
from asf.repair.repair_dry_run import RepairDryRun
from asf.repair.repair_plan import RepairPlan
from asf.repair.repair_validation import RepairValidation


@dataclass
class RepairReport:
    schema: str
    repair_report_id: str
    repair_plan_hash: str
    validation_status: str
    mutation_performed: bool
    repair_performed: bool
    wound_closed: bool
    next_legal_action: str
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def build_report(plan: RepairPlan, dry_run_report: RepairDryRun, validation: RepairValidation) -> RepairReport:
    plan_hash = dry_run_report.repair_plan_hash
    payload = {"plan_hash": plan_hash, "valid": validation.valid, "wound_id": plan.wound_id}
    return RepairReport(
        schema="ASF-REPAIR-REPORT-v0.1",
        repair_report_id=f"ASF-REPAIR-REPORT-{stable_hash(payload)[:12]}",
        repair_plan_hash=plan_hash,
        validation_status="valid" if validation.valid else "invalid",
        mutation_performed=False,
        repair_performed=False,
        wound_closed=False,
        next_legal_action="request scoped authorization" if validation.valid else "repair plan",
        non_claim_lock="Repair report records repair planning state only. It does not perform repair or close wounds.",
    )
