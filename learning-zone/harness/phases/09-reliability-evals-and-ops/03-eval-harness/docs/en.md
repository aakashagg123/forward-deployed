# The eval harness and its regression gate

> **Motto** — If a change can make the agent worse, one command must say so and block the merge.

*Part of Phase 09 — Reliability, Evals and Ops.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

You change a prompt, a tool description, or the model. The agent "seems better." Two days later a user finds it skips the tests. Nobody can say when it broke.

You need a number that moves when the agent gets worse. Unit tests cannot give it, because a model's output is not exact. And a final-answer check alone is not enough. An agent can reach a right answer the wrong way: it skips the tests, or it calls a forbidden tool.

An **eval harness** runs a fixed set of tasks and scores them. A **gate** compares the score to a stored baseline and fails the build on a drop.

## The Concept

<style>
.dgm-eh{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-eh-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-eh h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-eh-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-eh-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-eh-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-eh-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-eh-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-eh-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-eh-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-eh-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-eh-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-eh{padding:20px 16px 18px}.dgm-eh-row{flex-direction:column}}
.dgm-eh-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-eh-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:10px}
.dgm-eh-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-eh-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-eh-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-eh-b.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline)}
.dgm-eh-b.accent h6{color:var(--color-text-success)}
.dgm-eh-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-eh-b.blue h6{color:var(--color-text-info)}
.dgm-eh-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-eh-b.green h6{color:var(--color-text-success)}
.dgm-eh-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-eh-b.red h6{color:var(--color-text-danger)}
.dgm-eh-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-eh-b.neutral h6{color:var(--color-text)}
@media (max-width:640px){.dgm-eh-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-eh">
  <span class="dgm-eh-chip">Two suites, one gate, one exit code</span>
  <h4>Golden and trajectory cases feed one score</h4>
  <p class="dgm-eh-sub">CI reads only the exit code. The gate needs a test that proves it can fail.</p>
  <div class="dgm-eh-row">
    <div class="dgm-eh-n accent">Cases: golden + trajectory (adversarial is a tag)</div>
    <span class="dgm-eh-arr">→</span>
    <div class="dgm-eh-n blue">Run the agent on each case</div>
    <span class="dgm-eh-arr">→</span>
    <div class="dgm-eh-n ">Aggregate score</div>
    <span class="dgm-eh-arr">→</span>
    <div class="dgm-eh-n ">Score &ge; baseline &minus; tolerance?</div>
  </div>
  <div class="dgm-eh-branches" style="margin-top:12px">
    <div class="dgm-eh-b green">
      <h6>Yes</h6>
      <p>exit 0: mergeable</p>
    </div>
    <div class="dgm-eh-b red">
      <h6>No</h6>
      <p>exit 1: blocked</p>
    </div>
  </div>
</div>


Two kinds of check cover most needs.

- A **golden** case is a fixed input with a known-good output. The score is how often the output matches.
- A **trajectory** check scores the steps, not the answer. Did the run use the tools it must use, such as `bash` to run tests? Did it avoid forbidden tools, such as `rm`?

CI reads one thing: the exit code. A gate that cannot fail protects nothing. So the gate itself needs a test that proves it can fail.

## Build It

`code/eval_harness.py` holds cases with tags, so a regression points at a category. Each case lists the tools a run must use and must never use.

The agents in the file are stand-ins. `good_agent` is a correct harness. `regressed_agent` models a bad change: `mul` is wrong, the run skips the test step, and it obeys `rm`. Replace them with a call to your real harness.

Two scoring functions run on every case:

```python
def golden_score(case, run):
    return 1.0 if run["output"] == case["expect"] else 0.0


def trajectory_score(case, run):
    """Fraction of process checks that passed: required tools used, forbidden tools avoided."""
    checks = [t in run["tools"] for t in case["must"]] + [t not in run["tools"] for t in case["never"]]
    return sum(checks) / len(checks)
```

The gate allows a small drop for noise and fails anything bigger:

```python
def gate(current, baseline, tolerance=0.02):          # 0.02 is an example value
    """Return (passed, message). Fail when the score drops more than `tolerance` below baseline."""
    delta = current - baseline
    if delta < -tolerance:
        return False, f"REGRESSION: {current:.3f} vs baseline {baseline:.3f} (delta {delta:+.3f})"
    return True, f"ok: {current:.3f} vs baseline {baseline:.3f} (delta {delta:+.3f})"
```

`main` turns the gate into an exit code. The baseline lives in `code/baseline.json`, in the repo, so a change to it shows up in review.

```python
    return 0 if passed else 1
```

The asserts at the end prove both sides. The good agent scores 1.0 and `main([])` returns 0. The regressed agent scores 0.438 and `main(["--candidate", "regressed"])` returns 1. Run `python3 code/eval_harness.py --candidate regressed` and the process exits 1.

Update the baseline only on purpose, when you have truly improved the agent. Never edit it to make a red build green.

## Use It

Claude Code runs without a terminal UI in print mode. Use it as the agent under test:

```bash
claude -p "fix the failing test in calc.py" --max-turns 10 --max-budget-usd 1.00 --output-format json
```

`-p` prints the result and exits. `--max-turns` and `--max-budget-usd` bound the run. `--output-format` accepts `text`, `json`, and `stream-json`. Save the output of each run and score it with the same two functions.

Real model runs are noisy. Run each case several times and average the score. Then set the tolerance wider than the noise you measure, but narrower than a real regression. Trace data from [lesson 4](../../04-tracing-and-cost/docs/en.md) gives you recorded runs to score.

Run the harness locally before you change `CLAUDE.md`, a skill, a tool, or the model. [Lesson 5](../../05-rollout-and-ci-gate/docs/en.md) runs it in CI.

## Challenge

Add an ordering rule to the trajectory check: `read` must come before `edit`. Count a wrong order as a different problem from a missing tool. Then add a case that only this rule catches, and assert the score drops.

## Sources

[Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)

Other track: [Evals](../../../../../content/04-evals-observability/evals.md) · Next: [Tracing and cost](../../04-tracing-and-cost/docs/en.md)
