# Repair Validation Replay

ASF-R v0.6 makes repair plans replayable evidence.

Core law:

```text
A repair plan is not a repair.
A repair replay is not wound closure.
```

Replay may prove repair-path coherence. Replay may not perform repair, close the
wound, grant authority, or enable `enforce_full`.

Replay binds:

- repair plan hash,
- repair dry-run hash,
- repair validation hash,
- non-mutation status,
- wound-open status,
- authority-not-granted status.
