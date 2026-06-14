from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from asf.core.permissions import rank
from asf.core.policy import Policy


@dataclass(frozen=True)
class PolicyDiff:
    schema: str
    from_policy: str
    to_policy: str
    added_actions: list[str]
    removed_actions: list[str]
    lowered_ceilings: list[str]
    raised_ceilings: list[str]
    added_required_controls: list[str]
    removed_required_controls: list[str]
    changed_human_authorization: list[str]
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def diff_policies(old: Policy, new: Policy) -> PolicyDiff:
    old_actions = set(old.actions)
    new_actions = set(new.actions)
    common = old_actions & new_actions
    lowered: list[str] = []
    raised: list[str] = []
    added_controls: list[str] = []
    removed_controls: list[str] = []

    for action in sorted(common):
        old_level = old.requirement_for(action)
        new_level = new.requirement_for(action)
        if rank(new_level) < rank(old_level):
            lowered.append(action)
        if rank(new_level) > rank(old_level):
            raised.append(action)
        old_controls = set(old.required_controls_for(action))
        new_controls = set(new.required_controls_for(action))
        if new_controls - old_controls:
            added_controls.append(action)
        if old_controls - new_controls:
            removed_controls.append(action)

    changed_auth = sorted(set(old.human_authorization_actions) ^ set(new.human_authorization_actions))
    return PolicyDiff(
        schema="ASF-POLICY-DIFF-v0.1",
        from_policy=old.name,
        to_policy=new.name,
        added_actions=sorted(new_actions - old_actions),
        removed_actions=sorted(old_actions - new_actions),
        lowered_ceilings=lowered,
        raised_ceilings=raised,
        added_required_controls=added_controls,
        removed_required_controls=removed_controls,
        changed_human_authorization=changed_auth,
        non_claim_lock="Policy diff exposes governance mutation. It does not approve the mutation.",
    )

