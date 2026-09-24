---
name: check-the-docs
description: >
  Before answering any question about an LLM API (model ids, pricing, parameters,
  limits, caching, deprecations), verify against the current official docs/SDK
  reference instead of training memory. Trigger on "which model", "API parameter",
  "is X deprecated", "token limit", "pricing".
version: 1.0.0
kind: skill
phase: 0
lesson: 5
---

# Check the docs first

When a question depends on facts that change over time (model ids, parameters, limits,
pricing, deprecations), do not answer from memory.

## Procedure

1. **Locate the authoritative source** — the provider's official API docs or SDK
   reference. Not a blog, not recollection.
2. **Verify the specifics** named in the question (exact model id, parameter spelling,
   context window, rate limits).
3. **Answer with a citation** — name the source so the reader can re-verify.

## Defaults (verify before relying on them)

- Prefer the latest, most capable models. Current ids: **Fable 5.1** (`claude-fable-5-1`);
  **Opus 5** (`claude-opus-5`), **Sonnet 5** (`claude-sonnet-5`),
  **Haiku 4.5** (`claude-haiku-4-5-20251001`).
- If unsure whether an id or parameter is current, say so and check before using it.

## Anti-patterns

- Quoting a model id from memory without checking it still exists.
- Stating a price or limit as fact without a source.
- Using a removed parameter because it "used to work."
