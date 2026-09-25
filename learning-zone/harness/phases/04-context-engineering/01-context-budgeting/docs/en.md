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

<style>
.dgm-cb{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-cb-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-cb h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-cb-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-cb-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-cb-branches{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.dgm-cb-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-cb-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-cb-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-cb-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-cb-b.accent h6{color:#0d5c0d}
.dgm-cb-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-cb-b.blue h6{color:#0550ae}
.dgm-cb-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-cb-b.green h6{color:#1a614f}
.dgm-cb-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-cb-b.red h6{color:#82061e}
.dgm-cb-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-cb-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-cb{padding:20px 16px 18px}.dgm-cb-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-cb">
  <span class="dgm-cb-chip">Five claims on one fixed window</span>
  <h4>System, memory, retrieved files, history, and output reserve all compete for the same tokens</h4>
  <p class="dgm-cb-sub">Nothing here is optional — the only lever is how much each claim gets.</p>
  <div class="dgm-cb-q">Context window limit</div>
  <div class="dgm-cb-branches">
    <div class="dgm-cb-b accent">
      <h6>System + tools</h6>
      <p>Fixed</p>
    </div>
    <div class="dgm-cb-b blue">
      <h6>Project memory</h6>
      <p>CLAUDE.md / AGENTS.md</p>
    </div>
    <div class="dgm-cb-b green">
      <h6>Retrieved files</h6>
    </div>
    <div class="dgm-cb-b neutral">
      <h6>Conversation history</h6>
    </div>
    <div class="dgm-cb-b red">
      <h6>Reserve for output</h6>
      <p>max_tokens</p>
    </div>
  </div>
</div>


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
