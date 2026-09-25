# Persisting & resuming conversations

> **Motto** — A session you can save is a session you can resume — don't lose work to a closed terminal.

*Part of Phase 09 — Memory & Persistence.*

## The Problem

Close the terminal, hit a crash, or come back tomorrow, and the conversation is gone
unless the harness persisted it. Resuming means restoring the message history (Phase 2
lesson 04) and the scratchpad (lesson 01), so the agent continues where it left off. The
serialization has to round-trip cleanly, including tool-call pairing.

## The Concept

<style>
.dgm-pr{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pr-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-pr h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-pr-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-pr-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-pr-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-pr-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-pr-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-pr-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-pr-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-pr-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-pr-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-pr{padding:20px 16px 18px}.dgm-pr-row{flex-direction:column}}
</style>
<div class="dgm-pr">
  <span class="dgm-pr-chip">Serialize to disk, load to resume</span>
  <h4>History and scratchpad both round-trip through session.json</h4>
  <p class="dgm-pr-sub">Resume means the agent loop continues exactly where the serialized state left it.</p>
  <div class="dgm-pr-row">
    <div class="dgm-pr-n accent">Session: history + scratchpad</div>
    <span class="dgm-pr-arr">→</span>
    <div class="dgm-pr-n blue">Serialize → session.json</div>
    <span class="dgm-pr-arr">→</span>
    <div class="dgm-pr-n neutral">Disk</div>
    <span class="dgm-pr-arr">→</span>
    <div class="dgm-pr-n ">Load → restore</div>
    <span class="dgm-pr-arr">→</span>
    <div class="dgm-pr-n green">Continue the agent loop</div>
  </div>
</div>


## Build It

`code/session_store.py` — save/load a full session:

```python
import json, os

class SessionStore:
    def __init__(self, path):
        self.path = path

    def save(self, history, scratch):
        with open(self.path, "w") as f:
            json.dump({"history": history, "scratch": scratch}, f, indent=2)
        return f"saved {len(history)} messages"

    def load(self):
        if not os.path.exists(self.path):
            return [], {}
        with open(self.path) as f:
            data = json.load(f)
        return data.get("history", []), data.get("scratch", {})
```

```python
import tempfile
store = SessionStore(tempfile.mktemp(suffix=".json"))
store.save([{"role": "user", "content": "hi"}], {"editing": "a.py"})
hist, scratch = store.load()
print(len(hist), scratch)        # 1 {'editing': 'a.py'}
```

Saving after each turn, or each tool call, makes the session crash-resilient. Loading on
start resumes it exactly.

## Use It

This is Claude Code's session resume (`claude --resume` / `--continue`) and Codex's session
history. Conversations are persisted so you can pick a prior session back up. On Claude Code
on the web, the container is ephemeral. That's *why* anything worth keeping must be
committed and pushed, and why long state belongs in files, not just the chat.

## Ship It

[`code/session_store.py`](../../02-persist-resume/code/session_store.py) — a session save/load
store.

## Check Yourself

**Q1.** What must a resumable session restore?

- A) only the last message
- B) the message history (with valid tool pairing) and the scratchpad
- C) the system prompt only
- D) nothing

<details><summary>Answer</summary>B — history + working state, intact.</details>

**Q2.** On an ephemeral cloud container, durable state should live…

- A) only in the chat
- B) in files you commit/push (the container is reclaimed)
- C) in memory
- D) nowhere

<details><summary>Answer</summary>B — persist to the repo; the box is temporary.</details>

**Challenge.** Save after every turn. Add a `--resume` flag to the Phase 0 REPL that loads
the last session on start.

## Related

- Builds on: [Scratchpad](../../01-scratchpad/docs/en.md); Phase 2 — [Turn history](../../../02-the-agent-loop/04-turn-history/docs/en.md)
- Next: [Long-term memory & retrieval](../../03-long-term-memory/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
