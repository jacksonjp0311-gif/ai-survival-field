from __future__ import annotations

from asf.adapters.event import AdapterEvent


AGENT_ACTIONS = {
    "write_file": "patch_repository",
    "update_memory": "update_memory",
    "call_tool": "autonomous_action",
    "publish_claim": "publish",
    "autonomous_action": "autonomous_action",
}


def observe_agent_action(*, artifact_reference: str, action: str, actor: str = "agent", mode: str = "dry_run") -> AdapterEvent:
    return AdapterEvent(
        adapter_name="agent",
        adapter_mode=mode,
        observed_action=AGENT_ACTIONS.get(action, "autonomous_action"),
        source_surface="agent_runtime",
        target_surface="agent_runtime",
        artifact_reference=artifact_reference,
        proposed_mutation={"operation": action},
        actor=actor,
    )

