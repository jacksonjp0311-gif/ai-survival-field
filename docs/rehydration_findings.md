# Rehydration Findings from Hermes Agent Evo

ASF-R v0.1 was rehydrated against the Hermes/RHP example repository before
implementation.

The useful techniques carried forward were:

- **Latest pointer pattern**: a compact machine-readable pointer to latest state,
  latest evidence, latest operation, next operation, and authority status.
- **Non-authorizing rehydration**: rehydration loads state but does not grant
  permission by itself.
- **Claim ledger pattern**: ledger records provenance, conflicts, hashes, actors,
  timestamps, and status without self-authorizing repairs.
- **Wound packet pattern**: blocked propagation becomes a structured repair
  object instead of a loose error.
- **Operator startup surface**: runtime health is shown as locks, gates, and
  degraded/pass states.
- **Adapter separation**: adapters observe, package, route, enforce, and report
  instead of merging runtime policy into one command.
- **Boundary language**: every report carries a non-claim lock so status cannot
  be confused with truth, safety, or production authority.

## ASF-R Translation

Hermes/RHP technique translated into ASF-R:

| Hermes/RHP Pattern | ASF-R v0.1 Implementation |
| --- | --- |
| latest pointer | `asf.rhp.rehydration.RehydrationReport` |
| claim ledger | `asf.ledger.ledger.LedgerRecord` |
| CI wound packet | `asf.wounds.wound.WoundPackage` |
| operator startup status | `asf.ui.geometric_console.render` |
| alignment guard | `asf.core.validator.validate` |
| adapter contracts | `asf.adapters.base.ASFAdapter` |

## What Emerged

ASF-R is not merely SFT with renamed files.

SFT answers:

```text
Is this artifact allowed to support this action?
```

ASF-R expands the runtime question:

```text
Was state rehydrated?
Was the artifact routed?
Which policy applies?
Which gate or lock limits continuation?
What wound package is emitted when continuation is blocked?
What ledger record proves the decision path?
What geometry does the operator see?
```

That is the production shift:

```text
reference validator -> runtime governance loop
```

