from __future__ import annotations

import argparse
import json
from pathlib import Path

from asf.core.governance_debt import registry as governance_debt_registry
from asf.core.invariants import registry as invariant_registry
from asf.core.policy import load_policy
from asf.core.policy_diff import diff_policies
from asf.ledger.ledger import verify_record
from asf.ledger.replay import replay_decision
from asf.runtime import run_loop
from asf.ui.doctor import run_doctor


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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
