from __future__ import annotations

from asf.adapters.enforcement_report import EnforcementReport, build_report
from asf.adapters.event import AdapterEvent
from asf.runtime import run_loop


def simulate(event: AdapterEvent, *, policy_path: str = "policies/default.yaml", root: str = ".") -> EnforcementReport:
    event_data = event.as_dict()
    result = run_loop(
        event_data["artifact_reference"],
        action=event_data["observed_action"],
        policy_path=policy_path,
        root=root,
        operator_authorized=True,
        adapter_mode=event_data["adapter_mode"],
        adapter_event_hash=event_data["event_hash"],
    )
    simulated_effect = {
        "would_attempt": event_data["proposed_mutation"],
        "mutation_performed": False,
        "law": "Dry-run may describe the mutation. Dry-run may not perform the mutation.",
    }
    return build_report(event, result, simulated_effect)

