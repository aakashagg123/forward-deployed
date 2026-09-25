# Idempotency & side-effecting tools

> **Motto** — The loop may retry; a side-effecting tool must not act twice.

*Part of Phase 03 — Tool Engineering.*

## The Problem

Read-only tools are safe to retry. But the moment a tool *does* something — sends an
email, charges a card, creates a file, opens a PR — retries become dangerous. The agent
loop retries on errors (Phase 2 lesson 06), a transient network blip can re-trigger a
call, and a confused model can repeat itself. Without idempotency you get double-sends
and duplicate charges. This is the most expensive class of tool bug, because it touches
the real world.

## The Concept

Make each side-effecting call carry an **idempotency key** derived from its intent. The
harness records completed keys. A repeat with the same key returns the stored result
instead of acting again.

<style>
.dgm-idem{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-idem-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-idem h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-idem-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-idem-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-idem-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-idem-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-idem-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-idem-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-idem-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-idem-b.accent h6{color:#0d5c0d}
.dgm-idem-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-idem-b.blue h6{color:#0550ae}
.dgm-idem-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-idem-b.green h6{color:#1a614f}
.dgm-idem-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-idem-b.red h6{color:#82061e}
.dgm-idem-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-idem-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-idem{padding:20px 16px 18px}.dgm-idem-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-idem">
  <span class="dgm-idem-chip">A seen key means the action already happened</span>
  <h4>The idempotency key is what makes a retried call safe</h4>
  <p class="dgm-idem-sub">Without it, a retry after a timeout can double-charge or double-send.</p>
  <div class="dgm-idem-q">Call + idempotency key — key seen before?</div>
  <div class="dgm-idem-branches">
    <div class="dgm-idem-b accent">
      <h6>Yes</h6>
      <p>Return stored result — no re-action</p>
    </div>
    <div class="dgm-idem-b green">
      <h6>No</h6>
      <p>Act, store result under key</p>
    </div>
  </div>
</div>


## Build It

`code/idempotency.py` — a wrapper that dedupes by key:

```python
class Idempotent:
    def __init__(self):
        self._done = {}                        # key -> result

    def run(self, key, action):
        if key in self._done:
            return self._done[key], "replayed"
        result = action()                      # the real side effect
        self._done[key] = result
        return result, "executed"

def key_for(tool, args):
    import hashlib, json
    blob = json.dumps([tool, args], sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]
```

```python
idem = Idempotent()
sends = []
send = lambda: (sends.append("email"), "sent")[1]
k = key_for("send_email", {"to": "a@b.com"})
print(idem.run(k, send))     # ('sent', 'executed')
print(idem.run(k, send))     # ('sent', 'replayed')  ← no second send
print("emails sent:", len(sends))   # 1
```

One real action happens, even though the loop "called" twice. The key is derived from
intent, so an identical request dedupes while a different one proceeds.

## Use It

In production the `_done` store is durable (a DB or Redis), keyed by a client-supplied
idempotency key, often with a TTL. Many real APIs, payments especially, accept an
`Idempotency-Key` header for exactly this reason. Your wrapper is the agent-side
counterpart.

## Ship It

[`code/idempotency.py`](../../04-idempotency/code/idempotency.py) — an idempotency wrapper +
key derivation.

## Check Yourself

**Q1.** Why do side-effecting tools need idempotency but read-only ones don't?

- A) they're slower
- B) retries on a side-effecting tool cause double actions (double-send/charge)
- C) the model prefers it
- D) they don't

<details><summary>Answer</summary>B — retries are safe for reads, dangerous for
writes.</details>

**Q2.** What should the idempotency key be derived from?

- A) the current time
- B) the call's intent (tool + args), so identical requests dedupe
- C) a random number
- D) the model name

<details><summary>Answer</summary>B — intent-derived keys dedupe repeats but let distinct
calls through.</details>

**Challenge.** Add a TTL so keys expire, and make `run` re-execute (not replay) once a key
has aged out.

## Related

- Builds on: [Results & errors](../../03-results-and-errors/docs/en.md)
- Next: [Tool budgets & rate limits](../../05-tool-budgets/docs/en.md)
- Related: Phase 14 — Reliability (retries)
- [Roadmap](../../../../ROADMAP.md)
