# Phase 04 — Prompts and instructions
*Part of [Harness engineering](../../README.md).*

Three layers of text steer an agent. The system prompt sets its role and rules. Memory files carry project facts into every session. Output contracts say what a reply must look like. This phase builds each layer, lints it, and shows where a prompt must hand off to code that enforces the rule.

## Lessons
1. [System prompt and steering](./01-system-prompt-and-steering/docs/en.md) — five sections in a stable order, steering lines, and a guard that enforces what the prompt only asks.
2. [Memory files](./02-memory-files/docs/en.md) — keep CLAUDE.md and AGENTS.md short, checkable and pointer-based.
3. [Output contracts](./03-output-contracts/docs/en.md) — extract, validate and re-prompt, with a retry bound.

## Where the depth lives
| If you want | Read |
| --- | --- |
| The anatomy of a prompt at PM depth | [The anatomy of a prompt](../../../prompt-engineering/the-anatomy-of-a-prompt.md) |
| Prompting inside coding agents | [Prompting inside coding agents](../../../prompt-engineering/prompting-inside-coding-agents.md) |
| Structured output patterns | [Structured prompting](../../../prompt-engineering/structured-prompting.md) |
| Why prompts fail | [When prompts fail](../../../prompt-engineering/when-prompts-fail.md) |
| The principles behind a lean memory file | [Ten principles of a working harness](../../foundations/harness-principles.md) |

## Test yourself
1. **Why must volatile data such as today's date stay out of the system prompt?**
   <details><summary>Answer</summary>The system prompt is the cached prefix. One changed byte early in it invalidates the cache for everything after it, so per-turn facts belong in the user message. (<a href="./01-system-prompt-and-steering/docs/en.md">Lesson 1</a>)</details>
2. **Your prompt says "Never edit .env", yet the agent edits it once. What was wrong with the design?**
   <details><summary>Answer</summary>A prompt only asks, and models can fail to comply. A rule that must hold needs enforcing code, such as a hook that denies the edit, with the prompt line as the polite explanation. (<a href="./01-system-prompt-and-steering/docs/en.md">Lesson 1</a>)</details>
3. **Where do a tone rule, an ask-before-deleting rule and a refusal style each belong?**
   <details><summary>Answer</summary>Tone belongs in the output contract, ask-before-deleting in the workflow, and the refusal style in the constraints. Each steering line goes in the section it shapes. (<a href="./01-system-prompt-and-steering/docs/en.md">Lesson 1</a>)</details>
4. **Moving rules behind an @import keeps CLAUDE.md short. Does it save context?**
   <details><summary>Answer</summary>No. Imported files load at launch with the file that imports them, so the cost stays. To save context, move path-specific rules to scoped rule files or use a skill that loads on demand. (<a href="./02-memory-files/docs/en.md">Lesson 2</a>)</details>
5. **The agent keeps repeating the same mistake. Why not just add a paragraph to CLAUDE.md?**
   <details><summary>Answer</summary>Longer files lower adherence and cost budget every turn. Fix the harness instead, with a lint rule or a hook, and keep the file to facts that hold in every session. (<a href="./02-memory-files/docs/en.md">Lesson 2</a>)</details>
6. **A model returns valid JSON wrapped in prose with a trailing comma. What does the harness do, and what stops an endless loop?**
   <details><summary>Answer</summary>It extracts the block, repairs the comma, then validates keys and types. When a reply still fails, it re-prompts with the exact violation, and a retry budget makes it fail loudly after a few attempts. (<a href="./03-output-contracts/docs/en.md">Lesson 3</a>)</details>
7. **When do you rely on the prompt contract alone, and when do you add a check or a schema?**
   <details><summary>Answer</summary>A human reader can tolerate small drift, so the prompt is enough. Machine-read output needs a check, and a JSON schema through structured outputs where the API supports it. (<a href="./03-output-contracts/docs/en.md">Lesson 3</a>)</details>
