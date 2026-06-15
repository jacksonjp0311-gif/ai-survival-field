# GitHub Actions Guard

ASF-R v0.4 includes a GitHub Actions template for controlled blocking only.

The workflow:

- checks out the repository read-only,
- runs the test suite,
- runs ASF-R against example artifacts,
- fails if a blocked example is expected to block.

The workflow does not push commits, create releases, edit files, update memory,
or call live mutation APIs.

## Boundary

```text
GitHub Actions may observe and fail closed.
GitHub Actions may not mutate.
```
