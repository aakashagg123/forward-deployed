# Lexical search & repo maps

> **Motto** — Give the agent a map of the repo's symbols before it goes hunting line by line.

*Part of Phase 13 — Retrieval & Codebase Understanding.*

## The Problem

Grep (Phase 6) finds exact strings. But on a big repo, the agent first needs *orientation*:
what files exist, and what functions or classes each one defines. A **repo map** is a
compact index of files and their top-level symbols. It lets the agent jump to the right file
fast, and lexical search over that map answers "where is `X` defined?" cheaply, before any
semantic search.

## The Concept

<style>
.dgm-rm{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-rm-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-rm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-rm-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-rm-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-rm-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-rm-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-rm-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-rm-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-rm-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-rm-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-rm-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-rm{padding:20px 16px 18px}.dgm-rm-row{flex-direction:column}}
</style>
<div class="dgm-rm">
  <span class="dgm-rm-chip">A lexical map, ranked by match</span>
  <h4>file → [symbols] built once, then matched lexically against the query</h4>
  <p class="dgm-rm-sub">No embeddings here — this is the cheap first line, not the semantic layer.</p>
  <div class="dgm-rm-row">
    <div class="dgm-rm-n neutral">Repo</div>
    <span class="dgm-rm-arr">→</span>
    <div class="dgm-rm-n accent">Map: file → [symbols]</div>
  </div>
  <div class="dgm-rm-row" style="margin-top:8px">
    <div class="dgm-rm-n neutral">Query</div>
    <span class="dgm-rm-arr">→</span>
    <div class="dgm-rm-n blue">Lexical match over symbols + names</div>
    <span class="dgm-rm-arr">→</span>
    <div class="dgm-rm-n green">Ranked files</div>
  </div>
</div>


## Build It

`code/repo_map.py` — build a symbol map (via `ast`) and search it:

```python
import ast, os

def build_map(root):
    repo = {}
    for dp, _, files in os.walk(root):
        for fn in files:
            if fn.endswith(".py"):
                path = os.path.join(dp, fn)
                try:
                    tree = ast.parse(open(path).read())
                except SyntaxError:
                    continue
                repo[path] = [n.name for n in ast.walk(tree)
                              if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    return repo

def search(repo, query):
    q = query.lower()
    hits = [(path, syms) for path, syms in repo.items()
            if q in path.lower() or any(q in s.lower() for s in syms)]
    return hits
```

```python
import tempfile, os
d = tempfile.mkdtemp()
open(os.path.join(d, "auth.py"), "w").write("def login(): pass\nclass Session: pass\n")
m = build_map(d)
print(search(m, "login"))      # [('.../auth.py', ['login', 'Session'])]
```

The map is small — names, not bodies — so it fits in context as an overview. Lexical search
over it points the agent at the right file to read.

## Use It

This is the "understand the codebase" step coding agents do. Claude Code and Codex build an
implicit map through Glob, Grep, and reading key files, and tools like repo-map generators
make it explicit. As a user, a good `CLAUDE.md` that names where things live (Phase 5) is a
hand-written repo map. It saves the agent the discovery cost.

## Ship It

[`code/repo_map.py`](../../01-repo-maps/code/repo_map.py) — a symbol repo map + lexical search.

## Check Yourself

**Q1.** Why build a repo map of symbols instead of reading every file?

- A) reading all is faster
- B) the map is small enough for context and points the agent to the right file cheaply
- C) the OS requires it
- D) no reason

<details><summary>Answer</summary>B — orientation without loading everything.</details>

**Q2.** Lexical search is the ____ pass; semantic search (next lesson) is the ____ pass.

- A) last; first
- B) cheap first; deeper second
- C) only; never
- D) slow; fast

<details><summary>Answer</summary>B — try cheap lexical first, then semantic.</details>

**Challenge.** Extend the map with each symbol's line number so a hit links directly to
`path:line` for the read tool (Phase 6).

## Related

- Builds on: Phase 6 — [Grep](../../../06-file-and-code-operations/05-grep/docs/en.md)
- Next: [Embeddings & semantic code search](../../02-embeddings/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
