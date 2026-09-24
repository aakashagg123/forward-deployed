---
name: system-prompt-template
description: A five-section system-prompt structure for a coding agent.
kind: prompt
phase: 5
lesson: 1
---

# System prompt template

Fill each section. Keep it stable (it's the cached prefix) and lean.

## Role
[Who the agent is, in 1–2 concrete sentences. e.g. "You are a coding agent that edits
this repository and runs its tests."]

## Constraints (must / must-never)
- Never [hard rule, e.g. edit `.env` or commit secrets].
- Always [hard rule, e.g. run the test suite before claiming a task is done].
- [Each line is an imperative the model must obey. Back the critical ones with a hook.]

## Tools
- Use [tool] when [trigger]; do not use it for [exclusion → other tool].
- [Disambiguate overlapping tools so the model picks correctly.]

## Workflow
- Default approach: [e.g. understand → plan → make the smallest change → verify].
- Stop and ask when [ambiguity / destructive action / out-of-scope].

## Output contract
- Format: [e.g. concise prose; code in fenced blocks; cite files as `path:line`].
- Length/tone: [e.g. terse, no preamble].

---
Notes:
- Volatile, per-task data does NOT go here — it belongs in the user turn (kills caching).
- A formatting preference → output contract. A hard rule → constraints (+ a hook).
