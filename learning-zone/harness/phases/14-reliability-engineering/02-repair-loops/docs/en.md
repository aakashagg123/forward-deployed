# Validation & repair loops

> **Motto** — When output fails validation, hand the model the error and let it fix itself — within a budget.

*Part of Phase 14 — Reliability Engineering.*

## The Problem

Even with good prompting, model output sometimes fails its contract: malformed JSON (Phase 1
L7), a missing section (Phase 5 L4), a tool arg that won't validate (Phase 3 L2). Rejecting
the output outright is wasteful. The model can usually *repair* it if you show it the
specific error. A repair loop validates the output, and on failure re-prompts with the
error. It stays bounded so it can't loop forever.

## The Concept

<style>
.dgm-rl{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-rl-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-rl h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-rl-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-rl-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-rl-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-rl-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-rl-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-rl-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-rl-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-rl-b.accent h6{color:#0d5c0d}
.dgm-rl-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-rl-b.blue h6{color:#0550ae}
.dgm-rl-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-rl-b.green h6{color:#1a614f}
.dgm-rl-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-rl-b.red h6{color:#82061e}
.dgm-rl-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-rl-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-rl{padding:20px 16px 18px}.dgm-rl-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-rl">
  <span class="dgm-rl-chip">Re-prompt with the error, not a blank retry</span>
  <h4>Invalid output loops back through generation carrying the specific failure</h4>
  <p class="dgm-rl-sub">The model gets to see what was wrong — that's what makes the retry more likely to succeed.</p>
  <div class="dgm-rl-q">Generate — valid?</div>
  <div class="dgm-rl-branches">
    <div class="dgm-rl-b green">
      <h6>Yes</h6>
      <p>Use it</p>
    </div>
    <div class="dgm-rl-b accent">
      <h6>No, attempts left</h6>
      <p>Re-prompt with the error → generate again</p>
    </div>
  </div>
  <div class="dgm-rl-branches" style="grid-template-columns:repeat(1,1fr)">
    <div class="dgm-rl-b red">
      <h6>No, budget spent</h6>
      <p>Give up → fallback</p>
    </div>
  </div>
</div>


## Build It

`code/repair.py` — a generic validate-and-repair loop:

```python
def repair_loop(generate, validate, max_attempts=3):
    """generate(feedback)->output; validate(output)->None|error_message."""
    feedback = None
    for attempt in range(max_attempts):
        out = generate(feedback)
        err = validate(out)
        if err is None:
            return {"ok": True, "output": out, "attempts": attempt + 1}
        feedback = f"Your output was invalid: {err}. Fix it and return only the corrected output."
    return {"ok": False, "error": err, "attempts": max_attempts}
```

```python
# model that omits a field until told
state = {"n": 0}
def gen(feedback):
    state["n"] += 1
    return '{"name": "ada"}' if state["n"] == 1 else '{"name": "ada", "age": 36}'
def val(o):
    import json
    return None if "age" in json.loads(o) else "missing 'age'"
print(repair_loop(gen, val))     # ok after 2 attempts
```

The error string is the repair signal. It's specific and model-readable, the same
errors-are-data principle as the agent loop, but now bounded by an attempt budget. A
persistently broken generator falls through to a fallback.

## Use It

This wraps any structured generation in Claude Code and Codex: JSON tool args, a required
output format, a code patch that must apply. Prefer prevention first, with tool-schema
output (Phase 3 L7). The repair loop is the safety net for when the contract still isn't
met. Pair it with retries (lesson 01): retries handle *transport* failures, and repair
handles *content* failures.

## Ship It

[`code/repair.py`](../../02-repair-loops/code/repair.py) — a bounded validate-and-repair loop.

## Check Yourself

**Q1.** What does the repair loop feed back to the model on failure?

- A) nothing
- B) the specific validation error, so it can correct
- C) the whole conversation
- D) a generic "try again"

<details><summary>Answer</summary>B — specific, model-readable errors drive repair.</details>

**Q2.** Retries vs. repair loops handle…

- A) the same thing
- B) retries → transport failures; repair → content/validation failures
- C) only JSON
- D) nothing

<details><summary>Answer</summary>B — different failure classes, often combined.</details>

**Challenge.** Combine with Phase 1 L7's JSON extractor: validate by parsing, and on failure
feed back the exact parse error and the offending substring.

## Related

- Builds on: [Retries](../../01-retries/docs/en.md); Phase 1 — [Structured output](../../../01-llm-io-foundations/07-structured-output/docs/en.md)
- Next: [Fallback chains & model routing](../../03-fallback-routing/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
