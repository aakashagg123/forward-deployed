# Phase 07 — Planning and Subagents
*Part of [Harness engineering](../../README.md).*

A long task needs a plan, and a big task needs more than one agent. This phase covers both. You give the agent a todo list whose steps close only when a check passes. You put it in plan mode so it reads before it writes. Then you split work across subagents: a contract, waves with disjoint files, and a supervisor that sees results, not transcripts.

## Lessons

1. [The Todo List](./01-todo-list/docs/en.md) — a status list with one step in progress and verified completion.
2. [Plan Mode](./02-plan-mode/docs/en.md) — a read-only state until a human approves the plan.
3. [Contract, Waves and Isolation](./03-contract-waves-and-isolation/docs/en.md) — budget, parallel waves, file ownership and checkpoints.
4. [Supervisor and Workers](./04-supervisor-and-workers/docs/en.md) — delegate with role allowlists and take back only results.

## Where the depth lives

| If you want | Read |
| --- | --- |
| Planning and reasoning for agents, in product terms | [Planning and reasoning](../../../agentic-ai/planning-and-reasoning.md) |
| How to keep a plan on track across a long run | [Planning, reasoning and reliability across a run](../../../ai-agents/planning-reasoning-and-reliability-across-a-run.md) |
| When several agents help and when they hurt | [Orchestrating more than one agent](../../../agentic-workflows/orchestrating-more-than-one-agent.md) |
| Multi-agent systems and the protocols between them | [Multi-agent and protocols](../../../agentic-ai/multi-agent-and-protocols.md) |

## Test yourself

1. **Why must the harness, not the model, decide that a todo step is complete?**
   <details><summary>Answer</summary>A model that grades its own work marks steps done too early. The harness runs a done-check, and only a pass sets `completed`. A step that keeps failing goes to `needs_replan` instead of looping. (<a href="./01-todo-list/docs/en.md">Lesson 1</a>)</details>
2. **Plan mode lets the agent run `git status` but not edit a file. Why allow any shell command?**
   <details><summary>Answer</summary>A good plan needs exploration, and exploration uses read-only commands. The gate allows reads and read-only commands and denies everything that changes state. (<a href="./02-plan-mode/docs/en.md">Lesson 2</a>)</details>
3. **Why is "ask the model to plan first" weaker than plan mode?**
   <details><summary>Answer</summary>A prompt is a request the model can forget. Plan mode is a permission state, so a blocked edit stays blocked. It still has limits: in an interactive session with bypass permissions available, Claude Code does not enforce the blocks. (<a href="./02-plan-mode/docs/en.md">Lesson 2</a>)</details>
4. **Two independent tasks both own `api/routes.py`. What does the wave planner do, and why?**
   <details><summary>Answer</summary>It puts them in different waves. Two parallel workers on one file would silently overwrite each other, so no wave may share a file. (<a href="./03-contract-waves-and-isolation/docs/en.md">Lesson 3</a>)</details>
5. **A worker hits its call limit. What should the run do?**
   <details><summary>Answer</summary>It stops and reports. Budget ceilings are hard and never extend themselves, so a human decides whether to spend more. (<a href="./03-contract-waves-and-isolation/docs/en.md">Lesson 3</a>)</details>
6. **How can you test that a wave truly runs in parallel and not one task after another?**
   <details><summary>Answer</summary>Make two workers wait on a shared barrier with a timeout. If they run in series, the barrier times out and the test fails. (<a href="./03-contract-waves-and-isolation/docs/en.md">Lesson 3</a>)</details>
7. **Why does a reviewer subagent get the diff but not the plan?**
   <details><summary>Answer</summary>A reviewer who sees the plan explains the output instead of judging it. You enforce this when you build the prompt, so the plan is never in scope. (<a href="./04-supervisor-and-workers/docs/en.md">Lesson 4</a>)</details>
8. **What does a supervisor receive from a worker, and what does that buy you?**
   <details><summary>Answer</summary>A short result, not the worker's transcript. The supervisor's context stays small, and a worker crash becomes one failed result instead of a crashed run. (<a href="./04-supervisor-and-workers/docs/en.md">Lesson 4</a>)</details>
