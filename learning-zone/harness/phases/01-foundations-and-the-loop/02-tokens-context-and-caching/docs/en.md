# Tokens, Context and Caching

> **Motto** — Count tokens before you send, and put the bytes that never change at the front so the provider can reuse them.

*Part of Phase 01 — Foundations and the Loop.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

The model reads tokens, not characters. Cost, speed, and the size of the context window are all measured in tokens. A harness that does not count them overflows the window or surprises you with a bill.

An agent also resends a large, mostly identical prefix on every turn. That prefix holds the system prompt, the tool schemas, and the project rules. Paying to process it each time is slow and costly. Lay the request out badly and you get no reuse at all.

## The Concept

A token is a word piece. For English, 4 characters is about 1 token on older tokenizers. Claude Opus 4.7 and later use a newer tokenizer that gives about 30% more tokens for the same text, roughly 2.5 characters per token. This is a planning rule only, and it is optimistic for current models. Use the token-counting endpoint for any tight budget.

The window is shared: `input + max_output` must stay within the model limit.

Prompt caching lets the provider reuse its work on an unchanged prefix. The prefix order is fixed: tools, then system, then messages. You mark its end with `cache_control`. A change at any level breaks the cache for that level and every level after it. Short prefixes are never cached. The minimum length depends on the model.

<style>
.dgm-pcac{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pcac-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-pcac h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-pcac-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-pcac-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-pcac-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-pcac-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-pcac-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-pcac-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-pcac-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-pcac-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-pcac-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
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


## Build It

`code/cache_layout.py` keeps the window rule in one function. The check uses the 4-character estimate.

```python
def fits(req, max_output, limit):
    """Window rule: input + max_output must stay within the model limit."""
    used, room = request_tokens(req), limit - max_output
    return used <= room, used, room
```

`build_request` orders the request by volatility. It puts the breakpoint on the last stable block.

```python
def build_request(system_text, tools, history, user_text):
    """Order by volatility: tools, then system, then messages. Mark the end of the prefix."""
    system = [{"type": "text", "text": system_text,
               "cache_control": {"type": "ephemeral"}}]       # breakpoint
    messages = history + [{"role": "user", "content": user_text}]
    return {"tools": tools, "system": system, "messages": messages}
```

The provider holds the real cache. This file models the one rule you control: the prefix must match byte for byte. `cache_hit` compares two prefixes and applies a minimum length.

```python
def cached_prefix(req):
    """Everything up to and including the block that carries cache_control."""
    return json.dumps([req["tools"], req["system"]], sort_keys=True)


def cache_hit(previous, new):
    """A hit needs an identical prefix that is long enough to be cached."""
    same = cached_prefix(previous) == cached_prefix(new)
    return same and estimate_tokens(cached_prefix(new)) >= MIN_CACHE_TOKENS
```

The asserts prove four cases. A new last message hits. A timestamp at the top of the system prompt misses. A reworded tool description misses, because tools come first. A short prompt misses even when identical.

## Use It

`code/cache_layout_sdk.py` sends two requests with the same prefix. It needs `pip install anthropic` and `ANTHROPIC_API_KEY`. The usage object tells you what happened:

- `cache_creation_input_tokens` counts tokens written to the cache.
- `cache_read_input_tokens` counts tokens read from it.
- `input_tokens` counts only the tokens after the last breakpoint.

The total input is the sum of the three. Watch these numbers. Do not guess.

Cache entries last 5 minutes by default, and you can set up to 4 breakpoints. A 5-minute write costs 1.25 times the base input price. A read costs a fraction of it: 0.1 times on most models and less on some (0.05 times on Opus 5.5). Check the pricing page for your model.

To plan before you send, call `client.messages.count_tokens(...)`. It takes the same arguments as `create`, returns `input_tokens`, and is free. The count is an estimate.

## Challenge

Add a second breakpoint after the older turns of the history. Then list which single edit breaks each breakpoint: a tool description, a system line, an old message, and the new message.

## Sources

[Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) · [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)

Other tracks: [Prompt vs. semantic caching](../../../../../content/01-inference-internals/prompt-vs-semantic-caching.md) and [KV cache management](../../../../../content/01-inference-internals/kv-cache-management.md) cover the inference side.

Next: [The Agent Loop](../../03-the-agent-loop/docs/en.md)
