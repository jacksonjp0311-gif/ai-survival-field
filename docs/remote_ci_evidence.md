# Remote CI Evidence

ASF-R v0.9 adds remote CI evidence as a public recoverability layer.

Core law:

```text
Local tests prove local coherence.
Remote CI proves recoverable public coherence.
Dogfooding proves operational contact.
```

The GitHub Actions workflow runs:

- unit tests,
- dogfood report,
- public demo,
- bounded draft permission,
- blocked release fail-closed check,
- CI evidence artifact upload.

The workflow has `contents: read` permission and does not mutate the repository.

Remote CI evidence is not production safety, formal verification, or truth.
