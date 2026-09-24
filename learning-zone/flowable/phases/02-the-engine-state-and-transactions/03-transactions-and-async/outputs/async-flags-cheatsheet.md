---
name: async-flags-cheatsheet
description: One-page reference for Flowable transaction boundaries and async flags
kind: cheat-sheet
phase: 02
lesson: 03
---

# Transactions & async — the cheat sheet

## The one rule

**Everything between two wait states is one transaction.** Wait states include:
user task, timer, message/signal catch, receive task, and every `async="true"`
boundary.

A failure anywhere in the segment rolls the token back to the previous wait
state. External side effects (HTTP, email, payments) are NOT rolled back.

## The flags

| Flag | Effect |
| :-- | :-- |
| `flowable:async="true"` | commit *before* this activity; a job runs it in a new TX, with retries |
| `flowable:exclusive="true"` (default) | no two async jobs of the same instance run concurrently, which keeps parallel branches from optimistic-lock fights |
| `flowable:asyncLeave="true"` | commit *after* the activity, before taking the outgoing flow (Flowable 6.7+) |
| Timer / message / receive | natural boundaries — commit on arrival, new TX on firing |

## Failure behaviour

| Segment type | On exception |
| :-- | :-- |
| Synchronous | rolls back to the previous wait state; the caller gets the exception |
| Async | the job retries (default 3×), then becomes a **dead-letter job** — nobody is notified unless you monitor `ACT_RU_DEADLETTER_JOB` (see Phase 9) |

## Placement rules of thumb

1. Third-party, slow, or flaky call → `async="true"` on that task.
2. Non-idempotent external effect (payments, postings) → async **plus** an
   idempotency key in the request. Make retries safe before you enable them.
3. Anything heavy right after a user submit → async, so the submit returns fast.
4. Chains of quick internal steps → leave synchronous; atomicity is a feature.
5. Parallel branches that must truly overlap → async on each branch's first
   task (and keep `exclusive` unless you've proven you need otherwise).

## Payment-safety checklist

- [ ] The paying task is async (failure can't roll back committed process state)?
- [ ] The payment request carries an idempotency key derived from instance + step?
- [ ] Retry count / backoff configured deliberately, not defaulted?
- [ ] Dead-letter jobs alerted on, with a runbook?
- [ ] Reconciliation path exists for "call succeeded but TX failed after"?
