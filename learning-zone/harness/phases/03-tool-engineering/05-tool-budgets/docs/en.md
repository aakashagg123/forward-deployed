# Tool budgets & rate limits

> **Motto** — Cap how often and how much the agent can act, before it caps your bill.

*Part of Phase 03 — Tool Engineering.*

## The Problem

A tool the agent can call freely is a tool it can call 200 times. Termination (Phase 2)
bounds *steps*, but a single step can fire many tool calls, and some tools are expensive
or rate-limited upstream. You need per-tool ceilings — total calls, calls per window —
enforced at the dispatch boundary. That way a runaway plan or a hammering loop stops
early.

## The Concept

<style>
.dgm-tb{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-tb-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-tb h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-tb-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-tb-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-tb-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-tb-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-tb-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-tb-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-tb-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-tb-b.accent h6{color:#0d5c0d}
.dgm-tb-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-tb-b.blue h6{color:#0550ae}
.dgm-tb-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-tb-b.green h6{color:#1a614f}
.dgm-tb-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-tb-b.red h6{color:#82061e}
.dgm-tb-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-tb-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-tb{padding:20px 16px 18px}.dgm-tb-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-tb">
  <span class="dgm-tb-chip">A budget check gates every call</span>
  <h4>Under budget runs and records; over budget gets a message, not an error</h4>
  <p class="dgm-tb-sub">The model can read a budget-denial message and change its plan.</p>
  <div class="dgm-tb-q">Tool call — under budget?</div>
  <div class="dgm-tb-branches">
    <div class="dgm-tb-b green">
      <h6>Yes</h6>
      <p>Run + record</p>
    </div>
    <div class="dgm-tb-b red">
      <h6>No</h6>
      <p>Deny: budget message → model</p>
    </div>
  </div>
</div>


Two limits cover most cases: a **total** count per request, and a **rate** (N per rolling
window) to respect upstream limits.

## Build It

`code/budgets.py` — a budget guard usable as a pre-dispatch gate (a PreToolUse hook in a
real harness):

```python
import time

class ToolBudget:
    def __init__(self, max_total=20, per_window=5, window_s=10):
        self.max_total, self.per_window, self.window_s = max_total, per_window, window_s
        self.total = 0
        self.calls = []                        # timestamps within the window

    def allow(self, now=None):
        now = now if now is not None else time.time()
        self.calls = [t for t in self.calls if now - t < self.window_s]
        if self.total >= self.max_total:
            return False, "total tool budget exhausted"
        if len(self.calls) >= self.per_window:
            return False, f"rate limit: max {self.per_window}/{self.window_s}s"
        self.calls.append(now); self.total += 1
        return True, None
```

```python
b = ToolBudget(max_total=20, per_window=2, window_s=10)
print(b.allow(now=0))    # (True, None)
print(b.allow(now=0))    # (True, None)
print(b.allow(now=0))    # (False, 'rate limit: max 2/10s')
print(b.allow(now=11))   # (True, None)  ← window slid
```

A denied call returns a message to the model ("budget exhausted"). The agent can wrap up
gracefully instead of crashing.

## Use It

In Claude Code this is a `PreToolUse` hook (Phase 8). It inspects the pending tool call
and exits non-zero to deny when over budget. The same guard protects an upstream API's
rate limit by keying the window per tool.

## Ship It

[`code/budgets.py`](../../05-tool-budgets/code/budgets.py) — a total + rolling-window tool
budget guard.

## Check Yourself

**Q1.** Why aren't step ceilings (Phase 2) enough?

- A) they are
- B) one step can fire many tool calls, so you also need per-tool/call ceilings
- C) steps are unlimited
- D) tools are free

<details><summary>Answer</summary>B — bound calls and rate, not just steps.</details>

**Q2.** When a tool budget is hit, the harness should…

- A) crash
- B) deny the call with a message so the model can wrap up
- C) silently allow it
- D) double the budget

<details><summary>Answer</summary>B — deny gracefully; never auto-extend.</details>

**Challenge.** Add per-tool budgets (a different ceiling for an expensive tool vs. a cheap
one) keyed by tool name.

## Related

- Builds on: [Idempotency](../../04-idempotency/docs/en.md)
- Next: [Writing tool descriptions](../../06-tool-descriptions/docs/en.md)
- Deepens in: Phase 8 — Permissions (hooks), Phase 14 — Reliability
- [Roadmap](../../../../ROADMAP.md)
