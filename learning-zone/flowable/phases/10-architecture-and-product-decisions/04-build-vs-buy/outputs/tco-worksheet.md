---
name: workflow-tco-worksheet
description: Five-year TCO worksheet for DIY vs open source vs commercial workflow platforms
kind: decision-guide
phase: 10
lesson: 04
---

# Workflow capability — 5-year TCO worksheet

Fill all three columns with numbers, not adjectives. Day-rate: ____ · Team: ____

| Cost line (5 yr) | DIY | Flowable OSS | Buy (Work / other) |
| :-- | :-- | :-- | :-- |
| Engine capability (build/maintain) | ____ | 0 (upstream) | 0 (included) |
| UIs: modeler, inbox, admin | ____ | ____ | license: ____ |
| Operations (Phase 9 practice) | ____ | ____ | ____ (reduced, ≠ 0) |
| Upgrades & security patching | ____ | ____ | vendor + ____ |
| People (FTEs × years) | ____ | ____ | ____ + vendor mgmt |
| Exit cost (year 5, forced) | rewrite: ____ | model-portable: ____ | models − proprietary: ____ |
| **Total** | | | |

## The DIY-mortgage checklist

Before accepting a DIY line under "we'll just use a status column", require
written answers for:

- [ ] Durable waits across restarts/deploys (Phase 2.01)
- [ ] Transaction boundaries & partial-failure semantics (2.03)
- [ ] Retries, backoff, dead-letter surfacing + alerting (2.04, 4.05, 9.04)
- [ ] Timers: expiry, reminders, escalation — drift-free (7.01)
- [ ] External callbacks correlated to the right case (7.02)
- [ ] Changing the flow with thousands in flight (Phase 8, all of it)
- [ ] Audit: "what happened, under which rules?" (8, 9.01)
- [ ] The ops surface: stuck-work visibility, retention, restore (9)

Each unanswered box is either a production incident on a schedule, or a line
item missing from the DIY column.

## Decision triggers (write yours)

- We switch OSS → buy the day: ______________________
- We switch buy → OSS the day: ______________________
- DIY is permissible only for flows scoring ≤ 2 on the Phase 0.01 checklist.
