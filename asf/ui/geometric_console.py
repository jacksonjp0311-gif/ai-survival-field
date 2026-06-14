from __future__ import annotations

from asf.core.decision import Decision
from asf.rcc.route import RCCRoute
from asf.rhp.rehydration import RehydrationReport
from asf.wounds.wound import WoundPackage


def render(rehydration: RehydrationReport, route: RCCRoute, decision: Decision, wound: WoundPackage | None) -> str:
    lock_lines = [f"  [{'PASS' if ok else 'OPEN'}] {name}" for name, ok in rehydration.locks.items()]
    wound_line = wound.wound_id if wound else "none"
    return "\n".join([
        "+======================================================================+",
        "|                    AI SURVIVAL FIELD RUNTIME                        |",
        "|                    RHP + RCC + SFT GOVERNANCE LOOP                  |",
        "+======================================================================+",
        "| STATE                                                                |",
        f"|  Rehydration:    {'PASS' if rehydration.ok else 'FAIL'}",
        f"|  RCC Surface:    {route.target_surface}",
        f"|  Claim Mode:     bounded",
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

