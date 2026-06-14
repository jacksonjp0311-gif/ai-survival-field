from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from asf.core.hashing import stable_hash


@dataclass
class Decision:
    schema: str = "ASF-DECISION-v0.1"
    artifact_id: str = ""
    action: str = ""
    status: str = "block"
    permission_ceiling: str = "blocked"
    limiting_evidence_node: str | None = None
    permitted_actions: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    missing_gates: list[dict[str, Any]] = field(default_factory=list)
    open_conflicts: list[dict[str, Any]] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)
    next_admissible_action: str = "repair"
    non_claim_lock: str = (
        "ASF-R decision is not truth, safety, or production readiness. "
        "It is bounded continuation permission under active policy."
    )
    decision_hash: str = ""

    def as_dict(self) -> dict[str, Any]:
        data = dict(self.__dict__)
        data["decision_hash"] = ""
        data["decision_hash"] = stable_hash(data)
        return data

