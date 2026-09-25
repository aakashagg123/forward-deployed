# A streaming agent loop

> **Motto** — Stream tokens so the human sees thinking, not a spinner.

*Part of Phase 02 — The Agent Loop. Builds on lessons 01–06; completes the phase.*

## The Problem

A non-streaming loop waits for the entire model response before showing anything. For a
coding agent that may "think" for many seconds, that's a dead UI. It also weakens the
user's sense of control: they can't tell if it's working or hung, and they can't
interrupt early. Streaming changes the experience — text appears token-by-token. But you
still have to *accumulate* those tokens, and any tool calls, into a complete message
before the act step can run.

## The Concept

<style>
.dgm-strl{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-strl-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-strl h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-strl-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-strl-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-strl-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-strl-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-strl-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-strl-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-strl-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-strl-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-strl-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-strl{padding:20px 16px 18px}.dgm-strl-row{flex-direction:column}}
.dgm-strl-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-strl-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-strl-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-strl-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-strl-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-strl-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-strl-b.accent h6{color:#0d5c0d}
.dgm-strl-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-strl-b.blue h6{color:#0550ae}
.dgm-strl-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-strl-b.green h6{color:#1a614f}
.dgm-strl-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-strl-b.red h6{color:#82061e}
.dgm-strl-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-strl-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-strl{padding:20px 16px 18px}.dgm-strl-branches{grid-template-columns:1fr}}
.dgm-strl-chain{display:flex;flex-direction:column;gap:2px}
.dgm-strl-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-strl-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-strl-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-strl{padding:20px 16px 18px}}
</style>
<div class="dgm-strl">
  <span class="dgm-strl-chip">Streaming and tool calls run on separate tracks</span>
  <h4>Text deltas print live; tool_use deltas accumulate silently until the message completes</h4>
  <p class="dgm-strl-sub">Only after the message is whole does the loop decide whether to act again.</p>
  <div class="dgm-strl-row">
    <div class="dgm-strl-n neutral">Stream start</div>
  </div>
  <div class="dgm-strl-row" style="margin-top:8px">
    <div class="dgm-strl-n blue">Text deltas → print live</div>
  </div>
  <div class="dgm-strl-row" style="margin-top:8px">
    <div class="dgm-strl-n accent">Tool_use deltas → accumulate</div>
  </div>
  <div class="dgm-strl-chain">
    <div class="dgm-strl-node alt">Message complete</div>
  </div>
  <div class="dgm-strl-q">Tool calls?</div>
  <div class="dgm-strl-branches">
    <div class="dgm-strl-b accent">
      <h6>Yes</h6>
      <p>Act → stream next</p>
    </div>
    <div class="dgm-strl-b green">
      <h6>No</h6>
      <p>Done</p>
    </div>
  </div>
</div>


The key insight: streaming changes *how you receive* the message, not the loop's logic.
You still end each turn with a complete message. Then you apply the same termination and
act steps from earlier lessons.

## Build It

A fake streamed model (a generator of deltas) proves the accumulation logic with no
network. `code/streaming.py`:

```python
import sys

def fake_stream(history):
    """Yield deltas like a real streaming API: text chunks, then maybe a tool call."""
    if not any(m["role"] == "tool" for m in history):
        for chunk in ["Let ", "me ", "add ", "those.\n"]:
            yield {"type": "text", "text": chunk}
        yield {"type": "tool_use", "name": "add", "args": {"a": 2, "b": 3}}
    else:
        for chunk in ["The ", "answer ", "is ", history[-1]["content"], "."]:
            yield {"type": "text", "text": chunk}

def stream_turn(history, model, on_text):
    """Consume the stream, print text live, return the assembled message."""
    text, tool_calls = "", []
    for delta in model(history):
        if delta["type"] == "text":
            on_text(delta["text"])              # live output
            text += delta["text"]
        elif delta["type"] == "tool_use":
            tool_calls.append({"name": delta["name"], "args": delta["args"]})
    return {"text": text, "tool_calls": tool_calls}

def run(query, model, tools, max_steps=10):
    history = [{"role": "user", "content": query}]
    for _ in range(max_steps):
        msg = stream_turn(history, model, on_text=lambda t: sys.stdout.write(t))
        history.append({"role": "assistant", "content": msg["text"]})
        if not msg["tool_calls"]:               # same termination as lesson 03
            return msg["text"]
        for call in msg["tool_calls"]:          # same act step as lesson 02
            out = str(tools[call["name"]](**call["args"]))
            history.append({"role": "tool", "content": out})
    return "stopped: max_steps"
```

```python
run("2 + 3?", fake_stream, {"add": lambda a, b: a + b})
# prints:  Let me add those.
#          The answer is 5.
```

The text streams as it arrives. The tool call is accumulated and dispatched only once the
turn is complete. Loop logic stays unchanged.

## Use It

The SDK exposes this as `with client.messages.stream(...) as stream:`. You iterate
`stream.text_stream` for live text, and `stream.get_final_message()` gives you the
assembled message, with `tool_use` blocks, to run the act step on. It's the same
two-part shape: stream for the human, assemble for the loop.

## Ship It

[`code/streaming.py`](../../07-streaming-loop/code/streaming.py) — a streaming loop that
prints live and still drives tools.

## Check Yourself

**Q1.** When can the act step run on a streamed turn?

- A) after the first text delta
- B) only once the message is fully assembled
- C) before the stream starts
- D) never

<details><summary>Answer</summary>B — you need the complete tool call (name + args)
before dispatching; deltas are partial.</details>

**Q2.** Streaming primarily changes…

- A) the loop's termination logic
- B) how the message is *received* (incrementally), not the loop logic
- C) which tools are available
- D) the model's accuracy

<details><summary>Answer</summary>B — same loop; only the delivery of the message is
incremental.</details>

**Challenge.** Add interrupt support: if the user sends a stop signal mid-stream, abandon
the current turn cleanly (close the stream, leave history valid) instead of crashing.

## Related

- Builds on: [tool-call parsing](../../02-tool-call-parsing/docs/en.md), [termination](../../03-termination/docs/en.md)
- Phase complete → next: Phase 3 [Tool Engineering](../../../../ROADMAP.md), Phase 4 [Context Engineering](../../../../ROADMAP.md)
