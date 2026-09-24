# Task decomposition prompts

> **Motto** — A good plan is small, ordered, verifiable steps — prompt the model to produce exactly that.

*Part of Phase 11 — Planning & Task Management.*

## The Problem

"Add authentication" is not a plan — it's a wish. The quality of the agent's work depends on
how well it decomposes a fuzzy goal into concrete, ordered, independently-verifiable steps.
Left to improvise, models produce plans that are too coarse ("implement the feature") or too
fine (50 trivial steps). A decomposition *prompt* steers the model to the right grain.

## The Concept

```mermaid
flowchart LR
  G["fuzzy goal"] --> D["decomposition prompt"] --> P["3–7 steps: each small, ordered, verifiable"]
```

The rubric for a good step: it changes one coherent thing, has a clear done-check, and is
ordered by dependency.

## Build It (the prompt)

The artifact is a reusable decomposition prompt. `outputs/decompose.md` instructs the model
to output a numbered plan where each step names the change, the files, and the verification:

- 3–7 steps (merge trivial ones, split giant ones).
- Each step: **what** changes, **where** (files), **how to verify** (test/command).
- Order by dependency.
- Flag steps that need human input.
- End with the overall acceptance check.

This maps directly onto the todo model (lesson 01) and, scaled up, the sprint contract
(Phase 10).

## Use It

In Claude Code / Codex you trigger this by asking the agent to "plan first" (often in plan
mode, lesson 02). Putting a decomposition rubric in `CLAUDE.md`/`AGENTS.md` makes *every*
plan well-formed without re-asking. A good decomposition is also what makes parallelization
(Phase 10 waves) possible — independent steps can run concurrently.

## Ship It

[`outputs/decompose.md`](../../03-decomposition/outputs/decompose.md) — a task-decomposition
prompt that yields small, ordered, verifiable steps.

## Check Yourself

**Q1.** What makes a step in a good plan?

- A) it's vague enough to be flexible
- B) it changes one coherent thing, names files, and has a done-check, ordered by dependency
- C) it's as large as possible
- D) it has no verification

<details><summary>Answer</summary>B — small, located, verifiable, ordered.</details>

**Q2.** Why does good decomposition enable parallelization (Phase 10)?

- A) it doesn't
- B) independent, well-bounded steps can run concurrently in waves
- C) it makes steps bigger
- D) no reason

<details><summary>Answer</summary>B — independence is what waves exploit.</details>

**Challenge.** Add to the prompt a requirement that each step declare the files it touches,
so you can detect conflicts (Phase 10) before dispatching steps in parallel.

## Related

- Builds on: [Todo model](../../01-todo-model/docs/en.md)
- Next: [Progress tracking & self-correction](../../04-progress-tracking/docs/en.md)
- Scales to: Phase 10 — sprint contracts
- [Roadmap](../../../../ROADMAP.md)
