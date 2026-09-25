# An MCP server: tools, resources, prompts

> **Motto** — An MCP server exposes three things: tools to call, resources to read, prompts to reuse.

*Part of Phase 12 — MCP & Extensibility.*

## The Problem

With the wire protocol in hand (lesson 01), build a real **server**. MCP servers expose
three capability types: **tools** (functions the agent calls), **resources** (data the agent
reads, like files or records), and **prompts** (reusable prompt templates). Implement
`tools/list`, `tools/call`, and the resource methods over the dispatcher. That gives you a
server any MCP client can use.

## The Concept

<style>
.dgm-ms{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ms-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ms h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ms-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ms-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-ms-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-ms-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-ms-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-ms-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-ms-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-ms-b.accent h6{color:#0d5c0d}
.dgm-ms-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-ms-b.blue h6{color:#0550ae}
.dgm-ms-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-ms-b.green h6{color:#1a614f}
.dgm-ms-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-ms-b.red h6{color:#82061e}
.dgm-ms-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-ms-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-ms{padding:20px 16px 18px}.dgm-ms-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-ms">
  <span class="dgm-ms-chip">Three capability families, one server</span>
  <h4>Tools, resources, and prompts each get their own list/call or list/read pair</h4>
  <p class="dgm-ms-sub">A server can offer any subset — nothing requires implementing all three.</p>
  <div class="dgm-ms-q">MCP server</div>
  <div class="dgm-ms-branches">
    <div class="dgm-ms-b accent">
      <h6>tools/list, tools/call</h6>
    </div>
    <div class="dgm-ms-b blue">
      <h6>resources/list, resources/read</h6>
    </div>
    <div class="dgm-ms-b green">
      <h6>prompts/list, prompts/get</h6>
    </div>
  </div>
</div>


## Build It

`code/server.py` — an MCP server (tools + resources) on the Phase 12 dispatcher:

```python
from protocol import Dispatcher, request   # lesson 01

class MCPServer:
    def __init__(self):
        self.d = Dispatcher()
        self.tools = {}          # name -> (schema, fn)
        self.resources = {}      # uri -> content
        self.d.method("tools/list")(lambda p: [s for s, _ in self.tools.values()])
        self.d.method("tools/call")(self._call)
        self.d.method("resources/read")(lambda p: self.resources.get(p["uri"], ""))

    def add_tool(self, name, schema, fn):
        self.tools[name] = ({**schema, "name": name}, fn)

    def add_resource(self, uri, content):
        self.resources[uri] = content

    def _call(self, params):
        name = params["name"]
        if name not in self.tools:
            raise ValueError(f"unknown tool {name}")
        return str(self.tools[name][1](**params.get("arguments", {})))

    def handle(self, raw):
        return self.d.handle(raw)
```

```python
srv = MCPServer()
srv.add_tool("add", {"description": "Add.", "input_schema": {}}, lambda a, b: a + b)
srv.add_resource("file://readme", "hello")
print(srv.handle(request(1, "tools/list")))
print(srv.handle(request(2, "tools/call", {"name": "add", "arguments": {"a": 2, "b": 3}})))
print(srv.handle(request(3, "resources/read", {"uri": "file://readme"})))
```

The server is just the dispatcher plus registries for tools and resources. `tools/list`
returns schemas, `tools/call` runs the function, and `resources/read` returns content.

## Use It

This is what a real MCP server does. The memory server from Phase 9 is one example. You add
such servers to Claude Code with `.mcp.json` or `claude mcp add`, and to Codex through its
MCP config. The agent then sees the server's tools alongside its built-ins. Popular servers
expose GitHub, databases, browsers, and docs this way.

## Ship It

[`code/server.py`](../../02-mcp-server/code/server.py) — an MCP server with tools + resources.

## Check Yourself

**Q1.** The three capability types an MCP server exposes are…

- A) read, write, delete
- B) tools, resources, prompts
- C) GET, POST, PUT
- D) input, output, error

<details><summary>Answer</summary>B — tools (call), resources (read), prompts
(reuse).</details>

**Q2.** `tools/list` returns…

- A) the tool implementations
- B) the tool schemas the client shows the model
- C) resources
- D) nothing

<details><summary>Answer</summary>B — schemas for discovery.</details>

**Challenge.** Add `prompts/list` and `prompts/get` so the server can ship reusable prompt
templates (like the artifacts this course produces).

## Related

- Builds on: [Wire protocol](../../01-wire-protocol/docs/en.md); Phase 9 — [memory server](../../../09-memory-and-persistence/05-memory-mcp/docs/en.md)
- Next: [An MCP client & tool discovery](../../03-mcp-client/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
