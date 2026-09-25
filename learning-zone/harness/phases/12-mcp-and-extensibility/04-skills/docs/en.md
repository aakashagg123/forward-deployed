# Skills (SKILL.md) & progressive disclosure

> **Motto** — A skill is a named capability the agent loads only when it's relevant.

*Part of Phase 12 — MCP & Extensibility.*

## The Problem

You can't put every workflow, rubric, and procedure into the system prompt. It would grow
huge and stay mostly irrelevant on any given task. **Skills** solve this with progressive
disclosure. Each skill is a small `SKILL.md` file with a name and description the agent
always sees, but its full body loads only when the description matches the task. The agent
gets a big library of capabilities at near-zero standing context cost.

## The Concept

<style>
.dgm-sk{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-sk-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-sk h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-sk-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-sk-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-sk-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-sk-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-sk-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-sk-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-sk-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-sk-b.accent h6{color:#0d5c0d}
.dgm-sk-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-sk-b.blue h6{color:#0550ae}
.dgm-sk-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-sk-b.green h6{color:#1a614f}
.dgm-sk-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-sk-b.red h6{color:#82061e}
.dgm-sk-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-sk-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-sk{padding:20px 16px 18px}.dgm-sk-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-sk">
  <span class="dgm-sk-chip">A cheap index, an expensive body loaded on demand</span>
  <h4>Names and descriptions are always loaded; the full SKILL.md loads only on a match</h4>
  <p class="dgm-sk-sub">Most tasks never trigger a skill, so most of that cost is never paid.</p>
  <div class="dgm-sk-q">Skill index: names + descriptions (always loaded) — task matches a description?</div>
  <div class="dgm-sk-branches">
    <div class="dgm-sk-b green">
      <h6>Yes</h6>
      <p>Load that SKILL.md body on demand</p>
    </div>
    <div class="dgm-sk-b neutral">
      <h6>No</h6>
      <p>Skip — costs nothing</p>
    </div>
  </div>
</div>


This is the legibility principle as a mechanism. Read the index, follow one link, and load
only what you need.

## Build It (the format)

The artifact is the skill format itself. `outputs/SKILL.md` is a template with YAML
frontmatter (`name`, `description` with trigger phrases) plus a procedure body. The whole
course ships skills in this exact shape (`/find-your-level`, `/check-understanding`,
`/agent-team`, `/plan-and-build`). A good description lists the *trigger phrases* so matching
stays reliable, and keeps the body focused on one capability.

## Use It

This is Claude Code and Codex **skills**. Drop a `SKILL.md` file under
`.claude/skills/<name>/`, and the agent surfaces it when relevant and loads its body on
demand. Progressive disclosure is why you can install dozens of skills without bloating
context — only the matching one's body enters the window. Every `outputs/SKILL.md` in this
course is installable this way.

## Ship It

[`outputs/SKILL.md`](../../04-skills/outputs/SKILL.md) — a SKILL.md template demonstrating the
format + progressive disclosure.

## Check Yourself

**Q1.** What is always loaded vs. loaded on demand for a skill?

- A) the whole body is always loaded
- B) the name + description are always loaded; the body loads only when relevant
- C) nothing is loaded
- D) only the body

<details><summary>Answer</summary>B — progressive disclosure: index always, body on
demand.</details>

**Q2.** What makes a skill's description reliable at triggering?

- A) being vague
- B) listing concrete trigger phrases for when to use it
- C) being long
- D) no description

<details><summary>Answer</summary>B — explicit triggers drive matching.</details>

**Challenge.** Write a skill for a workflow you repeat (e.g. "open a PR") with a tight
description and a 5-step body, and install it under `.claude/skills/`.

## Related

- Builds on: Phase 5 — [Memory files](../../../05-prompt-instruction-architecture/02-memory-files/docs/en.md)
- Next: [Plugins & deferred tool loading](../../05-plugins/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
