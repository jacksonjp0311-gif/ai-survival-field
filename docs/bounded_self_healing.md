# Bounded Self-Healing

ASF-R is not allowed to self-heal by mutation.

Current ladder:

```text
detect wound
package wound
recommend next admissible action
generate repair plan
dry-run repair
validate repair
request authorization
```

Self-healing law:

```text
ASF-R may learn how to repair.
ASF-R may not grant itself permission to repair.
```
