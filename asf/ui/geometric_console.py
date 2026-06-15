from __future__ import annotations

from asf.core.decision import Decision
from asf.core.policy import Policy
from asf.rcc.route import RCCRoute
from asf.rhp.rehydration import RehydrationReport
from asf.wounds.wound import WoundPackage


def render(
    rehydration: RehydrationReport,
    route: RCCRoute,
    decision: Decision,
    wound: WoundPackage | None,
    policy: Policy | None = None,
    *,
    adapter_mode: str = "observe_only",
) -> str:
    lock_lines = [f"  [{'PASS' if ok else 'OPEN'}] {name}" for name, ok in rehydration.locks.items()]
    wound_line = wound.wound_id if wound else "none"
    policy_name = policy.name if policy else decision.policy_name
    policy_hash = policy.policy_hash if policy else decision.policy_hash
    return "\n".join([
        "+======================================================================+",
        "|                    AI SURVIVAL FIELD RUNTIME                        |",
        "|                    RHP + RCC + SFT GOVERNANCE LOOP                  |",
        "+======================================================================+",
        "| STATE                                                                |",
        f"|  Rehydration:    {'PASS' if rehydration.ok else 'FAIL'}",
        f"|  RCC Surface:    {route.target_surface}",
        f"|  Adapter Mode:   {adapter_mode}",
        f"|  Claim Mode:     bounded",
        "+======================================================================+",
        "| ACTIVE POLICY                                                        |",
        f"|  Policy:         {policy_name}",
        f"|  Policy Hash:    {policy_hash[:16] if policy_hash else 'unknown'}",
        "+======================================================================+",
        "| LOCKS                                                                |",
        *lock_lines,
        "+======================================================================+",
        "| WOUND PACKAGE                                                        |",
        f"|  Wound ID:       {wound_line}",
        "+======================================================================+",
        "| DECISION                                                             |",
        f"|  Status:         {decision.status}",
        f"|  Ceiling:        {decision.permission_ceiling}",
        f"|  Permitted:      {', '.join(decision.permitted_actions)}",
        f"|  Blocked:        {', '.join(decision.blocked_actions)}",
        f"|  Next:           {decision.next_admissible_action}",
        "+======================================================================+",
    ])
