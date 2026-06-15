from __future__ import annotations

from pathlib import Path
from typing import Any

from asf.adapters.block_enforcer import enforce_block_only, event_for_artifact
from asf.core.hashing import stable_hash
from asf.repair.repair_plan import RepairPlan
from asf.repair.repair_replay import replay_repair
from asf.wounds.closure import build_closure_request, validate_closure


def run_dogfood(root: str | Path = ".") -> dict[str, Any]:
    base = Path(root)
    draft = enforce_block_only(event_for_artifact(str(base / "examples" / "artifacts" / "draft_allowed.json"), "draft"), root=str(base))
    blocked = enforce_block_only(event_for_artifact(str(base / "examples" / "artifacts" / "release_blocked_missing_tests.json"), "release"), root=str(base))
    import json
    plan = RepairPlan.from_dict(json.loads((base / "examples" / "repair_plans" / "missing_gate_repair_plan.json").read_text(encoding="utf-8")))
    replay = replay_repair(plan)
    synthetic_execution = {
        "status": "applied",
        "wound_closed": False,
        "repair_plan_hash": replay.repair_plan_hash,
        "repair_replay_hash": stable_hash(replay.as_dict()),
        "authorization_receipt_hash": "dogfood-auth",
        "evidence": {"post_repair_hash": "dogfood-post", "wound_closed": False},
    }
    request = build_closure_request(synthetic_execution, wound_id="ASF-WOUND-dogfood", closure_authorizer="dogfood")
    closure_validation = validate_closure(request, synthetic_execution)
    report = {
        "schema": "ASF-DOGFOOD-REPORT-v0.1",
        "draft_status": draft.decision["status"],
        "blocked_release_status": blocked.decision["status"],
        "repair_replay_pass": replay.replay_pass,
        "closure_validation_pass": closure_validation.valid,
        "mutation_performed": False,
        "self_healing_mutation_enabled": False,
        "enforce_full_enabled": False,
        "non_claim_lock": "Dogfood report demonstrates ASF-R operating on ASF-R fixtures. It is not production proof.",
    }
    report["dogfood_hash"] = stable_hash(report)
    return report
