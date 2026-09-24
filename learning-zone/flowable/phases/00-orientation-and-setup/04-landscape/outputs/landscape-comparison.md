---
name: landscape-comparison
description: Two-axis engine landscape (Flowable, Camunda 7/8, Temporal, DIY) with evaluation rules
kind: comparison-table
phase: 00
lesson: 04
---

# Workflow engine landscape — the worksheet

## The two axes (answer these before any feature matrix)

1. **Author axis** — who must read or author the flow?
   Business, compliance, or ops reads it → model-first (BPMN family).
   Only engineers read it → code-first (durable execution) is simpler and honest.
2. **State axis** — where may state live?
   State must stay in your existing RDBMS (audit, ops, data residency) →
   Flowable / Camunda 7 class. A separate platform is acceptable → Camunda 8 /
   Temporal enter the shortlist.

## The five-way table

| | Flow authored as | State lives in | Human tasks | Decisions | Ops model |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Flowable OSS | BPMN/CMMN models | your RDBMS (embedded or standalone) | native (Phase 3) | DMN native | you run it; it's a library or one service |
| Camunda 7 | BPMN models | your RDBMS, embedded | native | DMN native | same class; EOL path — legacy only |
| Camunda 8 | BPMN models | Zeebe cluster (SaaS/self-hosted) | native | DMN native | separate stateful platform |
| Temporal | code (Java/Go/TS/Py) | Temporal cluster/cloud | build your own | build your own | separate stateful platform |
| DIY | status columns + code | your tables | build your own | code | none today, all of it later |

## Shortlist logic

- Model-first + your-DB → **Flowable OSS** (this course's cell).
- Model-first + platform-OK + very high throughput → **Camunda 8**.
- Code-first + platform-OK → **Temporal**.
- Neither axis matters (tiny, stable, automated) → **DIY status+queue**, guilt-free.

## Questions that cut through vendor decks

- Ask for the audit answer: "which rules version decided case X?" (Phase 8's
  sentence.) Who produces it, and from which store?
- What is the *second* stateful system you'd now operate, and what is its
  backup/DR story?
- Where do human tasks, forms, and candidate groups come from — native, or DIY?
- What happens to in-flight instances on deploy? If the answer isn't Phase 8's
  three rules, dig deeper.
- Which parts are open source today, and what moved editions in the last three
  years?
