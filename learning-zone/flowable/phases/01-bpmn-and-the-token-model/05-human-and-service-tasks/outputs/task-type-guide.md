---
name: task-type-guide
description: One-page decision guide for choosing BPMN task types in model reviews
kind: decision-guide
phase: 01
lesson: 05
---

# Choosing the task type — a one-page guide

Work through the three questions in order. Stop at the first answer.

## 1. Does the flow stop until someone or something outside the engine acts?

- **A person acts** → **User task.** Use `assignee` only for genuinely personal
  work. Default to `candidateGroups` — one task, many eligible claimants, first
  claim wins.
- **An external system calls back later** → **Receive task / message catch event.**
  Correlate by business key, not by task ID.
- **Only time passes** → **Timer event** (ISO-8601: `PT4H`, `P3D`, `R3/PT1H`).
- **No — the engine can act right now** → question 2.

## 2. Is the call fast and reliable enough to hold a transaction open?

- **Yes (sub-second, internal, idempotent)** → **Service task** (delegate or
  expression) or **HTTP task** for plain REST.
- **No (slow, flaky, third-party, rate-limited)** → make it asynchronous. Add
  `flowable:async="true"` on the task and job executor retries come free, or
  fire-and-wait with a message catch for the callback.

## 3. Will the business want to change this logic without a release?

- **Yes** → **Business rule task → DMN decision table.** Thresholds, eligibility
  grids, pricing, routing policies.
- **No, it's engineering logic** → keep it in the service layer behind a service
  task. The model orchestrates; it does not implement.

## Red flags in model review

- ❌ Script task containing an `if` about the business domain → move to DMN or a service.
- ❌ Synchronous service task calling a third party → async it or catch a callback.
- ❌ Gateway conditions encoding policy numbers (`${score >= 700}`) that change
  quarterly → the number belongs in a DMN table or a variable set by one.
- ❌ User task with a hard-coded person as assignee → candidate group.
- ❌ Parallel user tasks used where "any one approver" was meant → one task +
  candidate group.
