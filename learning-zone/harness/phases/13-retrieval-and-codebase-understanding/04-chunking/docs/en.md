# Chunking code without breaking it

> **Motto** — Split code on structure, not on line counts — a chunk should be a whole function.

*Part of Phase 13 — Retrieval & Codebase Understanding.*

## The Problem

To embed and retrieve code (lessons 02–03), you split files into chunks. Naive fixed-size
chunking ("every 50 lines") slices through the middle of functions. A retrieved chunk ends up
as half a function with no context — useless to embed and worse to hand the model. Code
should be chunked on **structural boundaries**, like functions and classes, so each chunk is
a coherent, self-contained unit.

## The Concept

<style>
.dgm-chnk{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-chnk-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-chnk h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-chnk-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-chnk-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-chnk-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-chnk-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-chnk-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-chnk-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-chnk-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-chnk-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-chnk-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-chnk{padding:20px 16px 18px}.dgm-chnk-row{flex-direction:column}}
</style>
<div class="dgm-chnk">
  <span class="dgm-chnk-chip">Chunk boundaries follow syntax, not character counts</span>
  <h4>Parse, then chunk per function or class, so each embedded unit is coherent</h4>
  <p class="dgm-chnk-sub">A chunk cut mid-function embeds badly — syntax-aware chunking avoids that.</p>
  <div class="dgm-chnk-row">
    <div class="dgm-chnk-n neutral">Source file</div>
    <span class="dgm-chnk-arr">→</span>
    <div class="dgm-chnk-n accent">Parse (ast/tree-sitter)</div>
    <span class="dgm-chnk-arr">→</span>
    <div class="dgm-chnk-n blue">Chunk per function/class</div>
    <span class="dgm-chnk-arr">→</span>
    <div class="dgm-chnk-n green">Embed coherent units</div>
  </div>
</div>


## Build It

`code/chunk.py` — split a Python file into function/class chunks via `ast`:

```python
import ast

def chunk_code(source):
    tree = ast.parse(source)
    lines = source.splitlines()
    chunks = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = getattr(node, "end_lineno", start + 1)
            chunks.append({"name": node.name, "lines": (node.lineno, end),
                           "code": "\n".join(lines[start:end])})
    return chunks
```

```python
src = ("import os\n\n"
       "def login(u):\n    return u\n\n"
       "class Session:\n    def open(self):\n        return True\n")
for c in chunk_code(src):
    print(c["name"], c["lines"])     # login (3,4) ; Session (6,8)
```

Each chunk is a complete definition with its line span. It's coherent to embed, and it
carries `path:line` so a retrieval hit links straight to the read tool (Phase 6).

## Use It

Code-aware chunking — via `ast`, or tree-sitter from Phase 6 for multiple languages — is
what makes code retrieval actually useful. Retrieved units are whole functions, not
fragments. For an agent, this means "find code related to X" returns something it can read
and edit directly. Oversized definitions still need a secondary split, but the boundary
stays structural.

## Ship It

[`code/chunk.py`](../../04-chunking/code/chunk.py) — structural (function/class) code chunking.

## Check Yourself

**Q1.** Why chunk code on structural boundaries instead of fixed line counts?

- A) it's faster
- B) fixed chunks slice through functions, producing incoherent fragments
- C) the OS requires it
- D) no reason

<details><summary>Answer</summary>B — whole functions embed and retrieve far better.</details>

**Q2.** What should a code chunk carry alongside its text?

- A) nothing
- B) its name and `path:line` span so a hit links to the read tool
- C) the whole file
- D) a token count only

<details><summary>Answer</summary>B — location for navigation.</details>

**Challenge.** Handle over-large functions by splitting them into sub-chunks (e.g. by inner
blocks) while keeping each labeled with the parent function name.

## Related

- Builds on: Phase 6 — [tree-sitter](../../../06-file-and-code-operations/07-tree-sitter/docs/en.md); [Embeddings](../../02-embeddings/docs/en.md)
- Next: [Use It: a retrieval tool the agent calls](../../05-retrieval-tool/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
