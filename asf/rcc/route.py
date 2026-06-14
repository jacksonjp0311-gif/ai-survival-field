from __future__ import annotations

from dataclasses import dataclass

from asf.core.hashing import stable_hash


@dataclass(frozen=True)
class RCCRoute:
    schema: str
    artifact_id: str
    source: str
    intended_action: str
    target_surface: str
    claim_path: str
    evidence_path: str
    gate_path: str
    authority_path: str
    propagation_path: str
    route_hash: str

    def as_dict(self) -> dict[str, str]:
        return dict(self.__dict__)


def build_route(artifact_id: str, action: str) -> RCCRoute:
    target = classify_surface(action)
    data = {
        "schema": "ASF-RCC-ROUTE-v0.1",
        "artifact_id": artifact_id,
        "source": "artifact",
        "intended_action": action,
        "target_surface": target,
        "claim_path": f"artifact->{target}",
        "evidence_path": "artifact->missing_gates->evidence",
        "gate_path": f"policy->{action}->required_controls",
        "authority_path": f"human_authorization->{action}",
        "propagation_path": f"artifact->{action}->{target}",
    }
    return RCCRoute(route_hash=stable_hash(data), **data)


def classify_surface(action: str) -> str:
    if action in {"commit", "patch_repository"}:
        return "repository"
    if action == "update_memory":
        return "memory"
    if action in {"release", "publish", "mark_canonical"}:
        return "public_claim"
    if action == "autonomous_action":
        return "agent_runtime"
    return "draft_surface"

