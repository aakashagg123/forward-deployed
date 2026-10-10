# Phase 10 — Capstone
*Part of [Harness engineering](../../README.md).*

One lesson joins the parts of the track in a single file. The agent has a loop, tools, a permission gate, output limits, a todo list, and a step budget. A test runs it against a real temp repo and checks the repo, not the agent's words.

## Lessons
1. [Assemble the agent](./01-assemble-the-agent/docs/en.md) — One 150-line agent, a scripted model, and a test that proves the parts work together.

## Test yourself
1. **Why does the test judge the agent by running the repo's own tests?**
   <details><summary>Answer</summary>The agent can say "fixed" and be wrong. The repo's test run is an independent check of the real outcome. (<a href="./01-assemble-the-agent/docs/en.md">Lesson 1</a>)</details>
2. **A command chains an allowed test run with `rm -rf .`. What does the gate decide, and why?**
   <details><summary>Answer</summary>It decides deny. Deny rules run first, and the `rm` pattern matches anywhere in the command. The allow rule never gets a vote. (<a href="./01-assemble-the-agent/docs/en.md">Lesson 1</a>)</details>
3. **Why must trimming drop old turns in pairs?**
   <details><summary>Answer</summary>A tool call and its result must stay together. If one is dropped alone, the model sees an orphan, and the API can reject the history. (<a href="./01-assemble-the-agent/docs/en.md">Lesson 1</a>)</details>
4. **What does the step budget do when the model loops forever?**
   <details><summary>Answer</summary>The loop stops after the set number of model calls and returns status `budget`. Every call made so far has its result in the history. (<a href="./01-assemble-the-agent/docs/en.md">Lesson 1</a>)</details>
5. **What changes when you swap the scripted model for the real SDK?**
   <details><summary>Answer</summary>Only the one function that turns history into content blocks. The loop, tools, gate, limits, and tests stay the same. (<a href="./01-assemble-the-agent/docs/en.md">Lesson 1</a>)</details>
