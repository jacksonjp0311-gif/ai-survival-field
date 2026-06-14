from __future__ import annotations

import argparse
import json
from pathlib import Path

from asf.ledger.ledger import verify_record
from asf.runtime import run_loop


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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

