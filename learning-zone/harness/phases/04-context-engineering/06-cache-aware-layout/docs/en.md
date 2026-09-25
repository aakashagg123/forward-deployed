# Context windows in the wild (cache-aware layout)

> **Motto** — Lay the window out so the expensive, stable part is computed once and reused.

*Part of Phase 04 — Context Engineering.*

## The Problem

You've budgeted, assembled, trimmed, compacted, and injected. The last question is
*economic*. A coding agent resends a huge stable prefix every turn: system, memory, and
tool schemas. Without a cache-aware layout, you pay full price to reprocess it each call,
which grows slow and expensive across a long session. This lesson ties context engineering
to prompt caching (Phase 1 lesson 08).

## The Concept

<style>
.dgm-cal{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-cal-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-cal h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-cal-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-cal-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-cal-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-cal-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-cal-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-cal-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-cal-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-cal-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-cal-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-cal{padding:20px 16px 18px}.dgm-cal-row{flex-direction:column}}
</style>
<div class="dgm-cal">
  <span class="dgm-cal-chip">Everything converges on one call, from three sources</span>
  <h4>Only the stable prefix crosses the cache breakpoint</h4>
  <p class="dgm-cal-sub">History and this-turn files join the call fresh every time.</p>
  <div class="dgm-cal-row">
    <div class="dgm-cal-n accent">Stable prefix — system + memory + tools</div>
    <span class="dgm-cal-arr">→</span>
    <div class="dgm-cal-n blue">Cache</div>
  </div>
  <div class="dgm-cal-row" style="margin-top:8px">
    <div class="dgm-cal-n neutral">History (compacted)</div>
    <span class="dgm-cal-arr">→</span>
    <div class="dgm-cal-n green">Call</div>
  </div>
  <div class="dgm-cal-row" style="margin-top:8px">
    <div class="dgm-cal-n neutral">This-turn files</div>
    <span class="dgm-cal-arr">→</span>
    <div class="dgm-cal-n green">Call</div>
  </div>
</div>


The whole phase converges here: budget → assemble stable-first → compact history → inject
files last, with a **cache breakpoint** after the stable prefix.

## Build It / Use It

Caching is a provider feature, so this is **Use It** — but the layout is the payoff of
everything you built. `code/cache_aware.py` composes the phase's pieces and marks the
breakpoint, defaulting to **Claude Opus 5**:

```python
import anthropic
client = anthropic.Anthropic()

def build_request(memory, tools, history, files, user_msg):
    system = [{
        "type": "text",
        "text": "You are a coding agent.\n\n" + memory,    # stable: persona + project memory
        "cache_control": {"type": "ephemeral"},            # breakpoint after stable prefix
    }]
    messages = list(history)                                # compacted (lesson 04)
    if files:
        messages.append({"role": "user", "content": files})  # this-turn, wrapped (lesson 05)
    messages.append({"role": "user", "content": user_msg})
    return dict(model="claude-opus-5", max_tokens=1024,
                system=system, tools=tools, messages=messages)
```

Across a session the stable prefix is written to cache once and read cheaply after that.
`usage.cache_read_input_tokens` confirms it.

## Use It

This is precisely why **Claude Code / Codex** keep `CLAUDE.md` / `AGENTS.md` and tool
definitions stable and up front, and compact history instead of rewriting the prefix. A
changed byte early in the prefix would invalidate the cache. As a user, keep memory files
lean and stable, and let the tool manage history. As a builder, never interleave volatile
data into the cached prefix.

## Ship It

[`code/cache_aware.py`](../../06-cache-aware-layout/code/cache_aware.py) — a cache-aware
request builder composing the phase.

## Check Yourself

**Q1.** What invalidates a cached prefix?

- A) a new user message at the end
- B) changing a byte early in the stable prefix
- C) reading the cache
- D) lowering max_tokens

<details><summary>Answer</summary>B — caching reuses an *unchanged* prefix.</details>

**Q2.** Why keep `CLAUDE.md`/`AGENTS.md` lean and stable?

- A) readability only
- B) it's in the cached prefix; bloat costs tokens and churn invalidates the cache
- C) the API requires it
- D) no reason

<details><summary>Answer</summary>B — stable, lean memory maximizes cache value.</details>

**Challenge.** Add a second cache breakpoint after the (stable) tool schemas, and reason
about when two breakpoints help vs. one.

## Related

- Builds on: the whole phase; Phase 1 — [Prompt caching](../../../01-llm-io-foundations/08-prompt-caching/docs/en.md)
- Next: [Measuring context rot](../../07-measuring-context-rot/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
