from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from asf.adapters.enforcement_report import EnforcementReport, build_report, report_invariant_ok
from asf.adapters.event import AdapterEvent
from asf.runtime import run_loop


@dataclass
class BlockEnforcement:
    schema: str
    exit_code: int
    enforcement_report: dict[str, Any]
    decision: dict[str, Any]
    wound: dict[str, Any] | None
    ledger: dict[str, Any]
    ui: str
    mutation_performed: bool
    repair_performed: bool
    wound_closed: bool
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def event_for_artifact(artifact_reference: str, action: str, *, actor: str = "operator") -> AdapterEvent:
    return AdapterEvent(
        adapter_name="cli",
        adapter_mode="enforce_block_only",
        observed_action=action,
        source_surface="cli",
        target_surface="runtime",
        artifact_reference=artifact_reference,
        proposed_mutation={"operation": action, "artifact_reference": artifact_reference},
        actor=actor,
    )


def enforce_block_only(event: AdapterEvent, *, policy_path: str = "policies/default.yaml", root: str = ".") -> BlockEnforcement:
    event.adapter_mode = "enforce_block_only"
    event_data = event.as_dict()
    result = run_loop(
        event_data["artifact_reference"],
        action=event_data["observed_action"],
        policy_path=policy_path,
        root=root,
        operator_authorized=True,
        adapter_mode="enforce_block_only",
        adapter_event_hash=event_data["event_hash"],
    )
    simulated_effect = {
        "would_attempt": event_data["proposed_mutation"],
        "mutation_performed": False,
        "repair_performed": False,
        "wound_closed": False,
        "law": "The system may enforce a block. The system may not perform a mutation.",
    }
    report: EnforcementReport = build_report(event, result, simulated_effect)
    report_data = report.as_dict()
    if not report_invariant_ok(report_data):
        exit_code = 2
    else:
        exit_code = 0 if result["decision"]["status"] == "pass" else 2
    return BlockEnforcement(
        schema="ASF-BLOCK-ENFORCEMENT-v0.1",
        exit_code=exit_code,
        enforcement_report=report_data,
        decision=result["decision"],
        wound=result["wound"],
        ledger=result["ledger"],
        ui=result["ui"],
        mutation_performed=False,
        repair_performed=False,
        wound_closed=False,
        non_claim_lock="Controlled block enforcement may stop a workflow. It does not mutate, repair, or prove truth.",
    )
