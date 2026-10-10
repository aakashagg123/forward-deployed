# Output contracts

> **Motto** — State the output contract, then verify the output meets it. Do not just hope.

*Part of Phase 04 — Prompts and instructions.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

You ask for a shape: "a summary, then a list of changed files, then the diff". Or you ask for a JSON object. Most of the time you get it. "Most of the time" breaks automation.

Models wrap JSON in prose, add a trailing comma or put it in a code fence. One bad reply and a plain `json.loads` call stops the workflow. A text reply can skip a required section.

A *contract* is two things: the format stated in the prompt, and a check in the harness that the reply conforms. A violation is caught, fed back and repaired. It does not flow on silently.

## The Concept

<style>
.dgm-oc{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-oc-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-oc h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-oc-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-oc-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-oc-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-oc-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-oc-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-oc-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-oc-b.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline)}
.dgm-oc-b.accent h6{color:var(--color-text-success)}
.dgm-oc-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-oc-b.blue h6{color:var(--color-text-info)}
.dgm-oc-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-oc-b.green h6{color:var(--color-text-success)}
.dgm-oc-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-oc-b.red h6{color:var(--color-text-danger)}
.dgm-oc-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-oc-b.neutral h6{color:var(--color-text)}
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


The prompt states the contract. The harness enforces it in four steps.

1. **Extract.** Pull the JSON block out of the surrounding prose.
2. **Repair.** Fix cheap defects, such as trailing commas.
3. **Validate.** Check required keys, types and sections.
4. **Re-prompt.** Send back the exact violation, not the whole contract again.

The retry loop needs a bound. A model that never complies must not loop forever. After the budget runs out, the harness fails loudly. The failure ladder is in [Failure ladder](../../../09-reliability-evals-and-ops/01-failure-ladder/docs/en.md).

One more check comes first. A reply cut off at the token limit is not valid JSON. Read the stop reason before you parse: [Stopping, errors and recovery](../../../01-foundations-and-the-loop/04-stopping-errors-and-recovery/docs/en.md).

## Build It

`code/contract.py` has a JSON checker, a section checker and a bounded retry loop. All three return a list of problems. An empty list means the reply conforms.

```python
def check_json(text, schema):
    """schema maps key -> Python type. Returns a list of problems; empty means it conforms."""
    blob = extract_blob(text)
    if blob is None:
        return ["no JSON object found"]
    for candidate in (blob, repair(blob)):
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        problems = [f"missing key: {k}" for k in schema if k not in obj]
        problems += [f"{k} must be {t.__name__}" for k, t in schema.items()
                     if k in obj and not isinstance(obj[k], t)]
        return problems
    return ["unparseable JSON"]
```

```python
def enforce(ask, prompt, check, max_retries=2):
    """Ask, check, and re-prompt with the violation. Bounded: never loops forever."""
    for attempt in range(1, max_retries + 2):
        reply = ask(prompt)
        problems = check(reply)
        if not problems:
            return reply, attempt, []
        prompt = prompt + "\n\n" + repair_prompt(problems)
    return None, max_retries + 1, problems
```

The `extract_blob` function skips braces inside JSON strings, so `"a } b"` does not end the block early. The section checker also requires the headings in order, not only present.

The asserts use a scripted model. Its first reply skips the `Diff` section. The test checks that the second prompt contains the violation text, and that the second reply conforms. A second scripted model never complies. The test checks that `enforce` stops after three attempts and returns `None`.

## Use It

For a human reader, the prompt contract is usually enough. For machine-read output, add the check.

In Claude Code, an output style sets the response format for a whole session. Switch with `/output-style`. It is an instruction, so nothing enforces it. For a step that must happen every time, use a hook.

In the API, ask for the shape instead of hoping. Structured outputs take a JSON schema in `output_config` with `format` of type `json_schema`. The reply text is then JSON that matches the schema. The schema supports basic types, `enum` and `anyOf`. It does not support numeric limits such as `minimum`, or recursive schemas. Keep your own `check_json` as a backstop.

Tool use is the older route to the same goal. Define a tool whose input schema is your output type. Some current models reject forced tool use, meaning a `tool_choice` of `any` or `tool`, with a 400 error. On those models use `strict: true` on the tool with `tool_choice` set to `auto`, or use structured outputs. Set `additionalProperties: false` on every object. The schema guarantee does not hold if the reply stops on `max_tokens` or `refusal`, so check `stop_reason` first. Check the docs for your model.

`code/output_contract_sdk.py` shows the structured-output call. It needs `pip install anthropic` and an API key, so it does not run offline.

## Challenge

Extend `check_sections` to enforce a length cap per section. Then write a scripted model that fixes one problem per retry. Assert that the loop needs three attempts and stops.

## Sources

Claude API docs, "Structured outputs" and "Define tools" (platform.claude.com/docs). Claude Code docs, "Output styles" (code.claude.com/docs/en/output-styles).

Next phase: [Files and shell](../../../05-files-and-shell/01-read/docs/en.md)
