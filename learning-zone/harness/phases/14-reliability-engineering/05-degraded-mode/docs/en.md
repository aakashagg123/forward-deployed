# Degraded-mode UX

> **Motto** — When the agent can't do the whole job, do part of it well and say what's missing.

*Part of Phase 14 — Reliability Engineering.*

## The Problem

Retries fail, fallbacks exhaust, budgets run out. Sometimes the agent genuinely can't
complete the task. The wrong response is to crash with a stack trace or, worse, fabricate a
success. **Degraded mode** is the graceful answer. Return whatever partial, verified result
you have, state clearly what couldn't be done and why, and offer a next step. This is the
reliability payoff users actually feel.

## The Concept

<style>
.dgm-dm{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-dm-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-dm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-dm-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-dm-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-dm-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-dm-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-dm-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-dm-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-dm-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-dm-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-dm-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-dm{padding:20px 16px 18px}.dgm-dm-row{flex-direction:column}}
</style>
<div class="dgm-dm">
  <span class="dgm-dm-chip">A partial result, clearly labeled as partial</span>
  <h4>Salvage what's verified, say what's missing, offer a next step</h4>
  <p class="dgm-dm-sub">Degraded mode is a designed exit, not a crash — the user gets something plus a path forward.</p>
  <div class="dgm-dm-row">
    <div class="dgm-dm-n red">Run hits a wall (budget/fallback/error)</div>
    <span class="dgm-dm-arr">→</span>
    <div class="dgm-dm-n accent">Salvage verified partial result</div>
    <span class="dgm-dm-arr">→</span>
    <div class="dgm-dm-n blue">State clearly what's incomplete + why</div>
    <span class="dgm-dm-arr">→</span>
    <div class="dgm-dm-n green">Offer a next step (retry later / narrower scope / human)</div>
  </div>
</div>


The contract: never silently drop work, and never claim success you didn't verify. This ties
back to "report outcomes faithfully."

## Build It

`code/degraded.py` — wrap a run to always return a structured, honest result:

```python
def run_with_degrade(do, budget):
    """do(budget)->partial result dict. Always returns a structured outcome."""
    try:
        result = do(budget)
        hit = budget.exceeded()
        if hit:
            return {"status": "degraded", "partial": result,
                    "reason": f"budget exhausted: {hit}",
                    "next": "narrow the scope or raise the budget and resume"}
        return {"status": "complete", "result": result}
    except Exception as e:
        return {"status": "failed", "error": str(e),
                "next": "retry later or escalate to a human"}
```

```python
class B:                         # stand-in budget
    def __init__(self): self.over = True
    def exceeded(self): return ["tokens"] if self.over else []
print(run_with_degrade(lambda b: {"done": ["step1", "step2"]}, B()))
# status: degraded, partial result + reason + next step
```

Every outcome is structured and honest: complete, degraded (with partial result, reason, and
next step), or failed (with error and next step). The user always knows exactly where things
stand.

## Use It

For a Claude Code or Codex user, this is the difference between "I edited 3 of 5 files; the
other 2 failed type-checking — here's the error and what I'd try next" and a crash or a false
"done." Insist on it. A good agent reports partial progress and failures plainly. This is the
user-facing capstone of the whole reliability phase.

## Ship It

[`code/degraded.py`](../../05-degraded-mode/code/degraded.py) — a degrade-gracefully run
wrapper.

## Check Yourself

**Q1.** When the agent can't finish, the right response is…

- A) crash with a stack trace
- B) return verified partial work + what's missing + a next step
- C) claim success anyway
- D) silently stop

<details><summary>Answer</summary>B — degrade gracefully and honestly.</details>

**Q2.** Degraded mode must never…

- A) return partial results
- B) claim success that wasn't verified
- C) suggest a next step
- D) state a reason

<details><summary>Answer</summary>B — never fabricate success.</details>

**Challenge.** Extend the wrapper to attach the budget `report()` (Phase 14 L4) to a degraded
result so the user sees exactly what was spent.

## Related

- Builds on: [Budgets](../../04-budgets/docs/en.md), [Fallback routing](../../03-fallback-routing/docs/en.md)
- Next: [Production failure-mode playbook](../../06-failure-playbook/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
