# Retries, backoff & jitter

> **Motto** — Transient failures deserve a retry — with growing, jittered delays so you don't stampede.

*Part of Phase 14 — Reliability Engineering.*

## The Problem

Model and tool calls fail transiently: rate limits (429), overloaded servers (503), network
blips. Giving up on the first failure makes the agent flaky. Retrying *immediately*, in
lockstep with everyone else, makes the overload worse. The fix is **exponential backoff with
jitter**: wait longer after each failure, and add randomness so concurrent clients don't
retry in sync.

## The Concept

<style>
.dgm-ret{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ret-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ret h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ret-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ret-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-ret-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-ret-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-ret-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-ret-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-ret-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-ret-b.accent h6{color:#0d5c0d}
.dgm-ret-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-ret-b.blue h6{color:#0550ae}
.dgm-ret-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-ret-b.green h6{color:#1a614f}
.dgm-ret-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-ret-b.red h6{color:#82061e}
.dgm-ret-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-ret-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-ret{padding:20px 16px 18px}.dgm-ret-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-ret">
  <span class="dgm-ret-chip">Backoff with jitter, until the budget runs out</span>
  <h4>A transient failure waits and retries; a permanent one just returns or raises</h4>
  <p class="dgm-ret-sub">Jitter spreads retries out so they don't all hammer the service at the same instant.</p>
  <div class="dgm-ret-q">Call — transient failure?</div>
  <div class="dgm-ret-branches">
    <div class="dgm-ret-b green">
      <h6>No</h6>
      <p>Return / raise</p>
    </div>
    <div class="dgm-ret-b accent">
      <h6>Yes, retries left</h6>
      <p>Wait base×2^n + jitter → call again</p>
    </div>
    <div class="dgm-ret-b red">
      <h6>Yes, budget spent</h6>
      <p>Give up → fallback</p>
    </div>
  </div>
</div>


Only **transient** errors retry; a 400 (bad request) won't fix itself, so it fails fast.

## Build It

`code/retry.py` — exponential backoff + jitter (sleep injected so it's testable):

```python
import random

TRANSIENT = (429, 500, 502, 503, 504)

def retry(call, is_transient, max_attempts=5, base=0.5, sleep=lambda s: None, rng=random):
    for attempt in range(max_attempts):
        try:
            return call()
        except Exception as e:
            if not is_transient(e) or attempt == max_attempts - 1:
                raise
            delay = base * (2 ** attempt) + rng.uniform(0, base)   # backoff + jitter
            sleep(delay)
```

```python
calls = {"n": 0}
def flaky():
    calls["n"] += 1
    if calls["n"] < 3:
        raise RuntimeError("503")
    return "ok"
print(retry(flaky, is_transient=lambda e: "503" in str(e)))   # ok (after 2 backoffs)
```

The delay grows (`base·2ⁿ`) and adds jitter. A non-transient error, or an exhausted retry
budget, re-raises so the caller can fall back (lesson 03) instead of hanging.

## Use It

The Anthropic SDK retries idempotent requests with backoff by default. You add retries
around *your* tool calls and any non-SDK I/O. One rule pairs with this: retried actions must
be idempotent (Phase 3 lesson 04), or a retry will double-act. Backoff and jitter are the
same discipline whether it's an API call or a flaky test.

## Ship It

[`code/retry.py`](../../01-retries/code/retry.py) — exponential-backoff-with-jitter retry.

## Check Yourself

**Q1.** Why add jitter to backoff?

- A) to look random
- B) so many clients don't retry in lockstep and re-overload the server
- C) it's required
- D) no reason

<details><summary>Answer</summary>B — jitter de-synchronizes retries.</details>

**Q2.** Which error should NOT be retried?

- A) 429 rate limit
- B) 503 overloaded
- C) 400 bad request (won't fix itself)
- D) a network timeout

<details><summary>Answer</summary>C — fail fast on non-transient errors.</details>

**Challenge.** Add a maximum total delay cap and respect a `Retry-After` header value when
present (overriding the computed backoff).

## Related

- Builds on: Phase 3 — [Idempotency](../../../03-tool-engineering/04-idempotency/docs/en.md), Phase 2 — [Error recovery](../../../02-the-agent-loop/06-error-recovery/docs/en.md)
- Next: [Validation & repair loops](../../02-repair-loops/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
