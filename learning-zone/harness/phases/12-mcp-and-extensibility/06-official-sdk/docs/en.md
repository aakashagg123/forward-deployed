# Use it: the official MCP SDK

> **Motto** — You built the protocol; now let the SDK handle the framing and transport.

*Part of Phase 12 — MCP & Extensibility. Completes the phase.*

## The Problem

Your from-scratch server and client (lessons 01–03) taught you the protocol. But you don't
ship hand-rolled JSON-RPC framing and stdio plumbing in production. Instead you use the
official **MCP SDK** (`mcp` for Python, `@modelcontextprotocol/sdk` for TypeScript). It
handles the handshake, transports (stdio/HTTP), schemas, and errors. Because you built the
toy version first, the SDK's internals are transparent to you.

## The Concept

<style>
.dgm-osdk{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-osdk-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-osdk h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-osdk-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-osdk-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-osdk-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-osdk-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-osdk-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-osdk-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-osdk-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-osdk-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-osdk-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-osdk{padding:20px 16px 18px}.dgm-osdk-row{flex-direction:column}}
</style>
<div class="dgm-osdk">
  <span class="dgm-osdk-chip">Decorate a function, get an MCP server</span>
  <h4>@tool-decorated functions go through the SDK's framing and transport</h4>
  <p class="dgm-osdk-sub">The SDK handles the wire protocol so the tool author only writes the function.</p>
  <div class="dgm-osdk-row">
    <div class="dgm-osdk-n accent">@tool-decorated functions</div>
    <span class="dgm-osdk-arr">→</span>
    <div class="dgm-osdk-n blue">MCP SDK: framing + transport</div>
    <span class="dgm-osdk-arr">→</span>
    <div class="dgm-osdk-n green">Claude Code / Codex</div>
  </div>
</div>


You declare tools, and the SDK exposes them over a real transport to any MCP client.

## Build It / Use It

`code/sdk_server.py` shows the Python SDK shape (install `mcp` to run). It's the same memory
server from Phase 9, now a real MCP server:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("memory")

@mcp.tool()
def remember(fact: str) -> str:
    """Save a durable fact."""
    _STORE.append(fact)
    return "remembered"

@mcp.tool()
def recall(query: str, k: int = 3) -> list[str]:
    """Retrieve relevant facts."""
    return [f for f in _STORE if any(w in f for w in query.split())][:k]

_STORE: list[str] = []

if __name__ == "__main__":
    mcp.run()                    # serves over stdio by default
```

The `@mcp.tool()` decorator does what your lesson-02 `add_tool` did. It derives the schema
from the type hints and registers the handler, and `mcp.run()` is your dispatcher and
transport combined. Compare it to `server.py` to see exactly what the SDK abstracts.

## Use It

Register it with Claude Code (`claude mcp add memory -- python sdk_server.py`) or in Codex's
MCP config, and the agent gains `remember`/`recall` tools across sessions. This is the
end-state of the phase: a real, installable MCP server. You fully understand its internals
because you built the protocol by hand first.

## Ship It

[`code/sdk_server.py`](../../06-official-sdk/code/sdk_server.py) — a memory MCP server on the
official Python SDK.

## Check Yourself

**Q1.** What does the SDK's `@mcp.tool()` decorator save you from writing?

- A) the business logic
- B) JSON-RPC framing, schema derivation, and transport plumbing
- C) the tool's name
- D) nothing

<details><summary>Answer</summary>B — the protocol mechanics you built in lessons
01–03.</details>

**Q2.** How do you add this server to a coding agent?

- A) paste it into the prompt
- B) register it in the agent's MCP config (e.g. `claude mcp add ...`)
- C) you can't
- D) commit it to git only

<details><summary>Answer</summary>B — declare it as an MCP server in config.</details>

**Challenge.** Port `sdk_server.py` to the TypeScript SDK (`@modelcontextprotocol/sdk`) and
register it with both Claude Code and Codex.

## Related

- Builds on: the whole phase; Phase 9 — [memory server](../../../09-memory-and-persistence/05-memory-mcp/docs/en.md)
- Phase complete → next: Phase 13 — [Retrieval & Codebase Understanding](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
