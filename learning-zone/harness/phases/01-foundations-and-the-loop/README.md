# Phase 01 — Foundations and the Loop
*Part of [Harness engineering](../../README.md).*

A model call is one HTTPS POST. A harness is a loop around it. This phase builds both from the standard library. You make a raw call, count tokens, lay out a request for caching, and write the agent loop. Then you add stop rules, error recovery, and streaming. Every later phase attaches to this loop. Each lesson ends with a short SDK version of the same code.

## Lessons
1. [First Call and a REPL](./01-first-call-and-repl/docs/en.md) — the raw POST, message roles, and a loop that keeps history.
2. [Tokens, Context and Caching](./02-tokens-context-and-caching/docs/en.md) — count tokens, respect the window, and keep the prompt prefix stable.
3. [The Agent Loop](./03-the-agent-loop/docs/en.md) — call, act, feed back, repeat, with paired tool results.
4. [Stopping, Errors and Recovery](./04-stopping-errors-and-recovery/docs/en.md) — stop reasons, error classes, retries, and ceilings.
5. [The Streaming Loop](./05-the-streaming-loop/docs/en.md) — parse server-sent events and act on the finished message.

## Where the depth lives
| If you want | Read |
| --- | --- |
| The concept of an agent, without code | [What is an agent?](../../../agentic-ai/what-is-an-agent.md) |
| Why the harness matters as much as the model | [Harness engineering](../../../content/00-foundations/harness-engineering.md) |
| What caching does inside the inference server | [Prompt vs. semantic caching](../../../content/01-inference-internals/prompt-vs-semantic-caching.md) |
| How the KV cache behind a prefix works | [KV cache management](../../../content/01-inference-internals/kv-cache-management.md) |
| Why decode is slow and prefill is fast | [Prefill vs. decode](../../../content/01-inference-internals/prefill-vs-decode.md) |
| How to manage what fills the window | [Context engineering](../../../content/00-foundations/context-engineering.md) |

## Test yourself
1. **The model keeps no state. How does the loop remember the conversation, and what does that cost you?**
   <details><summary>Answer</summary>The loop sends the whole message list, tool results included, on every call. The input grows each turn, so cost and latency grow too, and the window can fill. (<a href="./03-the-agent-loop/docs/en.md">Lesson 3</a>)</details>
2. **An assistant turn contains a `tool_use`. What must the next message hold, and what happens if you get it wrong?**
   <details><summary>Answer</summary>It must be a user message with a `tool_result` for each `tool_use` id, with the results before any text. Otherwise the API rejects the request with a 400 error. (<a href="./03-the-agent-loop/docs/en.md">Lesson 3</a>)</details>
3. **You add a timestamp to the top of the system prompt, and cache reads drop to zero. Why?**
   <details><summary>Answer</summary>The cache matches a prefix byte for byte. A changed byte early in the prefix invalidates it and everything after it. Put volatile text last. (<a href="./02-tokens-context-and-caching/docs/en.md">Lesson 2</a>)</details>
4. **A reply ends with `max_tokens` and its last block is a half-written `tool_use`. What do you do?**
   <details><summary>Answer</summary>Do not run it, because the input is incomplete. A production loop retries once with a higher `max_tokens`. For cut-off plain text you can ask the model to continue instead. (<a href="./04-stopping-errors-and-recovery/docs/en.md">Lesson 4</a>)</details>
5. **A tool raises a timeout, and another raises a permission error. How should the loop treat each?**
   <details><summary>Answer</summary>Retry the timeout with backoff a bounded number of times. Treat the permission error as fatal and end the run. Other failures go back to the model as `is_error` results. (<a href="./04-stopping-errors-and-recovery/docs/en.md">Lesson 4</a>)</details>
6. **Why must a "you repeated that call" nudge be sent as a `tool_result` and not as plain user text?**
   <details><summary>Answer</summary>The repeated `tool_use` is still unanswered. A plain text message in its place breaks the pairing rule and the API rejects the next call. (<a href="./04-stopping-errors-and-recovery/docs/en.md">Lesson 4</a>)</details>
7. **While streaming, you see the first `input_json_delta` of a tool call. Why can you not run the tool yet?**
   <details><summary>Answer</summary>The fragments are not valid JSON until the content block stops. Join them, parse at `content_block_stop`, and act only on the finished message. (<a href="./05-the-streaming-loop/docs/en.md">Lesson 5</a>)</details>
