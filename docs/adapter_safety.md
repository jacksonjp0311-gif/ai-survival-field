# Adapter Safety

Adapters are non-mutating by default.

Default mode:

```text
observe_only
```

Allowed modes:

- `observe_only`
- `dry_run`
- `enforce_block_only`
- `enforce_full`

No adapter may self-authorize, convert unknown into pass, bypass policy, close a
wound without evidence, or display UI pass when the decision is blocked.
