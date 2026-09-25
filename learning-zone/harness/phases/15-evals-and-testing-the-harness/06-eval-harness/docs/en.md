# Use it: an eval harness you run on every change

> **Motto** — One command runs golden, trajectory, judge, and adversarial evals and gates the result.

*Part of Phase 15 — Evals & Testing the Harness. Completes the phase.*

## The Problem

The pieces — golden, trajectory, judge, adversarial, gate — are only useful assembled into
one **eval harness** you run with a single command. Run it locally before a change and in CI
to block regressions. This is the productized form of the phase: `run_evals()` produces an
aggregate score and a pass/fail you can wire into the same workflow as your tests.

## The Concept

<style>
.dgm-eh{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-eh-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-eh h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-eh-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-eh-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-eh-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-eh-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-eh-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-eh-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-eh-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-eh-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-eh-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-eh{padding:20px 16px 18px}.dgm-eh-row{flex-direction:column}}
</style>
<div class="dgm-eh">
  <span class="dgm-eh-chip">Four eval types, one gate, one exit code</span>
  <h4>Golden, trajectory, judge, and adversarial all feed one aggregate score</h4>
  <p class="dgm-eh-sub">CI only reads the exit code — everything upstream of it is this phase's four lessons.</p>
  <div class="dgm-eh-row">
    <div class="dgm-eh-n accent">Eval suite: golden + trajectory + judge + adversarial</div>
    <span class="dgm-eh-arr">→</span>
    <div class="dgm-eh-n blue">Run all</div>
    <span class="dgm-eh-arr">→</span>
    <div class="dgm-eh-n ">Aggregate score</div>
    <span class="dgm-eh-arr">→</span>
    <div class="dgm-eh-n ">Gate vs. baseline</div>
    <span class="dgm-eh-arr">→</span>
    <div class="dgm-eh-n green">Pass / fail (exit code)</div>
  </div>
</div>


## Build It / Use It

`code/eval_harness.py` composes the phase into one runnable suite:

```python
def run_evals(suites):
    """suites: {name: callable()->score 0..1}. Returns aggregate + per-suite."""
    scores = {name: fn() for name, fn in suites.items()}
    agg = sum(scores.values()) / len(scores)
    return {"aggregate": round(agg, 3), "suites": scores}

def gate(current, baseline, tol=0.02):
    return current >= baseline - tol
```

```python
suites = {
    "golden": lambda: 0.92,
    "trajectory": lambda: 1.0,
    "adversarial": lambda: 1.0,
}
report = run_evals(suites)
print(report, "PASS" if gate(report["aggregate"], 0.93) else "FAIL")
```

In a real setup, each suite runs the actual cases from lessons 01–05. `run_evals` aggregates
the scores, and `gate` (lesson 04) turns the result into a CI pass/fail.

## Use It

Add `python eval_harness.py` to your CI next to the tests, and run it locally before changing
`CLAUDE.md`, a skill, a tool, or the model. For a Claude Code or Codex user, this closes the
loop the whole course has been building toward. You change the harness, and the evals tell
you — with a number and a gate — whether it got better or worse. Evals are how harness
engineering stays engineering.

## Ship It

[`code/eval_harness.py`](../../06-eval-harness/code/eval_harness.py) — a one-command eval suite
+ gate.

## Check Yourself

**Q1.** What does the eval harness produce?

- A) a longer prompt
- B) an aggregate score + per-suite breakdown + a pass/fail gate
- C) a new model
- D) nothing

<details><summary>Answer</summary>B — measure, aggregate, gate.</details>

**Q2.** When should you run it?

- A) never
- B) locally before a harness change and in CI to block regressions
- C) only at release
- D) once

<details><summary>Answer</summary>B — every change, automatically.</details>

**Challenge.** Wire the real lesson 01–05 runners into `suites`, store the baseline in the
repo, and add it as a required CI check (Phase 18).

## Related

- Builds on: the whole phase
- Wired into CI in: Phase 18 — Production & Deployment
- Phase complete → next: Phase 16 — [Observability & Cost](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
