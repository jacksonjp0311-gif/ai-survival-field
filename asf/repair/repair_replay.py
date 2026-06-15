from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from asf.core.hashing import stable_hash
from asf.repair.repair_dry_run import dry_run
from asf.repair.repair_plan import RepairPlan
from asf.repair.repair_validation import validate_plan


@dataclass
class RepairReplayReport:
    schema: str
    replay_id: str
    repair_plan_hash: str
    dry_run_hash: str
    validation_hash: str
    replay_pass: bool
    drift_detected: bool
    failures: list[str]
    mutation_performed: bool
    repair_performed: bool
    wound_closed: bool
    authority_granted: bool
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def replay_repair(plan: RepairPlan, *, expected_repair_plan_hash: str | None = None) -> RepairReplayReport:
    plan_data = plan.as_dict()
    plan_hash = stable_hash(plan_data)
    dry = dry_run(plan)
    validation = validate_plan(plan)
    dry_hash = stable_hash(dry.as_dict())
    validation_hash = stable_hash(validation.as_dict())
    failures = list(validation.failures)
    if expected_repair_plan_hash and expected_repair_plan_hash != plan_hash:
        failures.append("REPAIR_PLAN_HASH_DRIFT")
    if dry.mutation_performed or validation.mutation_performed:
        failures.append("REPLAY_MUTATION_ATTEMPT")
    if dry.wound_closed or validation.wound_closed:
        failures.append("REPLAY_WOUND_CLOSURE_ATTEMPT")
    replay_pass = not failures
    payload = {"plan_hash": plan_hash, "dry_hash": dry_hash, "validation_hash": validation_hash}
    return RepairReplayReport(
        schema="ASF-REPAIR-REPLAY-v0.1",
        replay_id=f"ASF-REPAIR-REPLAY-{stable_hash(payload)[:12]}",
        repair_plan_hash=plan_hash,
        dry_run_hash=dry_hash,
        validation_hash=validation_hash,
        replay_pass=replay_pass,
        drift_detected=not replay_pass,
        failures=failures,
        mutation_performed=False,
        repair_performed=False,
        wound_closed=False,
        authority_granted=False,
        non_claim_lock="A repair replay is not wound closure. It proves repair-path reproducibility only.",
    )
