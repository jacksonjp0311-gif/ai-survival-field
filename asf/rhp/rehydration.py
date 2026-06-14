from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from asf.core.hashing import stable_hash
from asf.rhp.proof_state import ProofState


@dataclass(frozen=True)
class RehydrationReport:
    schema: str
    ok: bool
    locks: dict[str, bool]
    proof_state_hash: str
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def rehydrate(root: str | Path = ".", *, operator_authorized: bool = False) -> RehydrationReport:
    root_path = Path(root)
    proof = ProofState(operator_authorized=operator_authorized)
    locks = {
        "repo_root": root_path.exists(),
        "origin_manifest_declared": bool(proof.origin_manifest),
        "latest_state_declared": bool(proof.latest_state),
        "latest_evidence_declared": bool(proof.latest_evidence),
        "active_policy_declared": bool(proof.active_policy),
        "operator_authorized": operator_authorized,
    }
    return RehydrationReport(
        schema="ASF-REHYDRATION-v0.1",
        ok=all(locks.values()),
        locks=locks,
        proof_state_hash=stable_hash(proof.__dict__),
        non_claim_lock="Rehydration loads proof-state declarations. It grants no action authority by itself.",
    )

