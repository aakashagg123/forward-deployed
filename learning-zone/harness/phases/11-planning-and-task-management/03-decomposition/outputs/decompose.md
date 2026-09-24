---
name: task-decomposition
description: Turn a fuzzy goal into a small, ordered, verifiable plan.
kind: prompt
phase: 11
lesson: 3
---

# Decompose this task

Produce a numbered plan for the goal below. Rules:

- **3–7 steps.** Merge trivial steps; split steps that change many unrelated things.
- **Each step states:**
  - *What* changes (one coherent change).
  - *Where* — the files it touches.
  - *How to verify* — the test or command that proves it's done.
- **Order by dependency.** A step must not depend on a later one.
- **Flag** any step that needs human input or is irreversible (confirm first).
- **End** with the overall acceptance check for the whole goal.

Do not start implementing. Output only the plan, then stop for approval.

GOAL: <fill in>
