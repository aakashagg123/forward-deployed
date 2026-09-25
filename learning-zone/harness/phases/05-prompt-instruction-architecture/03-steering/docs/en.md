# Steering: tone, refusals & guardrail text

> **Motto** — Steering is the prompt text that shapes *how* the agent responds and *when* it declines.

*Part of Phase 05 — Prompt & Instruction Architecture.*

## The Problem

Beyond what the agent does, you control *how* it communicates: terse or explanatory,
quick to refuse or quick to ask for confirmation, and how it phrases guardrails. Weak
steering gives you an agent that over-explains, barrels through risky actions without
asking, or refuses unhelpfully. Steering text is the lever, but it's only persuasion. So it
pairs with hard enforcement — hooks, Phase 8 — for anything that truly matters.

## The Concept

<style>
.dgm-steer{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-steer-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-steer h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-steer-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-steer-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-steer-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-steer-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-steer-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-steer-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-steer-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-steer-b.accent h6{color:#0d5c0d}
.dgm-steer-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-steer-b.blue h6{color:#0550ae}
.dgm-steer-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-steer-b.green h6{color:#1a614f}
.dgm-steer-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-steer-b.red h6{color:#82061e}
.dgm-steer-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-steer-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-steer{padding:20px 16px 18px}.dgm-steer-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-steer">
  <span class="dgm-steer-chip">Three knobs shape how the agent behaves, not what it can do</span>
  <h4>Tone, ask-vs-act, and refusal style — with hooks as the hard-case backstop</h4>
  <p class="dgm-steer-sub">Steering text is a preference; a hook is the enforcement for when the stakes are high.</p>
  <div class="dgm-steer-q">Steering text</div>
  <div class="dgm-steer-branches">
    <div class="dgm-steer-b blue">
      <h6>Tone</h6>
      <p>Terse / verbose</p>
    </div>
    <div class="dgm-steer-b accent">
      <h6>Ask-vs-act</h6>
      <p>When to confirm</p>
    </div>
    <div class="dgm-steer-b green">
      <h6>Refusal style</h6>
      <p>Decline + offer alternative — hard cases add hook enforcement (Phase 8)</p>
    </div>
  </div>
</div>


Steering shapes the *soft* behavior. For safety-critical limits, steering is the polite
front, and a hook is the wall behind it.

## Build It

The artifact is a steering snippet library. `outputs/steering-snippets.md` provides
reusable lines for tone, ask-vs-act thresholds, and refusal phrasing, e.g.:

- **Tone:** "Be terse. No preamble or postamble. Lead with the answer."
- **Ask-vs-act:** "Make reversible changes directly. Before irreversible or out-of-scope
  actions, state a one-line plan and wait for confirmation."
- **Refusal:** "If you can't or shouldn't do something, say so in one sentence and offer
  the nearest safe alternative."

Each snippet is a line you can paste into the system prompt or memory file.

## Use It

In **Claude Code / Codex** this maps to output styles and your memory-file instructions,
such as "be concise" or "always confirm before deleting files." Steering is advisory,
though — for "never touch `.env`" you *also* add the PreToolUse hook from Phase 0/8. The
steering text explains the boundary, and the hook enforces it.

## Ship It

[`outputs/steering-snippets.md`](../../03-steering/outputs/steering-snippets.md) — reusable
tone / ask-vs-act / refusal lines.

## Check Yourself

**Q1.** Steering text alone is sufficient to enforce a safety-critical rule.

- A) true
- B) false — it's persuasion; pair it with a hook for hard enforcement
- C) true if the model is large
- D) true at temperature 0

<details><summary>Answer</summary>B — steering shapes soft behavior; hooks enforce.</details>

**Q2.** A good refusal…

- A) just says "no"
- B) declines in one sentence and offers the nearest safe alternative
- C) ignores the request
- D) explains at length

<details><summary>Answer</summary>B — brief, with a constructive alternative.</details>

**Challenge.** Write an ask-vs-act rule that classifies three example actions (rename a
local var, delete a file, push to main) into act-directly vs. confirm-first.

## Related

- Builds on: [System prompt anatomy](../../01-system-prompt-anatomy/docs/en.md)
- Next: [Output styles & response contracts](../../04-output-contracts/docs/en.md)
- Enforced by: Phase 8 — Permissions & hooks
- [Roadmap](../../../../ROADMAP.md)
