from __future__ import annotations

from dataclasses import dataclass
from typing import Any


READ_ONLY_UI_LAW = [
    "The UI may observe.",
    "The UI may illuminate.",
    "The UI may follow runtime state.",
    "The UI may render gates, wounds, evidence, and traces.",
    "The UI may not authorize repair.",
    "The UI may not execute mutation.",
    "The UI may not close wounds.",
    "The UI may not mutate policy.",
    "The UI may not write memory.",
    "The UI may not enable enforce_full.",
    "The UI may not grant authority.",
]


NON_CLAIM_LOCK = (
    "ASF-R Triadic Geometry Console observes and illuminates the governed loop only. "
    "It does not prove truth, make AI safe, provide formal verification, provide "
    "production security, authorize autonomous action, or grant repair authority."
)


@dataclass(frozen=True)
class GeometryGate:
    gate_id: int
    label: str
    sector: str
    status: str
    pass_condition: str
    detail: str = ""

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass(frozen=True)
class GeometryState:
    schema: str
    console_name: str
    mode: str
    vertices: dict[str, str]
    legend: dict[str, str]
    gates: list[dict[str, Any]]
    wound_panel: dict[str, Any]
    status_strip: dict[str, Any]
    cli_panel: dict[str, Any]
    read_only_law: list[str]
    non_claim_lock: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)
