# LLM-as-judge

> **Motto** — When there's no exact answer to match, have a model score the output against a rubric.

*Part of Phase 15 — Evals & Testing the Harness.*

## The Problem

Many outputs have no single correct string — a code explanation, a refactor, a summary. You
can't `==` them against an expectation. **LLM-as-judge** scores such outputs. A model grades
the candidate against a written rubric (correctness, completeness, style) and returns a score
and rationale. It scales subjective evaluation, but only if the rubric is specific and the
judge is well-controlled.

## The Concept

<style>
.dgm-laj{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-laj-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-laj h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-laj-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-laj-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-laj-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-laj-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-laj-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-laj-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-laj-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-laj-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-laj-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-laj{padding:20px 16px 18px}.dgm-laj-row{flex-direction:column}}
</style>
<div class="dgm-laj">
  <span class="dgm-laj-chip">A rubric turns judgment into a score</span>
  <h4>The judge model scores a candidate output against explicit criteria and a scale</h4>
  <p class="dgm-laj-sub">Rationale alongside the score is what makes a judge's verdict auditable.</p>
  <div class="dgm-laj-row">
    <div class="dgm-laj-n neutral">Candidate output</div>
    <span class="dgm-laj-arr">→</span>
    <div class="dgm-laj-n accent">Judge model + rubric</div>
    <span class="dgm-laj-arr">→</span>
    <div class="dgm-laj-n green">Score + rationale</div>
  </div>
  <div class="dgm-laj-row" style="margin-top:8px">
    <div class="dgm-laj-n blue">Rubric: criteria + scale</div>
  </div>
</div>


Guardrails: use a concrete rubric, a fixed scale, and low temperature. Ideally the judge
doesn't see which system produced the output, to avoid bias.

## Build It

`code/judge.py` — the judge harness with the model call abstracted (so it's testable):

```python
RUBRIC = """Score the answer 0-5 on:
- correctness (is it right?)
- completeness (does it cover the question?)
Return JSON: {"score": <0-5>, "reason": "<one line>"}."""

def judge(output, question, call_model, rubric=RUBRIC):
    prompt = f"{rubric}\n\nQuestion: {question}\nAnswer: {output}"
    import json
    return json.loads(call_model(prompt))      # model returns the JSON verdict

def normalize(verdict, scale=5):
    return verdict["score"] / scale            # 0..1 for aggregation
```

```python
fake_model = lambda p: '{"score": 4, "reason": "correct but missing an edge case"}'
v = judge("Paris is the capital of France.", "Capital of France?", fake_model)
print(v, "->", normalize(v))     # {'score': 4, ...} -> 0.8
```

In production, `call_model` is a real, low-temperature judge. The rubric and JSON contract
(Phase 1 L7) make the verdict parseable and the score aggregatable into a pass rate.

## Use It

LLM-as-judge powers evals where exact matching fails, such as code quality and explanations,
and it powers the rerank step in retrieval (Phase 13). It's also the review agent from Phase
10 — a judge over a diff. One caveat: judges have biases (length, position,
self-preference), so validate the judge against human labels before you trust it.

## Ship It

[`code/judge.py`](../../03-llm-as-judge/code/judge.py) — an LLM-as-judge rubric scorer.

## Check Yourself

**Q1.** When is LLM-as-judge the right eval?

- A) when there's an exact expected string
- B) when outputs are open-ended (quality, explanations) with no single correct answer
- C) for token counting
- D) never

<details><summary>Answer</summary>B — subjective, open-ended scoring.</details>

**Q2.** A key guardrail for a judge is…

- A) high temperature
- B) a concrete rubric + fixed scale (and validating against human labels)
- C) showing it the author
- D) no rubric

<details><summary>Answer</summary>B — specific rubric, controlled judge.</details>

**Challenge.** Add pairwise judging (A vs. B, "which is better?") which is often more
reliable than absolute scores, and aggregate win rates.

## Related

- Builds on: Phase 1 — [Structured output](../../../01-llm-io-foundations/07-structured-output/docs/en.md)
- Next: [Regression gates in CI](../../04-regression-gates/docs/en.md)
- Related: Phase 10 — review agent, Phase 13 — rerank
- [Roadmap](../../../../ROADMAP.md)
