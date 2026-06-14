from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from asf.core.decision import Decision
from asf.core.hashing import stable_hash


@dataclass
class WoundPackage:
    schema: str
    wound_id: str
    wound_class: str
    subject_artifact: str
    intended_action: str
    blocked_reason: str
    permission_ceiling: str
    blocked_actions: list[str]
    permitted_actions: list[str]
    required_evidence: list[str]
    next_admissible_action: str
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def from_decision(decision: Decision) -> WoundPackage | None:
    if decision.status == "pass":
        return None
    data = {
        "artifact": decision.artifact_id,
        "action": decision.action,
        "status": decision.status,
        "reasons": decision.reason_codes,
    }
    return WoundPackage(
        schema="ASF-WOUND-v0.1",
        wound_id=f"ASF-WOUND-{stable_hash(data)[:12]}",
        wound_class=decision.status,
        subject_artifact=decision.artifact_id,
        intended_action=decision.action,
        blocked_reason=", ".join(decision.reason_codes),
        permission_ceiling=decision.permission_ceiling,
        blocked_actions=decision.blocked_actions,
        permitted_actions=decision.permitted_actions,
        required_evidence=[gate.get("required_evidence", "") for gate in decision.missing_gates],
        next_admissible_action=decision.next_admissible_action,
        non_claim_lock="A wound package is not proof of failure in the world. It proves propagation is not yet permitted.",
    )

