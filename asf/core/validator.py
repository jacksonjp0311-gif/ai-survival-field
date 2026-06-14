from __future__ import annotations

from asf.core.artifact import ASFArtifact
from asf.core.capability_token import CapabilityToken, token_allows
from asf.core.decision import Decision
from asf.core.hashing import stable_hash
from asf.core.permissions import allowed, min_level
from asf.core.policy import Policy
from asf.rcc.route import RCCRoute
from asf.rhp.rehydration import RehydrationReport


CONSEQUENCE_KEYS = {
    "claim_boundary_moved",
    "constraint_downgraded",
    "constraint_upgraded",
    "constraint_rejected",
    "dependency_exposed",
    "conflict_resolved",
    "conflict_quarantined",
    "residual_layer_identified",
    "missing_gate_named",
    "overclaim_blocked",
    "next_admissible_action_changed",
}


def validate(
    artifact: ASFArtifact,
    action: str,
    policy: Policy,
    rehydration: RehydrationReport,
    route: RCCRoute,
    capability_token: CapabilityToken | None = None,
    adapter: str = "cli",
) -> Decision:
    if not rehydration.ok:
        return _decision(artifact, action, policy, "rehydration_failed", "blocked", ["ASF001_REHYDRATION_FAILED"])
    if not route.route_hash:
        return _decision(artifact, action, policy, "rcc_route_failed", "blocked", ["ASF002_RCC_ROUTE_FAILED"])

    schema_errors = shape_errors(artifact)
    if schema_errors:
        return _decision(artifact, action, policy, "schema_failed", "blocked", ["ASF003_SCHEMA_FAILED"])

    conflicts = open_load_bearing_conflicts(artifact)
    if conflicts:
        decision = _decision(artifact, action, policy, "conflict_failed", "blocked", ["ASF006_CONFLICT_OPEN"])
        decision.open_conflicts = conflicts
        return decision

    score = consequence_score(artifact)
    if score == 0:
        return _decision(artifact, action, policy, "ritualistic", "blocked", ["ASF008_RITUALISTIC"])

    limiting_node, weakest = weakest_node(artifact)
    ceiling = min_level(weakest, gate_cap(artifact))
    required = policy.requirement_for(action)
    missing = blocking_gates(artifact, action, policy.required_controls_for(action))
    if missing:
        decision = _decision(artifact, action, policy, "missing_gate_failed", ceiling, ["ASF005_MISSING_GATE"])
        decision.missing_gates = missing
        decision.limiting_evidence_node = limiting_node
        return decision

    if not allowed(ceiling, required):
        decision = _decision(artifact, action, policy, "permission_ceiling_failed", ceiling, ["ASF004_PERMISSION_CEILING_FAILED"])
        decision.limiting_evidence_node = limiting_node
        return decision

    if policy.requires_human_authorization(action) and artifact.human_authorization.get("granted") is not True:
        decision = _decision(artifact, action, policy, "authorization_failed", ceiling, ["ASF007_AUTHORIZATION_FAILED"])
        decision.limiting_evidence_node = limiting_node
        return decision

    if policy.requires_human_authorization(action):
        artifact_hash = stable_hash(artifact.as_dict())
        if not token_allows(capability_token, action=action, artifact_hash=artifact_hash, policy_hash=policy.policy_hash, adapter=adapter):
            decision = _decision(artifact, action, policy, "authorization_failed", ceiling, ["ASF007_AUTHORIZATION_FAILED"])
            decision.limiting_evidence_node = limiting_node
            return decision

    decision = _decision(artifact, action, policy, "pass", ceiling, [])
    decision.limiting_evidence_node = limiting_node
    return decision


def authorization_failed_decision(artifact: ASFArtifact, action: str, policy: Policy, ceiling: str = "blocked") -> Decision:
    return _decision(artifact, action, policy, "authorization_failed", ceiling, ["ASF007_AUTHORIZATION_FAILED"])


def _decision(artifact: ASFArtifact, action: str, policy: Policy, status: str, ceiling: str, reasons: list[str]) -> Decision:
    permitted = ["draft", "propose", "request_evidence"] if status != "pass" else ["draft", "propose", "request_evidence", action]
    blocked = sorted(set(["commit", "release", "update_memory", "mark_canonical", "autonomous_action"]) - set(permitted))
    next_action = {
        "pass": "perform bounded action",
        "rehydration_failed": "rehydrate proof state",
        "rcc_route_failed": "repair RCC route",
        "schema_failed": "repair artifact",
        "conflict_failed": "resolve or quarantine conflict",
        "missing_gate_failed": "acquire required evidence",
        "permission_ceiling_failed": "downgrade action or claim",
        "authorization_failed": "obtain human authorization",
        "ritualistic": "rewrite with consequence",
    }.get(status, "review")
    return Decision(
        artifact_id=artifact.artifact_id,
        action=action,
        policy_name=policy.name,
        policy_hash=policy.policy_hash,
        status=status,
        permission_ceiling=ceiling,
        permitted_actions=sorted(set(permitted)),
        blocked_actions=blocked,
        reason_codes=reasons,
        next_admissible_action=next_action,
    )


def shape_errors(artifact: ASFArtifact) -> list[str]:
    errors = []
    if artifact.mode not in {"draft_review", "enforced_review"}:
        errors.append("mode")
    if not artifact.artifact_id:
        errors.append("artifact_id")
    if not artifact.constraints:
        errors.append("constraints")
    if artifact.mode == "enforced_review" and not artifact.graph:
        errors.append("graph")
    return errors


def weakest_node(artifact: ASFArtifact) -> tuple[str | None, str]:
    load_bearing = [c for c in artifact.constraints if c.get("load_bearing")]
    if not load_bearing:
        return None, "blocked"
    weakest = min(load_bearing, key=lambda c: _rank(c.get("permission_level", "blocked")))
    return str(weakest.get("id")), str(weakest.get("permission_level", "blocked"))


def _rank(level: str) -> int:
    from asf.core.permissions import rank
    return rank(level)


def open_load_bearing_conflicts(artifact: ASFArtifact) -> list[dict]:
    return [
        conflict for conflict in artifact.conflicts
        if conflict.get("status", "open") == "open" and conflict.get("load_bearing") is True
    ]


def consequence_score(artifact: ASFArtifact) -> int:
    return len({item for item in artifact.audit_consequences if item in CONSEQUENCE_KEYS})


def blocking_gates(artifact: ASFArtifact, action: str, required_controls: list[str]) -> list[dict]:
    blocked = []
    for gate in artifact.missing_gates:
        blocks_action = action in gate.get("blocks_actions", [])
        blocks_control = gate.get("gate_type") in required_controls
        if blocks_action or blocks_control:
            blocked.append(gate)
    return blocked


def gate_cap(artifact: ASFArtifact) -> str:
    cap = "formal"
    for gate in artifact.missing_gates:
        level = gate.get("blocks_permission_level")
        if level:
            from asf.core.permissions import PERMISSION_LEVELS, rank
            cap = PERMISSION_LEVELS[max(0, min(rank(cap), rank(level) - 1))]
    return cap
