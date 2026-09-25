# A REPL you can talk to

> **Motto** — A read-eval-print loop over a model is the smallest useful harness.

*Part of Phase 00 — Setup & Tooling.*

## The Problem

You can make a one-shot call (lesson 02). But to *feel* the model as a conversational
partner, and to have a sandbox for every later concept, you need a loop. The loop reads
your input, sends the running conversation, prints the reply, and remembers the turn.
This is the agent loop (Phase 2) stripped of tools — just conversation state.

## The Concept

<style>
.dgm-repl{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-repl-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-repl h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-repl-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-repl-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-repl-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-repl-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-repl-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-repl-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-repl-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-repl-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-repl-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-repl{padding:20px 16px 18px}.dgm-repl-row{flex-direction:column}}
.dgm-repl-note{margin-top:10px;padding:9px 14px;background:#e6f5e6;border:1px dashed #a8d8a8;border-radius:10px;
  font-size:10.5px;color:#0d5c0d;line-height:1.4}
</style>
<div class="dgm-repl">
  <span class="dgm-repl-chip">The REPL is the agent loop's simplest shape</span>
  <h4>Read, append, call, print — then do it again</h4>
  <p class="dgm-repl-sub">Every later phase adds structure around this same four-step loop.</p>
  <div class="dgm-repl-row">
    <div class="dgm-repl-n blue">Read line</div>
    <span class="dgm-repl-arr">→</span>
    <div class="dgm-repl-n ">Append to history</div>
    <span class="dgm-repl-arr">→</span>
    <div class="dgm-repl-n accent">Call model with history</div>
    <span class="dgm-repl-arr">→</span>
    <div class="dgm-repl-n green">Print reply, append it</div>
  </div>
  <div class="dgm-repl-note">Loops back to read line — there is no exit until the user stops.</div>
</div>


The only state is the message list. Each turn appends the user message and the assistant
reply, so the model always sees the full conversation.

## Build It

`code/repl.py` — uses the SDK; type `exit` to quit:

```python
import anthropic
client = anthropic.Anthropic()

def repl(model="claude-opus-5"):
    history = []
    print("Talk to the model (type 'exit' to quit).")
    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user in ("exit", "quit"):
            break
        history.append({"role": "user", "content": user})
        msg = client.messages.create(model=model, max_tokens=1024, messages=history)
        text = "".join(b.text for b in msg.content if b.type == "text")
        print("ai>", text)
        history.append({"role": "assistant", "content": text})

if __name__ == "__main__":
    repl()
```

That's a working conversational harness in ~20 lines. Phase 2 adds tools to the same
loop. Everything else in the course thickens it.

## Use It

This is the shape the Claude Code CLI is built around — a loop carrying conversation
state, with tools, permissions, and rendering layered on. You'll recognize this skeleton
under every coding agent.

## Ship It

[`code/repl.py`](../../04-repl/code/repl.py) — a minimal conversational REPL you can extend
in later phases.

## Check Yourself

**Q1.** What is the REPL's only piece of state?

- A) the model name
- B) the message history list
- C) the API key
- D) the terminal

<details><summary>Answer</summary>B — history is the conversation memory; the model is
stateless.</details>

**Q2.** What turns this REPL into the Phase 2 agent loop?

- A) a bigger model
- B) adding tools and a tool-execution step inside the loop
- C) streaming
- D) a database

<details><summary>Answer</summary>B — tools + the act step make it an agent.</details>

**Challenge.** Add a `/reset` command that clears history, and print a running token
estimate each turn (4 chars ≈ 1 token).

## Related

- Builds on: [Your first raw model call](../../02-first-raw-call/docs/en.md)
- Leads to: Phase 2 — [The Agent Loop](../../../../ROADMAP.md)
