# Turn history & conversation state

> **Motto** — History is the only memory the model has — so own it deliberately.

*Part of Phase 02 — The Agent Loop. Builds on
[The agent loop from scratch](../../01-agent-loop/docs/en.md).*

## The Problem

The model is stateless: every call must carry the whole conversation, including tool
results. So far we've appended raw dicts to a list. That works until you need to
serialize a session to disk, replay it, or count its tokens. It also breaks if you don't
keep the `assistant` tool-request and its `tool_result` paired, since an unpaired request
makes the provider reject the call. History is a data structure with invariants, not just
a list.

## The Concept

<style>
.dgm-th{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-th-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-th h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-th-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-th-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.dgm-th-col{border-radius:12px;padding:12px 13px;border:1.5px solid}
.dgm-th-col.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-th-col.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-th-col.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-th-col.green{background:#dafbe1;border-color:#aceebb}
.dgm-th-col h6{margin:0 0 8px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px}
.dgm-th-col.neutral h6{color:#59636e}
.dgm-th-col.accent h6{color:#0d5c0d}
.dgm-th-col.blue h6{color:#0550ae}
.dgm-th-col.green h6{color:#1a614f}
.dgm-th-item{background:#ffffff;border:1px solid #e5e9ef;border-radius:8px;padding:6px 9px;font-size:10px;
  color:#1f2328;line-height:1.35;margin-bottom:5px}
.dgm-th-item:last-child{margin-bottom:0}
.dgm-th-link{display:flex;justify-content:center;color:#8c959f;font-size:9.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.3px;padding:6px 0}
@media (max-width:640px){.dgm-th{padding:20px 16px 18px}.dgm-th-cols{grid-template-columns:1fr}}
.dgm-th-chain{display:flex;flex-direction:column;gap:2px}
.dgm-th-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-th-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-th-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-th{padding:20px 16px 18px}}
</style>
<div class="dgm-th">
  <span class="dgm-th-chip">Three message kinds feed one history</span>
  <h4>User, assistant, and paired tool_result all accumulate into one structure</h4>
  <p class="dgm-th-sub">That structure is what gets serialized, replayed, and token-counted.</p>
  <div class="dgm-th-cols">
    <div class="dgm-th-col blue">
      <h6>User</h6>
    </div>
    <div class="dgm-th-col accent">
      <h6>Assistant (+ tool_use)</h6>
    </div>
    <div class="dgm-th-col green">
      <h6>Tool_result (paired to tool_use)</h6>
    </div>
  </div>
  <div class="dgm-th-chain">
    <div class="dgm-th-node alt">History</div>
    <div class="dgm-th-arr">↓</div>
    <div class="dgm-th-node ">Serialize / replay / token-count</div>
  </div>
</div>


Two invariants the harness must keep:

1. **Pairing:** every `tool_use` in an assistant turn must be followed by a matching
   `tool_result`. Truncation (Phase 4) must never split a pair.
2. **Order:** roles alternate as the API expects; tool results belong to the turn that
   requested them.

## Build It

`code/history.py` — a `History` that enforces pairing and serializes:

```python
import json
from dataclasses import dataclass, field

@dataclass
class History:
    messages: list = field(default_factory=list)
    _pending: set = field(default_factory=set)        # tool_use ids awaiting results

    def user(self, text):
        self.messages.append({"role": "user", "content": text})

    def assistant(self, text, tool_calls=None):
        msg = {"role": "assistant", "content": text, "tool_calls": tool_calls or []}
        self.messages.append(msg)
        self._pending = {c["id"] for c in msg["tool_calls"]}

    def tool_result(self, call_id, content):
        if call_id not in self._pending:
            raise ValueError(f"result for unknown/unpaired call {call_id!r}")
        self.messages.append({"role": "tool", "call_id": call_id, "content": content})
        self._pending.discard(call_id)

    def complete(self):
        """True when every requested tool call has a result — safe to call the model."""
        return not self._pending

    def dump(self):
        return json.dumps(self.messages, indent=2)

    @classmethod
    def load(cls, blob):
        return cls(messages=json.loads(blob))
```

```python
h = History()
h.user("what is 2 + 3?")
h.assistant("let me add", tool_calls=[{"id": "t1", "name": "add", "args": {"a": 2, "b": 3}}])
print(h.complete())          # False — result for t1 is missing
h.tool_result("t1", "5")
print(h.complete())          # True — safe to call the model again
```

`complete()` is the guard: the loop must not call the model while a tool result is
outstanding. `dump()` and `load()` make sessions resumable — the seed of Phase 9 memory.

## Use It

The SDK enforces the same pairing at the wire level. An assistant message with a
`tool_use` block must be followed by a user message containing a `tool_result` block
with the matching `tool_use_id`, or the API errors. Because you built `_pending`
tracking yourself, that error message ("expected tool_result for id …") is now obvious
rather than mysterious.

## Ship It

[`code/history.py`](../../04-turn-history/code/history.py) — a `History` class with
pairing invariants and JSON serialization, reused by the context manager (Phase 4) and
memory store (Phase 9).

## Check Yourself

**Q1.** Why must the loop check `complete()` before the next model call?

- A) For speed
- B) An unmatched `tool_use` without its `tool_result` is rejected by the API
- C) To save tokens
- D) It isn't necessary

<details><summary>Answer</summary>B — the provider requires every tool request to be
answered before the conversation continues.</details>

**Q2.** When truncating long history (Phase 4), the one thing you must never do is…

- A) drop the system prompt
- B) split a `tool_use` from its `tool_result`
- C) summarize old turns
- D) keep the most recent turn

<details><summary>Answer</summary>B — splitting a pair leaves the conversation in an
invalid state the API rejects.</details>

**Challenge.** Add `token_estimate()` that approximates the history's size (e.g. 4 chars
≈ 1 token) so a future context manager can decide when to compact.

## Related

- Builds on: [The agent loop from scratch](../../01-agent-loop/docs/en.md)
- Next: [Use It: the SDK tool-use loop](../../05-sdk-tool-use-loop/docs/en.md)
- Deepens in: Phase 4 — [Context Engineering](../../../../ROADMAP.md), Phase 9 — Memory
