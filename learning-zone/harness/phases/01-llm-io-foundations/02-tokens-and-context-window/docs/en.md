# Tokens & the context window

> **Motto** — You pay per token and you run out of context in tokens — so count them yourself.

*Part of Phase 01 — LLM I/O Foundations.*

## The Problem

The model doesn't see characters. It sees **tokens**. Cost, latency, and the hard limit
of the context window are all measured in tokens. If your harness doesn't track them, it
will silently overflow the window (truncating who-knows-what) or surprise you with a bill.
You need a way to estimate tokens and a budget check before every call.

## The Concept

A token is roughly a word-piece. A common rough rule is **~4 characters ≈ 1 token** for
English. The context window is a fixed budget shared by *input + output*:

```
window = input_tokens + max_output_tokens   ≤   model_limit
```

Your harness must keep the running input under `limit - max_tokens`, or the call fails or
truncates.

## Build It

`code/tokens.py` — a heuristic estimator and a budget guard (real tokenizers exist; the
heuristic is enough to reason about budgets):

```python
def estimate_tokens(text):
    # ~4 chars/token for English; good enough for budgeting decisions.
    return max(1, round(len(text) / 4))

def messages_tokens(messages):
    return sum(estimate_tokens(m["content"]) for m in messages
               if isinstance(m.get("content"), str))

def fits(messages, max_output, limit):
    used = messages_tokens(messages)
    headroom = limit - max_output
    return used <= headroom, used, headroom

def trim_to_budget(messages, max_output, limit, keep_last=2):
    """Drop oldest messages (after the first) until input fits, keeping recent turns."""
    msgs = list(messages)
    ok, *_ = fits(msgs, max_output, limit)
    while not ok and len(msgs) > keep_last + 1:
        del msgs[1]                                  # keep msgs[0]; drop next-oldest
        ok, *_ = fits(msgs, max_output, limit)
    return msgs
```

```python
msgs = [{"role": "user", "content": "x" * 4000}]   # ~1000 tokens
print(fits(msgs, max_output=500, limit=1200))      # (False, 1000, 700)
```

This is the seed of context management (Phase 4): measure, then trim, without splitting
tool pairs.

## Use It

The SDK returns real usage on every response: `msg.usage.input_tokens` and
`output_tokens`. Use the heuristic to *plan* (will this fit?) and the real usage to
*account* (what did it cost?). For exact pre-counting, providers expose a token-counting
endpoint.

## Ship It

[`code/tokens.py`](../../02-tokens-and-context-window/code/tokens.py) — a token estimator and
budget guard.

## Check Yourself

**Q1.** The context window budget is shared between…

- A) only input
- B) input + output tokens
- C) only output
- D) system prompt only

<details><summary>Answer</summary>B — `input + max_output ≤ limit`.</details>

**Q2.** When trimming history to fit, what must you avoid?

- A) keeping recent turns
- B) dropping the system context blindly or splitting a tool_use/tool_result pair
- C) measuring tokens
- D) nothing

<details><summary>Answer</summary>B — preserve required structure (Phase 4 formalizes
this).</details>

**Challenge.** Replace the heuristic with a real tokenizer for one model and compare its
counts to the 4-chars rule on a few samples.

## Related

- Builds on: [Messages, roles & turns](../../01-messages-roles-turns/docs/en.md)
- Next: [Sampling](../../03-sampling/docs/en.md) · Deepens in: Phase 4 — Context Engineering
- [Roadmap](../../../../ROADMAP.md)
