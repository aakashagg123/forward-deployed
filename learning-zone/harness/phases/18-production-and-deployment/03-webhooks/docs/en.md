# Webhooks & event-driven agents

> **Motto** — Let events wake the agent — a comment, a CI failure, a push — and route each to a handler.

*Part of Phase 18 — Production & Deployment.*

## The Problem

A production agent isn't only invoked by a human typing. It also reacts to **events**: a PR
comment, a failing CI run, a new issue, a merge. An event-driven harness receives webhooks,
authenticates them, routes each event type to a handler, and acts. This turns the agent into
a service that responds to your systems. The risk is untrusted event payloads (Phase 17), so
treat their content as data.

## The Concept

<style>
.dgm-wh{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-wh-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-wh h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-wh-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-wh-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-wh-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-wh-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-wh-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-wh-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-wh-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-wh-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-wh-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-wh{padding:20px 16px 18px}.dgm-wh-row{flex-direction:column}}
.dgm-wh-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-wh-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-wh-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-wh-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-wh-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-wh-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-wh-b.accent h6{color:#0d5c0d}
.dgm-wh-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-wh-b.blue h6{color:#0550ae}
.dgm-wh-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-wh-b.green h6{color:#1a614f}
.dgm-wh-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-wh-b.red h6{color:#82061e}
.dgm-wh-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-wh-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-wh{padding:20px 16px 18px}.dgm-wh-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-wh">
  <span class="dgm-wh-chip">Verify the signature, then route by type</span>
  <h4>Every webhook is verified before it's routed to a type-specific handler</h4>
  <p class="dgm-wh-sub">An unverified webhook is exactly the shape attackers would forge — verify first, always.</p>
  <div class="dgm-wh-row">
    <div class="dgm-wh-n neutral">Webhook event</div>
    <span class="dgm-wh-arr">→</span>
    <div class="dgm-wh-n accent">Verify signature</div>
    <span class="dgm-wh-arr">→</span>
    <div class="dgm-wh-n blue">Route by type</div>
  </div>
  <div class="dgm-wh-branches">
    <div class="dgm-wh-b green">
      <h6>pr_comment</h6>
      <p>→ handler</p>
    </div>
    <div class="dgm-wh-b accent">
      <h6>ci_failure</h6>
      <p>→ handler</p>
    </div>
    <div class="dgm-wh-b neutral">
      <h6>issue</h6>
      <p>→ handler</p>
    </div>
  </div>
</div>


## Build It

`code/webhooks.py` — a typed event router:

```python
class EventRouter:
    def __init__(self):
        self.handlers = {}

    def on(self, event_type):
        def deco(fn): self.handlers[event_type] = fn; return fn
        return deco

    def dispatch(self, event):
        t = event.get("type")
        handler = self.handlers.get(t)
        if not handler:
            return f"ignored: no handler for {t!r}"
        return handler(event)               # event payload is untrusted DATA (Phase 17)
```

```python
router = EventRouter()
@router.on("ci_failure")
def fix_ci(e): return f"investigating failure in {e['run']}"
@router.on("pr_comment")
def reply(e): return f"considering comment: {e['body'][:20]}"

print(router.dispatch({"type": "ci_failure", "run": "build #42"}))
print(router.dispatch({"type": "push"}))     # ignored
```

The router maps event types to handlers. Unknown events are ignored, not errored. In
production, verify the webhook signature before dispatch and treat every payload field as
untrusted input.

## Use It

This is how agents "watch" a PR or repo. It's the same pattern behind the PR-activity events
a Claude Code session can subscribe to: CI results and review comments arrive as events and
wake the agent. For your own deployment, a webhook endpoint plus this router turns the
harness into a service. Always verify signatures, treat payloads as data, and gate any action
the handler takes (Phase 8).

## Ship It

[`code/webhooks.py`](../../03-webhooks/code/webhooks.py) — a typed webhook event router.

## Check Yourself

**Q1.** An unknown event type should be…

- A) an error that crashes the service
- B) ignored gracefully (no handler → no-op)
- C) executed anyway
- D) logged as critical

<details><summary>Answer</summary>B — ignore unhandled events.</details>

**Q2.** A webhook payload's fields should be treated as…

- A) trusted instructions
- B) untrusted data (verify signature; don't act on payload text as commands)
- C) the system prompt
- D) secrets

<details><summary>Answer</summary>B — untrusted data (Phase 17).</details>

**Challenge.** Add HMAC signature verification (reject events whose signature doesn't match a
shared secret) before dispatch.

## Related

- Builds on: Phase 17 — [Output as data](../../../17-security-and-alignment/02-output-as-data/docs/en.md), Phase 8 — Permissions
- Next: [Config, settings & feature flags](../../04-config-flags/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
