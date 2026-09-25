# Structured output without tools (JSON + repair)

> **Motto** — Ask for JSON, but never trust that you got valid JSON — extract, validate, repair.

*Part of Phase 01 — LLM I/O Foundations.*

## The Problem

You want the model to return data your code can consume — a JSON object. Even with a clear
instruction, models sometimes wrap JSON in prose ("Here's the result: { … }"), add
trailing commas, or emit a code fence. One malformed reply and a naive `json.loads` call
takes down the workflow. The harness needs to *extract*, *validate*, and *repair* output
before it trusts that output.

## The Concept

<style>
.dgm-stro{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-stro-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-stro h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-stro-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-stro-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-stro-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-stro-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-stro-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-stro-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-stro-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-stro-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-stro-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-stro{padding:20px 16px 18px}.dgm-stro-row{flex-direction:column}}
.dgm-stro-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-stro-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-stro-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-stro-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-stro-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-stro-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-stro-b.accent h6{color:#0d5c0d}
.dgm-stro-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-stro-b.blue h6{color:#0550ae}
.dgm-stro-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-stro-b.green h6{color:#1a614f}
.dgm-stro-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-stro-b.red h6{color:#82061e}
.dgm-stro-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-stro-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-stro{padding:20px 16px 18px}.dgm-stro-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-stro">
  <span class="dgm-stro-chip">Extract, validate, repair — not parse-and-hope</span>
  <h4>A repair loop turns 'almost JSON' into valid JSON</h4>
  <p class="dgm-stro-sub">Repair re-enters the same parse check, not a fresh generation.</p>
  <div class="dgm-stro-row">
    <div class="dgm-stro-n neutral">Model text</div>
    <span class="dgm-stro-arr">→</span>
    <div class="dgm-stro-n blue">Extract first JSON object</div>
  </div>
  <div class="dgm-stro-q">Parses?</div>
  <div class="dgm-stro-branches">
    <div class="dgm-stro-b green">
      <h6>Yes</h6>
      <p>Validate shape</p>
    </div>
    <div class="dgm-stro-b accent">
      <h6>No</h6>
      <p>Repair → retry parse</p>
    </div>
  </div>
</div>


Three cheap layers: pull the JSON out of surrounding prose, attempt common repairs, then
validate the required fields before use.

## Build It

`code/structured.py` — extraction + light repair + validation, stdlib only:

```python
import json, re

def extract_json(text):
    """Grab the first balanced {...} block, ignoring surrounding prose/fences."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{": depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None

def repair(blob):
    blob = blob.strip().strip("`")                       # strip code fences
    blob = re.sub(r",\s*([}\]])", r"\1", blob)           # trailing commas
    return blob

def parse(text, required=()):
    blob = extract_json(text)
    if blob is None:
        return None, "no JSON object found"
    for candidate in (blob, repair(blob)):
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        missing = [k for k in required if k not in obj]
        if missing:
            return None, f"missing keys {missing}"
        return obj, None
    return None, "unparseable JSON"
```

```python
msg = 'Sure! Here you go:\n```json\n{"name": "ada", "age": 36,}\n```'
print(parse(msg, required=["name", "age"]))   # ({'name': 'ada', 'age': 36}, None)
```

When `parse` returns an error, the harness re-prompts the model with the error message
(the same errors-are-data pattern as the agent loop).

## Use It

The SDK also supports forcing structure via **tool use**: define a tool whose schema *is*
your output type and let the model fill it. That's the robust production path (Phase 3).
This lesson's extractor is the fallback for plain-text models, and the thing tools save
you from.

## Ship It

[`code/structured.py`](../../07-structured-output/code/structured.py) — JSON extract +
repair + validate.

## Check Yourself

**Q1.** Why not call `json.loads` directly on the model's reply?

- A) it's slow
- B) replies often include prose/fences/trailing commas that break a naive parse
- C) JSON is deprecated
- D) you can

<details><summary>Answer</summary>B — extract and repair first; trust nothing.</details>

**Q2.** What's the most robust way to get structured output in production?

- A) bigger model
- B) define a tool whose schema is the output type and let the model fill it
- C) lower temperature only
- D) ask twice

<details><summary>Answer</summary>B — tool-schema-constrained output (Phase 3).</details>

**Challenge.** Add a `coerce` step that fixes single-quoted keys/values before parsing,
and return how many repair steps were needed (useful for an eval metric).

## Related

- Builds on: [Stop reasons](../../05-stop-reasons/docs/en.md)
- Robust path: Phase 3 — [Tool Engineering](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
