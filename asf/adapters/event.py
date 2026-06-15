from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from asf.core.hashing import stable_hash


@dataclass
class AdapterEvent:
    schema: str = "ASF-ADAPTER-EVENT-v0.1"
    event_id: str = ""
    adapter_name: str = "cli"
    adapter_mode: str = "observe_only"
    observed_action: str = "draft"
    source_surface: str = "operator"
    target_surface: str = "draft_surface"
    artifact_reference: str = ""
    proposed_mutation: dict[str, Any] = field(default_factory=dict)
    actor: str = "operator"
    timestamp: str = ""
    environment: str = "development"
    metadata: dict[str, Any] = field(default_factory=dict)
    event_hash: str = ""

    def as_dict(self) -> dict[str, Any]:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        data = dict(self.__dict__)
        data["event_hash"] = ""
        event_hash = stable_hash(data)
        if not self.event_hash:
            self.event_hash = event_hash
        if not self.event_id:
            self.event_id = f"ASF-EVENT-{self.event_hash[:12]}"
        data = dict(self.__dict__)
        data["event_hash"] = self.event_hash
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AdapterEvent":
        return cls(**{key: value for key, value in data.items() if key in cls.__dataclass_fields__})
