from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Invariant:
    schema: str
    invariant_id: str
    statement: str
    scope: list[str]
    failure_status: str
    repair_action: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


INVARIANTS = [
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-001", "Unknown is not pass.", ["runtime", "policy", "adapter", "ui"], "block", "produce explicit evidence or preserve unknown"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-002", "No rehydration, no action.", ["rhp", "runtime"], "rehydration_failed", "rehydrate proof state"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-003", "No RCC route, no mutation.", ["rcc", "runtime"], "rcc_route_failed", "repair RCC route"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-004", "No policy, no permission.", ["policy", "runtime"], "block", "load valid policy"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-005", "No wound package, no blocked-state closure.", ["wound", "ledger"], "block", "emit wound package"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-006", "No ledger record, no durable decision.", ["ledger", "runtime"], "block", "record ledger evidence"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-007", "No human authorization, no durable authority.", ["authorization", "adapter"], "authorization_failed", "obtain scoped human authorization"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-008", "No adapter may self-authorize.", ["adapter"], "block", "require external authorization"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-009", "No UI may display pass if decision is blocked.", ["ui", "decision"], "block", "repair UI decision binding"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-010", "No README claim may exceed evidence state.", ["docs", "release"], "block", "downgrade README claim or add evidence"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-011", "Dry-run must not mutate state.", ["adapter", "dry_run"], "block", "preserve simulation only"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-012", "Adapter event hash must bind to enforcement report.", ["adapter", "report"], "block", "rebuild report from event"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-013", "Enforcement report must bind to decision hash.", ["adapter", "decision"], "block", "bind report to current decision"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-014", "Live enforcement is forbidden before explicit release gate.", ["adapter", "release"], "block", "use dry-run only"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-015", "Dry-run success is not production permission.", ["adapter", "operator"], "block", "require controlled enforcement gate"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-016", "enforce_block_only may fail closed but may not mutate.", ["adapter", "workflow"], "block", "emit enforcement report without mutation"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-017", "A controlled block is not a repair.", ["adapter", "wound"], "block", "preserve wound until closure evidence exists"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-018", "Blocking evidence does not close the wound.", ["ledger", "wound"], "block", "require closure evidence"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-019", "enforce_full remains forbidden before production release gate.", ["adapter", "release"], "block", "stay in block-only mode"),
    Invariant("ASF-INVARIANT-v0.1", "ASF-INV-020", "Workflow failure caused by ASF-R must emit an enforcement report.", ["workflow", "adapter"], "block", "write or return enforcement report"),
]


def registry() -> dict[str, Any]:
    return {
        "schema": "ASF-INVARIANT-REGISTRY-v0.1",
        "invariants": [item.as_dict() for item in INVARIANTS],
        "non_claim_lock": "Invariant registry defines runtime laws. It does not prove truth or production safety.",
    }


def assert_unknown_not_pass(status: str | None) -> bool:
    return bool(status) and status != "unknown"
