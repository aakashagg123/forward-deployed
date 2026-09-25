# Loop, tool & token budgets

> **Motto** — Put a hard ceiling on steps, tools, tokens, and dollars per request — always.

*Part of Phase 14 — Reliability Engineering.*

## The Problem

A **budget** is the single most important guard against a runaway agent. Step ceilings
(Phase 2), tool budgets (Phase 3), and token/cost ceilings work together to bound the worst
case. No request can loop forever or spend unbounded money. A harness without budgets is one
confused plan away from a $100 bill or an infinite loop. Budgets make the worst case *known*.

## The Concept

<style>
.dgm-bud{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-bud-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-bud h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-bud-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-bud-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-bud-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-bud-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-bud-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-bud-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-bud-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-bud-b.accent h6{color:#0d5c0d}
.dgm-bud-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-bud-b.blue h6{color:#0550ae}
.dgm-bud-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-bud-b.green h6{color:#1a614f}
.dgm-bud-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-bud-b.red h6{color:#82061e}
.dgm-bud-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-bud-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-bud{padding:20px 16px 18px}.dgm-bud-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-bud">
  <span class="dgm-bud-chip">One check, every kind of spend</span>
  <h4>Step, tool, and token spend all pass through the same under-budget check</h4>
  <p class="dgm-bud-sub">Stopping reports what was already spent, not just that the budget ran out.</p>
  <div class="dgm-bud-q">Each step/tool/token spend — under all budgets?</div>
  <div class="dgm-bud-branches">
    <div class="dgm-bud-b green">
      <h6>Yes</h6>
      <p>Proceed</p>
    </div>
    <div class="dgm-bud-b red">
      <h6>No</h6>
      <p>Stop, report what was spent, return partial</p>
    </div>
  </div>
</div>


Track multiple meters: steps, tool calls, tokens, and estimated cost. Hitting any one meter
stops the run gracefully and reports what happened. The harness never stops silently and
never auto-extends a budget.

## Build It

`code/budget.py` — a multi-meter budget that the loop checks each step:

```python
class Budget:
    def __init__(self, max_steps=20, max_tokens=100_000, max_usd=1.0):
        self.limits = {"steps": max_steps, "tokens": max_tokens, "usd": max_usd}
        self.spent = {"steps": 0, "tokens": 0, "usd": 0.0}

    def charge(self, steps=0, tokens=0, usd=0.0):
        self.spent["steps"] += steps
        self.spent["tokens"] += tokens
        self.spent["usd"] += usd

    def exceeded(self):
        return [k for k in self.limits if self.spent[k] >= self.limits[k]]

    def report(self):
        return {k: f"{self.spent[k]}/{self.limits[k]}" for k in self.limits}
```

```python
b = Budget(max_steps=3, max_tokens=1000, max_usd=0.10)
for _ in range(5):
    if b.exceeded():
        break
    b.charge(steps=1, tokens=400, usd=0.03)
print(b.exceeded(), b.report())     # ['tokens'] hit first
```

The loop calls `charge` after each model or tool call. It stops when `exceeded()` returns a
non-empty list, and returns what it has so far, with a report of where the budget went.

## Use It

Budgets generalize the orchestration ceilings from Phase 10 (`maxWorkers/maxCallsPerWorker/
maxWaves`) down to the single agent. This is why a Claude Code or Codex user should scope
long autonomous runs, and why the harness's step and token limits exist. Always set them.
Never let "it'll probably be fine" be the only ceiling.

## Ship It

[`code/budget.py`](../../04-budgets/code/budget.py) — a multi-meter budget guard that tracks
steps, tokens, and cost.

## Check Yourself

**Q1.** Why is a budget the most important runaway guard?

- A) it speeds things up
- B) it bounds the worst case — no infinite loops or unbounded spend
- C) it improves accuracy
- D) no reason

<details><summary>Answer</summary>B — a budget makes the worst case known.</details>

**Q2.** On hitting a budget, the harness should…

- A) auto-extend it
- B) stop, return the partial result, and report what was spent
- C) ignore it
- D) crash

<details><summary>Answer</summary>B — stop gracefully. Never auto-extend.</details>

**Challenge.** Wire `Budget` into the Phase 2 agent loop so each step charges steps+tokens
and the loop exits with the report when any meter is hit.

## Related

- Builds on: Phase 2 — [Termination](../../../02-the-agent-loop/03-termination/docs/en.md), Phase 3 — [Tool budgets](../../../03-tool-engineering/05-tool-budgets/docs/en.md)
- Next: [Degraded-mode UX](../../05-degraded-mode/docs/en.md)
- Related: Phase 10 — orchestration budgets, Phase 16 — cost
- [Roadmap](../../../../ROADMAP.md)
