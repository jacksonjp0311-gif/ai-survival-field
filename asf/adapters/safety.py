from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


AdapterMode = Literal["observe_only", "dry_run", "enforce_block_only", "enforce_full"]


@dataclass(frozen=True)
class AdapterSafety:
    mode: AdapterMode = "observe_only"
    self_authorized: bool = False
    policy_loaded: bool = True
    human_authorized: bool = False
    policy_signature_required: bool = False
    policy_signature_present: bool = False

    def can_mutate(self) -> bool:
        if self.mode != "enforce_full":
            return False
        if self.self_authorized or not self.policy_loaded or not self.human_authorized:
            return False
        if self.policy_signature_required and not self.policy_signature_present:
            return False
        return True

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "ASF-ADAPTER-SAFETY-v0.1",
            "mode": self.mode,
            "can_mutate": self.can_mutate(),
            "self_authorized": self.self_authorized,
            "policy_loaded": self.policy_loaded,
            "human_authorized": self.human_authorized,
            "policy_signature_required": self.policy_signature_required,
            "policy_signature_present": self.policy_signature_present,
            "non_claim_lock": "Adapter safety status is not permission to mutate unless can_mutate is true and decision is pass.",
        }

