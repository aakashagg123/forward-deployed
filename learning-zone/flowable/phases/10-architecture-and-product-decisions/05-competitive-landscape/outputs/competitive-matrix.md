---
name: competitive-matrix
description: Seven-question engine comparison (Flowable OSS/Work, Camunda 8, Temporal) + PoC script
kind: comparison-table
phase: 10
lesson: 05
---

# The seven-question matrix

Ask every candidate the course's questions; adjectives don't count as answers.

| # | Question (phase) | What a good answer shows |
| :-- | :-- | :-- |
| 1 | Where do waits live, and what happens on restart? (2) | durable state store you can operate/audit |
| 2 | Human tasks: pools, claim race, forms, identity source? (3) | native or honest "you build it" |
| 3 | Business errors vs technical retries — two planes? (4) | routable outcomes + dead-letter surface |
| 4 | Decisions outside code, deployable separately? (5) | DMN or equivalent, with governance story |
| 5 | Timers, correlation, broadcast — and their failure modes? (7) | disarm-on-complete, unmatched-delivery handling |
| 6 | 10,000 in flight; the flow changes — now what? (8) | pinning + migration tooling, or named discipline |
| 7 | The 2 a.m. story: stuck work visibility, retention, restore? (9) | queryable ops surface + retention controls |

## Snapshot (2026 — reverify rows before deciding)

- **Flowable OSS**: strong on all seven in your own RDBMS. UIs are yours to
  build. This course is the evidence file.
- **Flowable Work**: same engine answers. It adds modelers, task and admin UIs,
  and an SLA. This is the buy-the-edges decision (10.04).
- **Camunda 8**: BPMN/DMN answers on its own Zeebe platform. The ops story is
  platform-shaped — a unified Orchestration Cluster with built-in history
  since 8.8 (no separate exporter pipeline), and Operate — and embedding is
  gone. It's strongest at very high throughput or when you prefer SaaS.
- **Temporal**: superb on question 1, and questions 5 and 3 are handled as
  code. Questions 2 and 4 are DIY. Question 6 is worker discipline (patching)
  rather than tooling. It's the right answer when no non-engineer ever reads
  the flow.

## The two-week PoC script (run on any finalist)

1. Deploy the capstone equivalents: parallel checks, error-boundary fallback,
   decision step, timed offer.
2. Drive it end to end via API only (no vendor console) — the Phase 11 driver.
3. Kill the runtime mid-flight; verify resume (question 1).
4. Change the flow with 100 instances live; move 50 (question 6).
5. Point a probe at it: stuck work, oldest case, dead letters (question 7).
6. Have a non-engineer read the flow artifact and explain it back (the author
   axis, Phase 0.04 — skip for Temporal-class tools and note why).

Score each step 0-2. If anything scoring under 9/12 survives to contract, it's
being bought for reasons outside this matrix. Name them explicitly.
