from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from asf.core.hashing import stable_hash


FORBIDDEN_REPAIR_ACTIONS = [
    "perform_mutation",
    "close_wound_without_evidence",
    "grant_self_authority",
    "enable_enforce_full",
]


@dataclass
class RepairPlan:
    schema: str = "ASF-REPAIR-PLAN-v0.1"
    repair_plan_id: str = ""
    wound_id: str = ""
    repair_class: str = "documentation_alignment"
    source_decision_hash: str = ""
    source_policy_hash: str = ""
    source_ledger_hash: str = ""
    proposed_actions: list[str] = field(default_factory=list)
    mutation_mode: str = "dry_run"
    requires_authorization: bool = True
    forbidden_actions: list[str] = field(default_factory=lambda: list(FORBIDDEN_REPAIR_ACTIONS))
    expected_outputs: list[str] = field(default_factory=lambda: ["repair_dry_run_report", "repair_validation_report", "authorization_request"])
    repair_performed: bool = False
    wound_closed: bool = False
    authority_granted: bool = False
    enforce_full_enabled: bool = False
    non_claim_lock: str = "A repair plan is not a repair. It is a bounded proposal."

    def as_dict(self) -> dict[str, Any]:
        data = dict(self.__dict__)
        data["repair_plan_id"] = ""
        plan_hash = stable_hash(data)
        data["repair_plan_id"] = self.repair_plan_id or f"ASF-REPAIR-{plan_hash[:12]}"
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RepairPlan":
        return cls(**{key: value for key, value in data.items() if key in cls.__dataclass_fields__})
