from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from asf.core.hashing import stable_hash


@dataclass
class WoundClosureRequest:
    schema: str = "ASF-WOUND-CLOSURE-REQUEST-v0.1"
    wound_id: str = ""
    repair_plan_hash: str = ""
    repair_replay_hash: str = ""
    repair_execution_hash: str = ""
    post_repair_hash: str = ""
    authorization_receipt_hash: str = ""
    closure_authorizer: str = ""
    closure_scope: str = "exact_wound_only"
    requested_status: str = "closed"
    non_claim_lock: str = "A closure request is not wound closure. It asks whether exact evidence permits closure."

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WoundClosureRequest":
        return cls(**{key: value for key, value in data.items() if key in cls.__dataclass_fields__})


@dataclass
class WoundClosureValidation:
    schema: str
    valid: bool
    failures: list[str]
    wound_id: str
    wound_closure_eligible: bool
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class WoundClosureRecord:
    schema: str
    closure_record_id: str
    wound_id: str
    repair_plan_hash: str
    repair_replay_hash: str
    repair_execution_hash: str
    post_repair_hash: str
    authorization_receipt_hash: str
    closure_authorizer: str
    wound_closed: bool
    closure_performed: bool
    mutation_performed: bool
    authority_granted: bool
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def build_closure_request(execution: dict[str, Any], *, wound_id: str, closure_authorizer: str) -> WoundClosureRequest:
    evidence = execution.get("evidence") or {}
    return WoundClosureRequest(
        wound_id=wound_id,
        repair_plan_hash=str(execution.get("repair_plan_hash", "")),
        repair_replay_hash=str(execution.get("repair_replay_hash", "")),
        repair_execution_hash=stable_hash(execution),
        post_repair_hash=str(evidence.get("post_repair_hash", "")),
        authorization_receipt_hash=str(execution.get("authorization_receipt_hash", "")),
        closure_authorizer=closure_authorizer,
    )


def validate_closure(request: WoundClosureRequest, execution: dict[str, Any]) -> WoundClosureValidation:
    failures: list[str] = []
    evidence = execution.get("evidence") or {}
    if not request.wound_id:
        failures.append("WOUND_ID_MISSING")
    if not request.closure_authorizer:
        failures.append("CLOSURE_AUTHORIZER_MISSING")
    if request.closure_scope != "exact_wound_only":
        failures.append("CLOSURE_SCOPE_NOT_EXACT")
    if execution.get("status") != "applied":
        failures.append("REPAIR_EXECUTION_NOT_APPLIED")
    if execution.get("wound_closed") is not False:
        failures.append("WOUND_ALREADY_CLOSED")
    if evidence.get("wound_closed") is not False:
        failures.append("EVIDENCE_ALREADY_CLOSES_WOUND")
    if not request.repair_plan_hash or request.repair_plan_hash != execution.get("repair_plan_hash"):
        failures.append("REPAIR_PLAN_HASH_MISMATCH")
    if not request.repair_replay_hash or request.repair_replay_hash != execution.get("repair_replay_hash"):
        failures.append("REPAIR_REPLAY_HASH_MISMATCH")
    if not request.post_repair_hash or request.post_repair_hash != evidence.get("post_repair_hash"):
        failures.append("POST_REPAIR_HASH_MISMATCH")
    if not request.authorization_receipt_hash or request.authorization_receipt_hash != execution.get("authorization_receipt_hash"):
        failures.append("AUTHORIZATION_RECEIPT_HASH_MISMATCH")
    if request.repair_execution_hash != stable_hash(execution):
        failures.append("REPAIR_EXECUTION_HASH_MISMATCH")
    return WoundClosureValidation(
        schema="ASF-WOUND-CLOSURE-VALIDATION-v0.1",
        valid=not failures,
        failures=failures,
        wound_id=request.wound_id,
        wound_closure_eligible=not failures,
        non_claim_lock="Closure validation proves eligibility only. It is not a general healing claim.",
    )


def close_wound(request: WoundClosureRequest, execution: dict[str, Any]) -> WoundClosureRecord:
    validation = validate_closure(request, execution)
    if not validation.valid:
        raise ValueError(",".join(validation.failures))
    payload = {"wound_id": request.wound_id, "execution": request.repair_execution_hash, "post": request.post_repair_hash}
    return WoundClosureRecord(
        schema="ASF-WOUND-CLOSURE-RECORD-v0.1",
        closure_record_id=f"ASF-WOUND-CLOSURE-{stable_hash(payload)[:12]}",
        wound_id=request.wound_id,
        repair_plan_hash=request.repair_plan_hash,
        repair_replay_hash=request.repair_replay_hash,
        repair_execution_hash=request.repair_execution_hash,
        post_repair_hash=request.post_repair_hash,
        authorization_receipt_hash=request.authorization_receipt_hash,
        closure_authorizer=request.closure_authorizer,
        wound_closed=True,
        closure_performed=True,
        mutation_performed=False,
        authority_granted=False,
        non_claim_lock="Controlled wound closure records exact wound closure only. It grants no general authority and performs no repair mutation.",
    )
