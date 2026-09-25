# Messages, roles & turns

> **Motto** — A conversation is a typed list of role-tagged messages — nothing more, nothing less.

*Part of Phase 01 — LLM I/O Foundations.*

## The Problem

Every call you make sends a *list of messages*, each tagged with a role. Get the roles or
ordering wrong and the API rejects the request or the model misbehaves. Before any higher
abstraction, you need a precise mental model for well-formed message lists, and a small
helper to build them.

## The Concept

Three roles, one rule:

- **system** — instructions/context (passed as a top-level field, not a message).
- **user** — input from the human (or tool results, returned as a user turn).
- **assistant** — the model's replies (you echo these back to continue a conversation).

<style>
.dgm-mrt{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-mrt-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-mrt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-mrt-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-mrt-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-mrt-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-mrt-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-mrt-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-mrt-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-mrt-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-mrt-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-mrt-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-mrt{padding:20px 16px 18px}.dgm-mrt-row{flex-direction:column}}
</style>
<div class="dgm-mrt">
  <span class="dgm-mrt-chip">System sits above the turn loop</span>
  <h4>One system message, many turns of messages</h4>
  <p class="dgm-mrt-sub">System is set once; messages accumulate as the conversation runs.</p>
  <div class="dgm-mrt-row">
    <div class="dgm-mrt-n accent">System (top-level, set once)</div>
    <span class="dgm-mrt-arr">→</span>
    <div class="dgm-mrt-n blue">Messages: [user, assistant, user, …]</div>
    <span class="dgm-mrt-arr">→</span>
    <div class="dgm-mrt-n ">Model call</div>
    <span class="dgm-mrt-arr">→</span>
    <div class="dgm-mrt-n green">Assistant reply → append</div>
  </div>
</div>


Turns alternate user/assistant. The system prompt is separate.

## Build It

`code/messages.py` — typed constructors and a validator for alternation:

```python
def system(text): return text                       # passed as top-level `system=`
def user(text):   return {"role": "user", "content": text}
def assistant(t): return {"role": "assistant", "content": t}

def validate(messages):
    if not messages or messages[0]["role"] != "user":
        return "conversation must start with a user message"
    for a, b in zip(messages, messages[1:]):
        if a["role"] == b["role"]:
            return f"two {a['role']} messages in a row — turns must alternate"
    return None

def build(*turns):
    msgs = []
    for role, text in turns:
        msgs.append(user(text) if role == "user" else assistant(text))
    err = validate(msgs)
    if err:
        raise ValueError(err)
    return msgs
```

```python
msgs = build(("user", "hi"), ("assistant", "hello"), ("user", "2+2?"))
print(validate(msgs))    # None — well-formed
```

## Use It

`client.messages.create(model=..., system=system_text, messages=msgs)` takes exactly this
shape. Tool results (Phase 2/3) come back as `user` messages, preserving alternation —
which is why `validate` matters once tools enter.

## Ship It

[`code/messages.py`](../../01-messages-roles-turns/code/messages.py) — message constructors
plus an alternation validator.

## Check Yourself

**Q1.** Where does the system prompt go?

- A) as the first `user` message
- B) as a top-level `system` field, separate from `messages`
- C) as an `assistant` message
- D) anywhere

<details><summary>Answer</summary>B — system is its own field, not a message in the
list.</details>

**Q2.** Why must turns alternate user/assistant?

- A) style
- B) the API expects alternating roles; two in a row is malformed
- C) to save tokens
- D) they don't

<details><summary>Answer</summary>B — non-alternating turns are rejected.</details>

**Challenge.** Extend `build` to accept tool-result turns (a `user` message carrying
structured `tool_result` blocks) without breaking alternation.

## Related

- Next: [Tokens & the context window](../../02-tokens-and-context-window/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
