# Use it: a retrieval tool the agent calls

> **Motto** — Wrap chunk → embed → hybrid-search into one `search_code` tool the agent invokes.

*Part of Phase 13 — Retrieval & Codebase Understanding. Completes the phase.*

## The Problem

You've built repo maps, embeddings, hybrid search, and code chunking. The payoff is a single
**retrieval tool** the agent can call. `search_code(query)` returns the most relevant chunks
with their `path:line`, so on any task the agent can *find* the right code instead of
blindly grepping or reading whole files. This is retrieval as a first-class tool in the
loop.

## The Concept

<style>
.dgm-rt2{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-rt2-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-rt2 h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-rt2-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-rt2-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-rt2-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-rt2-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-rt2-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-rt2-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-rt2-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-rt2-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-rt2-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-rt2{padding:20px 16px 18px}.dgm-rt2-row{flex-direction:column}}
</style>
<div class="dgm-rt2">
  <span class="dgm-rt2-chip">Build the index once, search it every task</span>
  <h4>search_code(query) is the one tool an agent task actually calls</h4>
  <p class="dgm-rt2-sub">Top chunks come back as path:line — the agent still has to read and edit from there.</p>
  <div class="dgm-rt2-row">
    <div class="dgm-rt2-n neutral">Index: chunk → embed (build once)</div>
  </div>
  <div class="dgm-rt2-row" style="margin-top:8px">
    <div class="dgm-rt2-n neutral">Agent task</div>
    <span class="dgm-rt2-arr">→</span>
    <div class="dgm-rt2-n accent">search_code(query)</div>
    <span class="dgm-rt2-arr">→</span>
    <div class="dgm-rt2-n green">Top chunks (path:line) → read → edit</div>
  </div>
</div>


## Build It / Use It

`code/retrieval_tool.py` composes the phase: chunk files, index them, and expose
`search_code` returning ranked chunks (toy embedder so it runs; swap in a real model + the
RRF hybrid for production):

```python
# composes chunk_code (L4) + SemanticIndex (L2)
class CodeSearch:
    def __init__(self):
        self.index = SemanticIndex()
        self.meta = []

    def add_file(self, path, source):
        for ch in chunk_code(source):
            self.index.add(ch["code"])
            self.meta.append({"path": path, "name": ch["name"], "lines": ch["lines"]})

    def search_code(self, query, k=3):
        hits = self.index.search(query, k)
        # map hit text back to metadata (path:line) for the agent to read
        out = []
        for text in hits:
            i = next(j for j, (_, v) in enumerate(self.index.items) if _ == text)
            m = self.meta[i]
            out.append(f"{m['path']}:{m['lines'][0]}  {m['name']}")
        return out
```

```python
cs = CodeSearch()
cs.add_file("auth.py", "def login(u):\n    'authenticate the user'\n    return u\n")
cs.add_file("math.py", "def add(a, b):\n    return a + b\n")
print(cs.search_code("authenticate user"))   # ['auth.py:1  login']
```

Exposed as a tool (Phase 3), or as an MCP server (Phase 12), `search_code` lets the agent
locate code semantically, then read and edit the returned `path:line`.

## Use It

This is what "the agent understands the codebase" really means: a retrieval tool — built
in, or an MCP code-search server — that returns relevant locations, which the agent reads
and edits. Combined with the repo map and a good `CLAUDE.md`, this is how Claude Code and
Codex stay effective in large repos without loading everything into context.

## Ship It

[`code/retrieval_tool.py`](../../05-retrieval-tool/code/retrieval_tool.py) — a `search_code`
retrieval tool composing the phase.

## Check Yourself

**Q1.** What should `search_code` return to be useful to the agent?

- A) whole files
- B) ranked chunks with `path:line` to Read and Edit
- C) a yes/no
- D) embeddings

<details><summary>Answer</summary>B — locations the agent can act on.</details>

**Q2.** How is retrieval exposed to the agent?

- A) only in the prompt
- B) as a tool (Phase 3) or an MCP code-search server (Phase 12)
- C) it can't be
- D) as a resource only

<details><summary>Answer</summary>B — retrieval is a callable tool.</details>

**Challenge.** Swap the toy embedder for a real model and the single index for the RRF hybrid
(lesson 03), then expose `search_code` as an MCP server (Phase 12).

## Related

- Builds on: the whole phase
- Exposed via: Phase 3 — Tools, Phase 12 — MCP
- Phase complete → next: Phase 14 — [Reliability Engineering](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
