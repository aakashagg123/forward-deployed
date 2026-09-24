---
name: engine-dashboard-spec
description: Panel-by-panel spec for the process engine operations dashboard
kind: dashboard-spec
phase: 09
lesson: 04
---

# Engine operations dashboard — spec

One dashboard per business process (definition key), not per engine. Data
sources: the six probe signals (runtime) + two history queries. All counts are
`total`s over indexed queries — never row scans.

## Row 1 — "is anything stuck?" (runtime, red/green)

| Panel | Query | Alert |
| :-- | :-- | :-- |
| Dead letters | `management/deadletter-jobs` total | > 0 → page on-call eng |
| Overdue timer jobs | `management/timer-jobs?dueBefore=now` | > 10 sustained 10 min → page on-call eng |
| Oldest open instance | oldest `startTime`, runtime instances | > designed lifetime × 1.5 → notify process owner |

## Row 2 — "is the human side keeping up?" (runtime)

| Panel | Query | Alert |
| :-- | :-- | :-- |
| Pool depth per candidate group | `query/tasks` unassigned per group | > per-team SLA depth → ops lead |
| Oldest unclaimed item per pool | same query, sort dueDate/createTime asc | > claim SLA → ops lead |
| Overdue tasks | `query/tasks` dueBefore=now | > SLA budget → ops lead |

## Row 3 — "how is the process performing?" (history, trends)

| Panel | Query | Alert |
| :-- | :-- | :-- |
| Applications per day (started/completed) | historic instances by start/end date | started rate −X% WoW → product owner |
| Median time-to-decision | historic ACTINST: start → decision activity end | creeping trend, review weekly |
| Outcome mix | historic variable `decision` distribution | auto-approve share shift after any DMN deploy (Phase 5 impact replay, continuous) |
| Per-step wait times | ACTINST durations for user tasks | identifies the bottleneck step for staffing |

## Routing

- Row 1 → engineering on-call (these are system failures).
- Row 2 → ops leads (staffing/process, not code).
- Row 3 → product/process owner (weekly review, not paging).

## Non-goals

CPU, heap, and HTTP latency belong to the platform dashboard. DB health belongs to
lesson 05's runbook. This dashboard answers exactly one question: *is the
business process moving?*
