# Reading the docs like an engineer

> **Motto** — The model knows a lot; the docs know what's true *today*.

*Part of Phase 00 — Setup & Tooling.*

## The Problem

Model APIs change: new parameters, new models, deprecations. An agent (or a learner) that
answers from training memory will confidently use a stale model id or a removed flag. The
fix is a habit, encoded as a skill: *check the authoritative source before answering,
rather than guessing*.

## The Concept

Three moves separate guessing from engineering:

1. **Locate the source of truth** — official docs / SDK reference, not a blog.
2. **Verify specifics** — model ids, parameter names, limits — against it.
3. **Cite where it came from** — so the next reader can re-verify.

This is the human version of *legibility*: don't crawl everything. Go straight to the
authoritative file and quote it.

## Build It

A skill that encodes the habit so any agent applies it. `outputs/SKILL.md` triggers on
LLM/API questions and forces a docs check before answering. It defaults to the latest
models (Fable 5.1; the Claude 5 family — Opus 5 `claude-opus-5`, Sonnet 5, Haiku
4.5).

## Use It

Installed into Claude, Cursor, or Codex, the skill activates on questions about model
choice, pricing, parameters, or limits. It answers from the reference rather than
memory — the same discipline this whole course models.

## Ship It

[`outputs/SKILL.md`](../../05-reading-docs/outputs/SKILL.md) — a "check the docs first" skill
for any agent.

## Check Yourself

**Q1.** Why not answer model/API questions from memory?

- A) memory is slow
- B) APIs change; training can be stale, so verify against current docs
- C) it uses tokens
- D) you always can

<details><summary>Answer</summary>B — correctness depends on what's true today, not at
training time.</details>

**Q2.** What does "cite where it came from" buy you?

- A) nothing
- B) the answer is re-verifiable by the next reader
- C) faster responses
- D) shorter prompts

<details><summary>Answer</summary>B — traceability; a claim you can check beats one you
must trust.</details>

**Challenge.** Add to the skill a short checklist it must satisfy before answering a
"which model should I use?" question (latest ids, context window, relative cost).

## Related

- Builds on: the whole of Phase 0.
- Phase complete → next: Phase 1 — [LLM I/O Foundations](../../../../ROADMAP.md)
