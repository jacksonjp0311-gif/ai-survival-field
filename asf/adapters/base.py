from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AdapterEvent:
    action: str
    artifact_path: str
    actor: str = "operator"
    metadata: dict[str, Any] | None = None


class ASFAdapter:
    def observe(self, event: AdapterEvent) -> AdapterEvent:
        return event

    def enforce(self, decision_status: str) -> bool:
        return decision_status == "pass"

