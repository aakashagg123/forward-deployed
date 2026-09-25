# The MCP wire protocol from scratch

> **Motto** — MCP is JSON-RPC: a request with a method and params, a response with a result.

*Part of Phase 12 — MCP & Extensibility.*

## The Problem

MCP (the Model Context Protocol) is how Claude Code and Codex connect to external tool
servers. Before you use an SDK, understand the wire format. MCP runs on **JSON-RPC 2.0**.
Each message is a small JSON object with an `id`, a `method`, and `params`. The reply echoes
the `id` back with a `result` or an `error`. Once you frame and dispatch a few messages by
hand, the SDK is just ergonomics.

## The Concept

<style>
.dgm-wp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-wp-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-wp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-wp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-wp-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-wp-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-wp-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-wp-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-wp-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-wp-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-wp-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-wp-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-wp{padding:20px 16px 18px}.dgm-wp-row{flex-direction:column}}
</style>
<div class="dgm-wp">
  <span class="dgm-wp-chip">A method name and an id, both ways</span>
  <h4>The client sends {id, method, params}; the server replies {id, result} or {id, error}</h4>
  <p class="dgm-wp-sub">The id is what lets a client match an async reply back to its request.</p>
  <div class="dgm-wp-row">
    <div class="dgm-wp-n blue">Client → {id, method, params}</div>
    <span class="dgm-wp-arr">→</span>
    <div class="dgm-wp-n accent">Server dispatches by method</div>
    <span class="dgm-wp-arr">→</span>
    <div class="dgm-wp-n green">Server → {id, result} or {id, error}</div>
  </div>
</div>


Core methods: `initialize` (handshake), `tools/list` (discover), `tools/call` (invoke).

## Build It

`code/protocol.py` — JSON-RPC framing + a method dispatcher, in-memory:

```python
import json

def request(id, method, params=None):
    return json.dumps({"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}})

def response(id, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id}
    msg["error" if error else "result"] = error or result
    return json.dumps(msg)

class Dispatcher:
    def __init__(self):
        self.methods = {}

    def method(self, name):
        def deco(fn): self.methods[name] = fn; return fn
        return deco

    def handle(self, raw):
        msg = json.loads(raw)
        fn = self.methods.get(msg["method"])
        if not fn:
            return response(msg["id"], error={"code": -32601, "message": "method not found"})
        try:
            return response(msg["id"], result=fn(msg.get("params", {})))
        except Exception as e:
            return response(msg["id"], error={"code": -32603, "message": str(e)})
```

```python
d = Dispatcher()
d.method("ping")(lambda p: "pong")
print(d.handle(request(1, "ping")))          # {"jsonrpc":"2.0","id":1,"result":"pong"}
print(d.handle(request(2, "nope")))          # error -32601
```

That's the whole protocol core: frame a request, dispatch by method name, then frame a result
or a structured error with a JSON-RPC error code.

## Use It

Real MCP runs this JSON-RPC over a transport: **stdio** (a subprocess) or **HTTP/SSE**.
Claude Code and Codex speak exactly this to every MCP server you add. You'll use the SDK
(lesson 06), so you never hand-write framing. But when a server misbehaves, you can read the
JSON-RPC traffic and know what `tools/call` should look like.

## Ship It

[`code/protocol.py`](../../01-wire-protocol/code/protocol.py) — JSON-RPC framing + a method
dispatcher.

## Check Yourself

**Q1.** MCP is built on…

- A) REST
- B) JSON-RPC 2.0 (id + method + params → result/error)
- C) GraphQL
- D) gRPC only

<details><summary>Answer</summary>B — JSON-RPC messages over a transport.</details>

**Q2.** The three core methods to get tools working are…

- A) get, post, put
- B) `initialize`, `tools/list`, `tools/call`
- C) login, list, logout
- D) open, read, close

<details><summary>Answer</summary>B — handshake, discover, invoke.</details>

**Challenge.** Add `initialize` returning server capabilities and a protocol version, and
reject `tools/call` before `initialize` has run.

## Related

- Builds on: Phase 3 — [Tool registry](../../../03-tool-engineering/08-tool-registry/docs/en.md)
- Next: [An MCP server](../../02-mcp-server/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
