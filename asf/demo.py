from __future__ import annotations

from pathlib import Path

from asf.dogfood import run_dogfood


def public_demo(root: str | Path = ".") -> dict[str, object]:
    dogfood = run_dogfood(root)
    return {
        "schema": "ASF-PUBLIC-DEMO-v0.1",
        "headline": "ASF-R turns AI failure into evidence-gated recovery.",
        "loop": [
            "detect wound",
            "package wound",
            "plan repair",
            "dry-run",
            "validate",
            "replay",
            "authorize bounded repair",
            "capture evidence",
            "validate closure",
        ],
        "dogfood_hash": dogfood["dogfood_hash"],
        "mutation_performed": False,
        "non_claim_lock": "The public demo is a runnable explanation, not a production safety claim.",
    }
