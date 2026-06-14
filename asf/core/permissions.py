from __future__ import annotations

PERMISSION_LEVELS = [
    "blocked",
    "speculative",
    "heuristic",
    "exploratory",
    "constraint_audited",
    "residual_stratified",
    "reproducible",
    "domain_validated",
    "formal",
]

PERMISSION_RANK = {name: index for index, name in enumerate(PERMISSION_LEVELS)}


def rank(level: str) -> int:
    return PERMISSION_RANK.get(level, 0)


def min_level(*levels: str) -> str:
    return PERMISSION_LEVELS[min(rank(level) for level in levels)]


def allowed(actual_ceiling: str, required_ceiling: str) -> bool:
    return rank(actual_ceiling) >= rank(required_ceiling)

