from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from asf.core.artifact import ASFArtifact
from asf.core.authorization_receipt import AuthorizationReceipt, receipt_allows
from asf.core.capability_token import CapabilityToken
from asf.core.hashing import stable_hash
from asf.core.policy import load_policy
from asf.core.validator import authorization_failed_decision, validate
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
    capability_token: CapabilityToken | None = None,
    authorization_receipt: AuthorizationReceipt | None = None,
    adapter_mode: str = "observe_only",
    adapter_event_hash: str = "",
) -> dict[str, Any]:
    artifact = ASFArtifact.load(artifact_path)
    policy = load_policy(policy_path)
    rhp_report = rehydrate(root, operator_authorized=operator_authorized)
    route = orient(artifact, action)
    decision = validate(artifact, action, policy, rhp_report, route, capability_token=capability_token)
    if decision.status == "pass" and policy.requires_human_authorization(action):
        artifact_hash = stable_hash(artifact.as_dict())
        decision_hash = decision.as_dict()["decision_hash"]
        if not receipt_allows(
            authorization_receipt,
            action=action,
            artifact_hash=artifact_hash,
            policy_hash=policy.policy_hash,
            decision_hash=decision_hash,
        ):
            decision = authorization_failed_decision(artifact, action, policy, decision.permission_ceiling)
    wound = from_decision(decision)
    policy_data = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    ledger = build_record(decision, policy_data, rhp_report, route, wound, adapter_event_hash=adapter_event_hash)
    return {
        "rehydration": rhp_report.as_dict(),
        "route": route.as_dict(),
        "decision": decision.as_dict(),
        "wound": wound.as_dict() if wound else None,
        "ledger": ledger.as_dict(),
        "adapter_mode": adapter_mode,
        "adapter_event_hash": adapter_event_hash,
        "ui": render(rhp_report, route, decision, wound, policy, adapter_mode=adapter_mode),
    }
