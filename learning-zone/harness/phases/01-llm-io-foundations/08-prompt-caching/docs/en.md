# Prompt caching: what's cacheable and why

> **Motto** — Put the stable bytes first and mark them cacheable; the model re-reads them for almost free.

*Part of Phase 01 — LLM I/O Foundations.*

## The Problem

A coding agent resends a large, mostly-identical prefix on every turn: the system prompt,
tool definitions, project context. Reprocessing those tokens every call is slow and
expensive. Prompt caching lets the provider reuse the computation for an unchanged prefix.
But this only works if your harness lays out the context so the stable part comes first
and is marked cacheable. Lay it out wrong and you get zero cache hits.

## The Concept

<style>
.dgm-pcac{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pcac-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-pcac h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-pcac-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-pcac-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-pcac-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-pcac-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-pcac-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-pcac-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-pcac-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-pcac-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-pcac-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-pcac{padding:20px 16px 18px}.dgm-pcac-row{flex-direction:column}}
</style>
<div class="dgm-pcac">
  <span class="dgm-pcac-chip">Split the prompt at its volatility line</span>
  <h4>A stable prefix caches; a volatile suffix never does</h4>
  <p class="dgm-pcac-sub">System + tools + context rarely change turn to turn — this turn's message always does.</p>
  <div class="dgm-pcac-row">
    <div class="dgm-pcac-n accent">Stable prefix — system + tools + context</div>
    <span class="dgm-pcac-arr">→</span>
    <div class="dgm-pcac-n blue">Cache</div>
    <span class="dgm-pcac-arr">→</span>
    <div class="dgm-pcac-n green">Model call</div>
  </div>
  <div class="dgm-pcac-row" style="margin-top:8px">
    <div class="dgm-pcac-n neutral">Volatile suffix — this turn's user message</div>
    <span class="dgm-pcac-arr">→</span>
    <div class="dgm-pcac-n green">Model call</div>
  </div>
</div>


Rules of thumb:

- **Order by volatility:** stable content first (system, tool schemas, long context),
  changing content last (the new user turn).
- **Mark a cache breakpoint** at the end of the stable prefix.
- **Don't interleave volatile data into the prefix** — one changed byte early invalidates
  the whole cached prefix.

## Build It / Use It

Caching is a provider feature, so this is a **Use It** lesson — but the *layout* is yours.
`code/cache_layout.py` shows how to construct a request with a cached prefix (SDK
`cache_control`), defaulting to **Claude Opus 5**:

```python
import anthropic
client = anthropic.Anthropic()

SYSTEM = [
    {"type": "text", "text": "You are a coding agent. <long stable instructions...>",
     "cache_control": {"type": "ephemeral"}},          # cache breakpoint here
]

def ask(user_text, tools):
    return client.messages.create(
        model="claude-opus-5", max_tokens=1024,
        system=SYSTEM,                                   # stable, cached
        tools=tools,                                     # stable, cached (place before volatile)
        messages=[{"role": "user", "content": user_text}],  # volatile, last
    )
```

The response usage reports `cache_creation_input_tokens` (first call, writes the cache) and
`cache_read_input_tokens` (later calls, cheap reads). You verify caching is working by
watching those numbers, not by guessing.

## Ship It

[`code/cache_layout.py`](../../08-prompt-caching/code/cache_layout.py) — a cache-aware request
layout you reuse whenever a big stable prefix repeats.

## Check Yourself

**Q1.** Why must stable content come *before* volatile content?

- A) readability
- B) caching reuses an unchanged prefix; a change early invalidates everything after it
- C) the API sorts it
- D) it doesn't matter

<details><summary>Answer</summary>B — order by volatility so the cached prefix stays
valid.</details>

**Q2.** How do you confirm caching is actually happening?

- A) it always is
- B) check `cache_read_input_tokens` in the response usage
- C) time the call once
- D) you can't

<details><summary>Answer</summary>B — the usage fields report cache writes and
reads.</details>

**Challenge.** Measure it: make two identical-prefix calls and print
`cache_creation_input_tokens` then `cache_read_input_tokens` to see the cache populate
then hit.

## Related

- Builds on: [Tokens & the context window](../../02-tokens-and-context-window/docs/en.md)
- Deepens in: Phase 4 — Context Engineering, Phase 16 — Observability & Cost
- Phase complete → next: Phase 3 — [Tool Engineering](../../../../ROADMAP.md)
- Other tracks: [Prompt vs. semantic caching](../../../../../content/01-inference-internals/prompt-vs-semantic-caching.md) · [KV cache management](../../../../../content/01-inference-internals/kv-cache-management.md) — the inference-side view of what you cache and why.
- [Roadmap](../../../../ROADMAP.md)
