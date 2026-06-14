# AI Survival Field Runtime

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
ASF-R v0.2 policy-as-code hardening: experimental production line.
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
    traces/
  docs/
    architecture.md
    adapter_safety.md
    authorization_receipts.md
    capability_tokens.md
    decision_replay.md
    governance_debt.md
    invariant_registry.md
    non_claim_lock.md
    operator_doctor.md
    origin_statement.md
    production_maturity.md
    rehydration_findings.md
    runtime_alignment_auditor.md
    self_healing_horizon.md
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

Adapters remain non-mutating by default. Live enforcement is reserved for
`ASF-R v0.3 Adapter Enforcement Dry Run`.

## Non-Claim Lock

```text
AI Survival Field Runtime does not prove truth.
AI Survival Field Runtime does not make AI safe.
AI Survival Field Runtime does not replace human judgment.
AI Survival Field Runtime governs continuation.
```
