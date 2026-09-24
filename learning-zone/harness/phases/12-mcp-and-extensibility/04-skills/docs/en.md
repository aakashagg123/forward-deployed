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

```mermaid
flowchart LR
  L["skill index: names + descriptions (always loaded)"] --> M{"task matches a description?"}
  M -- "yes" --> F["load that SKILL.md body on demand"]
  M -- "no" --> S["skip — costs nothing"]
```

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
