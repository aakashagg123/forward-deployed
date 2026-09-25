# Streaming responses token-by-token

> **Motto** — Streaming is just parsing a sequence of server-sent events into a growing message.

*Part of Phase 01 — LLM I/O Foundations.*

## The Problem

A non-streaming call blocks until the whole reply is ready. For anything interactive that
feels broken. Streaming sends the reply as a series of **server-sent events (SSE)**. But
now your harness has to parse those events and *reassemble* them into the final message.
Build the parser and streaming stops being a black box.

## The Concept

The wire format is SSE: lines like `event: <type>` and `data: <json>`, blocks separated
by blank lines. For messages you get `content_block_delta` events carrying text fragments,
then a final `message_stop`.

<style>
.dgm-strm{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-strm-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-strm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-strm-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-strm-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-strm-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-strm-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-strm-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-strm-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-strm-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-strm-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-strm-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-strm{padding:20px 16px 18px}.dgm-strm-row{flex-direction:column}}
</style>
<div class="dgm-strm">
  <span class="dgm-strm-chip">Server-sent events become one message</span>
  <h4>Parse, accumulate, then assemble the final message</h4>
  <p class="dgm-strm-sub">The client never waits for the whole response before it starts showing text.</p>
  <div class="dgm-strm-row">
    <div class="dgm-strm-n neutral">SSE lines</div>
    <span class="dgm-strm-arr">→</span>
    <div class="dgm-strm-n blue">Parse event/data pairs</div>
    <span class="dgm-strm-arr">→</span>
    <div class="dgm-strm-n accent">Accumulate text deltas</div>
    <span class="dgm-strm-arr">→</span>
    <div class="dgm-strm-n green">Final message</div>
  </div>
</div>


## Build It

`code/sse.py` — a from-scratch SSE parser fed a fake event stream:

```python
import json

def parse_sse(lines):
    """Yield (event, data) pairs from raw SSE lines."""
    event, data = None, None
    for line in lines:
        line = line.rstrip("\n")
        if line.startswith("event:"):
            event = line[6:].strip()
        elif line.startswith("data:"):
            data = json.loads(line[5:].strip())
        elif line == "":                              # blank line ends an event
            if event is not None:
                yield event, data
            event, data = None, None

def assemble(events):
    text = ""
    for event, data in events:
        if event == "content_block_delta":
            text += data["delta"]["text"]
    return text
```

```python
raw = [
  'event: content_block_delta', 'data: {"delta":{"text":"Hel"}}', '',
  'event: content_block_delta', 'data: {"delta":{"text":"lo"}}', '',
  'event: message_stop', 'data: {}', '',
]
print(assemble(parse_sse(raw)))      # "Hello"
```

You just reconstructed a streamed message from raw events — exactly what the SDK does
behind `for text in stream.text_stream`.

## Use It

`with client.messages.stream(...) as stream:` gives you `stream.text_stream` (live text)
and `stream.get_final_message()` (the assembled message with tool_use blocks). The agent
loop streams for the human and assembles for the act step (you built both halves in
Phase 2 lesson 07).

## Ship It

[`code/sse.py`](../../04-streaming/code/sse.py) — an SSE parser + message assembler.

## Check Yourself

**Q1.** What separates one SSE event from the next?

- A) a comma
- B) a blank line
- C) a semicolon
- D) nothing

<details><summary>Answer</summary>B — events are blocks of lines ended by a blank
line.</details>

**Q2.** When is the act step (tool dispatch) safe to run on a streamed reply?

- A) on the first delta
- B) only after the message is fully assembled
- C) never
- D) before streaming

<details><summary>Answer</summary>B — partial deltas can't be dispatched; assemble
first.</details>

**Challenge.** Handle `error` events in the stream: surface them as a clean exception
instead of silently producing a truncated message.

## Related

- Builds on: [Messages](../../01-messages-roles-turns/docs/en.md)
- Related: Phase 2 — [A streaming agent loop](../../../02-the-agent-loop/07-streaming-loop/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
