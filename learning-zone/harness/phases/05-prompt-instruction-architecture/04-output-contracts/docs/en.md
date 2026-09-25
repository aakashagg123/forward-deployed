# Output styles & response contracts

> **Motto** — State the output contract, then verify the output meets it — don't just hope.

*Part of Phase 05 — Prompt & Instruction Architecture.*

## The Problem

You ask the agent for a specific shape — "a summary, then a bullet list of changed files,
then the diff" — and most of the time you get it. "Most of the time" breaks downstream
automation. A response *contract* is the format stated in the prompt **plus** a check in
the harness that the response conforms. Violations get caught, and can trigger a repair,
instead of silently flowing through.

## The Concept

<style>
.dgm-oc{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-oc-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-oc h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-oc-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-oc-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-oc-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-oc-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-oc-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-oc-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-oc-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-oc-b.accent h6{color:#0d5c0d}
.dgm-oc-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-oc-b.blue h6{color:#0550ae}
.dgm-oc-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-oc-b.green h6{color:#1a614f}
.dgm-oc-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-oc-b.red h6{color:#82061e}
.dgm-oc-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-oc-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-oc{padding:20px 16px 18px}.dgm-oc-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-oc">
  <span class="dgm-oc-chip">A contract only works if you check it</span>
  <h4>Conformance gets used as-is; a violation gets re-prompted with the violation shown</h4>
  <p class="dgm-oc-sub">Re-prompting with the specific violation works better than repeating the whole contract.</p>
  <div class="dgm-oc-q">Response conforms to the contract?</div>
  <div class="dgm-oc-branches">
    <div class="dgm-oc-b green">
      <h6>Yes</h6>
      <p>Use it</p>
    </div>
    <div class="dgm-oc-b red">
      <h6>No</h6>
      <p>Re-prompt with the violation</p>
    </div>
  </div>
</div>


The prompt states the contract, and the harness enforces it. This is the structured-output
idea (Phase 1 L7), generalized from JSON to any response shape.

## Build It

`code/contract.py` — declare required sections and verify a response:

```python
import re

def check_contract(text, required_sections, max_chars=None):
    problems = []
    for heading in required_sections:
        if not re.search(rf"^#+\s*{re.escape(heading)}", text, re.MULTILINE | re.IGNORECASE):
            problems.append(f"missing section: {heading}")
    if max_chars and len(text) > max_chars:
        problems.append(f"too long: {len(text)} > {max_chars} chars")
    return problems            # empty list == conforms

def repair_prompt(problems):
    return ("Your previous response did not meet the format contract:\n- "
            + "\n- ".join(problems) + "\nReformat to satisfy all requirements.")
```

```python
resp = "## Summary\nDid the thing.\n## Files\n- a.py"
print(check_contract(resp, ["Summary", "Files", "Diff"]))
# ['missing section: Diff']
```

A non-empty problem list feeds `repair_prompt`, which you send back to the model — bounded
by your retry budget (Phase 14).

## Use It

In **Claude Code / Codex** this maps to **output styles** — declare the response format
once — plus your own verification when the response feeds a script. For human-facing chat,
the prompt contract is usually enough. For machine-consumed output, add the check, and
prefer tool-schema output (Phase 3 L7) when the shape is strict.

## Ship It

[`code/contract.py`](../../04-output-contracts/code/contract.py) — a response-contract checker
+ repair-prompt builder.

## Check Yourself

**Q1.** A response contract is…

- A) just a prompt instruction
- B) the format in the prompt PLUS a harness check that the output conforms
- C) a tool
- D) a model setting

<details><summary>Answer</summary>B — state it and verify it.</details>

**Q2.** When the output feeds a downstream script, you should…

- A) trust the prompt
- B) verify the contract (or use tool-schema output) and repair on violation
- C) lower temperature only
- D) ask twice

<details><summary>Answer</summary>B — machine-consumed output needs enforcement.</details>

**Challenge.** Extend `check_contract` to require sections in a specific *order*, not just
presence.

## Related

- Builds on: Phase 1 — [Structured output](../../../01-llm-io-foundations/07-structured-output/docs/en.md)
- Next: [Few-shot & in-context examples](../../05-few-shot/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
