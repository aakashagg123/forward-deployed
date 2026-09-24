---
name: table-families-cheatsheet
description: Runtime vs history query routing, key tables, and the vanished-instance triage
kind: cheat-sheet
phase: 09
lesson: 01
---

# ACT_RU_* vs ACT_HI_* — the cheat sheet

## Query routing

| Question | Family | Endpoint |
| :-- | :-- | :-- |
| open tasks / pools / inbox | runtime | `/query/tasks` |
| where are the tokens now | runtime | `/runtime/executions` |
| stuck async work | runtime | `/management/deadletter-jobs`, `timer-jobs` |
| completed instances, outcomes | history | `/history/historic-process-instances` |
| step timeline, durations | history | `/history/historic-activity-instances` |
| who claimed/completed a task | history | `/history/historic-task-instances` (+ identity links) |
| variable values of a finished case | history | `/history/historic-variable-instances` |
| which definition version decided case X | history | PROC_DEF_ID_ on the historic instance |

## Key tables

- Runtime: `ACT_RU_EXECUTION` (tokens), `ACT_RU_TASK`, `ACT_RU_VARIABLE`,
  `ACT_RU_JOB` / `ACT_RU_TIMER_JOB` / `ACT_RU_DEADLETTER_JOB`.
- History: `ACT_HI_PROCINST`, `ACT_HI_ACTINST`, `ACT_HI_TASKINST`,
  `ACT_HI_VARINST`, `ACT_HI_IDENTITYLINK`.

## "The instance disappeared" — triage

1. `/history/historic-process-instances?processInstanceId=X`
   - has `endTime` → it **completed**. Read the outcome variables from history. Done.
   - `deleteReason` set → it was **terminated/cancelled**. The reason field says by what.
2. No history row at all → it never started. Check the caller's error handling.
3. History row open but no runtime row → you're on the wrong engine or schema.
   Check the datasource before anything else.

## Two standing rules

- A row leaving runtime is *success*. Alert on runtime rows that **stay** (old
  instances, deep pools, due jobs), never on rows leaving.
- History grows forever until lesson 02's retention decision is made. If nobody
  owns retention, the DBA eventually owns an outage.
