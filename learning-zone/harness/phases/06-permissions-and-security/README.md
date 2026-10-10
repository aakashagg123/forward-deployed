# Phase 06 — Permissions and Security
*Part of [Harness engineering](../../README.md).*

A harness must stay safe when the model is wrong or hijacked. This phase builds the layers: a permission gate with a fixed rule order, hooks that run as code, a settings file that declares both, and a test for prompt injection that can fail. Each lesson says what its layer cannot stop, so you know why you need the next one.

## Lessons
1. [Permission Gate: Allow, Ask, Deny](./01-permission-gate/docs/en.md) — rules, modes and approvals, with deny checked first.
2. [Hooks: Rules That Run as Code](./02-hooks/docs/en.md) — the stdin JSON and exit-code protocol, with a working `.env` hook.
3. [Settings.json: Declare the Safety Layer](./03-settings-json/docs/en.md) — a real config file and a lint that can fail.
4. [Untrusted Content: Treat What the Agent Reads as Data](./04-untrusted-content/docs/en.md) — fence, gate, egress guard, redaction, and an eval that measures side effects.

## Where the depth lives
| If you want | Read |
| --- | --- |
| Permissions and blast radius for tools | [Permissions, blast radius and the trust boundary](../../../tool-calling/permissions-blast-radius-and-the-trust-boundary.md) |
| The threat model and guardrails for AI products | [The threat model and guardrails](../../../ai-security-and-guardrails/the-threat-model-and-guardrails.md) |
| Access control for agents (identity, roles, policy) | [Access control for AI agents](../../../access-control/access-control-for-ai-agents.md) |
| Safety, security and governance of agentic products | [Safety, security and governance](../../../agentic-ai/safety-security-and-governance.md) |

## Test yourself
1. **`Bash(aws s3 ls)` is allowed and `Bash(aws *)` is denied. Does `aws s3 ls` run?**
   <details><summary>Answer</summary>No. Rules run in the order deny, ask, allow, and the first match wins. Specificity does not change the order, so a narrow allow cannot carve an exception out of a deny. (<a href="./01-permission-gate/docs/en.md">Lesson 1</a>)</details>
2. **The rule `Bash(git status *)` is allowed. Why does `git status && git push origin` not run without a prompt?**
   <details><summary>Answer</summary>The gate splits the command into subcommands. An allow rule must cover every part, so the unmatched `git push` makes the call ask. A deny rule on `git push` would block the whole call. (<a href="./01-permission-gate/docs/en.md">Lesson 1</a>)</details>
3. **A PreToolUse hook crashes with exit code 1. Does the tool call run? How do you write a hook that fails closed?**
   <details><summary>Answer</summary>Yes, the call runs, because only exit 2 (or a deny decision in JSON) blocks. A safe hook exits 2 itself when it cannot parse its input or reach a verdict. (<a href="./02-hooks/docs/en.md">Lesson 2</a>)</details>
4. **A hook returns `permissionDecision: "allow"`, but a deny rule matches the call. What happens?**
   <details><summary>Answer</summary>The deny rule wins. A hook allow does not bypass deny or ask rules. A hook that exits 2 blocks the call before the rules even run. (<a href="./02-hooks/docs/en.md">Lesson 2</a>)</details>
5. **Why does `Write(src/**)` in a permissions list do nothing?**
   <details><summary>Answer</summary>Claude Code consults only `Edit(path)` and `Read(path)` for file paths. Rules for Write, Glob, NotebookEdit and MultiEdit are accepted and never used, so you write `Edit(src/**)` instead. (<a href="./03-settings-json/docs/en.md">Lesson 3</a>)</details>
6. **Why is a `Bash(rm *)` deny rule not a security boundary, and what do you add?**
   <details><summary>Answer</summary>It matches command text, so `/bin/rm` and `bash -c 'rm ...'` slip past it. Add a PreToolUse hook that inspects the command and the OS sandbox, which enforces limits whatever the text says. (<a href="./03-settings-json/docs/en.md">Lesson 3</a>)</details>
7. **The injection eval scores a bare harness at 0.0. Why keep that case?**
   <details><summary>Answer</summary>It proves the eval can fail, so a score of 1.0 means something. Removing any single layer must also lower the score, which shows each layer is doing real work. (<a href="./04-untrusted-content/docs/en.md">Lesson 4</a>)</details>
8. **A secret was printed into a transcript, and redaction is now on. Is the problem solved?**
   <details><summary>Answer</summary>No. Redaction stops the next leak, not the last one. Rotate the exposed secret. (<a href="./04-untrusted-content/docs/en.md">Lesson 4</a>)</details>
