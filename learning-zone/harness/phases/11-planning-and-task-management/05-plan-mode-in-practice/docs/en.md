# Use it: plan mode in a real harness

> **Motto** — Wire decomposition, plan mode, the todo list, and progress tracking into one workflow.

*Part of Phase 11 — Planning & Task Management. Completes the phase.*

## The Problem

You've built the pieces — task model (01), plan-mode gate (02), decomposition prompt (03),
progress tracker (04). The payoff is a single workflow a Claude Code / Codex user runs on any
non-trivial task: **decompose → review in plan mode → execute with verification → re-plan on
stall**. This lesson packages that as a skill.

## The Concept

```mermaid
flowchart LR
  G["goal"] --> D["decompose → plan"]
  D --> R{"approve (plan mode)"}
  R -- "no" --> D
  R -- "yes" --> E["execute step, verify (progress)"]
  E --> C{"all complete?"}
  C -- "no, stalled" --> D
  C -- "yes" --> DONE["done"]
```

## Build It / Use It

The artifact is `outputs/SKILL.md` — a `/plan-and-build` skill that runs the loop using this
phase's discipline. It produces a decomposed plan, then stops in plan mode for approval.
After approval, it executes each step and checks it off only when verification passes.
If a step stalls, it re-plans.

## Use It

Install the skill and run `/plan-and-build "<goal>"` in Claude Code / Codex. It enforces the
habits this phase teaches: plan before acting, keep a visible todo list, verify each step,
and re-plan instead of grinding. For most users, this is the single highest-leverage workflow. It turns "the agent went off
and did something" into "the agent and I agreed on a plan, and I watched it land."

## Ship It

[`outputs/SKILL.md`](../../05-plan-mode-in-practice/outputs/SKILL.md) — a `/plan-and-build`
skill composing the phase.

## Check Yourself

**Q1.** The plan-and-build loop's order is…

- A) act, then plan
- B) decompose → approve (plan mode) → execute with verification → re-plan on stall
- C) execute → verify → decompose
- D) random

<details><summary>Answer</summary>B — plan first, verify throughout, re-plan when
stuck.</details>

**Q2.** Why is this the highest-leverage workflow for a coding-agent user?

- A) it's fastest
- B) it gives a checkpoint before work and verified progress during it
- C) it uses fewer tokens
- D) no reason

<details><summary>Answer</summary>B — alignment up front + real progress.</details>

**Challenge.** Extend the skill so that, for a large goal, it offers to dispatch independent
steps in parallel (Phase 10 waves) instead of sequentially.

## Related

- Builds on: the whole phase
- Scales to: Phase 10 — Orchestration
- Phase complete → next: Phase 12 — [MCP & Extensibility](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
