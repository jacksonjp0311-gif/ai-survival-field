# Quickstart

Run the public demo:

```powershell
python -m asf.cli demo
```

Run the repository dogfood loop:

```powershell
python -m asf.cli dogfood run
```

Permit a bounded draft:

```powershell
python -m asf.cli enforce block-only examples/artifacts/draft_allowed.json --action draft
```

Fail closed on a blocked release:

```powershell
python -m asf.cli enforce block-only examples/artifacts/release_blocked_missing_tests.json --action release
```

Expected result: the blocked release exits with code `2` and emits an
enforcement report. It does not mutate files, memory, repositories, or releases.

## One-Command Demo Path

```powershell
python -m asf.cli demo
```

The demo summarizes the governed recovery loop:

```text
detect wound
package wound
plan repair
dry-run repair
validate repair
replay repair
authorize bounded repair
capture evidence
validate closure
record closure
```

## Non-Claim Lock

The quickstart demonstrates bounded continuation behavior. It does not prove
truth, production security, autonomous safety, or formal correctness.
