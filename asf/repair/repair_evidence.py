from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from asf.core.hashing import stable_hash


@dataclass
class RepairEvidence:
    schema: str
    pre_repair_hash: str
    proposed_diff_hash: str
    post_repair_hash: str
    applied_paths: list[str]
    repair_plan_hash: str
    repair_replay_hash: str
    authorization_receipt_hash: str
    mutation_performed: bool
    wound_closed: bool
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def hash_paths(root: str | Path, paths: list[str]) -> str:
    base = Path(root)
    payload = []
    for item in sorted(paths):
        path = base / item
        payload.append({"path": item, "exists": path.exists(), "content": path.read_text(encoding="utf-8") if path.is_file() else ""})
    return stable_hash(payload)


def build_evidence(
    *,
    root: str | Path,
    applied_paths: list[str],
    proposed_diff: dict,
    repair_plan_hash: str,
    repair_replay_hash: str,
    authorization_receipt_hash: str,
    pre_repair_hash: str,
    mutation_performed: bool,
) -> RepairEvidence:
    return RepairEvidence(
        schema="ASF-REPAIR-EVIDENCE-v0.1",
        pre_repair_hash=pre_repair_hash,
        proposed_diff_hash=stable_hash(proposed_diff),
        post_repair_hash=hash_paths(root, applied_paths),
        applied_paths=applied_paths,
        repair_plan_hash=repair_plan_hash,
        repair_replay_hash=repair_replay_hash,
        authorization_receipt_hash=authorization_receipt_hash,
        mutation_performed=mutation_performed,
        wound_closed=False,
        non_claim_lock="Repair evidence records bounded local repair effects. It does not close wounds or grant authority.",
    )
