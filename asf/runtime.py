from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from asf.core.artifact import ASFArtifact
from asf.core.policy import load_policy
from asf.core.validator import validate
from asf.ledger.ledger import build_record
from asf.rcc.nexus import orient
from asf.rhp.rehydration import rehydrate
from asf.ui.geometric_console import render
from asf.wounds.wound import from_decision


def run_loop(
    artifact_path: str | Path,
    *,
    action: str,
    policy_path: str | Path = "policies/default.yaml",
    operator_authorized: bool = True,
    root: str | Path = ".",
) -> dict[str, Any]:
    artifact = ASFArtifact.load(artifact_path)
    policy = load_policy(policy_path)
    rhp_report = rehydrate(root, operator_authorized=operator_authorized)
    route = orient(artifact, action)
    decision = validate(artifact, action, policy, rhp_report, route)
    wound = from_decision(decision)
    policy_data = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    ledger = build_record(decision, policy_data, rhp_report, route, wound)
    return {
        "rehydration": rhp_report.as_dict(),
        "route": route.as_dict(),
        "decision": decision.as_dict(),
        "wound": wound.as_dict() if wound else None,
        "ledger": ledger.as_dict(),
        "ui": render(rhp_report, route, decision, wound),
    }

