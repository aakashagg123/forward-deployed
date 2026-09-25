# Plan mode: propose before you act

> **Motto** — For risky or ambiguous work, the agent proposes a plan and waits — read-only until you say go.

*Part of Phase 11 — Planning & Task Management.*

## The Problem

Letting an agent start editing immediately on a big or fuzzy task is how you get the wrong
thing built fast. **Plan mode** inverts that. The agent may *read and analyze* but **not
mutate** anything. It produces a plan. You approve it, or redirect it. Only then does it
act. It's the spec-first principle (Phase 10) at the single-agent level.

## The Concept

<style>
.dgm-plm{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-plm-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-plm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-plm-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-plm-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-plm-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-plm-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-plm-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-plm-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-plm-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-plm-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-plm-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-plm{padding:20px 16px 18px}.dgm-plm-row{flex-direction:column}}
.dgm-plm-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-plm-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-plm-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-plm-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-plm-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-plm-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-plm-b.accent h6{color:#0d5c0d}
.dgm-plm-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-plm-b.blue h6{color:#0550ae}
.dgm-plm-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-plm-b.green h6{color:#1a614f}
.dgm-plm-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-plm-b.red h6{color:#82061e}
.dgm-plm-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-plm-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-plm{padding:20px 16px 18px}.dgm-plm-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-plm">
  <span class="dgm-plm-chip">Read-only, until a human says go</span>
  <h4>Plan mode can analyze and propose — it cannot act until the plan is approved</h4>
  <p class="dgm-plm-sub">That read-only boundary is what makes it safe to let the agent plan autonomously.</p>
  <div class="dgm-plm-row">
    <div class="dgm-plm-n neutral">Task</div>
    <span class="dgm-plm-arr">→</span>
    <div class="dgm-plm-n accent">PLAN MODE: read-only — analyze + propose</div>
  </div>
  <div class="dgm-plm-q">Human approves plan?</div>
  <div class="dgm-plm-branches">
    <div class="dgm-plm-b red">
      <h6>No</h6>
      <p>Revise / redirect</p>
    </div>
    <div class="dgm-plm-b green">
      <h6>Yes</h6>
      <p>Exit plan mode → act</p>
    </div>
  </div>
</div>


The enforcement is a permission mode (Phase 8). In plan mode, mutating tools
(write/edit/bash) are denied, but reads are allowed.

## Build It

`code/plan_mode.py` — a read-only gate that blocks mutations until approved:

```python
MUTATING = {"write", "edit", "bash"}

class PlanMode:
    def __init__(self):
        self.active = True
        self.plan = None

    def propose(self, plan):
        self.plan = plan
        return "plan ready for approval:\n" + plan

    def approve(self):
        self.active = False
        return "approved — exiting plan mode"

    def gate(self, tool):
        if self.active and tool in MUTATING:
            return f"blocked: '{tool}' not allowed in plan mode (read-only until approved)"
        return "allowed"
```

```python
pm = PlanMode()
print(pm.gate("read"))        # allowed
print(pm.gate("write"))       # blocked (plan mode)
pm.propose("1) edit api.py 2) add test")
pm.approve()
print(pm.gate("write"))       # allowed (after approval)
```

The gate makes plan mode real: the agent literally cannot mutate the repo until you approve
the plan — not by promise, by permission.

## Use It

This is Claude Code's **plan mode** (shift-tab / `--permission-mode plan`): the agent
researches and presents a plan, and edits are blocked until you accept it. Codex has an
equivalent propose-then-apply flow. Use it for anything non-trivial — it's the cheapest way
to catch a wrong approach before any code is written.

## Ship It

[`code/plan_mode.py`](../../02-plan-mode/code/plan_mode.py) — a read-only plan-mode gate.

## Check Yourself

**Q1.** What can the agent do in plan mode?

- A) anything
- B) read and analyze, but not mutate (write/edit/bash) until approved
- C) nothing
- D) only write

<details><summary>Answer</summary>B — read-only until the plan is accepted.</details>

**Q2.** Plan mode is enforced by…

- A) a polite prompt
- B) a permission mode that denies mutating tools (Phase 8)
- C) the model's goodwill
- D) a timeout

<details><summary>Answer</summary>B — it's permission enforcement, not persuasion.</details>

**Challenge.** Wire `PlanMode` into the Phase 8 `PermissionGate` as a mode that returns
`deny` for mutating tools, so plan mode is just a permission configuration.

## Related

- Builds on: [Todo model](../../01-todo-model/docs/en.md), Phase 8 — [Permission modes](../../../08-permissions-and-safety-gating/01-permission-modes/docs/en.md)
- Next: [Task decomposition prompts](../../03-decomposition/docs/en.md)
- Related: Phase 10 — spec-first
- [Roadmap](../../../../ROADMAP.md)
