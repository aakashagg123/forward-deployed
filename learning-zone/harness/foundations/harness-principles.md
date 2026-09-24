# The ten principles of a working harness

*Harness Engineering · Foundations. See the [Roadmap](../ROADMAP.md).*

## TL;DR

A harness is the system that orchestrates agents. Its job is to spend **human attention
only on decisions that matter — and never twice on the same class of problem**. Ten
principles form its skeleton. Each principle encodes a lesson. Skip it, and the lesson
resurfaces as a runtime failure: wasted tokens, corrupted state, or an agent confidently
doing the wrong thing. The fix is almost never "try harder" or "write a longer prompt."
It's to add the missing *structural* capability to the repo.

> 🎯 **For the AI-native PM**
>
> **Why it matters** — These ten principles are the difference between an agent demo
> and an agent *pipeline* you can run on real work. They tell you where the human gates
> are, who's accountable, and what the budget ceiling is.
>
> **What it changes in your decisions** — How you scope agent work, where you insert
> approval gates, and how you read a "the agent did it" claim.
>
> **Ask your eng team** — *"When an agent makes the same mistake twice, do we lengthen
> the prompt or add an enforced rule?"* (The right answer is the rule.)
>
> **Product risk if ignored** — Runaway cost, silent overwrites between parallel
> agents, and review that rationalises instead of evaluating.

## The principles

| # | Principle | The lesson it encodes |
| --- | --- | --- |
| 01 | **Spec first, always** | Lock the sprint contract — tasks, files in scope, acceptance criteria, budget ceilings — and halt for human approval *before* any worker fires. Everything after is execution against a known target. |
| 02 | **Bounded roles, bounded context** | Each agent sees only what its role needs. The reviewer sees the diff, never the plan — context leakage turns review into rationalisation. Enforce via an explicit read allowlist in prompt construction, not agent self-restraint. |
| 03 | **Declare the budget upfront** | Every run declares `maxWorkers`, `maxCallsPerWorker`, `maxWaves` before dispatch. Human attention is the scarce resource. Budget it like compute. On a hit, stop and report — never auto-extend. |
| 04 | **Hard stops between waves** | After each parallel wave the orchestrator emits a one-line summary and halts. The next wave needs an explicit human "continue." Each break is a real decision: proceed, pivot, or stop. |
| 05 | **Independent adversarial review** | The reviewer gets only the diff. Score across seven named, weighted dimensions. A composite below **70** blocks the wave. Two verdicts only: **ship** or **hold** — no "ship with caveats." |
| 06 | **File isolation per worker** | Each worker runs in its own git worktree. Zero shared files per wave, enforced by the dependency graph. Shared files between parallel workers cause merge conflicts and silent overwrites — the worst harness failure. |
| 07 | **Persistent cross-sprint memory** | `knowledge.md` is the append-only system of record — evidence only, no opinions. Each entry: symptom, root cause, fix. A short `AGENTS.md` (~100 lines) is a table of contents, not an encyclopedia. |
| 08 | **Patch the harness, not the prompt** | When an agent repeats a class of mistake, encode the fix once — as a lint rule, a pattern file, or a contract test. Then delete the matching prose from the prompt. The rule is now the authority. |
| 09 | **Right-size before dispatching** | The harness has real overhead (≥5 orchestration turns before any code). Apply the **45-minute test**: would parallelising save more than 45 minutes of sequential work? If not, implement directly. |
| 10 | **Checkpoint everything** | Workers write progressive `checkpoint.md` files — phase done, what changed, next step. An interrupted run resumes from the last checkpoint, not from zero. |

## The pipeline these principles produce

```
spec ──▶ [planning agent] ──▶ sprint contract ──▶ (human approval gate)
            │
            ▼
        [discovery agent] ──▶ codebase map + dependency graph
            │
            ▼
   ┌─ wave ───────────────────────────────────────────┐
   │  [worker]  [worker]  [worker]   (isolated worktrees)│
   └────────────────────────────┬──────────────────────┘
            │ diff only
            ▼
        [review agent] ──▶ ship / hold  (score ≥ 70)
            │
            ▼ (human "continue")  ── hard stop between waves
            ▼
        [memory agent] ──▶ append to knowledge.md
```

Five agents, five turns of orchestration minimum. Deploy it only when **coordination
complexity is the bottleneck** (principle 09).

## Failure modes (one per principle skipped)

- **No contract (01)** → workers build the wrong thing, fast and in parallel.
- **Leaked context (02)** → the reviewer defends the author's intent instead of judging output.
- **No budget (03)** → a wave runs 40 steps and spends $12.
- **Auto-chained waves (04)** → no decision point; scope drifts unchecked.
- **Soft review (05)** → "ship with caveats" lands defects that never get fixed.
- **Shared files (06)** → silent overwrites and merge conflicts.
- **No memory (07)** → the same failure recurs every sprint.
- **Prompt patching (08)** → an ever-growing system prompt nobody reads.
- **Over-dispatch (09)** → five orchestration turns to fix a two-line bug.
- **No checkpoints (10)** → an interrupted wave is re-run from the beginning.

## Practitioner checklist

- [ ] Is there a signed sprint contract with a budget ceiling before any worker runs?
- [ ] Does each agent have an explicit read allowlist?
- [ ] Does the orchestrator hard-stop between waves and wait for a human?
- [ ] Does the reviewer see only the diff, and is the threshold a hard 70?
- [ ] Are parallel workers guaranteed zero shared files?
- [ ] Does every recurring mistake become a rule (and leave the prompt)?
- [ ] Can any interrupted run resume from a checkpoint?

## Related

- The [Roadmap](../ROADMAP.md) — where each principle becomes a phase.
- Build it: [The agent loop from scratch](../phases/02-the-agent-loop/01-agent-loop/docs/en.md)
- Build it: [Sprint contracts & budgeted waves](../phases/10-subagents-and-orchestration/01-sprint-contract-and-waves/docs/en.md)
- Other tracks: [The method: deconstruct, challenge, reconstruct](../../first-principles/the-method.md) — reasoning an engine up from fundamentals.
