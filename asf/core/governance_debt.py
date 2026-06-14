from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GovernanceDebt:
    schema: str
    debt_id: str
    description: str
    severity: str
    does_block_current_version: bool
    required_resolution: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


DEBTS = [
    GovernanceDebt("ASF-GOVERNANCE-DEBT-v0.1", "ASF-DEBT-001", "Adapters are not live enforcement integrations yet.", "medium", False, "Implement dry-run adapters in v0.3."),
    GovernanceDebt("ASF-GOVERNANCE-DEBT-v0.1", "ASF-DEBT-002", "Ledger records are hashed but not signed.", "medium", False, "Add signed ledger records before production release."),
    GovernanceDebt("ASF-GOVERNANCE-DEBT-v0.1", "ASF-DEBT-003", "Schema validation is lightweight.", "medium", False, "Integrate JSON Schema validation engine."),
    GovernanceDebt("ASF-GOVERNANCE-DEBT-v0.1", "ASF-DEBT-004", "No external security review has been performed.", "high", False, "Complete review before production claim."),
]


def registry() -> dict[str, Any]:
    return {
        "schema": "ASF-GOVERNANCE-DEBT-REGISTER-v0.1",
        "debts": [item.as_dict() for item in DEBTS],
        "non_claim_lock": "Governance debt records known gaps. It does not close them.",
    }

