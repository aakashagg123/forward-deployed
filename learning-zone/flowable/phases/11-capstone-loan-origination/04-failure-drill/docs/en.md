# Capstone 04 — Failure drill: bureau down, offer expired, manual override

> **Motto** — A process you haven't watched fail is a process you don't operate yet;
> drill the failures while they're cheap.

*Part of Phase 11 — Capstone. Combines Phases 4, 7, 9.*

## The Project

Five injected failures against the deployed capstone, each with an expected
behaviour, a verification, and the recovery — written up as a runbook you keep:
[`outputs/failure-drill-runbook.md`](../outputs/failure-drill-runbook.md).

| Drill | Injects | Proves |
| :-- | :-- | :-- |
| 1 · bureau unreachable | `bureau.invalid` | error boundary → human fallback; instances never freeze on a dead dependency |
| 2 · bureau flaky | 502 twice, then 200 | async + job retries absorb transient failure invisibly |
| 3 · offer expires | `offerValidity=PT15S`, nobody accepts | interrupting timer cancels the task; instance ends `expired` on its own |
| 4 · manual override | business wants an auto-decline reviewed | the fix is a new *table version*, not instance surgery — and why |
| 5 · silent stuck state | 502 forever | retries exhaust → dead letter → **nothing visible anywhere** until you alert on the table |

Drill 5 is the one to internalise. Drills 1-4 fail *visibly* — a task appears, a
timeline ends. Drill 5 fails *silently*: the instance is frozen, no inbox shows
anything, and the only trace is a row in `ACT_RU_DEADLETTER_JOB`. The whole
operational chapter (Phase 9) exists because of this class of failure. The
runbook's standing defence — alert on dead-letter count > 0 — is its minimum
viable form.

The runbook closes with the **five-line health check**: oldest open instances,
dead-letter count, overdue timer jobs, and deepest task pools. Those four numbers
answer "is origination healthy?" before any dashboard exists. They're the seed of
the one Phase 9 builds.

## Verify It

Run drills 1 and 3 today — both are deterministic with the stock Docker engine and
the driver's defaults. Drills 2 and 5 need the 20-line flaky server from the
runbook. Drill 4 is a policy exercise on paper plus a `.dmn` redeploy.

Success criterion for the whole capstone: **every drill's outcome matches the
runbook's "expected" line without touching engine internals** — failures land in
inboxes, timelines, or the dead-letter table, never in a debugger.

**Challenge.** Add drill 6 yourself: the *customer withdraws mid-review* (Phase 7's
interrupting message event subprocess, once you've added it per capstone 01's
challenge). Write the expected timeline before injecting it, then check. When the
prediction matches, you've finished the track: you can now read a Flowable process
the way the engine does.
