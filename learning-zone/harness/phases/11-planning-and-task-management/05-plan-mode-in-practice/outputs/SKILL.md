---
name: plan-and-build
description: >
  Plan a non-trivial task before acting, then execute with verification.
  Trigger with /plan-and-build "<goal>", or "plan first then build", "make a plan
  for X".
version: 1.0.0
kind: skill
phase: 11
lesson: 5
---

# Plan and build

Run any non-trivial task through: decompose → approve → execute (verified) → re-plan on
stall. Do not start editing before the plan is approved.

## Procedure

1. **Decompose.** Produce a numbered plan: 3–7 steps, each naming *what* changes, *which
   files*, and *how to verify* (test/command). Order by dependency. (See the
   task-decomposition prompt, Phase 11 L3.)
2. **Plan mode.** Stay read-only — analyze and present the plan. **Stop and ask for
   approval.** Do not write/edit/run mutating commands yet.
3. **Execute.** After approval, work one step at a time. Keep a visible todo list with
   exactly one item in progress. Run each step's verification. Only mark it complete when
   the check passes.
4. **Self-correct.** If a step fails after a small retry budget, stop grinding — re-plan
   that step or escalate to the human. Never mark a step done that didn't verify.
5. **Finish.** Run the overall acceptance check. Report honestly: if tests fail, say so
   with output.

## Notes
- For a large goal with independent steps, offer to dispatch them in parallel (Phase 10).
- Append anything learned to `knowledge.md` (Phase 9) at the end.
