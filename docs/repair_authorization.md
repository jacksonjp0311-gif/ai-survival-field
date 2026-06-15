# Repair Authorization

ASF-R v0.7 introduces scoped human authorization for one bounded repair plan.

Core law:

```text
Authorization may permit one bounded repair plan.
Authorization may not grant general repair authority.
```

The receipt binds:

- human authorizer,
- repair plan hash,
- repair replay hash,
- allowed repair class,
- allowed paths,
- single-use scope.

The receipt does not close wounds, grant autonomous authority, or enable
`enforce_full`.
