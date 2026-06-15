# Examples Walkthrough

ASF-R v1.0-rc1 keeps the examples small and reproducible.

## Bounded Draft

```powershell
python -m asf.cli guard examples/artifacts/draft_allowed.json --action draft
```

Expected continuation: permitted bounded draft.

## Blocked Release

```powershell
python -m asf.cli enforce block-only examples/artifacts/release_blocked_missing_tests.json --action release
```

Expected continuation: controlled block with exit code `2`.

## Wound

```powershell
python -m asf.cli repair plan examples/wounds/missing_gate_wound.json
```

Expected continuation: repair plan proposal only.

## Repair Plan

```powershell
python -m asf.cli repair dry-run examples/repair_plans/missing_gate_repair_plan.json
python -m asf.cli repair validate examples/repair_plans/missing_gate_repair_plan.json
python -m asf.cli repair replay examples/repair_plans/missing_gate_repair_plan.json
```

Expected continuation: dry-run, validation, and replay evidence without repair
execution.

## Closure

Closure is intentionally stricter than repair. It requires exact post-repair
evidence, closure-specific validation, and a closure authorizer.

## Non-Claim Lock

Examples are runnable governance fixtures. They do not claim production
readiness, security certification, or general repair authority.
