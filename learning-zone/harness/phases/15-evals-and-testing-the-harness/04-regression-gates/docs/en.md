# Regression gates in CI

> **Motto** — Block the change that drops the score — run the evals before it merges.

*Part of Phase 15 — Evals & Testing the Harness.*

## The Problem

Evals only protect you if they *run automatically* and *block regressions*. A **regression
gate** runs the golden, trajectory, and judge evals in CI on every change to prompts, skills,
tools, or the model. It compares the score to a baseline and **fails the build** if the score
dropped beyond a tolerance. This is what stops the silent "it worked yesterday" regression
from the failure playbook.

## The Concept

<style>
.dgm-rg{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-rg-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-rg h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-rg-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-rg-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-rg-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-rg-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-rg-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-rg-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-rg-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-rg-b.accent h6{color:#0d5c0d}
.dgm-rg-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-rg-b.blue h6{color:#0550ae}
.dgm-rg-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-rg-b.green h6{color:#1a614f}
.dgm-rg-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-rg-b.red h6{color:#82061e}
.dgm-rg-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-rg-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-rg{padding:20px 16px 18px}.dgm-rg-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-rg">
  <span class="dgm-rg-chip">A change only merges if the score holds</span>
  <h4>Every prompt/model/tool change reruns the eval suite before it can land</h4>
  <p class="dgm-rg-sub">The tolerance band is what stops noisy scoring from blocking every harmless change.</p>
  <div class="dgm-rg-q">Change (prompt/model/tool) → run eval suite — score ≥ baseline − tolerance?</div>
  <div class="dgm-rg-branches">
    <div class="dgm-rg-b green">
      <h6>Yes</h6>
      <p>Merge</p>
    </div>
    <div class="dgm-rg-b red">
      <h6>No</h6>
      <p>Block: regression</p>
    </div>
  </div>
</div>


## Build It

`code/gate.py` — a CI gate comparing current score to a baseline:

```python
def gate(current, baseline, tolerance=0.02):
    """Return (passed, message). Fails if current dropped > tolerance below baseline."""
    delta = current - baseline
    if delta < -tolerance:
        return False, f"REGRESSION: {current:.3f} < baseline {baseline:.3f} (Δ{delta:+.3f})"
    return True, f"ok: {current:.3f} vs baseline {baseline:.3f} (Δ{delta:+.3f})"

def main(current, baseline):
    passed, msg = gate(current, baseline)
    print(msg)
    return 0 if passed else 1        # nonzero exit fails CI
```

```python
print(gate(0.91, 0.90))     # ok (improved)
print(gate(0.85, 0.90))     # REGRESSION (dropped 0.05 > tolerance)
```

The gate returns a nonzero exit code on regression, so CI fails the PR. The eval suite becomes
a required check, exactly like unit tests.

## Use It

Wire this into the same CI that runs your tests. On a PR that touches `CLAUDE.md`, a skill,
a tool, or bumps the model, run the eval suite and gate on the score. For a Claude Code or
Codex user, even a tiny golden set gated in CI catches the prompt or skill change that
quietly made things worse. Store the baseline in the repo, and update it intentionally when
you genuinely improve.

## Ship It

[`code/gate.py`](../../04-regression-gates/code/gate.py) — a CI regression gate with exit codes.

## Check Yourself

**Q1.** What makes a regression gate effective?

- A) running it manually sometimes
- B) running automatically in CI and failing the build on a score drop
- C) a longer prompt
- D) more models

<details><summary>Answer</summary>B — automatic and blocking.</details>

**Q2.** Why a tolerance band rather than exact equality?

- A) to ignore regressions
- B) to allow acceptable noise (non-determinism) while catching real drops
- C) it's required
- D) no reason

<details><summary>Answer</summary>B — tolerate noise, catch real regressions.</details>

**Challenge.** Make the gate write the new score back as the baseline only when run on the
main branch *and* the score improved, so baselines ratchet up.

## Related

- Builds on: [Golden tasks](../../01-golden-tasks/docs/en.md), [LLM-as-judge](../../03-llm-as-judge/docs/en.md)
- Next: [Adversarial & red-team cases](../../05-adversarial/docs/en.md)
- Related: Phase 18 — CI/deployment
- [Roadmap](../../../../ROADMAP.md)
