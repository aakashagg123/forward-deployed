# Phase 05 — Files and Shell
*Part of [Harness engineering](../../README.md).*

A coding agent works through two tool families. File tools read, search and change code. The shell tool runs everything else. This phase builds both from the standard library. Each tool gets a safety rule: numbered reads, unique edits, capped searches, deadlines, honest shell state, and a default-deny egress guard. The last lesson says plainly what resource limits do not stop.

## Lessons
1. [Read: Numbered Lines and Bounded Ranges](./01-read/docs/en.md) — a read tool the model can cite and page through.
2. [Edit, Write and Patch: Change Files Safely](./02-edit-write-and-patch/docs/en.md) — exact-string edits, read-gated writes, atomic patches.
3. [Search: Glob by Name, Grep by Content](./03-search/docs/en.md) — find the right lines without reading the repo.
4. [Bash: Capture Everything and Set a Deadline](./04-bash-and-timeouts/docs/en.md) — three signals, process-group kill, bounded output.
5. [Background Jobs and Shell State](./05-background-jobs-and-shell-state/docs/en.md) — long-running jobs, and what survives between calls.
6. [Sandbox and Egress: Limits, Allowlists, and Honest Gaps](./06-sandbox-and-egress/docs/en.md) — a parsing egress guard and resource limits.

## Where the depth lives
| If you want | Read |
| --- | --- |
| How tool contracts and error results should look | [Tool contracts and reliability](../../../tool-calling/tool-contracts-and-reliability.md) |
| The blast radius of a tool and the trust boundary | [Permissions, blast radius and the trust boundary](../../../tool-calling/permissions-blast-radius-and-the-trust-boundary.md) |
| The threat model behind egress control | [The threat model and guardrails](../../../ai-security-and-guardrails/the-threat-model-and-guardrails.md) |
| The product view of agent tools | [Tools and function calling](../../../agentic-ai/tools-and-function-calling.md) |

## Test yourself
1. **Why does a read tool return line numbers and a footer such as `call read with offset=8`?**
   <details><summary>Answer</summary>Numbers let the model cite and target exact lines. The footer tells it how to page on, so a large file is read on purpose and not swallowed whole. (<a href="./01-read/docs/en.md">Lesson 1</a>)</details>
2. **An edit's `old` string matches twice. What should the tool do, and what second gate guards a write?**
   <details><summary>Answer</summary>It refuses and asks for more context, because a guessed spot is worse than a rejected edit. A write to an existing file also needs a prior read with an unchanged digest. (<a href="./02-edit-write-and-patch/docs/en.md">Lesson 2</a>)</details>
3. **Why does a multi-file patch validate every hunk before it writes anything?**
   <details><summary>Answer</summary>One failed hunk must not leave the tree half edited. Staging in memory means later hunks see earlier ones, and the disk changes only if all pass. (<a href="./02-edit-write-and-patch/docs/en.md">Lesson 2</a>)</details>
4. **Glob and Grep both skip `.git` and cap their results. Why?**
   <details><summary>Answer</summary>Vendored and VCS folders fill the output with noise. A cap with a truncation note keeps results inside the context budget and tells the model to narrow the query. (<a href="./03-search/docs/en.md">Lesson 3</a>)</details>
5. **A command hangs. Why kill the process group, and how does Claude Code differ?**
   <details><summary>Answer</summary>Killing only the shell leaves its children running, so the group is killed. Claude Code does not kill a foreground command at its timeout. It moves the command to the background, unless it starts with `sleep`. (<a href="./04-bash-and-timeouts/docs/en.md">Lesson 4</a>)</details>
6. **In Claude Code, one call runs `cd backend`, another runs `export TOKEN=x`, a third runs `npm test`. What does the third call see?**
   <details><summary>Answer</summary>It runs in `backend`, because the cwd carries over inside the project. `TOKEN` is gone, because exports do not persist unless `CLAUDE_ENV_FILE` or a SessionStart hook sets them. (<a href="./05-background-jobs-and-shell-state/docs/en.md">Lesson 5</a>)</details>
7. **Why does a regex for `https://` URLs fail as an egress guard?**
   <details><summary>Answer</summary>`curl evil.test`, `nc host`, `sh -c '...'`, `$(...)` and `/dev/tcp` use no URL. A guard must parse the command, check every network program and host argument, and deny what it cannot verify. (<a href="./06-sandbox-and-egress/docs/en.md">Lesson 6</a>)</details>
8. **What do `setrlimit` limits and a stripped environment stop, and what do they leave open?**
   <details><summary>Answer</summary>They cap CPU, memory and file size, and they keep parent secrets out of the child. The child can still read files and open sockets, so you need an OS sandbox for real containment. (<a href="./06-sandbox-and-egress/docs/en.md">Lesson 6</a>)</details>
