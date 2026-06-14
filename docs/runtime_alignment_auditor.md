# Runtime Alignment Auditor

The alignment auditor checks whether runtime surfaces describe the same state.

Compared surfaces:

- decision
- wound package
- ledger record
- RCC route
- rehydration report
- UI render
- README status

Failure codes include `UI_DECISION_DRIFT`, `WOUND_DECISION_DRIFT`,
`LEDGER_HASH_DRIFT`, `RCC_ROUTE_DRIFT`, `REHYDRATION_STATE_DRIFT`, and
`NON_CLAIM_LOCK_MISSING`.
