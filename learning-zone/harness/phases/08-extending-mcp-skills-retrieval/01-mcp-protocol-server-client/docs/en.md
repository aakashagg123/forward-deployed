# The MCP Protocol: Server and Client

> **Motto** — MCP is JSON-RPC over a pipe: shake hands, list the tools, call them, and report failures in the right place.

*Part of Phase 08 — Extending: MCP, Skills, Retrieval.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

An agent needs tools that live outside the harness: a database, a ticket system, a browser. Writing a custom adapter for each one does not scale.

The **Model Context Protocol (MCP)** is the shared wire format. A **server** exposes tools. A **client** inside the harness discovers them and calls them. Once the model sees a server tool, it looks like any built-in tool.

If you know the messages, you can debug a server that fails to appear. Most failures happen in the handshake or in the tool list.

## The Concept

<style>
.dgm-wp{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-wp-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-wp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-wp-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-wp-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-wp-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-wp-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-wp-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-wp-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-wp-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-wp-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-wp-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-wp{padding:20px 16px 18px}.dgm-wp-row{flex-direction:column}}
</style>
<div class="dgm-wp">
  <span class="dgm-wp-chip">A handshake, then normal work</span>
  <h4>Initialize, notify, list tools, call a tool</h4>
  <p class="dgm-wp-sub">A notification has no id and gets no reply. A tool failure comes back as isError, not a protocol error.</p>
  <div class="dgm-wp-row">
    <div class="dgm-wp-n blue">Client → initialize</div>
    <span class="dgm-wp-arr"><span class="lbl">reply</span>→</span>
    <div class="dgm-wp-n green">Server → result (version, capabilities, serverInfo)</div>
  </div>
  <div class="dgm-wp-row" style="margin-top:8px">
    <div class="dgm-wp-n blue">Client → notifications/initialized</div>
    <span class="dgm-wp-arr"><span class="lbl">no reply</span>→</span>
    <div class="dgm-wp-n neutral">Normal work begins</div>
  </div>
  <div class="dgm-wp-row" style="margin-top:8px">
    <div class="dgm-wp-n blue">Client → tools/list</div>
    <span class="dgm-wp-arr"><span class="lbl">reply</span>→</span>
    <div class="dgm-wp-n green">Server → {tools: [name, description, inputSchema]}</div>
  </div>
  <div class="dgm-wp-row" style="margin-top:8px">
    <div class="dgm-wp-n blue">Client → tools/call (name, arguments)</div>
    <span class="dgm-wp-arr"><span class="lbl">reply</span>→</span>
    <div class="dgm-wp-n green">Server → {content, isError}</div>
  </div>
</div>


MCP uses JSON-RPC 2.0. A request has an `id`, a `method` and `params`. A **notification** has no `id` and gets no reply. The client sends `initialize` first, then the `notifications/initialized` notification. Only then does normal work begin.

Errors have two homes. A **protocol error** (unknown method, unknown tool) is a JSON-RPC `error`. A **tool failure** (the tool ran and broke) is a normal result with `isError: true`. The model reads the second kind and can recover. It usually cannot act on the first kind, and many clients do not show it to the model.

## Build It

`code/mcp_stdio.py` holds a working server and client in one file. The client starts the server as a subprocess and talks over its stdin and stdout. The `handle` function is the whole server. Its tool branch shows the two error homes:

```python
    elif method == "tools/call":
        p = msg.get("params", {})
        if p.get("name") not in {t["name"] for t in TOOLS}:      # protocol error
            return {"jsonrpc": "2.0", "id": mid, "error": {
                "code": -32602, "message": f"Unknown tool: {p.get('name')}"}}
        try:
            text, is_error = str(run_tool(p["name"], p.get("arguments", {}))), False
        except Exception as e:                # tool failure: a result with isError
            text, is_error = f"{type(e).__name__}: {e}", True
        result = {"content": [{"type": "text", "text": text}], "isError": is_error}
```

The file follows the stdio rules. Each message is one line of JSON, with no embedded newline. The server writes only protocol messages to stdout and sends its logs to stderr. The client calls `json.loads` on every stdout line, so a stray print would crash it.

The asserts walk the full flow. A `tools/list` before the handshake fails. `initialize` returns the version and server info. `tools/list` returns `name` and `inputSchema`, which are required, and `description`, which is optional but you should always set. `add` returns `"5"`. `divide` by zero returns `isError: true` as a result, not as an error. An unknown tool returns code `-32602`.

This server holds no state and writes nothing to disk. It also skips resources and prompts, the two other MCP capabilities. A server may offer any mix of tools, resources and prompts.

## Use It

You do not write this by hand in production. Claude Code is the client. Add a stdio server like this:

```bash
claude mcp add my-server -- python3 server.py
```

For a remote server, use HTTP:

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

The `--` separates Claude's options from the server command. Project-shared servers go in `.mcp.json` at the project root, under the `mcpServers` key. Run `/mcp` in a session to see server status.

MCP has two standard transports. **stdio** runs the server as a subprocess, as you built. **Streamable HTTP** serves one endpoint that handles POST and GET, and may stream replies with SSE. A server that does not stream may answer GET with 405. It replaced the older HTTP+SSE transport, and Claude Code marks SSE as deprecated. A server must validate the `Origin` header, and a local one should bind only to localhost. Newer spec revisions exist (2025-11-25); this lesson follows 2025-06-18.

When a server's tools do not show up, check `initialize` and `tools/list`. Also check stdout. Any non-protocol output there breaks a stdio server.

## Challenge

Add a `resources/list` and `resources/read` pair that serves one file from a directory you choose. Reject any URI that escapes that directory, and assert that `../secret` fails.

## Sources

MCP specification 2025-06-18: lifecycle, transports, tools. Claude Code docs, "Connect to tools via MCP" (code.claude.com/docs).

Next: [The official MCP SDK](../../02-official-mcp-sdk/docs/en.md)
