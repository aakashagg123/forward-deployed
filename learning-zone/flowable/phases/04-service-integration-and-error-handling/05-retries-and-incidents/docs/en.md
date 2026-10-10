# Retries & incident handling: what happens when a bureau call fails

> **Motto** — Retries buy you time, not correctness. After the last retry, a failed
> job goes silent in the dead-letter table, and your incident process is whatever
> you built to watch it.

*Part of Phase 04 — Service integration & error handling. Builds directly on
[Phase 2, lesson 04 — the job executor](../../../02-the-engine-state-and-transactions/04-job-executor/docs/en.md).*

## The Problem

It's month-end, 22:40. The bureau starts returning 502s. Two hundred loan
applications hit their async `bureauCall` task. Each one fails, retries three times
over a few minutes, still gets a 502, and dead-letters. At 23:05 the bureau
recovers, but nothing happens. The two hundred instances sit frozen. They're
invisible to customers ("my application just says processing"), invisible to the
diagram (technical failures don't appear there — lesson 03), and invisible to
everyone except a table nobody is watching. The engine did exactly what it promised.
The gap is operational, and this lesson closes it.

## The Concept

The failure pipeline for an async task, end to end:

<style>
.dgm-ri{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-danger-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ri-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-danger-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-danger-solid) 28%, transparent)}
.dgm-ri h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-ri-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-ri-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-ri-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-ri-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-ri-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-ri-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-ri-b.accent{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-ri-b.accent h6{color:var(--color-text-danger)}
.dgm-ri-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-ri-b.blue h6{color:var(--color-text-info)}
.dgm-ri-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-ri-b.green h6{color:var(--color-text-success)}
.dgm-ri-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-ri-b.red h6{color:var(--color-text-danger)}
.dgm-ri-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-ri-b.neutral h6{color:var(--color-text)}
@media (max-width:640px){.dgm-ri{padding:20px 16px 18px}.dgm-ri-branches{grid-template-columns:1fr}}
.dgm-ri-chain{display:flex;flex-direction:column;gap:2px}
.dgm-ri-node{background:var(--color-background-danger-surface);border:1.5px solid var(--color-border-danger-surface);border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:var(--color-text-danger)}
.dgm-ri-node.alt{background:var(--color-surface-tertiary);border-color:var(--color-border);color:var(--color-text)}
.dgm-ri-arr{display:flex;justify-content:center;color:var(--color-text-tertiary);padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-ri{padding:20px 16px 18px}}
</style>
<div class="dgm-ri">
  <span class="dgm-ri-chip">From retry to incident</span>
  <h4>Exhausted retries become a human problem, not a silent failure</h4>
  <p class="dgm-ri-sub">The dead-letter table is where automatic recovery hands off to a person.</p>
  <div class="dgm-ri-q">Task throws — retries left?</div>
  <div class="dgm-ri-branches">
    <div class="dgm-ri-b accent">
      <h6>Yes</h6>
      <p>Wait backoff, re-run via the job executor — loops back to the task</p>
    </div>
    <div class="dgm-ri-b red">
      <h6>No</h6>
      <p>Move to the dead-letter table (ACT_RU_DEADLETTER_JOB)</p>
    </div>
  </div>
  <div class="dgm-ri-chain">
    <div class="dgm-ri-node alt">Monitoring alerts a human</div>
    <div class="dgm-ri-arr">↓</div>
    <div class="dgm-ri-node alt">Fix the cause</div>
    <div class="dgm-ri-arr">↓</div>
    <div class="dgm-ri-node accent">Move jobs back — fresh retry budget</div>
  </div>
</div>


Your three levers, and where each is set:

1. **The retry policy** — set per task in the model:
   `flowable:failedJobRetryTimeCycle="R5/PT10M"` (5 attempts, 10 minutes apart). The
   defaults (3 tries, immediate-ish) are almost never what a flaky third party needs,
   so an external call without an explicit cycle is a model-review flag. Match the
   cycle to the dependency. A bureau with 15-minute blips deserves `R6/PT15M`, not
   three instant retries that all land inside the same outage.
2. **The dead-letter watch** — a monitor on the dead-letter count (Phase 9 wires it
   properly). The count's normal value is zero, and anything else pages someone.
   Without this, every lever downstream is decoration.
3. **The revive loop** — after the cause is fixed, move the jobs back
   (`action: move`). They re-enter the executable queue with a fresh budget. Because
   the failed transaction rolled back, re-running is safe *if the task is
   idempotent*, which you guaranteed when you made it async (Phase 2's
   payment-safety checklist).

The escalation pattern from lesson 03 completes the picture. Where ops wants a
*modelled* fallback instead of a frozen instance ("after retries exhaust, route to
manual processing"), convert the terminal failure into a BPMN error the diagram
catches. Transient blips stay invisible, and persistent failure becomes a drawn,
staffed path.

## Use It

[`code/incident_client.py`](../code/incident_client.py) is the ops loop as a script —
stdlib only, same auth as Phase 1's client. Triage groups the table by root cause,
so two hundred identical 502s read as one line, not two hundred:

```
$ python3 incident_client.py
200 dead-letter job(s), 2 distinct cause(s):

  199 x org.flowable.common.engine.api.FlowableException: HTTP 502 from bureau
        e.g. job 5821  instance 5760  element bureauCall

    1 x java.lang.NullPointerException
        e.g. job 5900  instance 5872  element notifyTask

fix the cause, then revive with: python3 incident_client.py retry-all
```

— and the revive half is one call per job:

```python
def revive(job_id):
    """Move the job back to the executable table; the executor picks it up
    with a fresh retry budget. Only do this AFTER fixing the cause."""
    call("POST", f"/management/deadletter-jobs/{job_id}", {"action": "move"})
```

Note what the triage output *separates*. The 199 jobs share a cause that recovery
will fix, so revive them all. The lone NPE is a code bug — reviving it without a fix
just buys another lap through the retry loop. Group-by-cause is the difference
between an incident and a mystery.

## Ship It

This lesson ships
[`outputs/incident_client.py`](../outputs/incident_client.py): triage and revive for
the dead-letter table. The capstone's failure drill uses it verbatim, and Phase 9
turns its counts into alerts.

## Check Yourself

**Q1.** `flowable:failedJobRetryTimeCycle="R5/PT10M"` means…

- A) 5 retries, 10 minutes total
- B) 5 attempts spaced 10 minutes apart
- C) retry every 5 minutes for 10 cycles
- D) 10 retries in 5 minutes

<details><summary>Answer</summary>B — ISO-8601 repetition: R⟨count⟩/⟨interval⟩. Size
the interval to outlive the dependency's typical outage.</details>

**Q2.** Reviving a dead-letter job is safe when…

- A) always — the engine handles it
- B) the underlying cause is fixed and the task is idempotent (its failed attempts rolled back but external effects may have fired)
- C) the instance is suspended first
- D) never; dead letters are terminal

<details><summary>Answer</summary>B — `move` re-runs the task from its last committed
state. Rollback undid engine state, not external calls — idempotency (Phase 2) is
what makes the re-run safe.</details>

**Q3.** Why does triage group dead letters by stack-trace first line?

- A) the API requires it
- B) an incident is usually one cause hitting many instances — grouping turns 200 rows into the 2 decisions actually needed
- C) to save bandwidth
- D) sorting is prettier

<details><summary>Answer</summary>B — the operational question is "what broke and can
I revive in bulk", not "what is job 5821's story".</details>

**Challenge.** Extend the client with `retry --cause "HTTP 502"`. Revive only jobs
whose stack trace matches, leaving genuine bugs dead. Then add a `--watch` mode that
polls the count every 60 seconds and prints only on change. You've written the
minimum viable dead-letter monitor, one webhook short of Phase 9's alerting.

## Related

- Next: [Compensation](../../06-compensation/docs/en.md)
- The executor you're operating: [Phase 2, lesson 04](../../../02-the-engine-state-and-transactions/04-job-executor/docs/en.md)
