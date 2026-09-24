# Harness engineering from scratch — roadmap

> Build a production coding agent (a "harness" like Claude Code) **by hand**, one piece
> at a time — then use the real SDKs and frameworks. Every lesson ships a reusable
> artifact: a prompt, a skill, a hook, a harness module, an eval, or an MCP server.

**Status:** `✅` done · `🚧` in progress · `⬚` planned — **all 20 phases complete ✅**

The phases stack. **The model-as-a-function is the floor. A full coding agent is the
roof.** Skip ahead if you know a lower layer, but don't skip and then wonder why the
top is breaking.

```mermaid
flowchart TB
  P0["Phase 0 — Setup & Tooling"] --> P1["Phase 1 — LLM I/O Foundations"]
  P1 --> P2["Phase 2 — The Agent Loop"]
  P2 --> P3["Phase 3 — Tool Engineering"]
  P2 --> P4["Phase 4 — Context Engineering"]
  P3 --> P5["Phase 5 — Prompt & Instruction Architecture"]
  P4 --> P5
  P3 --> P6["Phase 6 — File & Code Operations"]
  P3 --> P7["Phase 7 — Shell & Sandbox Execution"]
  P6 --> P8["Phase 8 — Permissions & Safety Gating"]
  P7 --> P8
  P4 --> P9["Phase 9 — Memory & Persistence"]
  P2 --> P10["Phase 10 — Subagents & Orchestration"]
  P5 --> P11["Phase 11 — Planning & Task Management"]
  P3 --> P12["Phase 12 — MCP & Extensibility"]
  P4 --> P13["Phase 13 — Retrieval & Codebase Understanding"]
  P8 --> P14["Phase 14 — Reliability Engineering"]
  P14 --> P15["Phase 15 — Evals & Testing the Harness"]
  P14 --> P16["Phase 16 — Observability & Cost"]
  P8 --> P17["Phase 17 — Security & Alignment"]
  P15 --> P18["Phase 18 — Production & Deployment"]
  P16 --> P18
  P17 --> P18
  P10 --> P19["Phase 19 — Capstone: Build Your Own Coding Agent"]
  P18 --> P19
```

---

## Phase 0 — Setup & tooling `5 lessons` ✅
*Get a model talking to your terminal with nothing but the standard library.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Dev environment & the SDK](./phases/00-setup-and-tooling/01-dev-environment/docs/en.md) ✅ | Build | Python | setup script |
| 02 | [Your first raw model call (HTTP, no SDK)](./phases/00-setup-and-tooling/02-first-raw-call/docs/en.md) ✅ | Build | Python | prompt |
| 03 | [API keys, secrets & env hygiene](./phases/00-setup-and-tooling/03-secrets-and-env/docs/en.md) ✅ | Build | Python | hook |
| 04 | [A REPL you can talk to](./phases/00-setup-and-tooling/04-repl/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Reading the docs like an engineer](./phases/00-setup-and-tooling/05-reading-docs/docs/en.md) ✅ | Build | — | skill |

## Phase 1 — LLM I/O foundations `8 lessons` ✅
*The model is a fast, stateless, non-deterministic function. Learn its interface.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Messages, roles & turns](./phases/01-llm-io-foundations/01-messages-roles-turns/docs/en.md) ✅ | Build | Python | harness module |
| 02 | [Tokens & the context window](./phases/01-llm-io-foundations/02-tokens-and-context-window/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Sampling: temperature, top-p, determinism](./phases/01-llm-io-foundations/03-sampling/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Streaming responses token-by-token](./phases/01-llm-io-foundations/04-streaming/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Stop reasons & max tokens](./phases/01-llm-io-foundations/05-stop-reasons/docs/en.md) ✅ | Build | Python | harness module |
| 06 | [System vs. user vs. assistant — who controls what](./phases/01-llm-io-foundations/06-roles-precedence/docs/en.md) ✅ | Build | — | prompt |
| 07 | [Structured output without tools (JSON + repair)](./phases/01-llm-io-foundations/07-structured-output/docs/en.md) ✅ | Build | Python | harness module |
| 08 | [Prompt caching: what's cacheable and why](./phases/01-llm-io-foundations/08-prompt-caching/docs/en.md) ✅ | Use | Python | harness module |

## Phase 2 — The agent loop `7 lessons` ✅
*The ~120 lines at the heart of every coding agent.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [The agent loop from scratch](./phases/02-the-agent-loop/01-agent-loop/docs/en.md) ✅ | Build | Python | agent |
| 02 | [Tool-call parsing & the act step](./phases/02-the-agent-loop/02-tool-call-parsing/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Termination: stop conditions & max steps](./phases/02-the-agent-loop/03-termination/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Turn history & conversation state](./phases/02-the-agent-loop/04-turn-history/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Use It: the same loop with the SDK tool-use API](./phases/02-the-agent-loop/05-sdk-tool-use-loop/docs/en.md) ✅ | Use | Python, TS | agent |
| 06 | [Error recovery inside the loop](./phases/02-the-agent-loop/06-error-recovery/docs/en.md) ✅ | Build | Python | harness module |
| 07 | [A streaming agent loop](./phases/02-the-agent-loop/07-streaming-loop/docs/en.md) ✅ | Build | Python | agent |

## Phase 3 — Tool engineering `8 lessons` ✅
*Tools are the agent's hands. Define, dispatch, validate, and trust them.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Tool schemas & dispatch by hand](./phases/03-tool-engineering/01-schemas-and-dispatch/docs/en.md) ✅ | Build | Python | harness module |
| 02 | [Argument validation & JSON-schema enforcement](./phases/03-tool-engineering/02-argument-validation/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Tool results, errors & the feedback channel](./phases/03-tool-engineering/03-results-and-errors/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Idempotency & side-effecting tools](./phases/03-tool-engineering/04-idempotency/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Tool budgets & rate limits](./phases/03-tool-engineering/05-tool-budgets/docs/en.md) ✅ | Build | Python | hook |
| 06 | [Writing tool descriptions the model obeys](./phases/03-tool-engineering/06-tool-descriptions/docs/en.md) ✅ | Build | — | prompt |
| 07 | [Use It: SDK tool definitions & parallel tool use](./phases/03-tool-engineering/07-sdk-parallel-tools/docs/en.md) ✅ | Use | Python | agent |
| 08 | [A tool registry & discovery layer](./phases/03-tool-engineering/08-tool-registry/docs/en.md) ✅ | Build | Python | harness module |

## Phase 4 — Context engineering `7 lessons` ✅
*What the model "knows" is whatever your harness put in the window.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Context budgeting & token accounting](./phases/04-context-engineering/01-context-budgeting/docs/en.md) ✅ | Build | Python | harness module |
| 02 | [Message assembly & ordering](./phases/04-context-engineering/02-message-assembly/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Truncation strategies that don't break tool calls](./phases/04-context-engineering/03-truncation/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Compaction & summarization across turns](./phases/04-context-engineering/04-compaction/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Injecting files & retrieved context safely](./phases/04-context-engineering/05-injecting-context/docs/en.md) ✅ | Build | Python | harness module |
| 06 | [Context windows in the wild (cache-aware layout)](./phases/04-context-engineering/06-cache-aware-layout/docs/en.md) ✅ | Use | Python | harness module |
| 07 | [Measuring context rot](./phases/04-context-engineering/07-measuring-context-rot/docs/en.md) ✅ | Build | Python | eval |

## Phase 5 — Prompt & instruction architecture `6 lessons` ✅
*System prompts, steering files, and output styles — the harness's voice.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Anatomy of a system prompt](./phases/05-prompt-instruction-architecture/01-system-prompt-anatomy/docs/en.md) ✅ | Build | — | prompt |
| 02 | [Memory files (CLAUDE.md / AGENTS.md)](./phases/05-prompt-instruction-architecture/02-memory-files/docs/en.md) ✅ | Build | — | skill |
| 03 | [Steering: tone, refusals, and guardrail text](./phases/05-prompt-instruction-architecture/03-steering/docs/en.md) ✅ | Build | — | prompt |
| 04 | [Output styles & response contracts](./phases/05-prompt-instruction-architecture/04-output-contracts/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Few-shot & in-context examples that scale](./phases/05-prompt-instruction-architecture/05-few-shot/docs/en.md) ✅ | Build | Python | harness module |
| 06 | [Prompt versioning & A/B in the harness](./phases/05-prompt-instruction-architecture/06-prompt-versioning/docs/en.md) ✅ | Build | Python | harness module |

## Phase 6 — File & code operations `7 lessons` ✅
*Read, search, and edit a codebase the way a coding agent does.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [A read tool with line numbers & ranges](./phases/06-file-and-code-operations/01-read-tool/docs/en.md) ✅ | Build | Python | harness module |
| 02 | [Exact-string edit & why diffs beat rewrites](./phases/06-file-and-code-operations/02-edit-tool/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Write & overwrite safety](./phases/06-file-and-code-operations/03-write-safety/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Glob & file discovery](./phases/06-file-and-code-operations/04-glob/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Grep / ripgrep-style content search](./phases/06-file-and-code-operations/05-grep/docs/en.md) ✅ | Build | Python | harness module |
| 06 | [Applying & validating patches](./phases/06-file-and-code-operations/06-patches/docs/en.md) ✅ | Build | Python | harness module |
| 07 | [Use It: tree-sitter for structural edits](./phases/06-file-and-code-operations/07-tree-sitter/docs/en.md) ✅ | Use | Python | harness module |

## Phase 7 — Shell & sandbox execution `6 lessons` ✅
*Let the agent run commands without letting it run wild.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [A bash tool: capture stdout, stderr, exit code](./phases/07-shell-and-sandbox-execution/01-bash-tool/docs/en.md) ✅ | Build | Python | harness module |
| 02 | [Timeouts & killing runaway processes](./phases/07-shell-and-sandbox-execution/02-timeouts/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Background tasks & long-running commands](./phases/07-shell-and-sandbox-execution/03-background-tasks/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Working-directory & shell-state pitfalls](./phases/07-shell-and-sandbox-execution/04-cwd-and-state/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Sandboxing: containers, namespaces, seccomp](./phases/07-shell-and-sandbox-execution/05-sandboxing/docs/en.md) ✅ | Use | Python | harness module |
| 06 | [Network policies & egress control](./phases/07-shell-and-sandbox-execution/06-egress-control/docs/en.md) ✅ | Use | — | hook |

## Phase 8 — Permissions & safety gating `6 lessons` ✅
*The line between "agent" and "incident" is the permission layer.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Permission modes (ask / allow / deny)](./phases/08-permissions-and-safety-gating/01-permission-modes/docs/en.md) ✅ | Build | Python | harness module |
| 02 | [Allowlists, denylists & pattern matching](./phases/08-permissions-and-safety-gating/02-allow-deny/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Pre/post tool-use hooks](./phases/08-permissions-and-safety-gating/03-hooks/docs/en.md) ✅ | Build | Python | hook |
| 04 | [Human-in-the-loop approval flows](./phases/08-permissions-and-safety-gating/04-approvals/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Least privilege & capability scoping](./phases/08-permissions-and-safety-gating/05-least-privilege/docs/en.md) ✅ | Build | Python | harness module |
| 06 | [Use It: settings.json & the hooks system](./phases/08-permissions-and-safety-gating/06-settings-json/docs/en.md) ✅ | Use | — | settings |

## Phase 9 — Memory & persistence `5 lessons` ✅
*Statelessness is the model's problem; memory is the harness's job.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Session state & the scratchpad](./phases/09-memory-and-persistence/01-scratchpad/docs/en.md) ✅ | Build | Python | harness module |
| 02 | [Persisting & resuming conversations](./phases/09-memory-and-persistence/02-persist-resume/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Long-term memory & retrieval](./phases/09-memory-and-persistence/03-long-term-memory/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Compaction across sessions](./phases/09-memory-and-persistence/04-cross-session-compaction/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Use It: a memory MCP server](./phases/09-memory-and-persistence/05-memory-mcp/docs/en.md) ✅ | Use | Python | mcp |

## Phase 10 — Subagents & orchestration `6 lessons` ✅
*One agent spawns many. Coordinate them with contracts, budgets, and waves.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Sprint contracts & budgeted waves](./phases/10-subagents-and-orchestration/01-sprint-contract-and-waves/docs/en.md) ✅ | Build | Python | module, prompt, settings |
| 02 | [Bounded roles & context allowlists](./phases/10-subagents-and-orchestration/02-bounded-roles/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Worktree isolation & the dependency graph](./phases/10-subagents-and-orchestration/03-worktree-isolation/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Checkpoints & resumable runs](./phases/10-subagents-and-orchestration/04-checkpoints/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Supervisor / worker patterns](./phases/10-subagents-and-orchestration/05-supervisor-worker/docs/en.md) ✅ | Build | Python | agent |
| 06 | [Use It: the agent-team pipeline](./phases/10-subagents-and-orchestration/06-agent-team-pipeline/docs/en.md) ✅ | Use | Python, TS | skill |

## Phase 11 — Planning & task management `5 lessons` ✅
*Decompose, plan, track — so long tasks don't drift.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [A todo/task data model](./phases/11-planning-and-task-management/01-todo-model/docs/en.md) ✅ | Build | Python | harness module |
| 02 | [Plan mode: propose before you act](./phases/11-planning-and-task-management/02-plan-mode/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Task decomposition prompts](./phases/11-planning-and-task-management/03-decomposition/docs/en.md) ✅ | Build | — | prompt |
| 04 | [Progress tracking & self-correction](./phases/11-planning-and-task-management/04-progress-tracking/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Use It: plan mode in a real harness](./phases/11-planning-and-task-management/05-plan-mode-in-practice/docs/en.md) ✅ | Use | — | skill |

## Phase 12 — MCP & extensibility `6 lessons` ✅
*Make the harness pluggable. Build the protocol, then a server.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [The MCP wire protocol from scratch](./phases/12-mcp-and-extensibility/01-wire-protocol/docs/en.md) ✅ | Build | Python | mcp |
| 02 | [An MCP server: tools, resources, prompts](./phases/12-mcp-and-extensibility/02-mcp-server/docs/en.md) ✅ | Build | Python | mcp |
| 03 | [An MCP client & tool discovery](./phases/12-mcp-and-extensibility/03-mcp-client/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Skills (`SKILL.md`) & progressive disclosure](./phases/12-mcp-and-extensibility/04-skills/docs/en.md) ✅ | Build | — | skill |
| 05 | [Plugins & deferred tool loading](./phases/12-mcp-and-extensibility/05-plugins/docs/en.md) ✅ | Build | Python | harness module |
| 06 | [Use It: the official MCP SDK](./phases/12-mcp-and-extensibility/06-official-sdk/docs/en.md) ✅ | Use | Python | mcp |

## Phase 13 — Retrieval & codebase understanding `5 lessons` ✅
*Help the agent find the right 200 lines in a million-line repo.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Lexical search & repo maps](./phases/13-retrieval-and-codebase-understanding/01-repo-maps/docs/en.md) ✅ | Build | Python | harness module |
| 02 | [Embeddings & semantic code search](./phases/13-retrieval-and-codebase-understanding/02-embeddings/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Hybrid search & reranking](./phases/13-retrieval-and-codebase-understanding/03-hybrid-search/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Chunking code without breaking it](./phases/13-retrieval-and-codebase-understanding/04-chunking/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Use It: a retrieval tool the agent calls](./phases/13-retrieval-and-codebase-understanding/05-retrieval-tool/docs/en.md) ✅ | Use | Python | harness module |

## Phase 14 — Reliability engineering `6 lessons` ✅
*Make a stochastic system dependable enough to ship.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Retries, backoff & jitter](./phases/14-reliability-engineering/01-retries/docs/en.md) ✅ | Build | Python | harness module |
| 02 | [Validation & repair loops](./phases/14-reliability-engineering/02-repair-loops/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Fallback chains & model routing](./phases/14-reliability-engineering/03-fallback-routing/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Loop, tool & token budgets](./phases/14-reliability-engineering/04-budgets/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Degraded-mode UX](./phases/14-reliability-engineering/05-degraded-mode/docs/en.md) ✅ | Build | Python | harness module |
| 06 | [Use It: production failure-mode playbook](./phases/14-reliability-engineering/06-failure-playbook/docs/en.md) ✅ | Use | — | prompt |

## Phase 15 — Evals & testing the harness `6 lessons` ✅
*You cannot improve a harness you cannot measure.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Golden tasks & fixtures](./phases/15-evals-and-testing-the-harness/01-golden-tasks/docs/en.md) ✅ | Build | Python | eval |
| 02 | [Trajectory evals (did it take the right steps?)](./phases/15-evals-and-testing-the-harness/02-trajectory-evals/docs/en.md) ✅ | Build | Python | eval |
| 03 | [LLM-as-judge](./phases/15-evals-and-testing-the-harness/03-llm-as-judge/docs/en.md) ✅ | Build | Python | eval |
| 04 | [Regression gates in CI](./phases/15-evals-and-testing-the-harness/04-regression-gates/docs/en.md) ✅ | Build | Python | eval |
| 05 | [Adversarial & red-team cases](./phases/15-evals-and-testing-the-harness/05-adversarial/docs/en.md) ✅ | Build | Python | eval |
| 06 | [Use It: an eval harness you run on every change](./phases/15-evals-and-testing-the-harness/06-eval-harness/docs/en.md) ✅ | Use | Python | eval |

## Phase 16 — Observability & cost `5 lessons` ✅
*Traces, tokens, latency, dollars — per call, per session, per tenant.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Tracing & spans for an agent](./phases/16-observability-and-cost/01-tracing/docs/en.md) ✅ | Build | Python | harness module |
| 02 | [Token & cost accounting](./phases/16-observability-and-cost/02-cost-accounting/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Latency: prefill vs. decode, TTFT](./phases/16-observability-and-cost/03-latency/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Drift detection](./phases/16-observability-and-cost/04-drift/docs/en.md) ✅ | Build | Python | eval |
| 05 | [Use It: OpenTelemetry for agents](./phases/16-observability-and-cost/05-opentelemetry/docs/en.md) ✅ | Use | Python | harness module |

## Phase 17 — Security & alignment `6 lessons` ✅
*The agent reads untrusted data. Assume it's hostile.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Prompt injection from tool results & files](./phases/17-security-and-alignment/01-prompt-injection/docs/en.md) ✅ | Build | Python | eval |
| 02 | [Treating model output as data, never control flow](./phases/17-security-and-alignment/02-output-as-data/docs/en.md) ✅ | Build | Python | harness module |
| 03 | [Data exfiltration & egress guards](./phases/17-security-and-alignment/03-exfiltration/docs/en.md) ✅ | Build | Python | hook |
| 04 | [Secret redaction in context & logs](./phases/17-security-and-alignment/04-secret-redaction/docs/en.md) ✅ | Build | Python | harness module |
| 05 | [Multi-tenant isolation & cache contamination](./phases/17-security-and-alignment/05-multitenancy/docs/en.md) ✅ | Build | Python | harness module |
| 06 | [Use It: a security-review skill](./phases/17-security-and-alignment/06-security-review/docs/en.md) ✅ | Use | — | skill |

## Phase 18 — Production & deployment `6 lessons` ✅
*Ship the harness to real users and real repos.*

| # | Lesson | Type | Lang | Ships |
|---|--------|------|------|-------|
| 01 | [Remote / sandboxed execution environments](./phases/18-production-and-deployment/01-remote-execution/docs/en.md) ✅ | Use | — | settings |
| 02 | [GitHub integration & CI triggers](./phases/18-production-and-deployment/02-github-ci/docs/en.md) ✅ | Build | — | settings |
| 03 | [Webhooks & event-driven agents](./phases/18-production-and-deployment/03-webhooks/docs/en.md) ✅ | Build | Python | harness module |
| 04 | [Config, settings & feature flags](./phases/18-production-and-deployment/04-config-flags/docs/en.md) ✅ | Build | Python | settings |
| 05 | [Rollout, canary & kill switches](./phases/18-production-and-deployment/05-rollout/docs/en.md) ✅ | Build | Python | harness module |
| 06 | [Use It: deploy the capstone agent](./phases/18-production-and-deployment/06-deploy/docs/en.md) ✅ | Use | — | harness module |

## Phase 19 — Capstone: build your own coding agent `4 lessons` ✅
*Assemble every phase into one working harness.*

| # | Project | Combines | Lang | Ships |
|---|---------|----------|------|-------|
| 01 | [Minimal coding agent (loop + tools + files)](./phases/19-capstone-coding-agent/01-minimal-agent/docs/en.md) ✅ | P2,3,6,7 | Python | agent |
| 02 | [Add context, memory & permissions](./phases/19-capstone-coding-agent/02-context-memory-permissions/docs/en.md) ✅ | P4,8,9 | Python | agent |
| 03 | [Add subagents, MCP & retrieval](./phases/19-capstone-coding-agent/03-subagents-mcp-retrieval/docs/en.md) ✅ | P10,12,13 | Python | agent |
| 04 | [Add evals, observability & ship it](./phases/19-capstone-coding-agent/04-evals-observability-ship/docs/en.md) ✅ | P14,15,16,18 | Python | agent |

---

### Totals (planned)

20 phases · ~120 lessons · Python + TypeScript · every lesson ships an artifact.
