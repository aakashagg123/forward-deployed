# First Call and a REPL

> **Motto** — A model call is one HTTPS POST, and a read-eval-print loop around it is the smallest useful harness.

*Part of Phase 01 — Foundations and the Loop.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

An SDK hides the wire. When a call fails, you cannot tell if the bug is yours or the library's. You also need a place to try every later idea.

Two things fix this. First, make one call with nothing but `urllib`. You see the URL, the headers, and the JSON body. Second, wrap that call in a loop that keeps the conversation. The loop is where tools, memory, and permissions will attach in later lessons.

## The Concept

A request is a POST to `/v1/messages`. It needs three headers: `x-api-key`, `anthropic-version`, and `content-type`. The body needs `model`, `max_tokens`, and `messages`. The reply holds a `content` list of typed blocks. Read the `text` blocks.

The model keeps no state. Your `messages` list is the only memory, so the REPL appends every turn to it.

Roles have a job each:

- **system** holds durable rules. It is a top-level field. The Messages API has no `"system"` role inside `messages`.
- **user** holds the task and any outside text, such as a file or a web page.
- **assistant** holds the model's earlier replies.

The API combines consecutive turns that have the same role. Alternate them anyway, so you see what the model sees. Wrap outside text in tags and tell the system prompt to treat it as data. This lowers the risk of injected instructions. It does not remove it.

<style>
.dgm-repl{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-repl-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-repl h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-repl-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-repl-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-repl-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-repl-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-repl-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-repl-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-repl-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-repl-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-repl-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-repl{padding:20px 16px 18px}.dgm-repl-row{flex-direction:column}}
.dgm-repl-note{margin-top:10px;padding:9px 14px;background:var(--color-background-success-surface);border:1px dashed var(--color-border-success-outline);border-radius:10px;
  font-size:10.5px;color:var(--color-text-success);line-height:1.4}
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


## Build It

`code/repl.py` has no dependencies. `build_request` makes the POST but does not send it, so you can inspect it offline.

```python
def build_request(messages, system=None, api_key="", max_tokens=1024):
    """Build the one HTTPS POST behind every model call. Nothing is sent here."""
    body = {"model": MODEL, "max_tokens": max_tokens, "messages": messages}
    if system:
        body["system"] = system        # top-level field: messages have no "system" role
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01",
               "content-type": "application/json"}
    return urllib.request.Request(API_URL, data=json.dumps(body).encode(),
                                  headers=headers, method="POST")
```

`untrusted` marks outside text as data. It also stops that text from closing the tag early.

```python
def untrusted(text, title="document"):
    """Wrap outside text as data. This lowers risk. It does not remove it."""
    safe = text.replace("</document>", "&lt;/document&gt;")   # block an early close tag
    return f'<document title="{title}">\n{safe}\n</document>'
```

`repl` takes any `send(history)` function. It rolls back the user turn if the call fails. Without that line, the next call would carry two user turns and a broken thread.

```python
def repl(send, read=input, write=print):
    """Read a line, append it, call the model, print and append the reply."""
    history = []
    while True:
        try:
            line = read("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if line in ("exit", "quit"):
            break
        history.append({"role": "user", "content": line})
        try:
            reply = send(history)
        except Exception as exc:
            history.pop()              # a failed call must not leave a dangling user turn
            write(f"error: {exc}")
            continue
        write("ai>", reply)
        history.append({"role": "assistant", "content": reply})
    return history
```

The file ends with asserts. A scripted model proves that it sees the whole history each turn, that a failed call leaves no dangling turn, and that the request has the right shape.

## Use It

`code/repl_sdk.py` swaps `send` for the official SDK. It needs `pip install anthropic` and `ANTHROPIC_API_KEY`.

```python
def send(history):
    msg = client.messages.create(model=MODEL, max_tokens=1024,
                                 system=SYSTEM, messages=history)
    return "".join(b.text for b in msg.content if b.type == "text")
```

`MODEL` comes from the `HARNESS_MODEL` environment variable. Every model ID is a pinned snapshot, so one constant is the only place to change it. The SDK sends the same POST you built. It reads the key from the environment and returns typed blocks.

Every coding agent is this loop plus tools. The next lessons add the parts around it.

## Challenge

Make `call_api` catch `urllib.error.HTTPError`. Print the status code and the JSON error body. Then force a 401 with a bad key and read the message.

## Sources

[Messages API reference](https://platform.claude.com/docs/en/api/messages)

Next: [Tokens, Context and Caching](../../02-tokens-context-and-caching/docs/en.md)
