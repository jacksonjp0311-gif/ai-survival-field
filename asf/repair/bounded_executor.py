from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from asf.core.hashing import stable_hash
from asf.repair.repair_authorization import RepairAuthorizationReceipt, verify_receipt
from asf.repair.repair_evidence import RepairEvidence, build_evidence, hash_paths
from asf.repair.repair_plan import RepairPlan
from asf.repair.repair_replay import replay_repair


ALLOWED_REPAIR_CLASSES = {
    "documentation_alignment",
    "latest_pointer_alignment",
    "repository_hygiene_metadata",
    "runtime_geometry_documentation_drift",
}

FORBIDDEN_PATH_PREFIXES = (
    "asf/core/policy",
    "asf/core/validator",
    "asf/adapters/",
    "policies/",
    "memory/",
    "releases/",
    ".github/workflows/release",
)


@dataclass
class BoundedRepairExecution:
    schema: str
    execution_id: str
    status: str
    failures: list[str]
    repair_plan_hash: str
    repair_replay_hash: str
    authorization_receipt_hash: str
    evidence: dict[str, Any] | None
    ledger_evidence_hash: str
    mutation_performed: bool
    repair_performed: bool
    wound_closed: bool
    authority_granted: bool
    enforce_full_enabled: bool
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def execute_bounded(
    plan: RepairPlan,
    receipt: RepairAuthorizationReceipt | None,
    *,
    root: str | Path = ".",
    target_path: str = "docs/repair_notes.md",
    content: str = "bounded repair evidence\n",
) -> BoundedRepairExecution:
    replay = replay_repair(plan)
    plan_hash = stable_hash(plan.as_dict())
    replay_hash = stable_hash(replay.as_dict())
    receipt_hash = stable_hash(receipt.as_dict()) if receipt else ""
    failures: list[str] = []
    if not replay.replay_pass:
        failures.append("REPAIR_REPLAY_NOT_PASS")
    if plan.repair_class not in ALLOWED_REPAIR_CLASSES:
        failures.append("REPAIR_CLASS_NOT_ALLOWLISTED")
    if forbidden_path(target_path):
        failures.append("FORBIDDEN_PATH")
    auth = verify_receipt(receipt, plan, replay, target_path=target_path)
    failures.extend(str(item) for item in auth["failures"])
    if failures:
        return _execution("blocked", failures, plan_hash, replay_hash, receipt_hash, None)
    base = Path(root)
    target = base / target_path
    pre_hash = hash_paths(base, [target_path])
    target.parent.mkdir(parents=True, exist_ok=True)
    before = target.read_text(encoding="utf-8") if target.exists() else ""
    target.write_text(before + content, encoding="utf-8")
    proposed_diff = {"path": target_path, "before": before, "after": before + content}
    evidence: RepairEvidence = build_evidence(
        root=base,
        applied_paths=[target_path],
        proposed_diff=proposed_diff,
        repair_plan_hash=plan_hash,
        repair_replay_hash=replay_hash,
        authorization_receipt_hash=receipt_hash,
        pre_repair_hash=pre_hash,
        mutation_performed=True,
    )
    return _execution("applied", [], plan_hash, replay_hash, receipt_hash, evidence.as_dict())


def forbidden_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(normalized.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES)


def _execution(status: str, failures: list[str], plan_hash: str, replay_hash: str, receipt_hash: str, evidence: dict[str, Any] | None) -> BoundedRepairExecution:
    payload = {"status": status, "failures": failures, "plan_hash": plan_hash, "replay_hash": replay_hash}
    mutation_performed = status == "applied"
    return BoundedRepairExecution(
        schema="ASF-BOUNDED-REPAIR-EXECUTION-v0.1",
        execution_id=f"ASF-BOUNDED-REPAIR-{stable_hash(payload)[:12]}",
        status=status,
        failures=failures,
        repair_plan_hash=plan_hash,
        repair_replay_hash=replay_hash,
        authorization_receipt_hash=receipt_hash,
        evidence=evidence,
        ledger_evidence_hash=stable_hash(evidence or payload),
        mutation_performed=mutation_performed,
        repair_performed=mutation_performed,
        wound_closed=False,
        authority_granted=False,
        enforce_full_enabled=False,
        non_claim_lock="Repair execution is not wound closure. Authorization permits only one bounded local repair plan.",
    )
