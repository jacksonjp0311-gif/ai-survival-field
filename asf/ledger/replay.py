from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from asf.core.hashing import stable_hash
from asf.runtime import run_loop


@dataclass(frozen=True)
class ReplayReport:
    schema: str
    replay_id: str
    decision_hash_expected: str
    decision_hash_observed: str
    replay_pass: bool
    drift_detected: bool
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def replay_decision(
    artifact_path: str | Path,
    *,
    action: str,
    expected_decision_hash: str,
    policy_path: str | Path = "policies/default.yaml",
    root: str | Path = ".",
    operator_authorized: bool = True,
) -> ReplayReport:
    result = run_loop(artifact_path, action=action, policy_path=policy_path, root=root, operator_authorized=operator_authorized)
    observed = str(result["decision"]["decision_hash"])
    payload = {"artifact_path": str(artifact_path), "action": action, "expected": expected_decision_hash, "observed": observed}
    replay_pass = observed == expected_decision_hash
    return ReplayReport(
        schema="ASF-REPLAY-REPORT-v0.1",
        replay_id=f"ASF-REPLAY-{stable_hash(payload)[:12]}",
        decision_hash_expected=expected_decision_hash,
        decision_hash_observed=observed,
        replay_pass=replay_pass,
        drift_detected=not replay_pass,
        non_claim_lock="Replay proves decision reproducibility, not truth.",
    )

