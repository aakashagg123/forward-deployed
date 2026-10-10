# The Official MCP SDK

> **Motto** — You know the protocol now, so let the SDK write the framing and keep your effort on the tools.

*Part of Phase 08 — Extending: MCP, Skills, Retrieval.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

In [lesson 01](../../01-mcp-protocol-server-client/docs/en.md) you wrote the handshake, the dispatch and the error rules by hand. That was for learning. In production the work is repetitive and easy to get wrong. One missed `isError` or one stray `print` breaks every client.

The official **MCP SDK** does that work. You write a plain function. The SDK builds the schema, runs the handshake, picks the transport and shapes the result. The SDK is also a fast-moving package, so you must check which version you have.

## The Concept

<style>
.dgm-osdk{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-osdk-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-osdk h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-osdk-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-osdk-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-osdk-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-osdk-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-osdk-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-osdk-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-osdk-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-osdk-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-osdk-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-osdk{padding:20px 16px 18px}.dgm-osdk-row{flex-direction:column}}
</style>
<div class="dgm-osdk">
  <span class="dgm-osdk-chip">Decorate a function, get an MCP server</span>
  <h4>@tool-decorated functions go through the SDK and out over a transport</h4>
  <p class="dgm-osdk-sub">The SDK handles the wire protocol so the tool author only writes the function.</p>
  <div class="dgm-osdk-row">
    <div class="dgm-osdk-n accent">@tool-decorated functions</div>
    <span class="dgm-osdk-arr">→</span>
    <div class="dgm-osdk-n blue">MCP SDK: schema, handshake, framing, transport</div>
    <span class="dgm-osdk-arr">→</span>
    <div class="dgm-osdk-n green">Any MCP client (Claude Code and others)</div>
  </div>
</div>


You declare tools. The SDK turns each function signature into an `inputSchema` and its docstring into a description. It then serves them over a transport. A tool needs three things from you: a clear name, type hints and a docstring. The model reads that docstring as the tool's manual, so write it for the model.

## Build It

The first file removes the magic. `code/tool_decorator.py` is a stdlib version of what the SDK decorator does. It reads the signature and builds the `tools/list` entry:

```python
def tool(fn):
    """Register fn as a tool. The schema comes from its signature and docstring."""
    props, required = {}, []
    for name, p in inspect.signature(fn).parameters.items():
        props[name] = {"type": JSON_TYPES[p.annotation]}
        if p.default is inspect.Parameter.empty:
            required.append(name)
        else:
            props[name]["default"] = p.default
    spec = {"name": fn.__name__, "description": inspect.getdoc(fn),
            "inputSchema": {"type": "object", "properties": props, "required": required}}
    TOOLS[fn.__name__] = {"spec": spec, "fn": fn}
    return fn
```

A parameter with a default is optional. A parameter without one goes in `required`. The `call` function checks required arguments and returns an `isError` result when one is missing. The asserts confirm each rule. The real SDK covers far more types than this toy, including nested types and return schemas.

## Use It

Install the SDK with `pip install mcp`. The shape changed between major versions. In `mcp` 1.x you write `from mcp.server.fastmcp import FastMCP`. In `mcp` 2.x the class is `MCPServer`, imported with `from mcp.server import MCPServer`. I ran the files below against `mcp` 2.2.0 and 2.3.0. The client file needs `mcp` 2.x, because `from mcp import Client` does not exist in 1.x. Pin a version in your own project.

`code/notes_server_sdk.py` is a small notes server with two tools and one resource. It writes notes to a JSON file, so they survive a restart:

```python
@mcp.tool()
def remember(note: str) -> str:
    """Save a note to disk."""
    notes = _load()
    notes.append(note)
    NOTES_FILE.write_text(json.dumps(notes))
    return f"saved ({len(notes)} notes)"
```

`mcp.run()` serves over stdio. `mcp.run("streamable-http")` serves over HTTP. A memory server persists only if it writes somewhere, as this one does. A server that keeps notes in a Python list loses them when the process exits.

`code/notes_client_sdk.py` starts the server with the SDK client, lists the tools and saves a note. It then starts a second server process and reads the note back. That check needs the `mcp` package, so it is not part of the offline set. Register the server with Claude Code like this:

```bash
claude mcp add notes -- python3 code/notes_server_sdk.py
```

In my check, the SDK negotiated a protocol revision newer than the 2025-06-18 shapes in lesson 01. Read the revision your SDK reports before you depend on field details.

## Challenge

Add a `forget(note: str)` tool to `notes_server_sdk.py` that removes one note. Extend `notes_client_sdk.py` so a second process confirms the note is gone. Make it raise an exception when the note does not exist. In `mcp` 2.x the client then receives a result with `is_error` set. Assert that, and read the error text. Note how little detail it holds.

## Sources

MCP Python SDK README and migration notes (github.com/modelcontextprotocol/python-sdk). Claude Code docs, "Connect to tools via MCP" (code.claude.com/docs).

Next: [Skills and deferred loading](../../03-skills-and-deferred-loading/docs/en.md)
