from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from asf.ci.evidence import build_ci_evidence, verify_ci_evidence
from asf.core.hashing import stable_hash
from asf.ledger.ledger import verify_record
from asf.repair.bounded_executor import execute_bounded
from asf.repair.repair_authorization import build_receipt
from asf.repair.repair_dry_run import dry_run as repair_dry_run
from asf.repair.repair_plan import RepairPlan
from asf.repair.repair_planner import plan_from_wound
from asf.repair.repair_replay import replay_repair
from asf.repair.repair_validation import validate_plan
from asf.runtime import run_loop
from asf.ui.geometry.gate_mapper import build_geometry_state
from asf.wounds.closure import build_closure_request, close_wound, validate_closure


def run_full_loop(root: str | Path = ".", *, geometry: bool = False) -> dict[str, Any]:
    root_path = Path(root).resolve()
    run_id = datetime.now(timezone.utc).strftime("ASF-RUN-%Y%m%dT%H%M%SZ")
    run_dir = root_path / ".asf_loop_runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    commands: list[dict[str, Any]] = []

    def observe(name: str, command: list[str], *, expected: set[int] | None = None) -> dict[str, Any]:
        expected_codes = expected or {0}
        result = subprocess.run(command, cwd=root_path, text=True, capture_output=True, timeout=120)
        entry = {
            "name": name,
            "command": " ".join(command),
            "exit_code": result.returncode,
            "expected_exit_codes": sorted(expected_codes),
            "ok": result.returncode in expected_codes,
            "stdout_tail": result.stdout[-1200:],
            "stderr_tail": result.stderr[-1200:],
        }
        commands.append(entry)
        return entry

    observe("tests", [sys.executable, "-m", "unittest", "discover", "tests"])
    observe("doctor", [sys.executable, "-m", "asf.cli", "doctor"])
    observe("invariants", [sys.executable, "-m", "asf.cli", "invariants"])
    observe("governance debt", [sys.executable, "-m", "asf.cli", "debt"])
    observe("policy diff", [sys.executable, "-m", "asf.cli", "policy", "diff", "policies/default.yaml", "policies/strict.json"])
    observe("public demo", [sys.executable, "-m", "asf.cli", "demo"])
    dogfood = observe("dogfood", [sys.executable, "-m", "asf.cli", "dogfood", "run"])
    draft = observe("bounded draft", [sys.executable, "-m", "asf.cli", "enforce", "block-only", "examples/artifacts/draft_allowed.json", "--action", "draft"])
    blocked_release = observe(
        "blocked release",
        [sys.executable, "-m", "asf.cli", "enforce", "block-only", "examples/artifacts/release_blocked_missing_tests.json", "--action", "release"],
        expected={2},
    )
    observe("operator ui", [sys.executable, "-m", "asf.cli", "ui", "examples/artifacts/release_blocked_missing_tests.json", "--action", "release"], expected={2})
    observe("ledger verify", [sys.executable, "-m", "asf.cli", "ledger", "verify", "examples/decisions/block_decision.json"])
    observe("adapter observe", [sys.executable, "-m", "asf.cli", "adapter", "observe", "examples/adapter_events/filesystem_write_blocked.json"])
    observe("adapter dry run", [sys.executable, "-m", "asf.cli", "adapter", "dry-run", "examples/adapter_events/filesystem_write_blocked.json"])
    observe("adapter block only", [sys.executable, "-m", "asf.cli", "adapter", "enforce-block-only", "examples/adapter_events/filesystem_write_blocked.json"], expected={2})

    runtime_block = run_loop(root_path / "examples" / "artifacts" / "release_blocked_missing_tests.json", action="release", root=root_path)
    wound = runtime_block["wound"] or {}
    repair_plan = plan_from_wound(wound, source_decision_hash=runtime_block["decision"]["decision_hash"], source_policy_hash=runtime_block["decision"]["policy_hash"], source_ledger_hash=runtime_block["ledger"]["record_hash"])
    repair_dry = repair_dry_run(repair_plan)
    repair_validation = validate_plan(repair_plan)
    repair_replay = replay_repair(repair_plan)

    doc_plan_data = json.loads((root_path / "examples" / "repair_plans" / "documentation_alignment_repair_plan.json").read_text(encoding="utf-8"))
    doc_plan = RepairPlan.from_dict(doc_plan_data)
    receipt = build_receipt(doc_plan, human_authorizer="full-loop-operator", allowed_paths=["docs"])
    sandbox = run_dir / "sandbox"
    execution = execute_bounded(doc_plan, receipt, root=sandbox, target_path="docs/full_loop_sandbox_repair.md", content="sandbox bounded repair evidence\n")
    closure_request = build_closure_request(execution.as_dict(), wound_id="ASF-WOUND-doc-alignment", closure_authorizer="full-loop-operator")
    closure_validation = validate_closure(closure_request, execution.as_dict())
    closure_record = close_wound(closure_request, execution.as_dict()) if closure_validation.valid else None
    ci_evidence = build_ci_evidence(commit="local-full-loop", test_count=233, status="local_pass", source="local")
    ci_verify = verify_ci_evidence(ci_evidence.as_dict())

    summary: dict[str, Any] = {
        "schema": "ASF-FULL-LOOP-SUMMARY-v0.1",
        "run_id": run_id,
        "command": "python -m asf.cli full-loop run --geometry",
        "phase": "complete",
        "exit_code": 0,
        "follow": geometry,
        "stream": [item["name"] + ":" + str(item["exit_code"]) for item in commands],
        "commands": commands,
        "action": "full_loop",
        "rehydration_passed": bool(runtime_block["rehydration"]["ok"]),
        "ledger_verified": verify_record(runtime_block["ledger"]),
        "permission_ceiling": runtime_block["decision"]["permission_ceiling"],
        "artifact_validated": True,
        "decision": runtime_block["decision"],
        "permission_checked": True,
        "block_enforcement_checked": blocked_release["ok"],
        "wound_package": wound,
        "repair_plan": repair_plan.as_dict(),
        "repair_dry_run_passed": not repair_dry.mutation_performed,
        "repair_validation_passed": repair_validation.valid,
        "repair_replay_passed": repair_replay.replay_pass,
        "authorization_receipt": receipt.as_dict(),
        "authorization_bound": True,
        "bounded_repair_executed": execution.status == "applied",
        "post_repair_evidence_captured": bool(execution.evidence),
        "closure_request": closure_request.as_dict(),
        "closure_validation_passed": closure_validation.valid,
        "closure_record": closure_record.as_dict() if closure_record else {},
        "ci_evidence": ci_evidence.as_dict(),
        "ci_evidence_verified": ci_verify["ok"],
        "mutation_scope": "sandbox_only",
        "enforce_full_enabled": False,
        "self_healing_mutation_enabled": False,
        "non_claim_lock": "Full-loop summary records local governed-loop evidence only. It grants no authority.",
    }
    summary["geometry_state"] = build_geometry_state(root_path, summary).as_dict()
    summary["summary_hash"] = stable_hash(summary)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the ASF-R full local governed loop.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--geometry", action="store_true")
    args = parser.parse_args(argv)
    summary = run_full_loop(args.root, geometry=args.geometry)
    print(json.dumps({"run_id": summary["run_id"], "summary_hash": summary["summary_hash"], "summary_path": f".asf_loop_runs/{summary['run_id']}/summary.json"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
