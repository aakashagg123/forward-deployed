# Progress tracking & self-correction

> **Motto** — Watch the plan execute — when a step stalls or fails, re-plan instead of grinding.

*Part of Phase 11 — Planning & Task Management.*

## The Problem

A plan is only useful if the agent *tracks* its execution and reacts. Two failure modes:
the agent marks a step done that didn't actually pass its check (false progress), or it
retries the same failing step forever (no self-correction). The harness needs to verify each
step's done-check and, on repeated failure, trigger a re-plan rather than spin.

## The Concept

<style>
.dgm-pt{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pt-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-pt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-pt-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-pt-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-pt-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-pt-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-pt-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-pt-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-pt-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-pt-b.accent h6{color:#0d5c0d}
.dgm-pt-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-pt-b.blue h6{color:#0550ae}
.dgm-pt-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-pt-b.green h6{color:#1a614f}
.dgm-pt-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-pt-b.red h6{color:#82061e}
.dgm-pt-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-pt-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-pt{padding:20px 16px 18px}.dgm-pt-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-pt">
  <span class="dgm-pt-chip">A done-check gates every step, with a retry budget</span>
  <h4>Pass and move on; fail and either retry or re-plan the step</h4>
  <p class="dgm-pt-sub">Re-planning only kicks in once the retry budget for that one step is spent.</p>
  <div class="dgm-pt-q">Step — done-check passes?</div>
  <div class="dgm-pt-branches">
    <div class="dgm-pt-b green">
      <h6>Yes</h6>
      <p>Mark complete → next</p>
    </div>
    <div class="dgm-pt-b accent">
      <h6>No, retries left</h6>
      <p>Retry the step</p>
    </div>
  </div>
  <div class="dgm-pt-branches" style="grid-template-columns:repeat(1,1fr)">
    <div class="dgm-pt-b red">
      <h6>No, retries spent</h6>
      <p>Re-plan this step / escalate</p>
    </div>
  </div>
</div>


Progress is measured by *verification*, not by the agent's say-so. Stalls trigger re-planning.

## Build It

`code/progress.py` — track step outcomes and decide continue / re-plan:

```python
class Progress:
    def __init__(self, max_retries=2):
        self.max_retries = max_retries
        self.attempts = {}

    def run_step(self, step, do, verify):
        n = self.attempts.get(step, 0)
        while n <= self.max_retries:
            do(step)
            if verify(step):
                return {"step": step, "status": "complete", "attempts": n + 1}
            n += 1
            self.attempts[step] = n
        return {"step": step, "status": "needs_replan", "attempts": n}
```

```python
calls = {"build": 0}
def do(s): calls[s] += 1
def verify(s): return calls[s] >= 3          # passes on the 3rd attempt
p = Progress(max_retries=3)
print(p.run_step("build", do, verify))       # complete after retries

calls2 = {"flaky": 0}
print(Progress(max_retries=1).run_step("flaky", lambda s: None, lambda s: False))
# needs_replan — stop grinding, escalate/re-plan
```

`verify` is the gate: a step is only "complete" when its check passes. Persistent failure
returns `needs_replan`, so the agent (or human) changes approach instead of looping.

## Use It

In Claude Code / Codex this is the agent updating its todo list as it verifies each step
(running the test before checking the box) and re-planning when stuck. As a user, insist on
verification ("run the tests after each step") so progress is real — tying back to "report
outcomes faithfully; if tests fail, say so."

## Ship It

[`code/progress.py`](../../04-progress-tracking/code/progress.py) — a verify-driven progress
tracker with re-plan escalation.

## Check Yourself

**Q1.** When is a step actually "complete"?

- A) when the agent says so
- B) when its done-check (test/command) passes
- C) after one attempt
- D) never

<details><summary>Answer</summary>B — verification, not the agent's claim.</details>

**Q2.** A step fails repeatedly. The right move is…

- A) retry forever
- B) stop after the retry budget and re-plan / escalate
- C) mark it done
- D) skip silently

<details><summary>Answer</summary>B — bounded retries, then re-plan.</details>

**Challenge.** Combine with the todo model (lesson 01): drive a whole `TodoList` with
`Progress`, marking tasks complete only on verify and surfacing any `needs_replan`.

## Related

- Builds on: [Todo model](../../01-todo-model/docs/en.md), [Decomposition](../../03-decomposition/docs/en.md)
- Next: [Use It: plan mode in a real harness](../../05-plan-mode-in-practice/docs/en.md)
- Related: Phase 14 — Reliability (budgets), Phase 15 — Evals
- [Roadmap](../../../../ROADMAP.md)
