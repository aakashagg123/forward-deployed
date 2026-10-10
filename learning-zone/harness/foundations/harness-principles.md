# The ten principles of a working harness

*Harness Engineering · Foundations. See the [Roadmap](../ROADMAP.md).*

*Last reviewed: 2026-10 · Volatility: medium*

## TL;DR

A harness is the system that runs agents. Its job is to spend human attention only on
decisions that matter, and never twice on the same class of problem. This page lists ten
principles for one specific pattern: a multi-agent pipeline with a signed contract, budgeted
waves, and an independent review. It is one pattern, not the only one. Phase 7 builds it.

When an agent repeats a mistake, the fix is almost never a longer prompt. The fix is to add
the missing structure to the repo.

> 🎯 **For the engineer**
>
> **Why it matters** — These principles are the difference between an agent demo and a
> pipeline you can run on real work. They say where the human gates are and what the
> budget ceiling is.
>
> **Ask your team** — *"When an agent makes the same mistake twice, do we lengthen the
> prompt or add an enforced rule?"* The right answer is the rule.

## The principles

Any numbers you meet in phase 7, such as worker or wave limits, are example values from
one team. Treat them as starting points to test, not as standards.

| # | Principle | The lesson it encodes |
| --- | --- | --- |
| 01 | **Spec first** | Lock a contract (tasks, files in scope, acceptance criteria, budget) and get human approval before any worker runs. |
| 02 | **Bounded roles, bounded context** | Each agent sees only what its role needs. A reviewer who sees the plan defends it. Enforce this with an explicit allowlist in prompt construction. |
| 03 | **Declare the budget upfront** | Set the worker, call and wave limits before dispatch. On a hit, stop and report. Never auto-extend. |
| 04 | **Hard stops between waves** | After each wave the orchestrator summarizes and waits for a human "continue." |
| 05 | **Independent adversarial review** | The reviewer sees only the diff and, in this pattern, gives one of two verdicts: ship or hold. |
| 06 | **File isolation per worker** | Each worker gets its own worktree and no shared files in a wave. Shared files cause silent overwrites. |
| 07 | **Persistent memory** | Keep an append-only record of failures: symptom, cause, fix. Keep the main instruction file short. |
| 08 | **Patch the harness, not the prompt** | Encode a repeated fix once, as a lint rule or a contract test. Then delete the matching prose from the prompt. |
| 09 | **Right-size before dispatching** | Orchestration has overhead. Use a single agent unless parallel work clearly saves time. |
| 10 | **Checkpoint everything** | Workers write progress files so an interrupted run resumes instead of restarting. |

## Where each principle is built

| Principle | Lesson |
| --- | --- |
| 01, 03, 04, 06 | [Contract, waves and isolation](../phases/07-planning-and-subagents/03-contract-waves-and-isolation/docs/en.md) |
| 02, 05 | [Supervisor and workers](../phases/07-planning-and-subagents/04-supervisor-and-workers/docs/en.md) |
| 07 | [Memory files](../phases/04-prompts-and-instructions/02-memory-files/docs/en.md) and [long-term memory](../phases/03-context-and-memory/05-long-term-memory/docs/en.md) |
| 08 | [Hooks](../phases/06-permissions-and-security/02-hooks/docs/en.md) |
| 09 | [Budgets, idempotency and degraded mode](../phases/09-reliability-evals-and-ops/02-budgets-idempotency-degraded-mode/docs/en.md) |
| 10 | [Persist, resume and checkpoints](../phases/03-context-and-memory/04-persist-resume-and-checkpoints/docs/en.md) |

For other orchestration patterns and their costs, see
[Agentic workflows](../../agentic-workflows/README.md).
