# Repair Planner

ASF-R v0.5 converts wound packages into bounded repair plans.

Core law:

```text
A wound may become a repair plan.
A repair plan is not a repair.
```

The planner binds to wound identity, source decision hash, policy hash, and
ledger hash. It proposes next admissible repair actions without applying them.
