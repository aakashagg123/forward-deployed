# Trajectory evals (did it take the right steps?)

> **Motto** — For an agent, *how* it got the answer matters as much as the answer.

*Part of Phase 15 — Evals & Testing the Harness.*

## The Problem

Golden-set scoring (lesson 01) checks the final output. But an agent can reach a right answer
the wrong way — skipping the tests, editing the wrong file first, calling a tool 10 times. A
**trajectory eval** scores the *sequence of actions*. Did it call the expected tools, in a
sane order, without forbidden steps? This catches process bugs a final-answer check misses.

## The Concept

<style>
.dgm-te2{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-te2-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-te2 h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-te2-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-te2-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-te2-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-te2-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-te2-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-te2-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-te2-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-te2-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-te2-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-te2{padding:20px 16px 18px}.dgm-te2-row{flex-direction:column}}
</style>
<div class="dgm-te2">
  <span class="dgm-te2-chip">Score the path, not just the answer</span>
  <h4>The recorded tool calls get checked against must-include / must-not-include / order</h4>
  <p class="dgm-te2-sub">A trajectory eval catches a right answer reached the wrong way.</p>
  <div class="dgm-te2-row">
    <div class="dgm-te2-n accent">Recorded trajectory: [tool calls]</div>
    <span class="dgm-te2-arr">→</span>
    <div class="dgm-te2-n blue">Compare to expectations</div>
    <span class="dgm-te2-arr">→</span>
    <div class="dgm-te2-n ">Must-include / must-not-include / order</div>
    <span class="dgm-te2-arr">→</span>
    <div class="dgm-te2-n green">Trajectory score</div>
  </div>
</div>


## Build It

`code/trajectory.py` — score a trajectory against expectations:

```python
def score_trajectory(steps, must_include=(), must_not=(), max_steps=None):
    tools = [s["tool"] for s in steps]
    problems = []
    for t in must_include:
        if t not in tools:
            problems.append(f"missing expected tool: {t}")
    for t in must_not:
        if t in tools:
            problems.append(f"used forbidden tool: {t}")
    if max_steps and len(steps) > max_steps:
        problems.append(f"too many steps: {len(steps)} > {max_steps}")
    score = 1.0 if not problems else max(0.0, 1 - 0.34 * len(problems))
    return {"score": round(score, 2), "problems": problems}
```

```python
traj = [{"tool": "read"}, {"tool": "edit"}, {"tool": "bash"}]   # ran tests via bash
print(score_trajectory(traj, must_include=["read", "bash"], must_not=["rm"], max_steps=10))
# score 1.0 — read the code, made the edit, ran tests; no forbidden tools
```

Trajectory checks encode process expectations, such as "always run tests", "never call the
delete tool", or "don't exceed N steps", and score how well a run followed them.

## Use It

For coding agents this is how you verify good *habits*, not just good answers. Did it read
before editing (Phase 6)? Did it run tests before claiming done (Phase 11)? Did it stay within
budget (Phase 14)? Trajectory evals over recorded runs (traces, Phase 16) catch regressions
in behavior that output-only checks would miss.

## Ship It

[`code/trajectory.py`](../../02-trajectory-evals/code/trajectory.py) — a trajectory scorer
(must-include / forbidden / step cap).

## Check Yourself

**Q1.** What does a trajectory eval check that a golden-output check doesn't?

- A) the final answer
- B) the sequence of actions — which tools, what order, forbidden steps
- C) latency
- D) cost

<details><summary>Answer</summary>B — the process, not just the result.</details>

**Q2.** A trajectory eval is the right tool to enforce…

- A) output formatting
- B) habits like "read before edit" and "run tests before done"
- C) token counts
- D) nothing

<details><summary>Answer</summary>B — process expectations.</details>

**Challenge.** Add ordering constraints (e.g. `read` must appear before `edit`) and penalize
violations distinctly from missing tools.

## Related

- Builds on: [Golden tasks](../../01-golden-tasks/docs/en.md)
- Next: [LLM-as-judge](../../03-llm-as-judge/docs/en.md)
- Uses: Phase 16 — traces
- [Roadmap](../../../../ROADMAP.md)
