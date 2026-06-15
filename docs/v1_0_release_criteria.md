# ASF-R v1.0 Release Criteria

v1.0 should be boring on purpose.

```text
v1.0 does not expand authority.
v1.0 makes the existing loop installable, testable, documented, and reproducible.
```

## Required Before v1.0 Final

- CI badge visible in README.
- One-command local demo documented.
- Editable install path documented.
- Full test suite passes locally.
- GitHub Actions ASF Guard passes on the release candidate head.
- Public demo, dogfood report, bounded draft, and blocked release run in CI.
- Example failure, wound, repair plan, replay, and closure path are documented.
- Latest pointer identifies the release candidate evidence.
- Release seal records non-claim locks.

## Authority Boundary

v1.0 final must not enable:

- `enforce_full`,
- autonomous repair,
- self-healing mutation,
- general repair authority,
- unscoped wound closure,
- live release mutation,
- memory mutation,
- external mutation APIs.

## Non-Claim Lock

ASF-R v1.0 may claim bounded reproducibility of the current governed recovery
loop. It may not claim production security, formal verification, autonomous
safety, factual truth validation, or external adoption readiness.
