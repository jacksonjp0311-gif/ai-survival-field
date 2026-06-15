from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from asf.adapters.event import AdapterEvent
from asf.core.hashing import stable_hash


@dataclass
class EnforcementReport:
    schema: str
    report_id: str
    event_hash: str
    decision_hash: str
    policy_hash: str
    route_hash: str
    rehydration_hash: str
    adapter_mode: str
    enforcement_result: str
    mutation_performed: bool
    simulated_effect: dict[str, Any]
    blocked_reason: str
    wound_id: str | None
    ledger_record_hash: str
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def build_report(event: AdapterEvent, runtime_result: dict[str, Any], simulated_effect: dict[str, Any]) -> EnforcementReport:
    event_data = event.as_dict()
    decision = runtime_result["decision"]
    wound = runtime_result.get("wound")
    ledger = runtime_result["ledger"]
    route = runtime_result["route"]
    rehydration = runtime_result["rehydration"]
    blocked = decision["status"] != "pass"
    adapter_mode = event_data["adapter_mode"]
    if blocked:
        enforcement_result = "block_enforced" if adapter_mode == "enforce_block_only" else "blocked"
    else:
        enforcement_result = "allowed" if adapter_mode == "enforce_block_only" else "dry_run_allowed"
    non_claim_lock = "Dry-run report describes simulated enforcement only. It performs no mutation and grants no production authority."
    if adapter_mode == "enforce_block_only":
        non_claim_lock = "Block-only enforcement may fail closed, but it performs no mutation, closes no wound, and grants no repair authority."
    payload = {
        "event_hash": event_data["event_hash"],
        "decision_hash": decision["decision_hash"],
        "policy_hash": decision["policy_hash"],
        "route_hash": route["route_hash"],
    }
    return EnforcementReport(
        schema="ASF-ENFORCEMENT-REPORT-v0.1",
        report_id=f"ASF-REPORT-{stable_hash(payload)[:12]}",
        event_hash=event_data["event_hash"],
        decision_hash=decision["decision_hash"],
        policy_hash=decision["policy_hash"],
        route_hash=route["route_hash"],
        rehydration_hash=rehydration["proof_state_hash"],
        adapter_mode=adapter_mode,
        enforcement_result=enforcement_result,
        mutation_performed=False,
        simulated_effect=simulated_effect,
        blocked_reason=",".join(decision.get("reason_codes", [])) if blocked else "",
        wound_id=wound["wound_id"] if wound else None,
        ledger_record_hash=ledger["record_hash"],
        non_claim_lock=non_claim_lock,
    )


def report_invariant_ok(report: dict[str, Any]) -> bool:
    if report.get("adapter_mode") == "dry_run" and report.get("mutation_performed") is not False:
        return False
    if report.get("adapter_mode") == "enforce_block_only" and report.get("mutation_performed") is not False:
        return False
    if report.get("adapter_mode") == "enforce_full":
        return False
    return bool(report.get("event_hash") and report.get("decision_hash"))
