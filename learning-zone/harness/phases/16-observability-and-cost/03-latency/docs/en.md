# Latency: prefill vs. decode, TTFT

> **Motto** — Latency has two halves: time to the first token, then time per token after.

*Part of Phase 16 — Observability & Cost.*

## The Problem

"The agent feels slow" is not actionable on its own. Model latency breaks into two parts:
**prefill**, which processes the input and produces the first token (measured as **TTFT**,
time-to-first-token), and **decode**, which generates each token after that. A long input
makes prefill slow. A long output makes decode slow. Measuring them separately tells you
which fix to apply — trim the context, or shorten the output.

## The Concept

```mermaid
flowchart LR
  R["request"] --> P["prefill (input → first token) = TTFT"]
  P --> D["decode (token by token)"]
  D --> E["total = TTFT + output_tokens × per_token"]
```

A big context inflates TTFT — this is why prompt caching (Phase 1 L8) helps. A long
generation inflates decode — this is why streaming (Phase 1 L4) improves *perceived*
latency.

## Build It

`code/latency.py` — measure TTFT vs. total from a (simulated) streamed call:

```python
import time

def measure(stream, now=time.perf_counter):
    start = now()
    ttft = None
    tokens = 0
    for _ in stream:
        if ttft is None:
            ttft = now() - start          # first token arrived
        tokens += 1
    total = now() - start
    decode = total - (ttft or 0)
    return {"ttft_s": round(ttft or 0, 4), "total_s": round(total, 4),
            "tokens": tokens,
            "per_token_ms": round(decode / max(tokens - 1, 1) * 1000, 2)}
```

```python
def fake_stream():
    time.sleep(0.05)            # prefill
    for _ in range(5):
        time.sleep(0.01)        # decode per token
        yield "tok"
print(measure(fake_stream()))   # ttft ~0.05s, then ~10ms/token
```

Now "slow" is a number, not a feeling. A high TTFT points at input size — trim the context
or cache it. A high per-token time points at output length — shorten it or stream it.

## Use It

The SDK's streaming API (Phase 1 L4) is how you observe TTFT in practice — the first delta
you receive is the TTFT. For a Claude Code or Codex user, streaming makes long generations
*feel* fast even when total latency is high. A lean, cached context also keeps TTFT low.
Track p50/p95 TTFT and total latency in your traces (lesson 01) to catch regressions.

## Ship It

[`code/latency.py`](../../03-latency/code/latency.py) — a TTFT / decode latency meter over a
stream.

## Check Yourself

**Q1.** A high TTFT points at…

- A) output length
- B) input size / prefill — trim context or use caching
- C) the network only
- D) nothing

<details><summary>Answer</summary>B — prefill dominates TTFT; shrink/cache input.</details>

**Q2.** Streaming improves…

- A) total latency
- B) *perceived* latency — the user sees tokens immediately even if total is unchanged
- C) cost
- D) accuracy

<details><summary>Answer</summary>B — perceived, via early first token.</details>

**Challenge.** Aggregate `measure` over many runs and report p50/p95 TTFT and per-token, so
you can alert on latency regressions.

## Related

- Builds on: Phase 1 — [Streaming](../../../01-llm-io-foundations/04-streaming/docs/en.md), [Prompt caching](../../../01-llm-io-foundations/08-prompt-caching/docs/en.md)
- Next: [Drift detection](../../04-drift/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
