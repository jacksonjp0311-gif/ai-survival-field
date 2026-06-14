from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from asf.core.hashing import stable_hash


@dataclass(frozen=True)
class AuthorizationReceipt:
    schema: str
    receipt_id: str
    operator: str
    action: str
    artifact_hash: str
    policy_hash: str
    decision_hash: str
    timestamp: str
    scope: dict[str, Any]
    expiration: str
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def issue_receipt(
    *,
    operator: str,
    action: str,
    artifact_hash: str,
    policy_hash: str,
    decision_hash: str,
    scope: dict[str, Any] | None = None,
    expiration: str = "2099-01-01T00:00:00+00:00",
) -> AuthorizationReceipt:
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    payload = {
        "operator": operator,
        "action": action,
        "artifact_hash": artifact_hash,
        "policy_hash": policy_hash,
        "decision_hash": decision_hash,
        "timestamp": timestamp,
        "scope": scope or {},
        "expiration": expiration,
    }
    return AuthorizationReceipt(
        schema="ASF-AUTHORIZATION-RECEIPT-v0.1",
        receipt_id=f"ASF-AUTH-{stable_hash(payload)[:12]}",
        non_claim_lock="Authorization receipt records scoped human authority. It does not prove truth or safety.",
        **payload,
    )


def receipt_allows(
    receipt: AuthorizationReceipt | None,
    *,
    action: str,
    artifact_hash: str,
    policy_hash: str,
    decision_hash: str,
) -> bool:
    if receipt is None:
        return False
    try:
        expiration = datetime.fromisoformat(receipt.expiration.replace("Z", "+00:00"))
    except ValueError:
        return False
    if expiration < datetime.now(timezone.utc):
        return False
    return (
        receipt.action == action
        and receipt.artifact_hash == artifact_hash
        and receipt.policy_hash == policy_hash
        and receipt.decision_hash == decision_hash
    )
