# Add context, memory & permissions

> **Motto** — A safe agent that remembers: gate every action, manage the window, keep a scratchpad.

*Part of Phase 19 — Capstone. Combines Phase 4 (context), 8 (permissions), 9 (memory).*

## The Problem

The minimal agent (project 01) is unsafe — it'll run anything. It's also forgetful, with no
memory, and context-blind, so it would overflow on a big task. Project 02 wraps it with three
layers from the curriculum: a **permission gate** (P8) on every tool call, a **scratchpad**
(P9) for working state, and **context budgeting/truncation** (P4) so long runs don't blow the
window. This turns a toy into something you'd let near a real repo.

## The Concept

<style>
.dgm-ca2{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ca2-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ca2 h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ca2-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ca2-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-ca2-branches{display:grid;grid-template-columns:repeat(1,1fr);gap:10px}
.dgm-ca2-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-ca2-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-ca2-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-ca2-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-ca2-b.accent h6{color:#0d5c0d}
.dgm-ca2-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-ca2-b.blue h6{color:#0550ae}
.dgm-ca2-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-ca2-b.green h6{color:#1a614f}
.dgm-ca2-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-ca2-b.red h6{color:#82061e}
.dgm-ca2-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-ca2-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-ca2{padding:20px 16px 18px}.dgm-ca2-branches{grid-template-columns:1fr}}
.dgm-ca2-chain{display:flex;flex-direction:column;gap:2px}
.dgm-ca2-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-ca2-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-ca2-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-ca2{padding:20px 16px 18px}}
</style>
<div class="dgm-ca2">
  <span class="dgm-ca2-chip">Capstone 2: the loop grows three managers</span>
  <h4>Permission gate, context manager, and scratchpad all wrap around the same core loop</h4>
  <p class="dgm-ca2-sub">None of these three replace the loop from lesson 01 — they sit alongside it.</p>
  <div class="dgm-ca2-chain">
    <div class="dgm-ca2-node accent">Loop</div>
  </div>
  <div class="dgm-ca2-branches" style="grid-template-columns:repeat(1,1fr)">
    <div class="dgm-ca2-b blue">
      <h6>Permission gate (P8)</h6>
      <p>allow / ask / deny → dispatch</p>
    </div>
  </div>
  <div class="dgm-ca2-branches">
    <div class="dgm-ca2-b green">
      <h6>Context manager (P4)</h6>
      <p>budget + truncate</p>
    </div>
    <div class="dgm-ca2-b accent">
      <h6>Scratchpad (P9)</h6>
      <p>working state</p>
    </div>
  </div>
</div>


## Build It

`code/agent.py` (project 02) wraps project 01's dispatch with the gate, adds a scratchpad,
and trims history each step:

```python
DENY = ["rm -rf", "git push"]                 # P8 denylist
def gate(name, args):
    blob = f"{name} {args}"
    if any(d in blob for d in DENY):
        return False, f"denied: matched denylist"
    return True, None

def run(task, model, scratch, max_steps=12, budget_chars=8000):
    history = [{"role": "user", "content": task}]
    for _ in range(max_steps):
        history = truncate(history, budget_chars)        # P4
        msg = model(history, scratch)
        history.append({"role": "assistant", "content": msg["text"]})
        if not msg["tool_calls"]:
            return msg["text"]
        for call in msg["tool_calls"]:
            ok, reason = gate(call["name"], call["args"])  # P8
            out = reason if not ok else dispatch(call["name"], call["args"])
            history.append({"role": "tool", "content": out})
```

The gate blocks dangerous calls: a denied `rm -rf` returns a message, not destruction. The
scratchpad carries facts across steps, and `truncate` keeps the window bounded. Run
`python3 agent.py` to see a denied dangerous command and a remembered note.

## Use It

This mirrors how you actually run Claude Code / Codex: permissions on every action
(`settings.json`), the agent's todo/scratch state, and automatic context compaction. Project
02 makes the minimal agent *operable* — the difference between a demo and something you trust
on a codebase.

## Ship It

[`code/agent.py`](../../02-context-memory-permissions/code/agent.py) — the agent with
permissions, memory, and context management.

## Check Yourself

**Q1.** What three layers does project 02 add?

- A) more tools
- B) permission gating (P8), scratchpad memory (P9), context budgeting (P4)
- C) evals
- D) deploy

<details><summary>Answer</summary>B — safety, memory, context.</details>

**Q2.** A denied dangerous tool call results in…

- A) the command running anyway
- B) a denial message returned to the model (no destructive action)
- C) a crash
- D) silent skip

<details><summary>Answer</summary>B — gated, returns data, never executes.</details>

**Challenge.** Replace the denylist with the Phase 8 `PermissionGate` (allow/ask/deny + rules)
and add an `ask` path that prompts before edits.

## Related

- Combines: Phase 4, 8, 9
- Builds on: [Minimal agent](../../01-minimal-agent/docs/en.md)
- Next: [Add subagents, MCP & retrieval](../../03-subagents-mcp-retrieval/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
