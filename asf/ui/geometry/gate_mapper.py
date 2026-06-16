from __future__ import annotations

import math
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

GEOMETRY_CENTER = {"x": 490, "y": 345}
GATE_ORBIT_RADIUS = 245
TRIANGLE_RADIUS = 185
CORE_RADIUS = 64
GATE_NODE_RADIUS = 17
LABEL_RADIUS = GATE_ORBIT_RADIUS + 42
ANGLE_STEP = 360 / 25
START_ANGLE = -130
ANGLE_DIRECTION = -1

LABEL_LINES = {
    "Latest Pointer Loaded": ["Latest Pointer", "Loaded"],
    "Rehydration Passed": ["Rehydration", "Passed"],
    "Release Seal Loaded": ["Release Seal", "Loaded"],
    "Repository Truth Aligned": ["Repository Truth", "Aligned"],
    "CI Evidence Loaded": ["CI Evidence", "Loaded"],
    "Ledger Verify": ["Ledger", "Verify"],
    "Policy Loaded": ["Policy", "Loaded"],
    "Invariants Loaded": ["Invariants", "Loaded"],
    "Claim Ceiling Assigned": ["Claim Ceiling", "Assigned"],
    "Artifact Validated": ["Artifact", "Validated"],
    "Decision Computed": ["Decision", "Computed"],
    "Permission Checked": ["Permission", "Checked"],
    "Non-Claim Lock Preserved": ["Non-Claim Lock", "Preserved"],
    "Block Enforcement Checked": ["Block Enforcement", "Checked"],
    "Wound Emitted": ["Wound", "Emitted"],
    "Repair Plan Created": ["Repair Plan", "Created"],
    "Repair Dry-Run Passed": ["Repair Dry-Run", "Passed"],
    "Repair Validation Passed": ["Repair Validation", "Passed"],
    "Repair Replay Passed": ["Repair Replay", "Passed"],
    "Authorization Bound": ["Authorization", "Bound"],
    "Bounded Repair Executed": ["Bounded Repair", "Executed"],
    "Post-Repair Evidence Captured": ["Post-Repair Evidence", "Captured"],
    "Closure Request Created": ["Closure Request", "Created"],
    "Closure Validation Passed": ["Closure Validation", "Passed"],
    "Closure Record Written": ["Closure Record", "Written"],
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
    closure_status = resolve_closure_status(summary, wound, closure)
    panel = wound_panel(wound, decision, closure_status)
    trace = trace_state(gates, panel, closure_status)
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
        "closure_status": closure_status,
        "ci_evidence_status": pointer.get("remote_ci_status", "unknown"),
        "non_claim_lock": pointer.get("non_claim_lock", NON_CLAIM_LOCK),
    }
    return GeometryState(
        schema="ASF-TRIADIC-GEOMETRY-STATE-v0.1",
        console_name="ASF-R Triadic Geometry Console",
        mode="read_only_observe",
        vertices=VERTICES,
        geometry=geometry_metadata(),
        legend=LEGEND,
        gates=[gate.as_dict() for gate in gates],
        wound_panel=panel,
        status_strip=status_strip,
        cli_panel=cli_panel(summary),
        read_only_law=READ_ONLY_UI_LAW,
        non_claim_lock=NON_CLAIM_LOCK,
        failed_gate_id=trace.get("failed_gate_id"),
        wound_source_node=trace.get("wound_source_node"),
        trace=trace,
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
    wound = summary.get("wound_package") or summary.get("wound") or {}
    decision = summary.get("decision") or {}
    failed = set(summary.get("failed_gates", []))
    if wound_source(wound, decision) == "missing_gate":
        failed.discard(12)
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
        angle = gate_angle(gate_id)
        x, y = orbit_point(angle, GATE_ORBIT_RADIUS)
        label_x, label_y = label_point(angle, gate_id)
        anchor = label_anchor(angle)
        real_failed_gate_id = failed_gate(summary, summary.get("wound_package") or summary.get("wound") or {}, summary.get("decision") or {})
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
            angle_deg=round(angle, 3),
            label_anchor=anchor,
            label_lines=LABEL_LINES.get(label, [label]),
            failed=status in {"blocked", "fail"},
            wound_linked=gate_id == real_failed_gate_id and status in {"blocked", "fail"},
        ))
    return gates


def wound_panel(wound: dict[str, Any], decision: dict[str, Any], closure_status: str | None = None) -> dict[str, Any]:
    if not wound:
        return {"status": "read_only", "message": "NO ACTIVE WOUND"}
    failure_class = wound.get("wound_class", decision.get("status", "unknown"))
    source = wound_source(wound, decision)
    failed_gate_id = failed_gate_from_source(wound, decision)
    return {
        "status": "blocked",
        "record_label": "ARCHIVED WOUND RECORD" if closure_status == "closed" else "WOUND PACKAGE",
        "badge_label": "ARCHIVED MISSING GATE CHECK" if closure_status == "closed" and source == "missing_gate" else "",
        "wound_id": wound.get("wound_id", "unknown"),
        "failed_gate": "Missing Gate Check" if source == "missing_gate" else wound.get("failed_gate", "Runtime Gate"),
        "failed_gate_id": failed_gate_id,
        "failure_class": failure_class,
        "decision": decision.get("status", "blocked"),
        "wound_source": source,
        "trace_source": "synthetic_wound_source" if failed_gate_id is None else "failed_gate",
        "permission_ceiling": decision.get("permission_ceiling", "unknown"),
        "blocked_actions": decision.get("blocked_actions", wound.get("blocked_actions", [])),
        "permitted_actions": decision.get("permitted_actions", wound.get("permitted_actions", [])),
        "recommended_repair_path": wound.get("next_admissible_action", decision.get("next_admissible_action", "request_evidence")),
        "repair_plan_status": "available",
        "closure_status": closure_status or "not closed",
    }


def cli_panel(summary: dict[str, Any]) -> dict[str, Any]:
    panel_state = cli_panel_state(summary)
    titles = {
        "active_run": "LIVE CLI RUN",
        "last_run_trace": "LAST RUN TRACE",
        "no_active_run": "NO ACTIVE RUN",
    }
    stream = summary.get("stream") or []
    if panel_state == "no_active_run":
        stream = ["waiting for full-loop run..."]
    return {
        "title": titles[panel_state],
        "panel_state": panel_state,
        "command": summary.get("command", "python -m asf.cli full-loop run --geometry"),
        "phase": summary.get("phase", "waiting" if panel_state == "no_active_run" else "complete"),
        "exit_code": summary.get("exit_code", "none"),
        "follow": summary.get("follow", panel_state == "active_run"),
        "mode": "read_only_observe",
        "stream": stream,
    }


def cli_panel_state(summary: dict[str, Any]) -> str:
    if not summary:
        return "no_active_run"
    exit_code = summary.get("exit_code")
    if summary.get("phase") == "complete" or exit_code not in (None, "", "none"):
        return "last_run_trace"
    return "active_run"


def gate_angle(gate_id: int) -> float:
    return START_ANGLE + (gate_id - 1) * ANGLE_DIRECTION * ANGLE_STEP


def orbit_point(angle_deg: float, radius: float) -> tuple[int, int]:
    theta = math.radians(angle_deg)
    return (
        round(GEOMETRY_CENTER["x"] + radius * math.cos(theta)),
        round(GEOMETRY_CENTER["y"] + radius * math.sin(theta)),
    )


def label_anchor(angle_deg: float) -> str:
    cosine = math.cos(math.radians(angle_deg))
    if cosine > 0.35:
        return "start"
    if cosine < -0.35:
        return "end"
    return "middle"


def label_point(angle_deg: float, gate_id: int | None = None) -> tuple[int, int]:
    normalized = normalize_angle(angle_deg)
    sine = math.sin(math.radians(angle_deg))
    radius = LABEL_RADIUS
    y_offset = 0
    if -125 <= normalized <= -55:
        radius = GATE_ORBIT_RADIUS + 72
        y_offset = -10 if (gate_id or 0) % 2 else -24
    elif sine < -0.65:
        radius = LABEL_RADIUS + 26
    x, y = orbit_point(angle_deg, radius)
    return x, y + y_offset


def normalize_angle(angle_deg: float) -> float:
    return ((angle_deg + 180) % 360) - 180


TRIANGLE_VERTICES = {
    "top": orbit_point(-90, TRIANGLE_RADIUS),
    "left": orbit_point(150, TRIANGLE_RADIUS),
    "right": orbit_point(30, TRIANGLE_RADIUS),
}


def geometry_metadata() -> dict[str, Any]:
    return {
        "center_x": GEOMETRY_CENTER["x"],
        "center_y": GEOMETRY_CENTER["y"],
        "gate_orbit_radius": GATE_ORBIT_RADIUS,
        "triangle_radius": TRIANGLE_RADIUS,
        "core_radius": CORE_RADIUS,
        "gate_node_radius": GATE_NODE_RADIUS,
        "label_radius": LABEL_RADIUS,
        "angle_step": ANGLE_STEP,
        "start_angle": START_ANGLE,
        "angle_direction": ANGLE_DIRECTION,
        "triangle_vertices": {
            key: {"x": value[0], "y": value[1]}
            for key, value in TRIANGLE_VERTICES.items()
        },
    }


def failed_gate(summary: dict[str, Any], wound: dict[str, Any], decision: dict[str, Any] | None = None) -> int | None:
    decision = decision or {}
    if wound:
        if wound_source(wound, decision) == "missing_gate":
            return None
        gate_id = wound.get("failed_gate_id")
        return int(gate_id) if gate_id else None
    failed = summary.get("failed_gates") or []
    return int(failed[0]) if failed else None


def wound_source(wound: dict[str, Any], decision: dict[str, Any]) -> str:
    status = decision.get("status") or wound.get("wound_class") or ""
    if status == "missing_gate_failed" or wound.get("wound_class") == "missing_gate_failed":
        return "missing_gate"
    if wound.get("failed_gate_id"):
        return "gate"
    return "generic_wound"


def failed_gate_from_source(wound: dict[str, Any], decision: dict[str, Any]) -> int | None:
    source = wound_source(wound, decision)
    if source == "missing_gate":
        return None
    gate_id = wound.get("failed_gate_id")
    return int(gate_id) if gate_id else None


def resolve_closure_status(summary: dict[str, Any], wound: dict[str, Any], closure_record: dict[str, Any]) -> str:
    if closure_record and closure_record.get("wound_closed") is True:
        return "closed"
    if wound:
        return "not closed"
    return "none"


def trace_state(gates: list[GeometryGate], panel: dict[str, Any], closure_status: str) -> dict[str, Any]:
    if panel.get("status") != "blocked":
        return {"visible": False, "mode": "hidden", "display": "none", "source": "none", "failed_gate_id": None}
    mode = "archived" if closure_status == "closed" else "active"
    display = "collapsed" if mode == "archived" else "full"
    real_gate_id = panel.get("failed_gate_id")
    if real_gate_id is not None:
        gate = next((item for item in gates if item.gate_id == real_gate_id), None)
        if gate and gate.failed:
            return {
                "visible": True,
                "mode": mode,
                "display": display,
                "source": "failed_gate",
                "failed_gate_id": real_gate_id,
                "wound_source_node": None,
            }
    node = synthetic_wound_source_node(panel.get("wound_source", "generic_wound"))
    return {
        "visible": True,
        "mode": mode,
        "display": display,
        "source": "synthetic_wound_source",
        "failed_gate_id": None,
        "wound_source_node": node,
    }


def synthetic_wound_source_node(source: str) -> dict[str, Any]:
    label = "Missing Gate" if source == "missing_gate" else "Wound Source"
    return {
        "id": f"{source}_source",
        "label": label,
        "status": "blocked",
        "x": 760,
        "y": 474,
        "visible": True,
    }
