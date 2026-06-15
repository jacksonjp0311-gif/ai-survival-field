from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from asf.core.hashing import stable_hash
from asf.repair.repair_plan import RepairPlan
from asf.repair.repair_replay import RepairReplayReport, replay_repair


@dataclass
class RepairAuthorizationReceipt:
    schema: str = "ASF-REPAIR-AUTHORIZATION-v0.1"
    authorization_receipt_id: str = ""
    human_authorizer: str = ""
    repair_plan_hash: str = ""
    repair_replay_hash: str = ""
    allowed_repair_class: str = ""
    allowed_paths: list[str] = field(default_factory=list)
    expires_at: str = ""
    single_use: bool = True
    authorization_scope: str = "bounded_local_repair"
    non_claim_lock: str = "Authorization may permit one bounded repair plan. Authorization may not grant general repair authority."

    def as_dict(self) -> dict[str, Any]:
        data = dict(self.__dict__)
        data["authorization_receipt_id"] = ""
        receipt_hash = stable_hash(data)
        data["authorization_receipt_id"] = self.authorization_receipt_id or f"ASF-REPAIR-AUTH-{receipt_hash[:12]}"
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RepairAuthorizationReceipt":
        return cls(**{key: value for key, value in data.items() if key in cls.__dataclass_fields__})


def build_receipt(plan: RepairPlan, *, human_authorizer: str, allowed_paths: list[str], expires_at: str = "", single_use: bool = True) -> RepairAuthorizationReceipt:
    replay = replay_repair(plan)
    return RepairAuthorizationReceipt(
        human_authorizer=human_authorizer,
        repair_plan_hash=stable_hash(plan.as_dict()),
        repair_replay_hash=stable_hash(replay.as_dict()),
        allowed_repair_class=plan.repair_class,
        allowed_paths=allowed_paths,
        expires_at=expires_at,
        single_use=single_use,
    )


def verify_receipt(receipt: RepairAuthorizationReceipt | None, plan: RepairPlan, replay: RepairReplayReport | None = None, *, target_path: str | None = None) -> dict[str, object]:
    failures: list[str] = []
    if receipt is None:
        failures.append("AUTHORIZATION_RECEIPT_MISSING")
        return _result(False, failures)
    replay_report = replay or replay_repair(plan)
    if not receipt.human_authorizer:
        failures.append("HUMAN_AUTHORIZER_MISSING")
    if receipt.repair_plan_hash != stable_hash(plan.as_dict()):
        failures.append("REPAIR_PLAN_HASH_MISMATCH")
    if receipt.repair_replay_hash != stable_hash(replay_report.as_dict()):
        failures.append("REPAIR_REPLAY_HASH_MISMATCH")
    if receipt.allowed_repair_class != plan.repair_class:
        failures.append("REPAIR_CLASS_NOT_AUTHORIZED")
    if receipt.expires_at:
        expires = datetime.fromisoformat(receipt.expires_at.replace("Z", "+00:00"))
        if expires < datetime.now(timezone.utc):
            failures.append("AUTHORIZATION_EXPIRED")
    if not receipt.single_use:
        failures.append("AUTHORIZATION_NOT_SINGLE_USE")
    if target_path and not path_allowed(target_path, receipt.allowed_paths):
        failures.append("PATH_NOT_AUTHORIZED")
    return _result(not failures, failures)


def path_allowed(path: str, allowed_paths: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    return any(normalized == item.rstrip("/") or normalized.startswith(item.rstrip("/") + "/") for item in allowed_paths)


def _result(ok: bool, failures: list[str]) -> dict[str, object]:
    return {
        "schema": "ASF-REPAIR-AUTHORIZATION-VERIFY-v0.1",
        "ok": ok,
        "failures": failures,
        "non_claim_lock": "Repair authorization verifies scoped human permission only. It does not close wounds or grant general authority.",
    }
