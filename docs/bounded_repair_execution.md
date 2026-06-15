# Bounded Repair Execution

ASF-R v0.7 permits only low-risk, human-authorized local bounded repair.

Allowed classes:

```text
documentation_alignment
latest_pointer_alignment
repository_hygiene_metadata
runtime_geometry_documentation_drift
```

Forbidden:

```text
policy logic
validator logic
adapter enforcement logic
memory state
release state
external mutation APIs
```

Repair execution is not wound closure.
