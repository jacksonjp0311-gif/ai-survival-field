# ASF-R Triadic Geometry Console

The ASF-R Triadic Geometry Console is a local read-only neon gate surface for
observing the governed runtime loop.

It is not a control panel.

v1.1.0-dev1 evolves the surface toward the product-grade target:

- top header badges,
- left gate legend,
- labeled 25-gate neon triadic loop,
- live CLI stream panel,
- red wound/failure package panel,
- bottom status cards,
- `GET /events` Server-Sent Events stream,
- no mutation endpoints.

It opens beside the full loop, follows runtime state, lights every gate in the
path, and surfaces wound/failure packages when propagation is blocked.

```text
The geometry shows the loop.
The CLI shows the runtime trace.
The wound package shows the consequence.
```

## Read-Only UI Law

```text
The UI may observe.
The UI may illuminate.
The UI may follow runtime state.
The UI may render gates, wounds, evidence, and traces.
The UI may not authorize repair.
The UI may not execute mutation.
The UI may not close wounds.
The UI may not mutate policy.
The UI may not write memory.
The UI may not enable enforce_full.
The UI may not grant authority.
```

## Triadic Geometry

```text
Evidence / Rehydration
Governance / Coherence
Action / Recovery
```

Gate colors:

```text
Green = pass
Red = blocked/fail
Amber = active/pending
Cyan = read-only evidence
Gray = inactive
Deep red lock = forbidden
```

## Gate Labels

1. Latest Pointer Loaded
2. Rehydration Passed
3. Release Seal Loaded
4. Repository Truth Aligned
5. CI Evidence Loaded
6. Ledger Verify
7. Policy Loaded
8. Invariants Loaded
9. Claim Ceiling Assigned
10. Artifact Validated
11. Decision Computed
12. Permission Checked
13. Non-Claim Lock Preserved
14. Block Enforcement Checked
15. Wound Emitted
16. Repair Plan Created
17. Repair Dry-Run Passed
18. Repair Validation Passed
19. Repair Replay Passed
20. Authorization Bound
21. Bounded Repair Executed
22. Post-Repair Evidence Captured
23. Closure Request Created
24. Closure Validation Passed
25. Closure Record Written

## Full Loop Runners

PowerShell:

```powershell
cd C:\Users\jacks\OneDrive\Desktop\ai-survival-field
.\scripts\run-asf-full-loop.ps1
```

PowerShell with geometry flag:

```powershell
cd C:\Users\jacks\OneDrive\Desktop\ai-survival-field
.\scripts\run-asf-full-loop.ps1 -Geometry
```

Bash:

```bash
cd ~/ai-survival-field
./scripts/run-asf-full-loop.sh
```

Bash with geometry flag:

```bash
cd ~/ai-survival-field
./scripts/run-asf-full-loop.sh --geometry
```

## Non-Claim Lock

ASF-R Triadic Geometry Console does not prove truth. It does not make AI safe,
provide formal verification, provide production security, authorize autonomous
action, or grant repair authority. It observes and illuminates the governed loop
only.
