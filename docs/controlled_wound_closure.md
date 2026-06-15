# Controlled Wound Closure

ASF-R v0.8 separates repair from closure.

Core law:

```text
A repaired wound is not a closed wound.
A wound may close only after post-repair evidence, replay, authorization, and closure-specific validation.
```

Closure requires:

- exact wound ID,
- repair plan hash,
- repair replay hash,
- repair execution hash,
- post-repair evidence hash,
- authorization receipt hash,
- closure-specific authorizer.

Closure records the semantic state of the wound. It performs no repair mutation
and grants no general authority.
