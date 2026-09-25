# Sampling: temperature, top-p, determinism

> **Motto** — The model outputs a distribution; sampling decides which token you actually get.

*Part of Phase 01 — LLM I/O Foundations.*

## The Problem

"Why did the model give a different answer this time?" Because generation is *sampling*
from a probability distribution over the next token. Temperature and top-p reshape that
distribution. If you don't understand them, you can't make outputs reproducible for
tests, or creative when you want variety. Build the sampler and the knobs stop being
magic.

## The Concept

For each step the model produces logits → a probability over the vocabulary.

- **Temperature** scales logits before softmax: `<1` sharpens (more deterministic), `>1`
  flattens (more random), `→0` ≈ argmax (greedy).
- **Top-p (nucleus)** keeps the smallest set of tokens whose probability sums to `p`,
  renormalizes, samples from those.

<style>
.dgm-samp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-samp-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-samp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-samp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-samp-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-samp-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-samp-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-samp-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-samp-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-samp-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-samp-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-samp-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-samp{padding:20px 16px 18px}.dgm-samp-row{flex-direction:column}}
</style>
<div class="dgm-samp">
  <span class="dgm-samp-chip">From logits to one sampled token</span>
  <h4>Four transforms turn a probability distribution into a choice</h4>
  <p class="dgm-samp-sub">Temperature reshapes it, top-p trims it, then sampling commits to one token.</p>
  <div class="dgm-samp-row">
    <div class="dgm-samp-n neutral">Logits</div>
    <span class="dgm-samp-arr">→</span>
    <div class="dgm-samp-n blue">÷ temperature</div>
    <span class="dgm-samp-arr">→</span>
    <div class="dgm-samp-n ">Softmax</div>
    <span class="dgm-samp-arr">→</span>
    <div class="dgm-samp-n accent">Top-p cut</div>
    <span class="dgm-samp-arr">→</span>
    <div class="dgm-samp-n green">Sample</div>
  </div>
</div>


## Build It

`code/sampling.py` — temperature + top-p over a toy distribution, pure stdlib:

```python
import math, random

def softmax(logits, temp):
    t = max(temp, 1e-6)
    m = max(logits)
    exps = [math.exp((x - m) / t) for x in logits]
    s = sum(exps)
    return [e / s for e in exps]

def top_p_filter(probs, p):
    ranked = sorted(enumerate(probs), key=lambda kv: -kv[1])
    kept, cum = [], 0.0
    for i, pr in ranked:
        kept.append((i, pr)); cum += pr
        if cum >= p:
            break
    z = sum(pr for _, pr in kept)
    return {i: pr / z for i, pr in kept}

def sample(logits, temp=1.0, p=1.0, rng=random.Random(0)):
    probs = softmax(logits, temp)
    nucleus = top_p_filter(probs, p)
    r, acc = rng.random(), 0.0
    for i, pr in nucleus.items():
        acc += pr
        if r <= acc:
            return i
    return next(iter(nucleus))
```

```python
logits = [2.0, 1.0, 0.1, -1.0]
print(sample(logits, temp=0.0001))   # ~always 0 (argmax) — deterministic
print([sample(logits, temp=1.0, rng=__import__('random').Random(s)) for s in range(5)])
```

Low temperature collapses to greedy (reproducible). Higher temperature with top-p gives
controlled variety.

## Use It

In the API you set `temperature` and `top_p` on `messages.create`. For reproducible
evals (Phase 15), pin a low temperature. For brainstorming, raise it. Note: even at
temperature 0, exact determinism isn't guaranteed across infrastructure — design tests to
tolerate small variation.

## Ship It

[`code/sampling.py`](../../03-sampling/code/sampling.py) — a from-scratch temperature/top-p
sampler for intuition and tests.

## Check Yourself

**Q1.** Temperature → 0 makes generation…

- A) more random
- B) greedy / near-deterministic (argmax)
- C) faster
- D) longer

<details><summary>Answer</summary>B — sharpening to the most likely token.</details>

**Q2.** Top-p = 0.9 means…

- A) keep 90% of tokens
- B) keep the smallest set of tokens whose probabilities sum to 0.9, then sample
- C) temperature 0.9
- D) top 9 tokens

<details><summary>Answer</summary>B — nucleus sampling over the cumulative mass.</details>

**Challenge.** Add top-k filtering (keep only the k highest-probability tokens) and show
how top-k and top-p interact.

## Related

- Builds on: [Tokens](../../02-tokens-and-context-window/docs/en.md)
- Next: [Streaming](../../04-streaming/docs/en.md) · Used in: Phase 15 — Evals
- [Roadmap](../../../../ROADMAP.md)
