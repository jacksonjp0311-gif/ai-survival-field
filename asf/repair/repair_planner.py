from __future__ import annotations

from asf.repair.repair_classes import classify_wound
from asf.repair.repair_plan import RepairPlan


def plan_from_wound(
    wound: dict,
    *,
    source_decision_hash: str = "",
    source_policy_hash: str = "",
    source_ledger_hash: str = "",
) -> RepairPlan:
    wound_id = wound.get("wound_id", "")
    if not wound_id:
        raise ValueError("repair planning requires source wound identity")
    repair_class = classify_wound(wound)
    required_evidence = [item for item in wound.get("required_evidence", []) if item]
    proposed_actions = ["inspect_wound", "rerun_guard", "emit_new_ledger_record", "request_authorization_for_closure"]
    if repair_class == "missing_gate_evidence":
        proposed_actions.insert(1, "collect_required_evidence")
    if repair_class == "authorization_missing":
        proposed_actions.insert(1, "request_scoped_authorization")
    if required_evidence:
        proposed_actions.append("name_required_evidence:" + ",".join(required_evidence))
    return RepairPlan(
        wound_id=wound_id,
        repair_class=repair_class,
        source_decision_hash=source_decision_hash,
        source_policy_hash=source_policy_hash,
        source_ledger_hash=source_ledger_hash,
        proposed_actions=proposed_actions,
    )
