# Fallback chains & model routing

> **Motto** — When the first choice fails or is overkill, route to the next — by health and by fit.

*Part of Phase 14 — Reliability Engineering.*

## The Problem

A single hardcoded model is a single point of failure, and often the wrong cost/latency
tradeoff. **Routing** picks the right model per task: a cheap model for simple work, a
strong model for hard work. A **fallback chain** tries the next option when one errors or is
overloaded, so a provider blip degrades quality instead of availability.

## The Concept

<style>
.dgm-fr{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-fr-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-fr h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-fr-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-fr-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-fr-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-fr-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-fr-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-fr-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-fr-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-fr-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-fr-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-fr{padding:20px 16px 18px}.dgm-fr-row{flex-direction:column}}
</style>
<div class="dgm-fr">
  <span class="dgm-fr-chip">A chain of fallbacks, routed by difficulty and cost</span>
  <h4>Primary fails, try fallback 1; that fails, try fallback 2; all fail, degrade</h4>
  <p class="dgm-fr-sub">Routing by difficulty upfront means most tasks never touch the fallback chain at all.</p>
  <div class="dgm-fr-row">
    <div class="dgm-fr-n neutral">Task</div>
    <span class="dgm-fr-arr">→</span>
    <div class="dgm-fr-n accent">Route by difficulty/cost</div>
    <span class="dgm-fr-arr"><span class='lbl'>fails</span>→</span>
    <div class="dgm-fr-n blue">Primary</div>
    <span class="dgm-fr-arr"><span class='lbl'>fails</span>→</span>
    <div class="dgm-fr-n accent">Fallback 1</div>
    <span class="dgm-fr-arr"><span class='lbl'>fails</span>→</span>
    <div class="dgm-fr-n red">Fallback 2</div>
    <span class="dgm-fr-arr">→</span>
    <div class="dgm-fr-n red">All failed → degraded mode</div>
  </div>
</div>


Routing chooses the *first* try by fit. The chain handles *failure* by trying the rest.

## Build It

`code/routing.py` — a router + fallback chain:

```python
def route(task, simple_model, strong_model, is_hard):
    return [strong_model, simple_model] if is_hard(task) else [simple_model, strong_model]

def with_fallback(chain, call):
    """Try each option in order; return first success, else raise the last error."""
    last = None
    for option in chain:
        try:
            return {"model": option, "result": call(option)}
        except Exception as e:
            last = e
    raise RuntimeError(f"all options failed: {last}")
```

```python
def call(model):
    if model == "strong": raise RuntimeError("overloaded")
    return f"answer from {model}"
chain = route("simple task", "haiku", "strong", is_hard=lambda t: "complex" in t)
print(with_fallback(["strong", "haiku"], call))   # falls back to haiku
```

Routing keeps cost down on easy tasks. The fallback chain keeps the service up when the
preferred model errors. Both decisions live in the harness, not the business logic.

## Use It

For Claude Code and Codex users, this is model selection — a fast model for routine edits, a
stronger model for hard reasoning — plus the SDK or provider's own resilience. In a custom
harness, you implement the chain explicitly. The key principle, from the conceptual track:
you can change models without rewriting business logic, because routing is a harness
concern.

## Ship It

[`code/routing.py`](../../03-fallback-routing/code/routing.py) — a model router + fallback
chain.

## Check Yourself

**Q1.** Routing decides ___; a fallback chain handles ___.

- A) failure; cost
- B) the first try by fit (cost/difficulty); failure by trying the next option
- C) nothing; everything
- D) tokens; latency

<details><summary>Answer</summary>B — fit first, failure next.</details>

**Q2.** Why route simple tasks to a cheaper model?

- A) accuracy
- B) cost/latency — don't pay for a strong model on trivial work
- C) it's required
- D) no reason

<details><summary>Answer</summary>B — match capability to need.</details>

**Challenge.** Add a circuit breaker: after N consecutive failures of an option, skip it for
a cooldown period instead of retrying it every time.

## Related

- Builds on: [Retries](../../01-retries/docs/en.md)
- Next: [Loop, tool & token budgets](../../04-budgets/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
