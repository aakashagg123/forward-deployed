# Message assembly & ordering

> **Motto** — Assemble context in a fixed order: stable first, volatile last.

*Part of Phase 04 — Context Engineering.*

## The Problem

The same pieces — system prompt, project memory, tool schemas, retrieved files, history,
and the new user turn — can be arranged many ways. Order matters for two reasons. Caching
rewards a stable-first order, because it keeps the cached prefix valid (Phase 1 lesson 08).
Salience rewards it too, because the model weights recent, closing context heavily. A
haphazard assembler quietly kills your cache hit rate and buries the current task.

## The Concept

<style>
.dgm-ma{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ma-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ma h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ma-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ma-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-ma-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-ma-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-ma-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-ma-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-ma-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-ma-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-ma-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-ma{padding:20px 16px 18px}.dgm-ma-row{flex-direction:column}}
</style>
<div class="dgm-ma">
  <span class="dgm-ma-chip">Assembly order is a caching decision</span>
  <h4>Stable content goes first, the user's request goes last</h4>
  <p class="dgm-ma-sub">Anything that changes every turn has to sit after everything that doesn't.</p>
  <div class="dgm-ma-row">
    <div class="dgm-ma-n accent">System + memory + tools (stable, cacheable)</div>
    <span class="dgm-ma-arr">→</span>
    <div class="dgm-ma-n blue">History (semi-stable)</div>
    <span class="dgm-ma-arr">→</span>
    <div class="dgm-ma-n ">Retrieved files for this turn</div>
    <span class="dgm-ma-arr">→</span>
    <div class="dgm-ma-n green">The user's request (last)</div>
  </div>
</div>


Use a canonical order: stable/cacheable prefix, then history, then this-turn context, then
the request itself last. That way the model's attention lands on the actual ask.

## Build It

`code/assembly.py` — a deterministic assembler:

```python
def assemble(system, memory, history, files, user_msg):
    system_block = "\n\n".join(filter(None, [system, memory]))   # stable, cacheable
    messages = list(history)                                      # semi-stable
    if files:                                                     # this-turn context
        joined = "\n\n".join(f"<file path=\"{p}\">\n{c}\n</file>" for p, c in files)
        messages.append({"role": "user", "content": f"Relevant files:\n{joined}"})
    messages.append({"role": "user", "content": user_msg})        # the ask, last
    return system_block, messages
```

```python
sys_block, msgs = assemble(
    system="You are a coding agent.",
    memory="Project: use the public API barrel.",
    history=[{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}],
    files=[("api.py", "def add(a,b): ...")],
    user_msg="Add a subtract function.")
print(sys_block.splitlines()[0]); print("msgs:", len(msgs))   # files + ask appended last
```

The assembler is the single place ordering is decided, so caching and salience are
consistent across every call.

## Use It

This mirrors how **Claude Code / Codex** lay out a turn. The system prompt and project
memory (`CLAUDE.md` / `AGENTS.md`) form the stable, cached head. Files the agent reads are
injected for the current turn, and your message comes last. Keeping memory files lean and
stable is what makes the cached prefix pay off (Phase 1 lesson 08).

## Ship It

[`code/assembly.py`](../../02-message-assembly/code/assembly.py) — a deterministic context
assembler.

## Check Yourself

**Q1.** Why put stable content first?

- A) readability
- B) it keeps the cacheable prefix valid and is cheaper to reuse
- C) the API sorts it
- D) no reason

<details><summary>Answer</summary>B — stable-first maximizes cache hits (Phase 1 L8).</details>

**Q2.** Why does the user's actual request go last?

- A) tradition
- B) the model weights closing context heavily, so the ask stays salient
- C) it's shorter
- D) no reason

<details><summary>Answer</summary>B — recency keeps the task in focus.</details>

**Challenge.** Make `assemble` take the `ContextBudget` (lesson 01) and skip/trim file
injection when the files category is over budget.

## Related

- Builds on: [Context budgeting](../../01-context-budgeting/docs/en.md)
- Next: [Truncation that doesn't break tool calls](../../03-truncation/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
