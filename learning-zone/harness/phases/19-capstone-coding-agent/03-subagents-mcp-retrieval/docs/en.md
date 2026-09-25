# Add subagents, MCP & retrieval

> **Motto** — Scale the agent out: delegate to subagents, plug in MCP servers, find code by meaning.

*Part of Phase 19 — Capstone. Combines Phase 10 (subagents), 12 (MCP), 13 (retrieval).*

## The Problem

The operable agent (project 02) still works alone, with only its built-in tools, and finds
code by grep. Project 03 scales it up. A **supervisor** spawns **subagents** (P10) for
parallel sub-tasks, an **MCP client** (P12) adds external tools, and a **retrieval tool**
(P13) lets it find code by meaning. This is the jump from "an agent" to "an agent system."

## The Concept

<style>
.dgm-ca3{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ca3-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ca3 h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ca3-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ca3-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-ca3-branches{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.dgm-ca3-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-ca3-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-ca3-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-ca3-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-ca3-b.accent h6{color:#0d5c0d}
.dgm-ca3-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-ca3-b.blue h6{color:#0550ae}
.dgm-ca3-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-ca3-b.green h6{color:#1a614f}
.dgm-ca3-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-ca3-b.red h6{color:#82061e}
.dgm-ca3-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-ca3-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-ca3{padding:20px 16px 18px}.dgm-ca3-branches{grid-template-columns:1fr}}
.dgm-ca3-chain{display:flex;flex-direction:column;gap:2px}
.dgm-ca3-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-ca3-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-ca3-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-ca3{padding:20px 16px 18px}}
</style>
<div class="dgm-ca3">
  <span class="dgm-ca3-chip">Capstone 3: a supervisor gains three extra reach points</span>
  <h4>Implement and test subagents, plus search_code and MCP tools, all under one supervisor</h4>
  <p class="dgm-ca3-sub">The supervisor still only aggregates results — subagents stay isolated per Phase 10.</p>
  <div class="dgm-ca3-chain">
    <div class="dgm-ca3-node accent">Supervisor (P10)</div>
  </div>
  <div class="dgm-ca3-branches">
    <div class="dgm-ca3-b blue">
      <h6>Subagent: implement</h6>
    </div>
    <div class="dgm-ca3-b green">
      <h6>Subagent: test</h6>
    </div>
    <div class="dgm-ca3-b accent">
      <h6>search_code (P13)</h6>
    </div>
    <div class="dgm-ca3-b neutral">
      <h6>MCP tools (P12)</h6>
    </div>
  </div>
</div>


## Build It

`code/agent.py` (project 03) adds a supervisor that decomposes and dispatches subagents,
merges MCP-discovered tools, and exposes `search_code`:

```python
def supervise(goal, run_subagent, search_code, max_workers=3):
    tasks = decompose(goal)                       # P10
    # locate relevant code first (P13)
    for t in tasks:
        t["context"] = search_code(t["text"])
    results = []
    for batch in chunked(tasks, max_workers):     # bounded parallelism
        results += [run_subagent(t) for t in batch]
    return aggregate(results)
```

```python
# subagents are isolated runs (bounded roles, P10); search_code is P13; MCP tools merge via P12
print(supervise("add and test a /health route",
                run_subagent=lambda t: {"task": t["text"], "ok": True},
                search_code=lambda q: "routes.py:1"))
```

The supervisor decomposes the goal, retrieves relevant code for each sub-task, and dispatches
isolated subagents in bounded batches. This composes the orchestration, retrieval, and MCP
layers onto the safe agent from project 02.

## Use It

This is the agent-team pattern (Phase 10) on top of the coding agent. Retrieval and MCP make
it effective in a large repo with external capabilities — the same shape as a Claude Code
session that spawns subagents, uses MCP servers, and navigates the codebase. Project 03 is
the agent at full capability.

## Ship It

[`code/agent.py`](../../03-subagents-mcp-retrieval/code/agent.py) — the agent with supervisor,
subagents, MCP, and retrieval.

## Check Yourself

**Q1.** What does the supervisor do before dispatching subagents?

- A) nothing
- B) decompose the goal and retrieve relevant code per sub-task
- C) merge files
- D) deploy

<details><summary>Answer</summary>B — decompose + retrieve, then dispatch.</details>

**Q2.** Subagents run…

- A) sharing one context
- B) isolated (bounded roles), in bounded-size batches
- C) sequentially only
- D) unbounded

<details><summary>Answer</summary>B — isolated + bounded (P10).</details>

**Challenge.** Wire the real Phase 13 `search_code` and a Phase 12 MCP client into the
supervisor so subagents get retrieved context and external tools.

## Related

- Combines: Phase 10, 12, 13
- Builds on: [Context/memory/permissions](../../02-context-memory-permissions/docs/en.md)
- Next: [Add evals, observability & ship it](../../04-evals-observability-ship/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
