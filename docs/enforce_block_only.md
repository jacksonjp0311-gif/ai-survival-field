# enforce_block_only

`enforce_block_only` is the v0.4 adapter mode.

Modes:

```text
observe_only         observe and report only
dry_run              simulate enforcement only
enforce_block_only   fail closed when blocked, without mutation
enforce_full         forbidden before production release gate
```

Allowed in v0.4:

- return exit code `2` for blocked workflows,
- return exit code `0` for permitted bounded workflows,
- emit enforcement reports,
- emit wound packages,
- write or return ledger evidence,
- render UI status.

Forbidden in v0.4:

- file writes,
- file edits,
- file deletes,
- repository mutation,
- commit,
- push,
- release creation,
- memory update,
- tool-call side effects,
- wound closure without evidence,
- self-healing mutation.

## CLI

```powershell
python -m asf.cli enforce block-only examples/artifacts/release_blocked_missing_tests.json --action release
python -m asf.cli adapter enforce-block-only examples/adapter_events/filesystem_write_blocked.json
```
