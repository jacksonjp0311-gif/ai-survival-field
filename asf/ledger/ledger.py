from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from asf.core.decision import Decision
from asf.core.hashing import stable_hash
from asf.rcc.route import RCCRoute
from asf.rhp.rehydration import RehydrationReport
from asf.wounds.wound import WoundPackage


@dataclass
class LedgerRecord:
    schema: str
    artifact_id: str
    decision_hash: str
    policy_hash: str
    rhp_state_hash: str
    rcc_route_hash: str
    actor: str
    timestamp: str
    reason_codes: list[str]
    wound_id: str | None
    adapter_event_hash: str
    non_claim_lock: str
    record_hash: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def build_record(
    decision: Decision,
    policy_data: dict[str, Any],
    rehydration: RehydrationReport,
    route: RCCRoute,
    wound: WoundPackage | None,
    *,
    actor: str = "operator",
    adapter_event_hash: str = "",
) -> LedgerRecord:
    data = {
        "artifact_id": decision.artifact_id,
        "decision_hash": decision.as_dict()["decision_hash"],
        "policy_hash": stable_hash(policy_data),
        "rhp_state_hash": rehydration.proof_state_hash,
        "rcc_route_hash": route.route_hash,
        "actor": actor,
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "reason_codes": decision.reason_codes,
        "wound_id": wound.wound_id if wound else None,
        "adapter_event_hash": adapter_event_hash,
        "non_claim_lock": "Ledger records provenance only. It grants no action authority and does not prove truth.",
    }
    return LedgerRecord(schema="ASF-LEDGER-RECORD-v0.1", record_hash=stable_hash(data), **data)


def verify_record(record: dict[str, Any]) -> bool:
    required = ["schema", "artifact_id", "decision_hash", "policy_hash", "rhp_state_hash", "rcc_route_hash", "record_hash", "non_claim_lock"]
    return all(record.get(key) for key in required) and record.get("schema") == "ASF-LEDGER-RECORD-v0.1"
