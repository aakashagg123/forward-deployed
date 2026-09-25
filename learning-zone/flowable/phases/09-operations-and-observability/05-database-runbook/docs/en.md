# The database is the engine: sizing, indexes, cleanup jobs

> **Motto** — Every engine promise from Phase 2 onward is a database behaviour in
> costume: treat the schema as the production system, because it is one.

*Part of Phase 09 — Operations & observability. Concept lesson — no code required.
Closes the loop opened by
[Principle 3](../../../../foundations/process-automation-principles.md).*

## The Problem

Phase 2 made the design bet explicit: state lives in the database. This whole
course has been cashing cheques against that bet — wait states are rows,
clustering is a shared schema, jobs are guarded UPDATEs, and history is an
append-only ledger.

The bill arrives in production. The engine's ceiling *is* the database's ceiling,
and most "Flowable is slow" incidents are database incidents wearing a workflow
costume. Executor tuning already hit this wall (lesson 03's third row). This
lesson is what's on the other side of it.

## The Concept

Where the load actually lands:

<style>
.dgm-dbr{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #a63d40;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-dbr-chip{position:absolute;top:-11px;left:24px;background:#a63d40;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(166,61,64,.28)}
.dgm-dbr h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-dbr-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-dbr-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.dgm-dbr-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-dbr-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-dbr-col.accent{background:#faeceb;border-color:#e3b3ad}
.dgm-dbr-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-dbr-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-dbr-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-dbr-col.neutral h6{color:#59636e}
.dgm-dbr-col.accent h6{color:#7a2c2e}
.dgm-dbr-col.blue h6{color:#0550ae}
.dgm-dbr-col.green h6{color:#1a614f}
.dgm-dbr-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-dbr-item:last-child{margin-bottom:0}
.dgm-dbr-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-dbr{padding:20px 16px 18px}.dgm-dbr-cols{grid-template-columns:1fr}}
</style>
<div class="dgm-dbr">
  <span class="dgm-dbr-chip">Where the contention actually lives</span>
  <h4>The job tables are the hottest rows in the whole schema</h4>
  <p class="dgm-dbr-sub">History tables are huge but calm — insert-only, never fought over.</p>
  <div class="dgm-dbr-cols">
    <div class="dgm-dbr-col red">
      <h6>Hot, small, contended — runtime</h6>
      <div class="dgm-dbr-item">EXECUTION / TASK / VARIABLE — update-heavy, optimistic-locked (REV_)</div>
      <div class="dgm-dbr-item">JOB tables — the acquisition UPDATE, hottest rows in the schema</div>
    </div>
    <div class="dgm-dbr-col blue">
      <h6>Warm, huge, append-only — history</h6>
      <div class="dgm-dbr-item">ACT_HI_* — insert-heavy; reads from dashboards &amp; audits</div>
    </div>
  </div>
</div>


The operational rules, each traceable to a lesson:

1. **Size for history, tune for runtime.** Runtime stays proportional to live load
   (Phase 2's delete-on-complete). History grows at `rate × level × retention`
   (lesson 02's formula — the worksheet's steady-state number is your sizing
   input). Disk planning is a history conversation; latency planning is a runtime
   one.
2. **Index for *your* queries, on history.** The engine ships correct indexes for
   its own runtime access paths — don't touch those. Your custom load is dashboard
   and audit queries on history (`ACT_HI_PROCINST(END_TIME_)` for cleanup,
   `ACT_HI_ACTINST(PROC_INST_ID_, ACT_ID_)` for timelines, business-key lookups).
   Profile them like any application query and index accordingly.
3. **Contention is a design smell before it's a DB problem.** Optimistic-lock
   exceptions on EXECUTION usually mean parallel branches are hammering shared
   state. The fix is Phase 2's `exclusive` default or restructuring the model, not
   `SELECT FOR UPDATE`. Job-acquisition contention across nodes needs lesson 03's
   stagger, not row-lock hints.
4. **Cleanup jobs are production workloads.** Lesson 02's retention deletes and
   Phase 8's dead-version pruning run *inside* business hours' blast radius.
   Batch them (bounded deletes), schedule them off-peak, watch replication lag,
   and reconcile archive counts before every delete. A runaway cleanup job has
   taken down more engines than any traffic spike.
5. **Backups must be schema-consistent.** Runtime and history describe the same
   instances (lesson 01's same-transaction rule). Restoring them to different
   points in time manufactures instances whose past disagrees with their present.
   Use one database, one snapshot, one restore point, and a quarterly restore
   drill that replays the capstone against the restored copy.

## Ship It

This lesson ships
[`outputs/database-runbook.md`](../outputs/database-runbook.md) — sizing worksheet,
the index guidance, cleanup-job guardrails, and the restore drill — closing Phase
9: what the tables mean (01), how big they get (02), how fast they're worked (03),
what to watch (04), and how to keep the whole thing alive (05).

## Check Yourself

**Q1.** "Flowable is slow" during month-end. The first dashboard to open is…

- A) JVM heap
- B) the database's — runtime-table latency and lock waits; the engine is a client of its schema (lesson 03's third row)
- C) the BPMN modeler
- D) network

<details><summary>Answer</summary>B — Principle 3 in incident form. Most engine
slowness is database pressure with a workflow label.</details>

**Q2.** Which tables get *your* custom indexes?

- A) ACT_RU_EXECUTION — it's the hottest
- B) history tables, for your dashboard/audit query shapes — runtime indexes are the engine's own, tuned for its access paths
- C) all of them, defensively
- D) none ever

<details><summary>Answer</summary>B — you own the history query load; the engine
owns runtime access. Adding runtime indexes also taxes every token write.</details>

**Q3.** Restoring runtime from Monday's backup and history from Sunday's produces…

- A) a working engine minus a day of reports
- B) instances whose audit trail contradicts their live state — the same-transaction guarantee broken retroactively
- C) automatic reconciliation
- D) a startup error

<details><summary>Answer</summary>B — consistency between the families exists only
inside one snapshot. Split restores forge history.</details>

**Challenge.** Fill the runbook's sizing worksheet with lesson 02's steady-state
number. Then run the restore drill against the local Docker engine: snapshot the
DB mid-capstone-run, destroy the container, restore, and verify the parked
instance resumes. That's Phase 2, lesson 01's promise — now *your* procedure, not
the course's claim.

## Related

- Phase README: [Operations & observability](../../README.md)
- The bet being operated: [Phase 2, lesson 01](../../../02-the-engine-state-and-transactions/01-wait-states-and-persistence/docs/en.md)
