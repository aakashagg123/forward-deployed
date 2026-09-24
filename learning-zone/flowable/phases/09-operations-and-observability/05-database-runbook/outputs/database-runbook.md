---
name: database-runbook
description: Operating the engine's database — sizing, indexes, cleanup guardrails, restore drill
kind: runbook
phase: 09
lesson: 05
---

# The engine's database — runbook

## Sizing worksheet

- Instances/month: ______  × avg activities/instance: ______
- History level (9.02): ______ → rows/instance ≈ activities + tasks + variables
- Keep window: ______ months
- **Steady-state history rows ≈ rate × rows/instance × keep window** = ______
- Runtime rows ≈ live instances × (tokens + open tasks + variables). This is
  small; verify it *stays* small (a growing runtime table is a stuck-work signal,
  9.04).

## Indexes

- Engine-shipped runtime indexes: leave alone; never add to ACT_RU_* without a
  measured engine-level regression justifying it (every index taxes token writes).
- Add for your query load on history, typically:
  - `ACT_HI_PROCINST (END_TIME_)` — cleanup + completed-work dashboards
  - `ACT_HI_PROCINST (BUSINESS_KEY_)` — case lookup by application id
  - `ACT_HI_ACTINST (PROC_INST_ID_, START_TIME_)` — timelines
  - `ACT_HI_VARINST (NAME_, TEXT_)` only if you must query by variable value —
    and consider a reporting replica instead.

## Cleanup-job guardrails (retention deletes, version pruning)

- [ ] Bounded batches (e.g. 10k rows), commit per batch, sleep between batches.
- [ ] Off-peak schedule; abort switch checked between batches.
- [ ] Archive verified (counts reconcile) *before* the delete of any batch.
- [ ] Replication lag watched during the run; pause threshold defined.
- [ ] END_TIME_-based only; open instances untouchable (9.02).

## Contention triage

| Symptom | Likely cause | Fix |
| :-- | :-- | :-- |
| FlowableOptimisticLockingException on EXECUTION | parallel branches on shared state | keep jobs `exclusive` (default); restructure model; never row-lock hints |
| Lock waits on job tables | many nodes, same acquisition instant | stagger poll intervals (9.03) |
| History insert latency | undersized IO for append load | separate tablespace/disk for ACT_HI_*; async history only with eyes open (9.01 Q2) |

## Restore drill (quarterly)

1. Snapshot the production schema (one snapshot — runtime + history together).
2. Restore to a scratch engine; point a capstone driver at it.
3. Verify: parked instances resume; history timelines are complete; probe (9.04)
   shows no dead letters *created by the restore*.
4. Record time-to-restore; that number is your real RPO/RTO, not the one in the
   DR document.
