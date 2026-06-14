from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProofState:
    origin_manifest: str = "origin_manifest.json"
    latest_state: str = "latest_state.json"
    latest_evidence: str = "latest_evidence.json"
    active_policy: str = "policies/default.yaml"
    open_wounds: list[str] = field(default_factory=list)
    operator_authorized: bool = False

