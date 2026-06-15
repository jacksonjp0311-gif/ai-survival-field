from __future__ import annotations

import argparse
import json
from pathlib import Path

from asf.adapters.block_enforcer import enforce_block_only, event_for_artifact
from asf.adapters.dry_run import simulate
from asf.adapters.event import AdapterEvent
from asf.adapters.enforcement_report import report_invariant_ok
from asf.core.governance_debt import registry as governance_debt_registry
from asf.core.invariants import registry as invariant_registry
from asf.core.policy import load_policy
from asf.core.policy_diff import diff_policies
from asf.ledger.ledger import verify_record
from asf.ledger.replay import replay_decision
from asf.repair.repair_dry_run import dry_run as repair_dry_run
from asf.repair.bounded_executor import execute_bounded
from asf.repair.repair_authorization import RepairAuthorizationReceipt, build_receipt
from asf.repair.repair_plan import RepairPlan
from asf.repair.repair_planner import plan_from_wound
from asf.repair.repair_report import build_report as build_repair_report
from asf.repair.repair_replay import replay_repair
from asf.repair.repair_validation import validate_plan
from asf.runtime import run_loop
from asf.ui.doctor import run_doctor
from asf.wounds.closure import WoundClosureRequest, build_closure_request, close_wound, validate_closure


def print_json(data: object) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def command_guard(args: argparse.Namespace) -> int:
    result = run_loop(args.artifact, action=args.action, policy_path=args.policy, operator_authorized=args.authorized)
    print_json(result["decision"])
    return 0 if result["decision"]["status"] == "pass" else 2


def command_loop_run(args: argparse.Namespace) -> int:
    result = run_loop(args.artifact, action=args.action, policy_path=args.policy, operator_authorized=args.authorized)
    print_json(result)
    return 0 if result["decision"]["status"] == "pass" else 2


def command_loop_dry_run(args: argparse.Namespace) -> int:
    result = run_loop(args.artifact, action=args.action, policy_path=args.policy, operator_authorized=args.authorized, adapter_mode="dry_run")
    print_json(result)
    return 0 if result["decision"]["status"] == "pass" else 2


def command_ui(args: argparse.Namespace) -> int:
    result = run_loop(args.artifact, action=args.action, policy_path=args.policy, operator_authorized=args.authorized)
    print(result["ui"])
    return 0 if result["decision"]["status"] == "pass" else 2


def command_ledger_verify(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.record).read_text(encoding="utf-8"))
    ok = verify_record(data)
    print_json({"ledger_record_ok": ok})
    return 0 if ok else 2


def command_doctor(args: argparse.Namespace) -> int:
    result = run_doctor(args.root)
    print_json(result)
    return 0 if result["ok"] else 2


def command_invariants(args: argparse.Namespace) -> int:
    print_json(invariant_registry())
    return 0


def command_debt(args: argparse.Namespace) -> int:
    print_json(governance_debt_registry())
    return 0


def command_replay(args: argparse.Namespace) -> int:
    report = replay_decision(
        args.artifact,
        action=args.action,
        expected_decision_hash=args.expected_decision_hash,
        policy_path=args.policy,
        root=args.root,
        operator_authorized=args.authorized,
    )
    print_json(report.as_dict())
    return 0 if report.replay_pass else 2


def command_policy_diff(args: argparse.Namespace) -> int:
    old = load_policy(args.old_policy)
    new = load_policy(args.new_policy)
    print_json(diff_policies(old, new).as_dict())
    return 0


def _load_event(path: str) -> AdapterEvent:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return AdapterEvent.from_dict(data)


def command_adapter_observe(args: argparse.Namespace) -> int:
    event = _load_event(args.event)
    print_json(event.as_dict())
    return 0


def command_adapter_dry_run(args: argparse.Namespace) -> int:
    event = _load_event(args.event)
    report = simulate(event, policy_path=args.policy, root=args.root)
    print_json(report.as_dict())
    return 0 if report_invariant_ok(report.as_dict()) else 2


def command_adapter_enforce_block_only(args: argparse.Namespace) -> int:
    event = _load_event(args.event)
    result = enforce_block_only(event, policy_path=args.policy, root=args.root)
    print_json(result.as_dict())
    return result.exit_code


def command_enforce_block_only(args: argparse.Namespace) -> int:
    event = event_for_artifact(args.artifact, args.action)
    result = enforce_block_only(event, policy_path=args.policy, root=args.root)
    print_json(result.as_dict())
    return result.exit_code


def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def command_repair_plan(args: argparse.Namespace) -> int:
    wound = _load_json(args.wound)
    plan = plan_from_wound(
        wound,
        source_decision_hash=args.source_decision_hash,
        source_policy_hash=args.source_policy_hash,
        source_ledger_hash=args.source_ledger_hash,
    )
    print_json(plan.as_dict())
    return 0


def command_repair_dry_run(args: argparse.Namespace) -> int:
    plan = RepairPlan.from_dict(_load_json(args.repair_plan))
    print_json(repair_dry_run(plan).as_dict())
    return 0


def command_repair_validate(args: argparse.Namespace) -> int:
    plan = RepairPlan.from_dict(_load_json(args.repair_plan))
    validation = validate_plan(plan)
    print_json(validation.as_dict())
    return 0 if validation.valid else 2


def command_repair_report(args: argparse.Namespace) -> int:
    plan = RepairPlan.from_dict(_load_json(args.repair_plan))
    dry = repair_dry_run(plan)
    validation = validate_plan(plan)
    print_json(build_repair_report(plan, dry, validation).as_dict())
    return 0 if validation.valid else 2


def command_repair_replay(args: argparse.Namespace) -> int:
    plan = RepairPlan.from_dict(_load_json(args.repair_plan))
    report = replay_repair(plan, expected_repair_plan_hash=args.expected_repair_plan_hash)
    print_json(report.as_dict())
    return 0 if report.replay_pass else 2


def command_repair_authorize(args: argparse.Namespace) -> int:
    plan = RepairPlan.from_dict(_load_json(args.repair_plan))
    receipt = build_receipt(plan, human_authorizer=args.authorizer, allowed_paths=args.allowed_path)
    print_json(receipt.as_dict())
    return 0


def command_repair_execute_bounded(args: argparse.Namespace) -> int:
    plan = RepairPlan.from_dict(_load_json(args.repair_plan))
    receipt = RepairAuthorizationReceipt.from_dict(_load_json(args.authorization))
    result = execute_bounded(plan, receipt, root=args.root, target_path=args.target_path, content=args.content)
    print_json(result.as_dict())
    return 0 if result.status == "applied" else 2


def command_repair_evidence(args: argparse.Namespace) -> int:
    report = _load_json(args.execution_report)
    print_json(report.get("evidence") or {"found": False, "non_claim_lock": "Evidence display grants no repair authority."})
    return 0 if report.get("evidence") else 2


def command_wound_closure_request(args: argparse.Namespace) -> int:
    execution = _load_json(args.execution_report)
    request = build_closure_request(execution, wound_id=args.wound_id, closure_authorizer=args.authorizer)
    print_json(request.as_dict())
    return 0


def command_wound_closure_validate(args: argparse.Namespace) -> int:
    request = WoundClosureRequest.from_dict(_load_json(args.closure_request))
    execution = _load_json(args.execution_report)
    validation = validate_closure(request, execution)
    print_json(validation.as_dict())
    return 0 if validation.valid else 2


def command_wound_closure_close(args: argparse.Namespace) -> int:
    request = WoundClosureRequest.from_dict(_load_json(args.closure_request))
    execution = _load_json(args.execution_report)
    try:
        record = close_wound(request, execution)
    except ValueError as exc:
        print_json({"closed": False, "failures": str(exc).split(","), "non_claim_lock": "Failed closure grants no authority."})
        return 2
    print_json(record.as_dict())
    return 0


def command_adapter_report(args: argparse.Namespace) -> int:
    path = Path(args.report_id)
    if path.is_file():
        print(path.read_text(encoding="utf-8"))
        return 0
    print_json({"report_id": args.report_id, "found": False, "non_claim_lock": "Report lookup is read-only and grants no authority."})
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Survival Field Runtime")
    sub = parser.add_subparsers(dest="command", required=True)

    guard = sub.add_parser("guard")
    guard.add_argument("artifact")
    guard.add_argument("--action", required=True)
    guard.add_argument("--policy", default="policies/default.yaml")
    guard.add_argument("--authorized", action="store_true", default=True)
    guard.set_defaults(func=command_guard)

    loop = sub.add_parser("loop")
    loop_sub = loop.add_subparsers(dest="loop_command", required=True)
    run = loop_sub.add_parser("run")
    run.add_argument("artifact")
    run.add_argument("--action", required=True)
    run.add_argument("--policy", default="policies/default.yaml")
    run.add_argument("--authorized", action="store_true", default=True)
    run.set_defaults(func=command_loop_run)

    dry_run = loop_sub.add_parser("dry-run")
    dry_run.add_argument("artifact")
    dry_run.add_argument("--action", required=True)
    dry_run.add_argument("--policy", default="policies/default.yaml")
    dry_run.add_argument("--authorized", action="store_true", default=True)
    dry_run.set_defaults(func=command_loop_dry_run)

    ui = sub.add_parser("ui")
    ui.add_argument("artifact")
    ui.add_argument("--action", required=True)
    ui.add_argument("--policy", default="policies/default.yaml")
    ui.add_argument("--authorized", action="store_true", default=True)
    ui.set_defaults(func=command_ui)

    ledger = sub.add_parser("ledger")
    ledger_sub = ledger.add_subparsers(dest="ledger_command", required=True)
    verify = ledger_sub.add_parser("verify")
    verify.add_argument("record")
    verify.set_defaults(func=command_ledger_verify)

    doctor = sub.add_parser("doctor")
    doctor.add_argument("--root", default=".")
    doctor.set_defaults(func=command_doctor)

    invariants = sub.add_parser("invariants")
    invariants.set_defaults(func=command_invariants)

    debt = sub.add_parser("debt")
    debt.set_defaults(func=command_debt)

    replay = sub.add_parser("replay")
    replay.add_argument("artifact")
    replay.add_argument("--action", required=True)
    replay.add_argument("--expected-decision-hash", required=True)
    replay.add_argument("--policy", default="policies/default.yaml")
    replay.add_argument("--root", default=".")
    replay.add_argument("--authorized", action="store_true", default=True)
    replay.set_defaults(func=command_replay)

    policy = sub.add_parser("policy")
    policy_sub = policy.add_subparsers(dest="policy_command", required=True)
    diff = policy_sub.add_parser("diff")
    diff.add_argument("old_policy")
    diff.add_argument("new_policy")
    diff.set_defaults(func=command_policy_diff)

    enforce = sub.add_parser("enforce")
    enforce_sub = enforce.add_subparsers(dest="enforce_command", required=True)
    block_only = enforce_sub.add_parser("block-only")
    block_only.add_argument("artifact")
    block_only.add_argument("--action", required=True)
    block_only.add_argument("--policy", default="policies/default.yaml")
    block_only.add_argument("--root", default=".")
    block_only.set_defaults(func=command_enforce_block_only)

    repair = sub.add_parser("repair")
    repair_sub = repair.add_subparsers(dest="repair_command", required=True)
    repair_plan = repair_sub.add_parser("plan")
    repair_plan.add_argument("wound")
    repair_plan.add_argument("--source-decision-hash", default="source-decision-hash-required")
    repair_plan.add_argument("--source-policy-hash", default="source-policy-hash-required")
    repair_plan.add_argument("--source-ledger-hash", default="")
    repair_plan.set_defaults(func=command_repair_plan)
    repair_dry = repair_sub.add_parser("dry-run")
    repair_dry.add_argument("repair_plan")
    repair_dry.set_defaults(func=command_repair_dry_run)
    repair_validate = repair_sub.add_parser("validate")
    repair_validate.add_argument("repair_plan")
    repair_validate.set_defaults(func=command_repair_validate)
    repair_report = repair_sub.add_parser("report")
    repair_report.add_argument("repair_plan")
    repair_report.set_defaults(func=command_repair_report)
    repair_replay = repair_sub.add_parser("replay")
    repair_replay.add_argument("repair_plan")
    repair_replay.add_argument("--expected-repair-plan-hash", default=None)
    repair_replay.set_defaults(func=command_repair_replay)
    repair_authorize = repair_sub.add_parser("authorize")
    repair_authorize.add_argument("repair_plan")
    repair_authorize.add_argument("--authorizer", required=True)
    repair_authorize.add_argument("--allowed-path", action="append", default=["docs"])
    repair_authorize.set_defaults(func=command_repair_authorize)
    repair_execute = repair_sub.add_parser("execute-bounded")
    repair_execute.add_argument("repair_plan")
    repair_execute.add_argument("--authorization", required=True)
    repair_execute.add_argument("--root", default=".")
    repair_execute.add_argument("--target-path", default="docs/repair_notes.md")
    repair_execute.add_argument("--content", default="bounded repair evidence\n")
    repair_execute.set_defaults(func=command_repair_execute_bounded)
    repair_evidence = repair_sub.add_parser("evidence")
    repair_evidence.add_argument("execution_report")
    repair_evidence.set_defaults(func=command_repair_evidence)

    wound = sub.add_parser("wound")
    wound_sub = wound.add_subparsers(dest="wound_command", required=True)
    closure = wound_sub.add_parser("closure")
    closure_sub = closure.add_subparsers(dest="closure_command", required=True)
    closure_request = closure_sub.add_parser("request")
    closure_request.add_argument("execution_report")
    closure_request.add_argument("--wound-id", required=True)
    closure_request.add_argument("--authorizer", required=True)
    closure_request.set_defaults(func=command_wound_closure_request)
    closure_validate = closure_sub.add_parser("validate")
    closure_validate.add_argument("closure_request")
    closure_validate.add_argument("--execution-report", required=True)
    closure_validate.set_defaults(func=command_wound_closure_validate)
    closure_close = closure_sub.add_parser("close")
    closure_close.add_argument("closure_request")
    closure_close.add_argument("--execution-report", required=True)
    closure_close.set_defaults(func=command_wound_closure_close)

    adapter = sub.add_parser("adapter")
    adapter_sub = adapter.add_subparsers(dest="adapter_command", required=True)
    observe = adapter_sub.add_parser("observe")
    observe.add_argument("event")
    observe.set_defaults(func=command_adapter_observe)
    dry = adapter_sub.add_parser("dry-run")
    dry.add_argument("event")
    dry.add_argument("--policy", default="policies/default.yaml")
    dry.add_argument("--root", default=".")
    dry.set_defaults(func=command_adapter_dry_run)
    enforce_block = adapter_sub.add_parser("enforce-block-only")
    enforce_block.add_argument("event")
    enforce_block.add_argument("--policy", default="policies/default.yaml")
    enforce_block.add_argument("--root", default=".")
    enforce_block.set_defaults(func=command_adapter_enforce_block_only)
    report = adapter_sub.add_parser("report")
    report.add_argument("report_id")
    report.set_defaults(func=command_adapter_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
