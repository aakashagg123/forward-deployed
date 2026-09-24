---
name: rollout-decision-guide
description: Drain / migrate / route decision path for process version rollouts, with canary sequence
kind: pattern-guide
phase: 08
lesson: 03
---

# Process rollout — the decision guide

## The path

1. **Is the old logic wrong (correction), or merely older (improvement)?**
   - Improvement → **DRAIN**. Deploy; new starts bind the new version; done.
     Record the cohort line ("started after D → vN+1").
   - Correction → 2.
2. **Must the fix reach in-flight instances?**
   - No (defect only affects paths already passed / not applicable) → **DRAIN** +
     batch compensating actions if the past needs repair (Phase 4).
   - Yes → 3.
3. **Can tokens be mapped to the new diagram?** (validate on a copy)
   - Yes → **MIGRATE** by cohort (sequence below).
   - No (structural rewrite) → **ROUTE**: new key, start-level router, run both
     until the old key drains.

## Incident brake

Bad version live? **Suspend the definition version** (stops new starts, running
instances unaffected) → deploy the fix as vN+2 → re-enter the path above for the
defective version's population. Never delete a version with live instances.

## Canary migration sequence

1. Restore a production backup to a scratch engine; run validate + migrate there;
   diff outcomes.
2. Migrate a canary cohort (1–5%, lowest-risk segment) in production; watch error
   rates, dead letters, task pools for one full business cycle of the process.
3. Migrate the rest in batches sized to your rollback appetite; validator-refused
   instances go to a named human, never forced.
4. Archive the migration log (who, when, from → to, ticket) with the change record
   — it is part of the audit narrative now.

## The audit sentence

For any application, you must be able to produce:
*"Application X executed under definition version V (deployed D1, change ticket T);
[it was migrated to V' on D2 under ticket T']."*
Lesson 01's pinning + kept history supply it. If Phase 9 retention would erase the
evidence before the question stops being asked, fix retention first.
