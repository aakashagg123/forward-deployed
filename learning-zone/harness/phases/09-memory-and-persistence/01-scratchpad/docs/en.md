# Session state & the scratchpad

> **Motto** — Give the agent a place to write down what it must not forget mid-task.

*Part of Phase 09 — Memory & Persistence.*

## The Problem

Within a single task, the agent accumulates facts it needs to remember: the file it's
editing, a value it computed, a decision it made. Re-deriving these every turn wastes
tokens and invites drift. A **scratchpad** fixes this. It's a small key/value store the
harness keeps for the session. The agent writes notes and reads them back, and they
survive across turns without bloating the conversation.

## The Concept

<style>
.dgm-scr{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-scr-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-scr h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-scr-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-scr-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-scr-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-scr-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-scr-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-scr-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-scr-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-scr-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-scr-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-scr{padding:20px 16px 18px}.dgm-scr-row{flex-direction:column}}
</style>
<div class="dgm-scr">
  <span class="dgm-scr-chip">Session state a turn can write and a later turn can read</span>
  <h4>set() now, get() next turn — the scratchpad is just keyed session state</h4>
  <p class="dgm-scr-sub">Nothing here survives a process restart; that's what Phase 09.02 is for.</p>
  <div class="dgm-scr-row">
    <div class="dgm-scr-n neutral">Agent turn</div>
    <span class="dgm-scr-arr">→</span>
    <div class="dgm-scr-n accent">scratchpad.set(key, value)</div>
    <span class="dgm-scr-arr">→</span>
    <div class="dgm-scr-n blue">Session state</div>
    <span class="dgm-scr-arr">→</span>
    <div class="dgm-scr-n green">scratchpad.get(key) next turn</div>
  </div>
</div>


The scratchpad is *structured* state, distinct from the message history. It's durable for
the session, queryable by key, and cheap to keep out of the context until needed.

## Build It

`code/scratchpad.py` — a session scratchpad:

```python
class Scratchpad:
    def __init__(self):
        self._d = {}

    def set(self, key, value):
        self._d[key] = value
        return f"noted {key}"

    def get(self, key, default=None):
        return self._d.get(key, default)

    def summary(self):
        return "\n".join(f"- {k}: {v}" for k, v in self._d.items()) or "(empty)"
```

```python
sp = Scratchpad()
sp.set("editing", "api/routes.py")
sp.set("tests_pass", False)
print(sp.get("editing"))      # api/routes.py
print(sp.summary())
```

Expose `set`/`get` as tools and the agent manages its own working memory. `summary()` can
be injected into context when the agent needs a refresher.

## Use It

In Claude Code / Codex this maps to the **todo/plan list** the agent maintains (Phase 11)
and to scratch notes it keeps in the working directory — a `NOTES.md`, say, or the per-task
`checkpoint.md` from Phase 10. The principle: durable working state lives in the harness,
not in the model's head, so it survives turns and compaction.

## Ship It

[`code/scratchpad.py`](../../01-scratchpad/code/scratchpad.py) — a session scratchpad
(set/get/summary).

## Check Yourself

**Q1.** Why keep working facts in a scratchpad instead of re-deriving them each turn?

- A) it's prettier
- B) re-derivation wastes tokens and risks drift; the scratchpad is cheap durable state
- C) the API requires it
- D) no reason

<details><summary>Answer</summary>B — structured state beats re-deriving.</details>

**Q2.** How is the scratchpad different from message history?

- A) it isn't
- B) it's structured key/value state, queryable and kept out of context until needed
- C) it's bigger
- D) it's the system prompt

<details><summary>Answer</summary>B — structured, not a transcript.</details>

**Challenge.** Add a `tools`-exposed `note(key, value)`. Have the loop inject `summary()`
only when the scratchpad changed since the last turn.

## Related

- Builds on: Phase 2 — [Turn history](../../../02-the-agent-loop/04-turn-history/docs/en.md)
- Next: [Persisting & resuming conversations](../../02-persist-resume/docs/en.md)
- Related: Phase 11 — Task management
- [Roadmap](../../../../ROADMAP.md)
