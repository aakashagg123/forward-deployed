# Minimal coding agent (loop + tools + files)

> **Motto** — The smallest real coding agent: a loop that reads, edits, and runs code.

*Part of Phase 19 — Capstone. Combines Phase 2 (loop), 3 (tools), 6 (files), 7 (shell).*

## The Problem

You've built every piece in isolation. The capstone proves they compose. Project 1 is the
**minimal coding agent**: the agent loop (P2) dispatches file tools (P6) and a bash tool (P7)
through a typed registry (P3). It drives a real task end-to-end — read a file, edit it, run
it — on a real (temp) directory. There are no new concepts here, just integration.

## The Concept

<style>
.dgm-ca1{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ca1-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ca1 h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ca1-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ca1-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-ca1-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-ca1-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-ca1-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-ca1-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-ca1-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-ca1-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-ca1-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-ca1{padding:20px 16px 18px}.dgm-ca1-row{flex-direction:column}}
.dgm-ca1-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-ca1-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-ca1-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-ca1-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-ca1-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-ca1-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-ca1-b.accent h6{color:#0d5c0d}
.dgm-ca1-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-ca1-b.blue h6{color:#0550ae}
.dgm-ca1-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-ca1-b.green h6{color:#1a614f}
.dgm-ca1-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-ca1-b.red h6{color:#82061e}
.dgm-ca1-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-ca1-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-ca1{padding:20px 16px 18px}.dgm-ca1-branches{grid-template-columns:1fr}}
.dgm-ca1-note{margin-top:10px;padding:9px 14px;background:#e6f5e6;border:1px dashed #a8d8a8;border-radius:10px;
  font-size:10.5px;color:#0d5c0d;line-height:1.4}
</style>
<div class="dgm-ca1">
  <span class="dgm-ca1-chip">Capstone 1: the smallest agent that can edit code</span>
  <h4>Loop, dispatch, and two tool families — read/edit/write and bash</h4>
  <p class="dgm-ca1-sub">Every later capstone lesson adds a phase's mechanism on top of this minimal core.</p>
  <div class="dgm-ca1-row">
    <div class="dgm-ca1-n neutral">Task</div>
    <span class="dgm-ca1-arr">→</span>
    <div class="dgm-ca1-n accent">Agent loop (P2)</div>
    <span class="dgm-ca1-arr">→</span>
    <div class="dgm-ca1-n blue">Tool dispatch (P3)</div>
  </div>
  <div class="dgm-ca1-branches">
    <div class="dgm-ca1-b green">
      <h6>Read/edit/write (P6)</h6>
    </div>
    <div class="dgm-ca1-b accent">
      <h6>Bash (P7)</h6>
    </div>
  </div>
  <div class="dgm-ca1-note">Result → loop continues → done.</div>
</div>


## Build It

`code/agent.py` — a self-contained minimal coding agent. A scripted model stands in for the
real one (swap in the Phase 2 L5 SDK loop). This lets it run offline and demonstrate the full
read→edit→run cycle on a temp file:

```python
# tools: read, edit (exact-string), bash — the P6/P7 primitives
TOOLS = {
    "read":  lambda path: open(path).read(),
    "edit":  lambda path, old, new: _edit(path, old, new),
    "bash":  lambda cmd: subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout,
}

def run(task, model, max_steps=10):
    history = [{"role": "user", "content": task}]
    for _ in range(max_steps):
        msg = model(history)                       # P2 loop
        history.append({"role": "assistant", "content": msg["text"]})
        if not msg["tool_calls"]:
            return msg["text"]
        for call in msg["tool_calls"]:             # P3 dispatch
            out = dispatch(call["name"], call["args"])
            history.append({"role": "tool", "content": out})
```

The scripted model reads a buggy file, edits the bug, and runs it to confirm the fix. This
wires the agent loop from Phase 2 to the real file/shell tools from Phases 6–7. Run
`python3 agent.py` to watch it fix and verify a file.

## Use It

This is Claude Code / Codex at its core: a loop, tools, files, shell. Everything else in the
curriculum — context, memory, permissions, subagents, evals, deploy — is a *layer* on this
skeleton. That's exactly what projects 02–04 add. Swap the scripted model for the Phase 2 L5
SDK loop, and it's a real agent.

## Ship It

[`code/agent.py`](../../01-minimal-agent/code/agent.py) — a runnable minimal coding agent
(loop + tools + files + shell).

## Check Yourself

**Q1.** What four phases does the minimal agent combine?

- A) any four
- B) the loop (P2), tools (P3), file ops (P6), shell (P7)
- C) only the loop
- D) evals and deploy

<details><summary>Answer</summary>B — the core execution skeleton.</details>

**Q2.** Everything else in the course relates to this skeleton how?

- A) it replaces it
- B) it's a layer added on top (context, memory, permissions, evals, deploy)
- C) it's unrelated
- D) no relation

<details><summary>Answer</summary>B — layers on the core loop.</details>

**Challenge.** Replace the scripted model with the Phase 2 L5 Anthropic SDK loop and give it
a real bug to fix in a small repo.

## Related

- Combines: Phase 2, 3, 6, 7
- Next: [Add context, memory & permissions](../../02-context-memory-permissions/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
