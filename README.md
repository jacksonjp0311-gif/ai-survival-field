# AI Survival Field Runtime

[![ASF Guard](https://github.com/jacksonjp0311-gif/ai-survival-field/actions/workflows/asf-guard.yml/badge.svg)](https://github.com/jacksonjp0311-gif/ai-survival-field/actions/workflows/asf-guard.yml)

AI Survival Field Runtime, or ASF-R, is a governed continuation engine for
AI-generated and human-generated artifacts.

It does not prove truth.

It determines what an artifact is allowed to become.

ASF-R rehydrates the current proof state, maps the artifact through RCC Nexus,
validates the artifact survival field, applies policy, checks locks and gates,
emits wound packages for blocked propagation, records evidence, and renders the
runtime geometry for the operator.

Core rule:

```text
Rehydrate before reasoning.
Orient before action.
Validate before mutation.
Gate before promotion.
Package every wound.
Show the geometry.
```

Inherited SFT law:

```text
Validate before action.
Ceiling before claim.
Gate before promotion.
Block before drift.
```

Production ASF law:

```text
No rehydration, no action.
No orientation, no mutation.
No valid artifact, no durable state.
No cleared gate, no promotion.
No evidence, no authority.
No wound package, no repair claim.
```

## Status

```text
ASF-R v1.0-rc1 bounded production release candidate.
```

This repository is the production-oriented successor line to Survivor Field
Theory v1.4. The SFT repository remains the clean reference theory and
experimental validator. ASF-R is a separate runtime line for enforcement
adapters, evidence ledgers, wound packages, rehydration, RCC routing, and
operator-visible geometry.

## What This Version Proves

ASF-R v0.1 proves the first production step:

```text
A reference validator can become a runtime loop.
```

The loop is:

```text
artifact
-> rehydration report
-> RCC route
-> policy
-> guard decision
-> wound package when blocked
-> ledger record
-> operator geometry
```

ASF-R v0.2 proves that explicit policy controls continuation.

ASF-R v0.3 proves that adapters can observe proposed real-world actions, package
them into governance events, run the runtime loop, emit evidence, and simulate
enforcement without mutating state.

ASF-R v0.4 proves that controlled workflows can fail closed when blocked while
still performing no mutation.

ASF-R v0.5 proves that wounds can become bounded repair plans, repair dry-runs,
validation reports, and authorization requests without performing repair.

ASF-R v0.6 proves that repair plans can become replayable evidence without
performing repair, closing wounds, or granting authority.

ASF-R v0.7 proves that a human can authorize one bounded local repair plan for
allowlisted low-risk repair classes without granting general repair authority.

ASF-R v0.8 proves that wound closure can be requested, validated, and recorded
only against exact post-repair evidence without repair mutation or general
authority.

ASF-R v0.9 proves that the runtime can emit CI evidence, dogfood reports, and a
public demo path without expanding mutation authority.

ASF-R v0.9.2 seals current-head remote CI evidence for commit
`d6fe7ad2352fd789fb16a1d20ad76974dc41b1b2`.

ASF-R v1.0-rc1 does not add new authority. It packages the existing governed
recovery loop so it is installable, testable, documented, and reproducible.

Core v1.0 law:

```text
v1.0 does not expand authority.
v1.0 makes the existing loop installable, testable, documented, and reproducible.
```

## What This Version Does Not Claim

ASF-R does not:

- prove truth,
- make AI safe,
- replace human judgment,
- provide formal verification,
- provide production security by itself,
- authorize autonomous action without policy and human authorization.

A pass means the artifact earned bounded permission under the active policy.
A fail means propagation is blocked, downgraded, quarantined, or converted into a
wound package.

## Quick Start

Install editable:

```powershell
python -m pip install -e .
```

Run the one-command demo:

```powershell
python -m asf.cli demo
```

Run tests:

```powershell
python -m unittest discover tests
```

Validate a draft artifact:

```powershell
python -m asf.cli guard examples/artifacts/draft_allowed.json --action draft
```

Block a release with a missing gate:

```powershell
python -m asf.cli loop run examples/artifacts/release_blocked_missing_tests.json --action release
```

Render the operator UI:

```powershell
python -m asf.cli ui examples/artifacts/release_blocked_missing_tests.json --action release
```

Run the public demo:

```powershell
python -m asf.cli demo
```

Run dogfood:

```powershell
python -m asf.cli dogfood run
```

Verify the ledger record:

```powershell
python -m asf.cli ledger verify examples/decisions/block_decision.json
```

Run the operator doctor:

```powershell
python -m asf.cli doctor
```

Show invariant registry:

```powershell
python -m asf.cli invariants
```

Show governance debt:

```powershell
python -m asf.cli debt
```

Compare policies:

```powershell
python -m asf.cli policy diff policies/default.yaml policies/strict.json
```

Observe an adapter event:

```powershell
python -m asf.cli adapter observe examples/adapter_events/filesystem_write_blocked.json
```

Run adapter dry-run enforcement:

```powershell
python -m asf.cli adapter dry-run examples/adapter_events/filesystem_write_blocked.json
```

Run the loop in dry-run adapter mode:

```powershell
python -m asf.cli loop dry-run examples/artifacts/release_blocked_missing_tests.json --action release
```

Enforce a controlled block:

```powershell
python -m asf.cli enforce block-only examples/artifacts/release_blocked_missing_tests.json --action release
```

Run adapter block-only enforcement:

```powershell
python -m asf.cli adapter enforce-block-only examples/adapter_events/filesystem_write_blocked.json
```

Create a repair plan from a wound:

```powershell
python -m asf.cli repair plan examples/wounds/missing_gate_wound.json
```

Dry-run a repair plan:

```powershell
python -m asf.cli repair dry-run examples/repair_plans/missing_gate_repair_plan.json
```

Validate a repair plan:

```powershell
python -m asf.cli repair validate examples/repair_plans/missing_gate_repair_plan.json
```

Replay a repair plan:

```powershell
python -m asf.cli repair replay examples/repair_plans/missing_gate_repair_plan.json
```

Create a bounded repair authorization receipt:

```powershell
python -m asf.cli repair authorize examples/repair_plans/documentation_alignment_repair_plan.json --authorizer "James Paul Jackson"
```

Execute a bounded repair with a receipt:

```powershell
python -m asf.cli repair execute-bounded examples/repair_plans/documentation_alignment_repair_plan.json --authorization receipt.json
```

## Runtime Geometry

```text
ASFLOAD
-> load origin manifest
-> load latest state
-> load latest evidence
-> load active policy
-> load open wounds
-> produce rehydration report
-> RCC Nexus route
-> SFT-style guard
-> enforcement decision
-> wound package if blocked
-> evidence ledger record
-> geometric operator UI
```

## Directory

```text
ai-survival-field/
  README.md
  pyproject.toml
  asf/
    cli.py
    runtime.py
    core/
    rhp/
    rcc/
    wounds/
    ledger/
    ui/
    adapters/
  schemas/
  policies/
  examples/
    adapter_events/
    hermes_lessons/
    repair_plans/
    traces/
    wounds/
  docs/
    architecture.md
    adapter_dry_run.md
    adapter_event_model.md
    adapter_safety.md
    authorization_receipts.md
    capability_tokens.md
    controlled_enforcement_gate.md
    decision_replay.md
    evolution_readiness_gate.md
    enforce_block_only.md
    forward_progress_governor.md
    governance_debt.md
    github_actions_guard.md
    install.md
    invariant_registry.md
    non_claim_lock.md
    operator_doctor.md
    origin_statement.md
    production_maturity.md
    rehydration_findings.md
    repository_hygiene.md
    repair_dry_run_boundary.md
    repair_planner.md
    repair_validation.md
    runtime_alignment_auditor.md
    self_healing_horizon.md
    quickstart.md
    examples_walkthrough.md
    v1_0_release_criteria.md
    v1_0_non_claim_lock.md
    v0.3_dry_run_boundary.md
    releases/
  tests/
```

## v0.1.1 Evidence Seal

v0.1.1 seals the initial runtime loop before feature expansion.

It adds:

- invariant registry,
- decision replay,
- golden traces,
- runtime alignment auditor,
- adapter safety defaults,
- operator doctor,
- governance debt register,
- release seal manifest,
- expanded tests.

Core seal rule:

```text
Before expansion, seal the loop.
```

## v0.2 Policy-As-Code Hardening

v0.2 proves that explicit policy controls continuation.

It adds:

- policy diff engine,
- policy regression tests,
- capability tokens,
- authorization receipts,
- policy hash binding in decisions,
- policy hash binding in ledger records,
- active policy panel in geometric UI,
- v0.2 release seal.

Required laws:

```text
A policy change is a governance mutation.
Dangerous actions require scoped capability tokens.
Durable authority requires authorization receipts.
Same artifact plus different policy may produce different allowed continuation.
Unknown is still not pass.
No adapter may self-authorize.
```

Adapters remain non-mutating by default.

## v0.3 Adapter Enforcement Dry Run

v0.3 proves that ASF-R can reach the boundary of real-world action without
crossing into unsafe mutation.

It adds:

- adapter event model,
- enforcement report,
- dry-run mutation simulator,
- filesystem adapter dry-run surface,
- GitHub adapter dry-run surface,
- agent adapter dry-run surface,
- adapter mode enforcement,
- adapter event hash binding in the ledger,
- v0.3 release seal.

Core v0.3 law:

```text
Dry-run may reveal the shape of a repair or mutation.
Dry-run may not perform it.
```

v0.3 does not enable live mutation, live self-healing, production enforcement,
or autonomous authority. Live enforcement is reserved for `ASF-R v0.4 Controlled
Enforcement Gate`.

## v0.4 Controlled Enforcement Gate

v0.4 proves that ASF-R can fail closed in controlled workflows while remaining
non-mutating.

It adds:

- `enforce_block_only` adapter mode,
- block enforcer,
- block enforcement schema,
- CLI controlled block command,
- adapter block-only enforcement command,
- GitHub Actions guard template,
- v0.4 release seal.

Core v0.4 law:

```text
The system may enforce a block.
The system may not perform a mutation.
```

v0.4 does not enable `enforce_full`, live mutation, live repair, self-healing
mutation, repository writes, release creation, or memory promotion. The next
operation is `ASF-R v0.5 Repair Planner Dry Run`.

## v0.5 Repair Planner Dry Run

v0.5 converts wound packages into bounded repair plans and validates repair paths
without applying them.

It adds:

- Hermes lesson primitives,
- evolution readiness gate,
- forward progress governor,
- runtime geometry contract,
- repository hygiene guard,
- zero-context latest pointer,
- repair planner,
- repair dry-run,
- repair validation,
- repair report,
- v0.5 release seal.

Core v0.5 law:

```text
ASF-R may plan repair.
ASF-R may dry-run repair.
ASF-R may validate a proposed repair.
ASF-R may not perform or authorize repair.
```

v0.5 does not enable live mutation, repair execution, wound closure,
self-healing mutation, or `enforce_full`. The next operation is `ASF-R v0.6
Repair Validation Replay`.

## v0.6 Repair Validation Replay

v0.6 converts repair plans into replayable evidence.

It adds:

- latest-pointer alignment guard,
- repair replay report,
- repair replay CLI,
- repair replay schema,
- latest pointer alignment schema,
- v0.6 release seal.

Core v0.6 law:

```text
A repair plan is not a repair.
A repair replay is not wound closure.
```

v0.6 may prove repair-path coherence. It may not perform repair, close the wound,
grant authority, enable `enforce_full`, or enable self-healing mutation. The next
operation is `ASF-R v0.7 Human-Authorized Bounded Repair`.

## v0.7 Human-Authorized Bounded Repair

v0.7 permits one scoped, human-authorized bounded local repair for allowlisted
low-risk repair classes.

Allowed repair classes:

- documentation_alignment,
- latest_pointer_alignment,
- repository_hygiene_metadata,
- runtime_geometry_documentation_drift.

Core v0.7 law:

```text
Authorization may permit one bounded repair plan.
Authorization may not grant general repair authority.
Repair execution is not wound closure.
```

v0.7 does not enable autonomous repair, self-healing mutation, `enforce_full`,
wound closure, policy logic mutation, validator logic mutation, adapter
enforcement mutation, memory updates, releases, or external mutation APIs. The
next operation is `ASF-R v0.8 Controlled Wound Closure`.

## v0.8 Controlled Wound Closure

v0.8 separates repair from closure.

Core v0.8 law:

```text
A repaired wound is not a closed wound.
A wound may close only after post-repair evidence, replay, authorization, and closure-specific validation.
```

It adds:

- wound closure request,
- wound closure validation,
- wound closure record,
- closure schemas,
- closure CLI,
- v0.8 release seal.

Controlled closure requires exact wound identity, repair plan hash, repair replay
hash, repair execution hash, post-repair evidence hash, authorization receipt
hash, and closure-specific authorizer. It performs no repair mutation and grants
no general authority. The next operation is `ASF-R v0.9 Remote CI Evidence and
Dogfood`.

## v0.9 Remote CI Evidence and Dogfood

v0.9 adds public recoverability evidence.

Core v0.9 law:

```text
Local tests prove local coherence.
Remote CI proves recoverable public coherence.
Dogfooding proves operational contact.
```

It adds:

- CI evidence records,
- GitHub Actions evidence artifact upload,
- dogfood report,
- public demo command,
- v0.9 release seal.

v0.9 does not expand repair authority, enable autonomous repair, enable
self-healing mutation, or enable `enforce_full`. Remote CI status remains
`remote_pending` until GitHub Actions records a run.

## v1.0-rc1 Bounded Production Release Candidate

v1.0-rc1 is deliberately boring. It does not invent a new power or relax an
authority boundary. It packages the loop that already exists:

```text
wound
-> repair plan
-> dry-run
-> validation
-> replay
-> authorization
-> bounded repair
-> evidence
-> closure validation
-> closure record
```

It adds public-facing reproducibility surfaces:

- CI badge,
- editable install command,
- one-command demo,
- quickstart,
- examples walkthrough,
- release criteria,
- release-candidate non-claim lock,
- v0.9.2 current-head CI seal,
- v1.0-rc1 release seal.

Core v1.0 law:

```text
v1.0 does not expand authority.
v1.0 makes the existing loop installable, testable, documented, and reproducible.
```

v1.0-rc1 does not enable `enforce_full`, autonomous repair, self-healing
mutation, general repair authority, unscoped wound closure, live release
mutation, memory mutation, or external mutation APIs.

## Non-Claim Lock

```text
AI Survival Field Runtime does not prove truth.
AI Survival Field Runtime does not make AI safe.
AI Survival Field Runtime does not replace human judgment.
AI Survival Field Runtime governs continuation.
```
