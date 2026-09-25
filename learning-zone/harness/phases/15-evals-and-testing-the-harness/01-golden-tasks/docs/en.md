# Golden tasks & fixtures

> **Motto** — A golden set is your harness's test suite: fixed inputs, known-good outputs, a score.

*Part of Phase 15 — Evals & Testing the Harness.*

## The Problem

You can't tell whether a prompt tweak, model bump, or tool change helped or hurt without a
*measurement*. A **golden set** is the answer. It's a fixed list of representative tasks, each
with a known-good expectation and a scoring function. Run it before and after a change, and
the diff in score tells you the truth. It replaces "seems better" with a number.

## The Concept

<style>
.dgm-gt{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-gt-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-gt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-gt-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-gt-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-gt-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-gt-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-gt-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-gt-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-gt-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-gt-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-gt-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-gt{padding:20px 16px 18px}.dgm-gt-row{flex-direction:column}}
</style>
<div class="dgm-gt">
  <span class="dgm-gt-chip">Run every golden case, score against expectation</span>
  <h4>The simplest eval: a fixed set of input/expectation pairs and a pass rate</h4>
  <p class="dgm-gt-sub">Golden tasks are the floor every other eval type in this phase builds on.</p>
  <div class="dgm-gt-row">
    <div class="dgm-gt-n accent">Golden cases: input + expectation</div>
    <span class="dgm-gt-arr">→</span>
    <div class="dgm-gt-n blue">Run harness on each</div>
    <span class="dgm-gt-arr">→</span>
    <div class="dgm-gt-n ">Score vs. expectation</div>
    <span class="dgm-gt-arr">→</span>
    <div class="dgm-gt-n green">Aggregate: pass rate</div>
  </div>
</div>


Cases should be representative — they cover the real distribution — and stable, meaning a
deterministic score, or one that tolerates acceptable variation.

## Build It

`code/golden.py` — a golden-set runner:

```python
def run_golden(cases, harness, score):
    """cases: [{input, expect}]; harness(input)->output; score(output, expect)->0..1."""
    results = []
    for c in cases:
        out = harness(c["input"])
        results.append({"input": c["input"], "score": score(out, c["expect"])})
    avg = sum(r["score"] for r in results) / len(results)
    return {"pass_rate": avg, "results": results}
```

```python
cases = [{"input": "2+2", "expect": "4"}, {"input": "cap of France", "expect": "Paris"}]
harness = lambda x: {"2+2": "4", "cap of France": "Lyon"}[x]   # buggy on case 2
score = lambda out, exp: 1.0 if exp.lower() in out.lower() else 0.0
print(run_golden(cases, harness, score)["pass_rate"])    # 0.5 — measurable
```

The pass rate is now a number you can track across changes. A drop points at exactly which
cases regressed.

## Use It

For a Claude Code or Codex workflow, a golden set can be a handful of representative tasks in
your repo ("fix this bug", "add this endpoint"), each with a check (tests pass, output
matches). Run it before and after changing `CLAUDE.md`, a skill, or the model. Evals are the
discipline that turns prompt and harness changes from guesswork into engineering.

## Ship It

[`code/golden.py`](../../01-golden-tasks/code/golden.py) — a golden-set eval runner.

## Check Yourself

**Q1.** What does a golden set let you do?

- A) make the agent faster
- B) measure whether a change helped or hurt, as a number
- C) remove tests
- D) nothing

<details><summary>Answer</summary>B — a measurement, not a guess.</details>

**Q2.** Good golden cases are…

- A) random and unstable
- B) representative of the real distribution, with stable scoring
- C) all edge cases only
- D) as few as possible

<details><summary>Answer</summary>B — representative and stable.</details>

**Challenge.** Add per-case tags (e.g. "math", "retrieval") and report pass rate per tag, so
a regression localizes to a category.

## Related

- Builds on: Phase 1 — [Sampling/determinism](../../../01-llm-io-foundations/03-sampling/docs/en.md)
- Next: [Trajectory evals](../../02-trajectory-evals/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
