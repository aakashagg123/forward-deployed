---
name: boundary-review-guide
description: Process/domain boundary rules as a review checklist, with the smell table
kind: pattern-guide
phase: 10
lesson: 03
---

# The process/domain boundary — review guide

## The four rules

1. Variables carry **references and routing facts**, never the only copy of
   business truth.
2. Translation lives in **delegates/HTTP tasks calling domain APIs** — never
   direct writes to another service's tables.
3. Query direction: pending work → engine; business truth → domain. Never derive
   one from the other.
4. `ACT_HI_*` answers process audit; business reporting reads domain
   events/warehouse. Retention must be free to delete engine rows.

## Review smell table

| Smell | Rule | Fix |
| :-- | :-- | :-- |
| variable holds an amount/PII no domain table has | 1 | write-through to domain; keep the reference |
| delegate contains SQL/repository for another service's schema | 2 | call that service's API; keep the delegate thin |
| UI/status endpoint reads task or execution state for customer-facing status | 3 | domain status field, updated by the process via delegate |
| BI dashboard joins ACT_HI_VARINST | 4 | domain events → warehouse; ACT_HI_ for process KPIs only (9.04 row 3) |
| retention (9.02) blocked because "we'd lose the loan data" | 1+4 | that data was misplaced; migrate it out, then set retention |
| engine upgrade plan includes "migrate business data" | all | the boundary is gone; treat restoration as an epic, not a review note |

## Variable audit tags (use in model review)

- **ref** — ID pointing at domain truth (`loanId`, `applicationId`) ✅
- **routing** — fact the flow branches on (`score`, `decision`, `kycOk`) ✅,
  domain must independently record any with business meaning
- **truth** — business data whose only home is the engine ❌ relocate

## The one-sentence policy

> The engine may always tell us *where a case is and who must act*; it may never
> be the only system that can tell us *what is true about the customer*.
