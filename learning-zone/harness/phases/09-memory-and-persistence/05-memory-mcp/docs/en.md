# Use it: a memory MCP server

> **Motto** — Expose memory as an MCP server and any agent — Claude Code or Codex — can use it.

*Part of Phase 09 — Memory & Persistence. Completes the phase.*

## The Problem

You've built scratchpad, persistence, long-term memory, and distillation as Python
modules. To make them usable from a *real* agent, they need to be reachable as **tools**
the agent can call. The clean, portable way is the Model Context Protocol (MCP): wrap
memory in an MCP server exposing `remember` and `recall`. Claude Code / Codex can then
connect to it and use it every session. You build MCP from scratch in Phase 12; here you
see why memory is a natural MCP server.

## The Concept

<style>
.dgm-mmc{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-mmc-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-mmc h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-mmc-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-mmc-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-mmc-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-mmc-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-mmc-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-mmc-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-mmc-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-mmc-b.accent h6{color:#0d5c0d}
.dgm-mmc-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-mmc-b.blue h6{color:#0550ae}
.dgm-mmc-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-mmc-b.green h6{color:#1a614f}
.dgm-mmc-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-mmc-b.red h6{color:#82061e}
.dgm-mmc-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-mmc-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-mmc{padding:20px 16px 18px}.dgm-mmc-branches{grid-template-columns:1fr}}
.dgm-mmc-chain{display:flex;flex-direction:column;gap:2px}
.dgm-mmc-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-mmc-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-mmc-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-mmc{padding:20px 16px 18px}}
</style>
<div class="dgm-mmc">
  <span class="dgm-mmc-chip">Memory as a swappable MCP server</span>
  <h4>The agent talks to remember() and recall() — never to the durable store directly</h4>
  <p class="dgm-mmc-sub">Swapping the memory backend never touches the agent's code, only the MCP server.</p>
  <div class="dgm-mmc-chain">
    <div class="dgm-mmc-node accent">Agent (Claude Code / Codex)</div>
    <div class="dgm-mmc-arr">↓</div>
    <div class="dgm-mmc-node alt">Memory server (MCP)</div>
  </div>
  <div class="dgm-mmc-branches">
    <div class="dgm-mmc-b blue">
      <h6>remember(fact, tags)</h6>
    </div>
    <div class="dgm-mmc-b green">
      <h6>recall(query, k)</h6>
    </div>
  </div>
</div>


Memory-as-a-server means it's shared across sessions and across tools. It survives the
ephemeral agent process.

## Build It / Use It

The real server uses the MCP SDK (Phase 12). `code/memory_server.py` shows the tool layer
over the Phase 9 store: a plain class whose methods are the MCP tools. This keeps the
logic testable without a transport.

```python
class MemoryServer:
    """The tool surface a memory MCP server exposes (transport added in Phase 12)."""
    def __init__(self, store):
        self.store = store                 # LongTermMemory from lesson 03

    def remember(self, fact, tags=None):
        return self.store.remember(fact, tags or [])

    def recall(self, query, k=3):
        return self.store.retrieve(query, k)

    def tools(self):
        return [
            {"name": "remember", "description": "Save a durable fact.",
             "input_schema": {"type": "object",
                "properties": {"fact": {"type": "string"}, "tags": {"type": "array"}},
                "required": ["fact"]}},
            {"name": "recall", "description": "Retrieve relevant facts.",
             "input_schema": {"type": "object",
                "properties": {"query": {"type": "string"}, "k": {"type": "integer"}},
                "required": ["query"]}},
        ]
```

```python
class Mem:                       # stand-in store
    def __init__(self): self.f = []
    def remember(self, fact, tags): self.f.append(fact); return "ok"
    def retrieve(self, q, k): return [x for x in self.f if any(w in x for w in q.split())][:k]

s = MemoryServer(Mem())
s.remember("Project uses pnpm.")
print(s.recall("pnpm"))         # ['Project uses pnpm.']
print([t["name"] for t in s.tools()])   # ['remember', 'recall']
```

In Phase 12 you wrap this exact surface in the MCP wire protocol. Here the point is that
memory is just two tools over a durable store.

## Use It

This is exactly a **memory MCP server** you add to Claude Code / Codex, for example via
`.mcp.json` / MCP config. The agent gains `remember` and `recall` tools and carries
knowledge across sessions. It's the productized form of everything in this phase, and a
real, popular category of MCP server.

## Ship It

[`code/memory_server.py`](../../05-memory-mcp/code/memory_server.py) — the tool surface of a
memory MCP server.

## Check Yourself

**Q1.** Why expose memory as an MCP server?

- A) it's trendy
- B) any MCP client (Claude Code/Codex) can then use it, shared across sessions and tools
- C) it's faster
- D) no reason

<details><summary>Answer</summary>B — portable, shared, persistent memory.</details>

**Q2.** A memory server's core tools are…

- A) read and write files
- B) `remember` (save a fact) and `recall` (retrieve relevant facts)
- C) start and stop
- D) login and logout

<details><summary>Answer</summary>B — write and relevance-read.</details>

**Challenge.** After Phase 12, wrap this `MemoryServer` in the MCP protocol. Connect it to
your agent so `recall` runs at the start of each task.

## Related

- Builds on: the whole phase
- Built into a server in: Phase 12 — [MCP & Extensibility](../../../../ROADMAP.md)
- Phase complete → next: Phase 11 — [Planning & Task Management](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
