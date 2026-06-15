# Evolution Readiness Gate

The evolution readiness gate classifies whether a requested ASF-R operation is
legal under current evidence.

Core law:

```text
Unknown test state blocks release, closure, promotion, live enforcement, and green claims.
It does not block diagnostics, documentation, guard hardening, policy hardening, or dry-run evidence.
```

The gate does not prove production readiness. It prevents version movement from
outrunning evidence.
