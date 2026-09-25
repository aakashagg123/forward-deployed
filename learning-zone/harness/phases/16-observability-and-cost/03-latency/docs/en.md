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

<style>
.dgm-lat{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-lat-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-lat h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-lat-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-lat-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-lat-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-lat-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-lat-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-lat-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-lat-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-lat-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-lat-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-lat{padding:20px 16px 18px}.dgm-lat-row{flex-direction:column}}
</style>
<div class="dgm-lat">
  <span class="dgm-lat-chip">Two phases, two different costs</span>
  <h4>Prefill is one cost to first token; decode is a per-token cost after that</h4>
  <p class="dgm-lat-sub">Total latency is TTFT plus output tokens times per-token time — they don't optimize the same way.</p>
  <div class="dgm-lat-row">
    <div class="dgm-lat-n neutral">Request</div>
    <span class="dgm-lat-arr">→</span>
    <div class="dgm-lat-n accent">Prefill (input → first token) = TTFT</div>
    <span class="dgm-lat-arr">→</span>
    <div class="dgm-lat-n blue">Decode (token by token)</div>
    <span class="dgm-lat-arr">→</span>
    <div class="dgm-lat-n green">Total = TTFT + output_tokens × per_token</div>
  </div>
</div>


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
