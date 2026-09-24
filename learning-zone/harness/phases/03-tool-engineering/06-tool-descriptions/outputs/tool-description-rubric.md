---
name: tool-description-rubric
description: How to write tool descriptions the model selects and calls correctly.
kind: prompt
phase: 3
lesson: 6
---

# Tool description rubric

Every tool description should answer four questions, in this order:

1. **What** — one action-first sentence. *"Fetch current weather for a city."*
2. **When / when not** — explicit triggers and exclusions. *"Use when the user asks about
   current conditions. Do NOT use for forecasts — use `forecast` instead."*
3. **Arguments** — each with type, units/format, and an example. *"`city`: city name, e.g.
   'Paris'. `unit`: 'c' or 'f' (default 'c')."*
4. **Returns** — the shape of the output. *"A short string, e.g. 'Paris: 18°C, clear.'"*

## Before → After

- ❌ `"Weather."`
- ✅ `"Fetch current weather for a city. Use when the user asks about current conditions;
  not for forecasts (use forecast). Args: city (name, e.g. 'Paris'), unit ('c'|'f').
  Returns a short string like 'Paris: 18°C, clear.'"`

## Rules

- Lead with the verb; describe the action, not the noun.
- State when NOT to use it when tools overlap.
- Give units and allowed values inline; the schema enforces, the description teaches.
- When an eval shows misuse, fix the description first (patch the harness, not the prompt).
