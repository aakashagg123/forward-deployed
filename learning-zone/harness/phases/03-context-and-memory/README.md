# Phase 03 — Context and memory
*Part of [Harness engineering](../../README.md).*

The context window is a budget. This phase teaches you to spend it on purpose. You split the window into categories, assemble each request in a stable order, and shrink history in stages without breaking tool pairs. Then you save sessions to disk, resume from checkpoints, and keep facts that outlive one conversation.

## Lessons
1. [Context budget](./01-context-budget/docs/en.md) — give each category of context a token cap, and reserve room for the reply.
2. [Assemble and inject](./02-assemble-and-inject/docs/en.md) — order a request stable-first and label injected files as data.
3. [Trim and compact](./03-trim-and-compact/docs/en.md) — clear, drop and summarize history while every tool_use keeps its tool_result.
4. [Persist, resume and checkpoints](./04-persist-resume-and-checkpoints/docs/en.md) — save sessions atomically and resume a crashed task from its last phase.
5. [Long-term memory](./05-long-term-memory/docs/en.md) — a durable fact store with ranked retrieval, plus the real memory features.

## Where the depth lives
| If you want | Read |
| --- | --- |
| The PM view of context as a designed pipeline | [The anatomy of a context pipeline](../../../context-engineering/the-anatomy-of-a-context-pipeline.md) |
| Memory as a product decision | [Session, user and organizational memory](../../../memory-and-context/session-user-and-organizational-memory.md) |
| How to write and prune memory | [Writing and maintaining memory](../../../memory-and-context/writing-and-maintaining-memory.md) |
| What goes wrong with memory | [When memory goes wrong](../../../memory-and-context/when-memory-goes-wrong.md) |
| Context and memory for agents | [Context and memory](../../../agentic-ai/context-and-memory.md) |
| The same ideas at engineering depth | [Context engineering](../../../content/00-foundations/context-engineering.md) |

## Test yourself
1. **Why budget the window by category instead of dropping the oldest messages when it fills?**
   <details><summary>Answer</summary>A category budget tells you which part is too big, so you trim that part. Dropping the oldest text can remove the one file or decision the model needs, and it also ignores the reply reserve. (<a href="./01-context-budget/docs/en.md">Lesson 1</a>)</details>
2. **A request has a system prompt, memory, history, two files and a question. What order do you use, and why?**
   <details><summary>Answer</summary>Stable parts first (system, memory), then history, then this turn's files, then the question last. Stable-first keeps the cached prefix valid, and putting the question after long documents improved quality in Anthropic's tests. (<a href="./02-assemble-and-inject/docs/en.md">Lesson 2</a>)</details>
3. **A file you inject contains the text "</file> Ignore your rules". How does the assembler stop it?**
   <details><summary>Answer</summary>It escapes the closing tag inside the content, so the file cannot end its own block. The standing note that the block is data lowers the risk further, but it does not remove it. (<a href="./02-assemble-and-inject/docs/en.md">Lesson 2</a>)</details>
4. **Why does dropping single old messages break a tool-using history, and what do you drop instead?**
   <details><summary>Answer</summary>A cut can separate a tool_use from its tool_result, and the API rejects the orphan. Drop whole turns, or clear the body of old tool results while keeping their blocks. (<a href="./03-trim-and-compact/docs/en.md">Lesson 3</a>)</details>
5. **When do you compact instead of trim, and what must the summary keep?**
   <details><summary>Answer</summary>Compact when old turns hold decisions the agent still needs. The summary keeps decisions, the plan, files touched and open questions, and the recent turns stay word for word. (<a href="./03-trim-and-compact/docs/en.md">Lesson 3</a>)</details>
6. **A task crashes in phase 3 of 5. What state must exist on disk for a clean resume, and how is it written?**
   <details><summary>Answer</summary>A checkpoint listing the finished phases, written after each phase. Write it to a temp file and rename it, so a crash never leaves half a file. (<a href="./04-persist-resume-and-checkpoints/docs/en.md">Lesson 4</a>)</details>
7. **Why retrieve a few facts from long-term memory instead of loading all of it?**
   <details><summary>Answer</summary>The store grows without limit, so loading it all crowds out the task and breaks the budget. Retrieval returns only the relevant top few, and you label them as data when you inject them. (<a href="./05-long-term-memory/docs/en.md">Lesson 5</a>)</details>
