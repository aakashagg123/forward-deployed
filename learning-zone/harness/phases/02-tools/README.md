# Phase 02 — Tools
*Part of [Harness engineering](../../README.md).*

A tool is a function plus a schema. The model reads the schema and the description, then names a tool and its arguments. The harness validates the call, runs it, and shapes the result. This phase builds the registry, the validator, the result envelope, and batched execution. It builds on the loop from Phase 01.

## Lessons
1. [Schemas, Registry and Descriptions](./01-schemas-registry-and-descriptions/docs/en.md) — one place to define, list, scope, and run tools.
2. [Validation, Results and Errors](./02-validation-results-and-errors/docs/en.md) — check arguments first, then return a capped, labeled result.
3. [Parallel Tool Use](./03-parallel-tool-use/docs/en.md) — run independent calls together and answer them in one message.

## Where the depth lives
| If you want | Read |
| --- | --- |
| The product view of tools and function calling | [Tools and function calling](../../../agentic-ai/tools-and-function-calling.md) |
| Function calling as a reliability pattern | [Function calling](../../../content/02-reliable-outputs/function-calling.md) |
| Forcing a fixed output shape | [Structured output](../../../content/02-reliable-outputs/structured-output.md) |
| Guardrails around what an agent may do | [Agent guardrails](../../../content/02-reliable-outputs/agent-guardrails.md) |
| Why a schema is a contract | [APIs and contracts](../../../technical-product-sense/apis-and-contracts.md) |

## Test yourself
1. **The model keeps calling the wrong tool. What do you change first, and why?**
   <details><summary>Answer</summary>The tool descriptions. The model picks a tool from its name and description. State what the tool does, when to use it and when not to, what each parameter means, and what it returns. (<a href="./01-schemas-registry-and-descriptions/docs/en.md">Lesson 1</a>)</details>
2. **A reviewer role must not delete files. Is removing `delete_file` from its schema list enough?**
   <details><summary>Answer</summary>No. Hiding the schema only stops the model from asking. Dispatch must also refuse the call, because a model can still name a tool it was not shown. (<a href="./01-schemas-registry-and-descriptions/docs/en.md">Lesson 1</a>)</details>
3. **A provider offers `strict: true`. Why still validate arguments yourself?**
   <details><summary>Answer</summary>Your check covers rules a schema cannot express, such as a path that must stay in the project. You also control the error wording, so the model can fix the call in one retry. (<a href="./02-validation-results-and-errors/docs/en.md">Lesson 2</a>)</details>
4. **A tool returns 50 KB of text. What do you send back?**
   <details><summary>Answer</summary>A capped `tool_result` with a visible note that says how much was cut and how to ask for the rest. A silent cut makes the model reason over a partial result as if it were whole. (<a href="./02-validation-results-and-errors/docs/en.md">Lesson 2</a>)</details>
5. **Why must a validation error be an `is_error` result and not an exception?**
   <details><summary>Answer</summary>An exception ends the loop and the model never sees it. A result lets the model read the message and retry with corrected arguments. (<a href="./02-validation-results-and-errors/docs/en.md">Lesson 2</a>)</details>
6. **A turn has three `tool_use` blocks: two reads and a write. How do you run them and what do you return?**
   <details><summary>Answer</summary>Run the batch in order, because it contains a write. Return one `tool_result` for each block in a single user message. If a call fails, answer the skipped calls with `is_error` results. (<a href="./03-parallel-tool-use/docs/en.md">Lesson 3</a>)</details>
