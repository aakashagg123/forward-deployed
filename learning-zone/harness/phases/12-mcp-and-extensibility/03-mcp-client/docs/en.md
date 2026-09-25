# An MCP client & tool discovery

> **Motto** — The client connects, discovers the server's tools, and exposes them to the model.

*Part of Phase 12 — MCP & Extensibility.*

## The Problem

A server is useless without a **client**. The harness side of MCP connects to a server,
calls `initialize`, and fetches `tools/list`. It merges those tools into the agent's tool set
so the model can call them, and routes each `tool_use` for a server tool back over
`tools/call`. This is how external tools become indistinguishable from built-ins to the
model.

## The Concept

<style>
.dgm-mc{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-mc-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-mc h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-mc-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-mc-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-mc-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-mc-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-mc-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-mc-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-mc-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-mc-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-mc-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-mc{padding:20px 16px 18px}.dgm-mc-row{flex-direction:column}}
</style>
<div class="dgm-mc">
  <span class="dgm-mc-chip">Discovered tools merge into the same registry</span>
  <h4>The MCP client lists what a server offers, then routes calls back through it</h4>
  <p class="dgm-mc-sub">From the model's point of view, an MCP tool looks identical to a native one.</p>
  <div class="dgm-mc-row">
    <div class="dgm-mc-n neutral">Harness</div>
    <span class="dgm-mc-arr">→</span>
    <div class="dgm-mc-n accent">MCP client</div>
    <span class="dgm-mc-arr"><span class='lbl'>tools/list</span>→</span>
    <div class="dgm-mc-n blue">Server</div>
  </div>
  <div class="dgm-mc-row" style="margin-top:8px">
    <div class="dgm-mc-n accent">Merge discovered tools into registry (Phase 3)</div>
    <span class="dgm-mc-arr">→</span>
    <div class="dgm-mc-n green">Model calls tool → client routes tools/call → server</div>
  </div>
</div>


## Build It

`code/client.py` — a client that discovers and invokes server tools (talks to the lesson-02
server in-process):

```python
import json

class MCPClient:
    def __init__(self, server):
        self.server = server          # anything with .handle(raw_json) -> raw_json
        self._id = 0

    def _rpc(self, method, params=None):
        self._id += 1
        raw = json.dumps({"jsonrpc": "2.0", "id": self._id,
                          "method": method, "params": params or {}})
        return json.loads(self.server.handle(raw))

    def list_tools(self):
        return self._rpc("tools/list").get("result", [])

    def call(self, name, **arguments):
        r = self._rpc("tools/call", {"name": name, "arguments": arguments})
        return r.get("result", r.get("error"))
```

```python
# server is an MCPServer from lesson 02 with an "add" tool
tools = client.list_tools()                 # [{'name': 'add', ...}]
print(client.call("add", a=2, b=3))         # 5
```

`list_tools()` feeds the model's `tools=` list, merged through the Phase 3 registry.
`call()` is what the loop runs when the model invokes a server tool. The model never knows
the tool lives in another process.

## Use It

This client logic is built into Claude Code and Codex. You declare servers in config, and
the tool connects and discovers their tools at startup. They then appear in the agent's
toolset, often namespaced like `mcp__github__*`. When a server's tools don't show up, the
cause is almost always a failed `initialize` or `tools/list` call — exactly the calls you
implemented.

## Ship It

[`code/client.py`](../../03-mcp-client/code/client.py) — an MCP client with tool discovery and
invocation.

## Check Yourself

**Q1.** After connecting, the client calls ____ to learn what the server offers.

- A) `ping`
- B) `tools/list`
- C) `resources/read`
- D) `shutdown`

<details><summary>Answer</summary>B — discovery via `tools/list`.</details>

**Q2.** To the model, an MCP server's tool looks like…

- A) a special remote call it must handle differently
- B) just another tool in its tool set (the client routes it)
- C) a resource
- D) a prompt

<details><summary>Answer</summary>B — discovered tools merge with built-ins.</details>

**Challenge.** Merge discovered tools into the Phase 3 `Registry` with a namespace prefix
(e.g. `mcp__demo__add`) so server and local tools share one dispatch path.

## Related

- Builds on: [MCP server](../../02-mcp-server/docs/en.md); Phase 3 — [Registry](../../../03-tool-engineering/08-tool-registry/docs/en.md)
- Next: [Skills (SKILL.md) & progressive disclosure](../../04-skills/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
