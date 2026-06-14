# ASF-R Architecture

ASF-R is a governed runtime loop:

```text
RHP -> RCC Nexus -> Guard -> Wound -> Ledger -> UI -> Adapter
```

The design borrows proven techniques from Hermes/RHP:

- latest-pointer style rehydration,
- non-authorizing claim ledgers,
- first-class wound packets,
- operator-visible lock panels,
- adapter contracts that separate observation from enforcement.

