from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from asf.core.hashing import stable_hash


@dataclass
class CIEvidence:
    schema: str
    commit: str
    workflow_name: str
    status: str
    test_count: int
    source: str
    timestamp: str
    mutation_performed: bool
    artifact_name: str
    evidence_hash: str
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def build_ci_evidence(
    *,
    commit: str,
    test_count: int,
    status: str = "local_pass",
    source: str = "local",
    workflow_name: str = "ASF Guard",
    artifact_name: str = "asf-ci-evidence",
) -> CIEvidence:
    data = {
        "commit": commit,
        "workflow_name": workflow_name,
        "status": status,
        "test_count": test_count,
        "source": source,
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "mutation_performed": False,
        "artifact_name": artifact_name,
    }
    return CIEvidence(
        schema="ASF-CI-EVIDENCE-v0.1",
        evidence_hash=stable_hash(data),
        non_claim_lock="CI evidence proves workflow execution state only. It does not prove production safety or truth.",
        **data,
    )


def verify_ci_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if evidence.get("schema") != "ASF-CI-EVIDENCE-v0.1":
        failures.append("CI_EVIDENCE_SCHEMA_INVALID")
    if not evidence.get("commit"):
        failures.append("CI_COMMIT_MISSING")
    if evidence.get("test_count", 0) <= 0:
        failures.append("CI_TEST_COUNT_MISSING")
    if evidence.get("mutation_performed") is not False:
        failures.append("CI_MUTATION_NOT_ALLOWED")
    if evidence.get("status") not in {"local_pass", "remote_pass", "remote_pending", "remote_failed"}:
        failures.append("CI_STATUS_INVALID")
    return {
        "schema": "ASF-CI-EVIDENCE-VERIFY-v0.1",
        "ok": not failures,
        "failures": failures,
        "non_claim_lock": "CI verification checks evidence shape only. It is not a production readiness claim.",
    }


def summarize_ci_for_pointer(evidence: dict[str, Any]) -> dict[str, Any]:
    verified = verify_ci_evidence(evidence)
    return {
        "remote_ci_status": evidence.get("status", "remote_pending"),
        "remote_ci_commit": evidence.get("commit", ""),
        "remote_ci_evidence_hash": evidence.get("evidence_hash", ""),
        "remote_ci_verified": verified["ok"] and evidence.get("source") == "github_actions",
    }
