from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from asf.core.errors import PolicyError


@dataclass(frozen=True)
class Policy:
    name: str
    actions: dict[str, dict[str, Any]]
    human_authorization_actions: list[str]

    def requirement_for(self, action: str) -> str:
        rule = self.actions.get(action)
        if not rule:
            return "formal"
        return str(rule.get("min_permission_ceiling", "formal"))

    def required_controls_for(self, action: str) -> list[str]:
        rule = self.actions.get(action, {})
        controls = rule.get("requires", [])
        return list(controls) if isinstance(controls, list) else []

    def requires_human_authorization(self, action: str) -> bool:
        return action in set(self.human_authorization_actions)


def load_policy(path: str | Path) -> Policy:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "actions" not in data:
        raise PolicyError("policy missing actions")
    return Policy(
        name=str(data.get("name", "unnamed-policy")),
        actions=dict(data["actions"]),
        human_authorization_actions=list(data.get("human_authorization_actions", [])),
    )

