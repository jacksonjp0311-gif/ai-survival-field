# Controlled Enforcement Gate

ASF-R v0.4 introduces controlled block enforcement.

The runtime may now fail closed in controlled workflows when a proposed
continuation is blocked by policy, missing gates, authorization, or evidence.

It still may not mutate.

Core law:

```text
The system may enforce a block.
The system may not perform a mutation.
```

This is the bridge between adapter dry-run and future bounded enforcement. The
gate proves that ASF-R can stop unsafe continuation while preserving all v0.3
non-mutation boundaries.

Blocked enforcement must emit:

- enforcement report,
- wound package,
- ledger record,
- UI status,
- nonzero exit code.

Passing enforcement may return zero only inside the active policy boundary.

## Non-Claim Lock

Controlled block enforcement is not repair, production safety, formal
verification, or truth. It is a bounded fail-closed decision under active policy.
