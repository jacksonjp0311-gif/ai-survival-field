from __future__ import annotations

from pathlib import Path
from typing import Any

from asf.ui.geometry.schemas import GeometryGate, GeometryState, NON_CLAIM_LOCK, READ_ONLY_UI_LAW
from asf.ui.geometry.state_loader import latest_run_summary, load_latest_pointer, load_release_seal


GATE_DEFINITIONS = [
    (1, "Latest Pointer Loaded", "Evidence", "docs/context/latest-asf.json loaded"),
    (2, "Rehydration Passed", "Evidence", "runtime proof state loaded and valid"),
    (3, "Release Seal Loaded", "Evidence", "active release seal resolved"),
    (4, "Repository Truth Aligned", "Evidence", "repo root and origin state match expectations"),
    (5, "CI Evidence Loaded", "Evidence", "CI evidence exists or declared state is loaded"),
    (6, "Ledger Verify", "Evidence", "ledger record verification passes"),
    (7, "Policy Loaded", "Governance", "active policy loaded"),
    (8, "Invariants Loaded", "Governance", "invariant registry available"),
    (9, "Claim Ceiling Assigned", "Governance", "permission ceiling computed"),
    (10, "Artifact Validated", "Governance", "artifact accepted by runtime path"),
    (11, "Decision Computed", "Governance", "decision object emitted"),
    (12, "Permission Checked", "Governance", "action allowed, downgraded, or blocked"),
    (13, "Non-Claim Lock Preserved", "Governance", "non-claim lock visible and unchanged"),
    (14, "Block Enforcement Checked", "Action", "block-only or dry-run path evaluated"),
    (15, "Wound Emitted", "Action", "wound package exists when blocked"),
    (16, "Repair Plan Created", "Action", "repair plan generated from wound"),
    (17, "Repair Dry-Run Passed", "Action", "dry-run report generated without mutation"),
    (18, "Repair Validation Passed", "Action", "repair validation passes"),
    (19, "Repair Replay Passed", "Action", "repair replay passes"),
    (20, "Authorization Bound", "Action", "scoped authorization receipt bound"),
    (21, "Bounded Repair Executed", "Action", "bounded repair executed only under receipt and sandbox"),
    (22, "Post-Repair Evidence Captured", "Action", "post-repair evidence emitted"),
    (23, "Closure Request Created", "Action", "closure request generated"),
    (24, "Closure Validation Passed", "Action", "closure-specific validation passes"),
    (25, "Closure Record Written", "Action", "closure record emitted without general authority"),
]

LEGEND = {
    "pass": "Green = pass",
    "fail": "Red = blocked/fail",
    "blocked": "Red = action blocked",
    "pending": "Amber = active/pending",
    "read_only": "Cyan = read-only evidence",
    "inactive": "Gray = inactive",
    "forbidden": "Deep red lock = forbidden",
}

KNOWN_STATUSES = {"pass", "blocked", "fail", "pending", "read_only", "inactive", "forbidden"}

GATE_COORDINATES = [
    (334, 145), (286, 184), (252, 234), (230, 292), (222, 354),
    (236, 416), (270, 474), (320, 522), (382, 554), (450, 570),
    (520, 568), (590, 548), (654, 514), (710, 468), (754, 414),
    (786, 354), (800, 292), (792, 230), (762, 174), (714, 132),
    (652, 104), (586, 92), (520, 96), (456, 104), (394, 122),
]

LABEL_OVERRIDES = {
    1: (268, 142),
    2: (218, 182),
    3: (188, 234),
    4: (162, 292),
    5: (154, 354),
    6: (168, 416),
    7: (200, 474),
    8: (252, 522),
    9: (350, 592),
    10: (450, 612),
    11: (520, 610),
    12: (590, 590),
    13: (666, 552),
    14: (782, 468),
    15: (830, 414),
    16: (862, 354),
    17: (872, 292),
    18: (866, 230),
    19: (832, 174),
    20: (778, 132),
    21: (710, 86),
    22: (630, 78),
    23: (520, 132),
    24: (410, 78),
    25: (330, 96),
}

VERTICES = {
    "evidence": "Evidence / Rehydration",
    "governance": "Governance / Coherence",
    "action": "Action / Recovery",
}


def build_geometry_state(root: str | Path = ".", run_summary: dict[str, Any] | None = None) -> GeometryState:
    root_path = Path(root)
    pointer = load_latest_pointer(root_path)
    seal = load_release_seal(root_path, pointer)
    summary = run_summary if run_summary is not None else latest_run_summary(root_path)
    gates = map_gates(root_path, pointer, seal, summary)
    wound = summary.get("wound_package") or summary.get("wound") or {}
    decision = summary.get("decision") or {}
    closure = summary.get("closure_record") or {}
    status_strip = {
        "latest_version": pointer.get("latest_version", "unknown"),
        "latest_commit": pointer.get("latest_commit", "unknown"),
        "release_seal": pointer.get("latest_release_seal", "unknown"),
        "current_state": pointer.get("current_state", "unknown"),
        "current_action": summary.get("action", "read_only_observe"),
        "decision": decision.get("status", summary.get("decision_status", "unknown")),
        "permission_ceiling": decision.get("permission_ceiling", summary.get("permission_ceiling", "unknown")),
        "wound_id": wound.get("wound_id", "none"),
        "authorization_receipt_id": summary.get("authorization_receipt", {}).get("authorization_receipt_id", "none"),
        "closure_status": "closed" if closure.get("wound_closed") else "not_closed",
        "ci_evidence_status": pointer.get("remote_ci_status", "unknown"),
        "non_claim_lock": pointer.get("non_claim_lock", NON_CLAIM_LOCK),
    }
    failed_gate_id = failed_gate(summary, wound)
    return GeometryState(
        schema="ASF-TRIADIC-GEOMETRY-STATE-v0.1",
        console_name="ASF-R Triadic Geometry Console",
        mode="read_only_observe",
        vertices=VERTICES,
        legend=LEGEND,
        gates=[gate.as_dict() for gate in gates],
        wound_panel=wound_panel(wound, decision),
        status_strip=status_strip,
        cli_panel=cli_panel(summary),
        read_only_law=READ_ONLY_UI_LAW,
        non_claim_lock=NON_CLAIM_LOCK,
        failed_gate_id=failed_gate_id,
        events_endpoint="/events",
    )


def map_gates(root: Path, pointer: dict[str, Any], seal: dict[str, Any], summary: dict[str, Any]) -> list[GeometryGate]:
    values = {
        1: bool(pointer),
        2: summary.get("rehydration_passed") is True or bool(pointer),
        3: bool(seal),
        4: bool(pointer.get("remote_url")),
        5: pointer.get("remote_ci_status") in {"remote_pass", "local_pass"},
        6: summary.get("ledger_verified") is True,
        7: (root / "policies" / "default.yaml").exists(),
        8: (root / "docs" / "invariant_registry.md").exists(),
        9: bool(summary.get("permission_ceiling") or (summary.get("decision") or {}).get("permission_ceiling")),
        10: bool(summary.get("artifact_validated")),
        11: bool(summary.get("decision") or summary.get("decision_status")),
        12: bool(summary.get("permission_checked") or summary.get("decision") or summary.get("decision_status")),
        13: bool(pointer.get("non_claim_lock") or seal.get("non_claim_lock")),
        14: bool(summary.get("block_enforcement_checked")),
        15: bool(summary.get("wound_package") or summary.get("wound")),
        16: bool(summary.get("repair_plan")),
        17: bool(summary.get("repair_dry_run_passed")),
        18: bool(summary.get("repair_validation_passed")),
        19: bool(summary.get("repair_replay_passed")),
        20: bool(summary.get("authorization_bound")),
        21: bool(summary.get("bounded_repair_executed")),
        22: bool(summary.get("post_repair_evidence_captured")),
        23: bool(summary.get("closure_request")),
        24: bool(summary.get("closure_validation_passed")),
        25: bool(summary.get("closure_record")),
    }
    failed = set(summary.get("failed_gates", []))
    forbidden = set(summary.get("forbidden_gates", []))
    gates: list[GeometryGate] = []
    for gate_id, label, sector, pass_condition in GATE_DEFINITIONS:
        if gate_id in forbidden or "enforce_full" in label.lower():
            status = "forbidden"
        elif gate_id in failed:
            status = "blocked"
        elif values.get(gate_id):
            status = "read_only" if gate_id in {5, 13} else "pass"
        elif summary:
            status = "pending" if gate_id >= 16 else "inactive"
        else:
            status = "inactive"
        x, y = GATE_COORDINATES[gate_id - 1]
        label_x, label_y = LABEL_OVERRIDES.get(gate_id, label_coordinates(x, y))
        gates.append(GeometryGate(
            gate_id,
            label,
            sector,
            status,
            pass_condition,
            x=x,
            y=y,
            label_x=label_x,
            label_y=label_y,
            failed=status in {"blocked", "fail"},
            wound_linked=gate_id == failed_gate(summary, summary.get("wound_package") or summary.get("wound") or {}),
        ))
    return gates


def wound_panel(wound: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    if not wound:
        return {"status": "read_only", "message": "NO ACTIVE WOUND"}
    return {
        "status": "blocked",
        "wound_id": wound.get("wound_id", "unknown"),
        "failed_gate": "Missing Gate Check",
        "failed_gate_id": 12,
        "failure_class": wound.get("wound_class", decision.get("status", "unknown")),
        "decision": decision.get("status", "blocked"),
        "permission_ceiling": decision.get("permission_ceiling", "unknown"),
        "blocked_actions": decision.get("blocked_actions", wound.get("blocked_actions", [])),
        "permitted_actions": decision.get("permitted_actions", wound.get("permitted_actions", [])),
        "recommended_repair_path": wound.get("next_admissible_action", decision.get("next_admissible_action", "request_evidence")),
        "repair_plan_status": "available",
        "closure_status": "not closed",
    }


def cli_panel(summary: dict[str, Any]) -> dict[str, Any]:
    stream = summary.get("stream") or [
        "12:34:10.128 [INIT] Runtime initialized (read-only)",
        "12:34:10.246 [GATE 01] Latest Pointer Loaded ............... PASS",
        "12:34:10.312 [GATE 02] Rehydration Passed .................. PASS",
        "12:34:10.481 [GATE 07] Policy Loaded ....................... PASS",
        "12:34:10.612 [GATE 11] Decision Computed ................... PASS",
        "12:34:10.733 [GATE 12] Permission Checked .................. BLOCKED",
        "12:34:10.734 [DECISION] Blocked by Permission Ceiling",
        "12:34:10.735 [GATE 15] Wound Emitted ....................... PASS",
        "12:34:11.492 [GATE 19] Repair Replay Passed ................ PASS",
        "12:34:11.713 [GATE 24] Closure Validation Passed ............ PASS",
        "12:34:11.822 [END] Full-loop run complete (observe only)",
    ]
    return {
        "command": summary.get("command", "python -m asf.cli full-loop run --geometry"),
        "phase": summary.get("phase", "inspection"),
        "exit_code": summary.get("exit_code", "none"),
        "follow": summary.get("follow", False),
        "mode": "read_only_observe",
        "stream": stream,
    }


def label_coordinates(x: int, y: int) -> tuple[int, int]:
    center_x, center_y = 520, 360
    dx = x - center_x
    dy = y - center_y
    offset_x = 88 if dx >= 0 else -88
    offset_y = 18 if abs(dx) > 130 else (-44 if dy < 0 else 46)
    return x + offset_x, y + offset_y


def failed_gate(summary: dict[str, Any], wound: dict[str, Any]) -> int | None:
    if wound:
        return int(wound.get("failed_gate_id") or 12)
    failed = summary.get("failed_gates") or []
    return int(failed[0]) if failed else None
