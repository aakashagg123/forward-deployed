# Writing tool descriptions the model obeys

> **Motto** — The description is the model's only manual — write it for the model, not for humans.

*Part of Phase 03 — Tool Engineering.*

## The Problem

You can have perfect schemas and dispatch and still get bad tool use, because the model
chooses *whether* and *how* to call a tool from its **description**. Vague descriptions
cause the model to skip the tool, call it for the wrong thing, or pass bad arguments. The
description is prompt engineering aimed at the model's tool-selection step.

## The Concept

A good tool description answers four questions the model is implicitly asking:

<style>
.dgm-td{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-td-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-td h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-td-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-td-matrix{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-td-cell{border-radius:11px;padding:11px 13px;position:relative;border:1.5px solid}
.dgm-td-cell h6{margin:2px 0 4px;font-size:11px;font-weight:700}
.dgm-td-cell p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-td-cell.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-td-cell.accent h6{color:#0d5c0d}
.dgm-td-cell.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-td-cell.blue h6{color:#0550ae}
.dgm-td-cell.green{background:#dafbe1;border-color:#aceebb}
.dgm-td-cell.green h6{color:#1a614f}
.dgm-td-cell.red{background:#ffebe9;border-color:#ffcecb}
.dgm-td-cell.red h6{color:#82061e}
.dgm-td-cell.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-td-cell.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-td{padding:20px 16px 18px}.dgm-td-matrix{grid-template-columns:1fr}}
</style>
<div class="dgm-td">
  <span class="dgm-td-chip">Four things every tool description must answer</span>
  <h4>What, when, arguments, and returns — skip one and the model guesses</h4>
  <p class="dgm-td-sub">The model only has the description to decide when to reach for a tool.</p>
  <div class="dgm-td-matrix">
    <div class="dgm-td-cell accent">
      <h6>WHAT</h6>
      <p>What it does, one line</p>
    </div>
    <div class="dgm-td-cell blue">
      <h6>WHEN</h6>
      <p>When to use it / when NOT to</p>
    </div>
    <div class="dgm-td-cell green">
      <h6>ARGUMENTS</h6>
      <p>What each argument means — units, format</p>
    </div>
    <div class="dgm-td-cell neutral">
      <h6>RETURNS</h6>
      <p>What it returns</p>
    </div>
  </div>
</div>


Lead with the action verb, name the trigger conditions explicitly, and spell out argument
formats: units, allowed values, examples. Avoid the anti-pattern of a noun phrase
("Weather tool") that tells the model nothing about when to reach for it.

## Build It (a description rubric)

The artifact is a written rubric plus before/after examples. `outputs/tool-description-rubric.md`:

- **What** — one sentence, action-first: "Fetch current weather for a city."
- **When / when not** — "Use when the user asks about current conditions. Do not use for
  forecasts (use `forecast`)."
- **Arguments** — each with type, units, format, example: "`city`: name, e.g. 'Paris';
  `unit`: 'c' or 'f'."
- **Returns** — "A short string like 'Paris: 18°C, clear.'"

Before: `"Weather."` After: the four-part version above. The model now knows exactly when
and how to call it.

## Use It

These strings populate the `description` field of each tool schema (lesson 01) sent to
the model. When an eval (Phase 15) shows the model misusing a tool, the first fix is
usually the description — not the model, and not the prompt. The principle: patch the
harness.

## Ship It

[`outputs/tool-description-rubric.md`](../../06-tool-descriptions/outputs/tool-description-rubric.md)
— a rubric + before/after examples for writing tool descriptions.

## Check Yourself

**Q1.** The model decides whether to call a tool mainly from its…

- A) implementation
- B) description (and schema)
- C) name only
- D) return type

<details><summary>Answer</summary>B — the description drives selection and argument
filling.</details>

**Q2.** The model keeps calling the wrong tool. First fix?

- A) a bigger model
- B) clarify the tool descriptions (what/when/args/returns)
- C) lower temperature
- D) remove the tool

<details><summary>Answer</summary>B — sharpen the descriptions before anything
else.</details>

**Challenge.** Take a tool with a one-word description, rewrite it with the four-part
rubric, and note what ambiguity each part removes.

## Related

- Builds on: [Tool schemas & dispatch](../../01-schemas-and-dispatch/docs/en.md)
- Next: [SDK tool definitions & parallel tool use](../../07-sdk-parallel-tools/docs/en.md)
- Deepens in: Phase 5 — Prompt Architecture
- [Roadmap](../../../../ROADMAP.md)
