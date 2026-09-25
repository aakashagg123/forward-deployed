# Transaction boundaries & async continuations

> **Motto** — Everything between two wait states is one transaction. Know where
> those boundaries are and incidents become mechanical. Guess, and "the engine
> re-ran my payment" becomes your war story.

*Part of Phase 02 — The engine: state & transactions. Concept lesson — no code
required. Concept reading:
[Principle 4](../../../../foundations/process-automation-principles.md).*

## The Problem

A process executes: service task A (reserve funds) → service task B (call the
disbursal API) → service task C (write the ledger entry). C throws. What
happened to A and B?

If you don't know the answer *precisely*, you can't write safe service tasks.
The answer is: **A and B roll back too**. The token returns to the previous
wait state as if none of the three ever ran — *except* the disbursal API really
was called, because an external HTTP call can't be rolled back by your database
transaction. Money moved, and your process has no record of it. This lesson is
about never being surprised by that again.

## The Concept

The engine advances tokens synchronously, in the caller's thread and
transaction, until it hits a wait state — then it commits. The unit of
atomicity is therefore *the segment between wait states*, not the individual
task:

<style>
.dgm-txa0{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-txa0-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-txa0 h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-txa0-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-txa0-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-txa0-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-txa0-n.accent{background:#faeceb;border-color:#e3b3ad;color:#7a2c2e}
.dgm-txa0-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-txa0-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-txa0-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-txa0-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-txa0-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-txa0{padding:20px 16px 18px}.dgm-txa0-row{flex-direction:column}}
.dgm-txa0-note{margin-top:10px;padding:9px 14px;background:#faeceb;border:1px dashed #e3b3ad;border-radius:10px;
  font-size:10.5px;color:#7a2c2e;line-height:1.4}
</style>
<div class="dgm-txa0">
  <span class="dgm-txa0-chip">One transaction, end to end (synchronous)</span>
  <h4>Everything between two wait states can be a single transaction</h4>
  <p class="dgm-txa0-sub">Task A, B and C commit or roll back together — nothing is durable until they all succeed.</p>
  <div class="dgm-txa0-row">
    <div class="dgm-txa0-n accent">Wait state — user task</div>
    <span class="dgm-txa0-arr">→</span>
    <div class="dgm-txa0-n ">Task A</div>
    <span class="dgm-txa0-arr">→</span>
    <div class="dgm-txa0-n ">Task B</div>
    <span class="dgm-txa0-arr">→</span>
    <div class="dgm-txa0-n ">Task C</div>
    <span class="dgm-txa0-arr">→</span>
    <div class="dgm-txa0-n accent">Wait state — timer</div>
  </div>
  <div class="dgm-txa0-note">TX 1: everything here commits or rolls back together.</div>
</div>


- C throws, so TX 1 rolls back and the token returns to W1. A's and B's
  *engine-side* effects (variables, state) are undone. The client that
  completed W1's task gets the exception.
- Any effect that escaped the transaction (an HTTP call, an email) is **not**
  undone.

**Async continuations** let you cut this segment. Marking a task
`flowable:async="true"` inserts a boundary *before* it: the engine commits the
token's position as a **job** and returns. The job executor (next lesson) picks
it up in a new transaction.

<style>
.dgm-txa1{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-txa1-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-txa1 h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-txa1-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-txa1-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-txa1-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-txa1-n.accent{background:#faeceb;border-color:#e3b3ad;color:#7a2c2e}
.dgm-txa1-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-txa1-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-txa1-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-txa1-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-txa1-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-txa1{padding:20px 16px 18px}.dgm-txa1-row{flex-direction:column}}
</style>
<div class="dgm-txa1">
  <span class="dgm-txa1-chip">Splitting the transaction with an async boundary</span>
  <h4>A job creates a new transaction boundary mid-flow</h4>
  <p class="dgm-txa1-sub">Task A commits on its own; task B and C run later, in a fresh transaction, picked up by the job executor.</p>
  <div class="dgm-txa1-row">
    <div class="dgm-txa1-n accent">User task</div>
    <span class="dgm-txa1-arr">→</span>
    <div class="dgm-txa1-n ">Task A</div>
    <span class="dgm-txa1-arr"><span class='lbl'>commit; job created</span>→</span>
    <div class="dgm-txa1-n blue">Task B (async)</div>
    <span class="dgm-txa1-arr">→</span>
    <div class="dgm-txa1-n ">Task C</div>
    <span class="dgm-txa1-arr">→</span>
    <div class="dgm-txa1-n accent">Timer</div>
  </div>
</div>


Now B failing rolls back only B and C. A's completion stays safely committed,
and the job retries B without re-running A. Async is how you get:

1. **Fault isolation** — flaky externals retry alone instead of dragging the
   whole segment back.
2. **Fast API responses** — the user's "submit" returns after the commit
   instead of after the slow bureau call.
3. **Real parallelism** — parallel branches actually run concurrently only if
   the branches are async (otherwise Phase 1's truth holds: one thread walks
   both).

There's a cost: after an async boundary, failures no longer surface to the
caller. They become **failed jobs** (dead-letter after retries), so you need
the job-executor operational story from lesson 04 and Phase 9's monitoring.

Rules of thumb for placing boundaries:

| Situation | Boundary? |
| :-- | :-- |
| Calling any third-party / flaky / slow system | `async="true"` on that task |
| Non-idempotent external effect (payment!) | async **and** idempotency key in the call — retries must be safe |
| Heavy computation after a user submit | async right after the user task |
| Chain of quick internal steps | no boundary — one transaction is simpler and atomic |
| Parallel branches that must truly overlap | async on the first task of each branch |

## Ship It

This lesson ships
[`outputs/async-flags-cheatsheet.md`](../outputs/async-flags-cheatsheet.md) — the
one-pager for model reviews. It covers what each flag does, where boundaries
fall, and the payment-safety checklist.

## Check Yourself

**Q1.** Tasks A → B → C run after a user task, no async flags. C throws. The engine
state is…

- A) A and B committed, C pending
- B) everything rolled back to the user task; the completer sees the exception
- C) the instance is dead-lettered
- D) C retries automatically

<details><summary>Answer</summary>B — one segment, one transaction. Without an
async boundary there are no retries, so the failure propagates to whoever
triggered the segment.</details>

**Q2.** Task B calls a payment API and is marked async. What *must* also be true?

- A) nothing; async makes it safe
- B) the call carries an idempotency key, because the job executor will re-run B on failure
- C) B must be the last task
- D) the process needs a second engine

<details><summary>Answer</summary>B — async means retries, and retries mean the
call can fire twice. Only idempotency on the receiving side makes that safe.
Async without idempotency is how double payments happen.</details>

**Q3.** Two parallel branches of synchronous service tasks: do they run concurrently?

- A) yes, the engine spawns threads per branch
- B) no — one thread walks both branches sequentially; concurrency requires async tasks
- C) only on a cluster
- D) only with more than two branches

<details><summary>Answer</summary>B — parallel gateways are token bookkeeping, not
threads. True overlap needs async boundaries so the job executor can run
branches on its own threads.</details>

**Challenge.** Take the loan-triage model from Phase 1 and decide, on paper,
where async boundaries belong if `creditCheck` calls a real bureau (slow,
flaky, but idempotent) and `autoApprove` posts to a core-banking API (fast, but
*not* idempotent). Write down what the failure of each task now does, and what
you'd need to monitor. Check your answer against the cheat sheet.

## Related

- Next: [The job executor](../../04-job-executor/docs/en.md) — the machinery that runs
  everything you just made async
- Concept: [Principle 4](../../../../foundations/process-automation-principles.md)
