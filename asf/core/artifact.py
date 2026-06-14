from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ASFArtifact:
    artifact_id: str
    mode: str
    intended_action: str
    raw_field: str
    constraints: list[dict[str, Any]]
    survivor_field: str
    residual_layers: list[str]
    missing_gates: list[dict[str, Any]]
    bounded_claim: str
    graph: dict[str, Any]
    conflicts: list[dict[str, Any]]
    audit_consequences: list[str]
    human_authorization: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ASFArtifact":
        return cls(
            artifact_id=str(data.get("artifact_id", "")),
            mode=str(data.get("mode", "")),
            intended_action=str(data.get("intended_action", "")),
            raw_field=str(data.get("raw_field", "")),
            constraints=list(data.get("constraints", [])),
            survivor_field=str(data.get("survivor_field", "")),
            residual_layers=list(data.get("residual_layers", [])),
            missing_gates=list(data.get("missing_gates", [])),
            bounded_claim=str(data.get("bounded_claim", "")),
            graph=dict(data.get("graph", {})),
            conflicts=list(data.get("conflicts", [])),
            audit_consequences=list(data.get("audit_consequences", [])),
            human_authorization=dict(data.get("human_authorization", {})),
        )

    @classmethod
    def load(cls, path: str | Path) -> "ASFArtifact":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)

