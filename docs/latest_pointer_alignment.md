# Latest Pointer Alignment

The latest pointer is the zero-context rehydration anchor.

v0.6 forbids `latest_commit: pending`.

Latest pointer law:

```text
If a fresh session cannot rehydrate the runtime state, the system is not mature.
If latest_commit is pending, zero-context rehydration is not aligned.
```

This guard checks rehydration continuity only. It grants no authority and does
not prove production readiness.
