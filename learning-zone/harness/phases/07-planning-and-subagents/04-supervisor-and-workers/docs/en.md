# Supervisor and Workers

> **Motto** — A supervisor plans and delegates, each worker sees only what it needs, and only results flow back up.

*Part of Phase 07 — Planning and Subagents.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

One agent that does everything hits two limits. Its context fills with detail that does not matter to the current step. And it cannot do independent work in parallel.

Splitting the work creates a new risk. The lazy way to share context is to give every agent everything. This breaks the design. A reviewer who sees the author's plan starts to explain the output ("the author meant well") instead of judging it. Shared context turns independent review into a rubber stamp.

## The Concept

<style>
.dgm-sw{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-sw-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-sw h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-sw-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-sw-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-sw-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-sw-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-sw-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-sw-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-sw-b.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline)}
.dgm-sw-b.accent h6{color:var(--color-text-success)}
.dgm-sw-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-sw-b.blue h6{color:var(--color-text-info)}
.dgm-sw-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-sw-b.green h6{color:var(--color-text-success)}
.dgm-sw-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-sw-b.red h6{color:var(--color-text-danger)}
.dgm-sw-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-sw-b.neutral h6{color:var(--color-text)}
@media (max-width:640px){.dgm-sw{padding:20px 16px 18px}.dgm-sw-branches{grid-template-columns:1fr}}
.dgm-sw-chain{display:flex;flex-direction:column;gap:2px}
.dgm-sw-node{background:var(--color-background-success-surface);border:1.5px solid var(--color-border-success-outline);border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:var(--color-text-success)}
.dgm-sw-node.alt{background:var(--color-surface-tertiary);border-color:var(--color-border);color:var(--color-text)}
.dgm-sw-arr{display:flex;justify-content:center;color:var(--color-text-tertiary);padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-sw{padding:20px 16px 18px}}
</style>
<div class="dgm-sw">
  <span class="dgm-sw-chip">Fan out, then fan back in</span>
  <h4>The supervisor decomposes, dispatches isolated workers, and aggregates what comes back</h4>
  <p class="dgm-sw-sub">Workers never see each other — only the supervisor sees every result.</p>
  <div class="dgm-sw-chain">
    <div class="dgm-sw-node accent">Supervisor: decompose → tasks</div>
    <div class="dgm-sw-arr">↓</div>
    <div class="dgm-sw-node alt">Dispatch workers (isolated)</div>
  </div>
  <div class="dgm-sw-branches">
    <div class="dgm-sw-b blue">
      <h6>Worker 1</h6>
      <p>→ result</p>
    </div>
    <div class="dgm-sw-b green">
      <h6>Worker 2</h6>
      <p>→ result</p>
    </div>
    <div class="dgm-sw-b neutral">
      <h6>Worker 3</h6>
      <p>→ result</p>
    </div>
  </div>
  <div class="dgm-sw-chain">
    <div class="dgm-sw-node accent">Supervisor: aggregate results</div>
    <div class="dgm-sw-arr">↓</div>
    <div class="dgm-sw-node alt">Combined output</div>
  </div>
</div>


The **supervisor** holds the plan. It writes no code. Each **worker** holds one task. Workers return a result, not a transcript, so the supervisor's context stays small.

Each role also has an **allowlist**: the exact context keys it may see. You enforce the allowlist when you build the prompt. The reviewer's prompt is built from the diff alone, so the plan is not there to leak. Asking the model to "ignore the plan" is not a control.

## Build It

`code/supervisor.py` has two parts. The first is the allowlist and the function that applies it:

```python
ROLE_ALLOWLIST = {
    "worker":   ["task", "files"],
    "reviewer": ["diff"],                 # never the plan or the spec
}


def build_context(role, store):
    """Copy only the allowed keys out of the shared store."""
    return {k: store[k] for k in ROLE_ALLOWLIST[role] if k in store}
```

The second is the `Supervisor`. It splits a goal into tasks, runs them through a thread pool capped at `max_workers`, and wraps each outcome in a `Result`. A worker that raises an exception becomes a failed `Result`. It does not crash the run:

```python
    def _one(self, task, store):
        ctx = build_context("worker", {**store, "task": task})
        try:
            return Result(task, True, self.run_worker(ctx))
        except Exception as e:            # a crash stays inside one Result
            return Result(task, False, f"{type(e).__name__}: {e}")
```

The asserts check four things. The reviewer context holds only the diff. No worker context contains the plan or spec. One failing worker leaves the others complete. And the peak number of live workers equals the cap, so the parallelism is real and bounded.

The decomposition is a toy that splits on `;`. A real supervisor asks the model for sub-tasks, and you can feed them through the wave planner from [lesson 03](../../03-contract-waves-and-isolation/docs/en.md) to avoid file clashes.

Run checks like these in CI, so a later refactor cannot widen a role's view by accident.

## Use It

In Claude Code the supervisor is your main session, and workers are subagents started through the `Agent` tool. The tool was called `Task` before version 2.1.63. Old `Task(...)` references still work as aliases.

A subagent starts with a fresh context window. It does not see your conversation history. The parent receives the subagent's final report, not its working steps. This is the "results, not transcripts" rule built in.

You choose the context by what you write into the delegation prompt. Pass the diff to a reviewer. Do not pass the plan. The `tools` field of a subagent definition is a different control. It limits tools, not what the subagent knows. A fork is a subagent that inherits the whole conversation, so do not use a fork for a reviewer.

## Challenge

Add a second reviewer role, `"style"`, that sees the diff and a style guide but not the plan. Write a test that the two reviewer roles together cover both concerns and that neither role's context contains `plan` or `spec`.

## Sources

Claude Code docs, "Subagents" (code.claude.com/docs).

Next: [MCP protocol, server and client](../../../08-extending-mcp-skills-retrieval/01-mcp-protocol-server-client/docs/en.md)
