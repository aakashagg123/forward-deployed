---
name: agent-team
description: >
  Orchestrate a five-agent sprint pipeline (planning, discovery, worker, review,
  memory) with budgeted, hard-stopped waves. Trigger with /agent-team "<goal>" to
  start a sprint, or /agent-team continue to proceed after a wave break.
version: 1.0.0
kind: skill
phase: 10
lesson: 06
tags: [orchestration, subagents, waves, review]
---

# Agent team

You orchestrate a sprint pipeline of five bounded-role agents. Spend human attention only
on decisions that matter (the contract approval and the wave gates). Never auto-chain.

## Budget defaults (declare in the contract — never auto-extend)

- maxWorkers: 3 · maxCallsPerWorker: 15 · maxWaves: 2

## The pipeline

1. **Planning agent** — input: the goal/spec only. Output: a sprint contract
   (`sprint_name`, `tasks[]` with file ownership + deps, `budget`, `acceptance_criteria`)
   plus 2–3 architecture options. **STOP and get human approval before any worker runs.**
2. **Discovery agent** — input: contract + codebase. Output: a codebase map and a
   dependency graph that assigns each task disjoint files.
3. **Worker agents** — each runs in its own `git worktree` off feature head, owns only its
   files, and writes a `checkpoint.md` after each phase. Zero shared files per wave.
4. **Review agent** — input: the **diff only** (never the plan or spec). Score seven
   weighted dimensions (correctness, security, regression risk, type safety, test
   coverage, requirements traceability, one domain rule). Composite < 70 = **hold**.
   Otherwise, **ship**. No "ship with caveats".
5. **Memory agent** — input: the review report. Append precise entries (symptom, root
   cause, fix) to `_agent-team/knowledge.md`. Evidence only, no opinions.

## Wave discipline

- After each wave: emit a one-line summary and **HALT**. Wait for the human to say
  `continue` before dispatching the next wave.
- On any budget ceiling hit (workers, calls, waves): stop and report. Do not extend.
- Right-size first: if parallelising wouldn't save >45 minutes of sequential work,
  recommend implementing directly instead of running the pipeline.

## Bounded-role context (enforce by construction)

| Agent | May read |
|-------|----------|
| planning | the goal/spec |
| discovery | contract + codebase |
| worker | its contract entry + its owned files |
| review | the diff |
| memory | the review report |

## Commands

- `/agent-team "<goal>"` — start: produce the contract, then stop for approval.
- `/agent-team continue` — proceed to the next wave after a break.

## Smoke test

`/agent-team "add a health-check route returning {status: ok}"`
