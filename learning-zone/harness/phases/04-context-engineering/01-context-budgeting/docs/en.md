# Context budgeting & token accounting

> **Motto** — Treat the context window as a budget you allocate, not a bucket you fill.

*Part of Phase 04 — Context Engineering.*

## The Problem

A coding agent's window fills fast with system prompt, tool schemas, project files
(`CLAUDE.md`/`AGENTS.md`), conversation history, and tool results. Left unmanaged, it
overflows. The harness then errors, or truncates blindly and drops exactly the file the
model needed. You need an explicit budget: set how many tokens each *category* may
consume, and check it before every call.

## The Concept

```mermaid
flowchart TB
  W["context window limit"] --> A["system + tools (fixed)"]
  W --> B["project memory (CLAUDE.md / AGENTS.md)"]
  W --> C["retrieved files"]
  W --> D["conversation history"]
  W --> E["reserve for output (max_tokens)"]
```

Allocate the window across categories, and reserve tokens for output. When a category
exceeds its slice, trim or compact that category (later lessons) instead of whatever data
happens to be oldest.

## Build It

`code/budget.py` — a category budgeter:

```python
def estimate(text):
    return max(1, round(len(text) / 4))      # ~4 chars/token (Phase 1)

class ContextBudget:
    def __init__(self, limit, reserve_output, weights):
        self.limit, self.reserve = limit, reserve_output
        self.weights = weights               # category -> fraction of remaining

    def allocation(self):
        usable = self.limit - self.reserve
        return {cat: int(usable * w) for cat, w in self.weights.items()}

    def check(self, sizes):
        alloc = self.allocation()
        return {cat: (sizes.get(cat, 0), alloc[cat], sizes.get(cat, 0) <= alloc[cat])
                for cat in alloc}
```

```python
b = ContextBudget(limit=200_000, reserve_output=8000,
                  weights={"system": .05, "memory": .10, "files": .45, "history": .40})
for cat, (used, cap, ok) in b.check({"files": 100_000, "history": 90_000}).items():
    print(cat, used, cap, "OK" if ok else "OVER")
```

Now "the window is full" becomes "the *files* category is over its 45% slice" — an
actionable signal pointing at what to trim.

## Use It

In **Claude Code / Codex** you don't set these numbers directly. But the same budgeting
governs what the agent loads: a lean `CLAUDE.md`/`AGENTS.md` for project memory, on-demand
file reads instead of dumping the repo, and automatic history compaction when the window
fills. This lesson explains the model behind those behaviors, and why a bloated memory
file crowds out the files the agent actually needs.

## Ship It

[`code/budget.py`](../../01-context-budgeting/code/budget.py) — a category context budgeter.

## Check Yourself

**Q1.** Why budget by *category* instead of just dropping the oldest messages?

- A) it's faster
- B) so you trim the right thing (e.g. bloated files) instead of losing needed history
- C) the API requires it
- D) no reason

<details><summary>Answer</summary>B — category budgets make overflow actionable.</details>

**Q2.** Why reserve tokens for output?

- A) style
- B) input + max_output share the window; without a reserve the reply gets truncated
- C) speed
- D) no reason

<details><summary>Answer</summary>B — leave room for the model to answer.</details>

**Challenge.** Add a `fit()` method that, given over-budget categories, returns how many
tokens each must shed — the input to truncation (lesson 03) and compaction (lesson 04).

## Related

- Builds on: Phase 1 — [Tokens](../../../01-llm-io-foundations/02-tokens-and-context-window/docs/en.md)
- Next: [Message assembly & ordering](../../02-message-assembly/docs/en.md)
- Other tracks: [Context engineering](../../../../../content/00-foundations/context-engineering.md) · [Context & memory in agents](../../../../../agentic-ai/context-and-memory.md) — the same curation discipline at PM and agent altitude.
- [Roadmap](../../../../ROADMAP.md)
