# The history tables: audit trail vs runtime state

> **Motto** — Two table families, two jobs: `ACT_RU_*` answers "what happens next",
> `ACT_HI_*` answers "what happened" — every ops question starts by picking the right
> family.

*Part of Phase 09 — Operations & observability. Concept lesson — no code required.*

## The Problem

Phase 2 showed that completed instances *vanish* from runtime tables. Every lesson
since has quietly leaned on the other side of that split. Phase 1's client read
`historic-activity-instances`. Phase 8's audit sentence depends on history pinning.
The capstone printed a timeline after the instance was already gone.

This lesson makes the split explicit. Querying the wrong family is the most common
ops mistake — someone says "the instance disappeared!" when it actually
*completed*. History is also the table family that grows forever if nobody owns it
(lesson 02).

## The Concept

<style>
.dgm-hist{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-hist-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-hist h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-hist-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-hist-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.dgm-hist-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-hist-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-hist-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-hist-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-hist-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-hist-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-hist-col.neutral h6{color:#59636e}
.dgm-hist-col.accent h6{color:#7a2c2e}
.dgm-hist-col.blue h6{color:#0550ae}
.dgm-hist-col.green h6{color:#1a614f}
.dgm-hist-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-hist-item:last-child{margin-bottom:0}
.dgm-hist-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-hist{padding:20px 16px 18px}.dgm-hist-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-hist">
  <span class="dgm-hist-chip">Runtime vs. history tables</span>
  <h4>ACT_RU_* is small and hot; ACT_HI_* is append-only and grows forever</h4>
  <p class="dgm-hist-sub">On each commit, the runtime row is mirrored into (or closed in) its history counterpart.</p>
  <div class="dgm-hist-cols">
    <div class="dgm-hist-col accent">
      <h6>ACT_RU_* — runtime (hot, small, deleted on completion)</h6>
      <div class="dgm-hist-item">EXECUTION — live tokens</div>
      <div class="dgm-hist-item">TASK — open tasks only</div>
      <div class="dgm-hist-item">VARIABLE — current values</div>
      <div class="dgm-hist-item">JOB / TIMER_JOB / DEADLETTER_JOB</div>
    </div>
    <div class="dgm-hist-col blue">
      <h6>ACT_HI_* — history (append-only, grows forever)</h6>
      <div class="dgm-hist-item">PROCINST — every instance ever</div>
      <div class="dgm-hist-item">ACTINST — every step taken</div>
      <div class="dgm-hist-item">TASKINST — every task incl. completed</div>
      <div class="dgm-hist-item">VARINST — final variable values</div>
      <div class="dgm-hist-item">IDENTITYLINK — who was candidate/assignee</div>
    </div>
  </div>
  <div class="dgm-hist-link">on each commit, rows are mirrored / closed →</div>
</div>


The rules of the split:

1. **Runtime is a working set, not a record.** Its size tracks only *live* load,
   and that keeps every token operation fast (Phase 2's design bet). A row leaving
   `ACT_RU_TASK` means success, not data loss.
2. **History is written in the same transaction** as the runtime change, at the
   default history level. The audit trail can't drift from what actually happened,
   and a rollback erases both sides together. Phase 2's transaction boundaries
   apply to history too.
3. **Query routing is mechanical.** Open work → runtime (`/runtime/tasks`,
   `/query/tasks`). Anything involving "completed", "how long did", "who did", or a
   date range → history (`/history/...`, `/query/historic-...`). Dashboards that
   join both (throughput + backlog) make two queries, not one clever one.
4. **History is where the metrics live:** cycle time (`START_TIME_` to
   `END_TIME_` on ACTINST), SLA attainment, per-step durations, and decision
   version per case (Phase 8). All of these are history reads. Lesson 04 builds
   the probe on exactly these.

## Ship It

This lesson ships
[`outputs/table-families-cheatsheet.md`](../outputs/table-families-cheatsheet.md) —
the query-routing table and the "instance disappeared" triage flow.

## Check Yourself

**Q1.** An ops dashboard needs average time-to-decision for last month. Which family?

- A) runtime — it's about instances
- B) history — completed work and durations live only in ACT_HI_*
- C) both
- D) the jobs tables

<details><summary>Answer</summary>B — runtime rows for those instances no longer
exist. Durations are history's whole purpose.</details>

**Q2.** Why is history written in the same transaction as the runtime change?

- A) performance
- B) so the audit trail can never disagree with what actually committed — a rolled-back step leaves no phantom history
- C) to save connections
- D) it isn't; a nightly job copies it

<details><summary>Answer</summary>B — audit integrity by construction. (Flowable's
async-history mode trades this for throughput — an explicit, documented
trade.)</details>

**Q3.** "Instance 8801 vanished from /runtime/process-instances" most likely means…

- A) data corruption
- B) it completed (or was terminated) — check /history/historic-process-instances for its END_TIME_ and outcome
- C) the engine restarted
- D) wrong tenant

<details><summary>Answer</summary>B — the triage flow on the cheat sheet: history
first, panic later.</details>

**Challenge.** Using only history endpoints, reconstruct the capstone driver's
closing summary (timeline and final variables) for an instance that finished
yesterday. Then compute one number the driver didn't: minutes spent waiting at
each user task (ACTINST start/end deltas). You've just written the seed of lesson
04's probe.

## Related

- Next: [History levels & data growth](../../02-history-levels/docs/en.md)
- The split's origin: [Phase 2, lesson 01](../../../02-the-engine-state-and-transactions/01-wait-states-and-persistence/docs/en.md)
