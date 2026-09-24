# Phase 11 — Capstone: loan origination

> One end-to-end build: BPMN flow + DMN credit decision + user-task review + bureau
> service calls + offer-expiry timers + error handling, driven over REST.

| # | Project | Combines | Lang | Ships |
|---|---------|----------|------|-------|
| 01 | [The process model: application → decision → offer → disbursal](./01-process-model/docs/en.md) ✅ | 1, 4, 7 | XML | process model |
| 02 | [The credit decision table](./02-credit-decision-table/docs/en.md) ✅ | 5 | XML | decision table |
| 03 | [The driver: a REST client that runs a full application](./03-the-driver/docs/en.md) ✅ | 2, 3, 4 | Python | client |
| 04 | [Failure drill: bureau down, offer expired, manual override](./04-failure-drill/docs/en.md) ✅ | 4, 7, 9 | Python | runbook |

Prerequisites: everything before it — that's the point. Full plan:
[`ROADMAP.md`](../../ROADMAP.md).
