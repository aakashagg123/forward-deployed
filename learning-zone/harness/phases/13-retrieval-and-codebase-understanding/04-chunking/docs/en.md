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

```mermaid
flowchart LR
  F["source file"] --> P["parse (ast/tree-sitter)"] --> C["chunk per function/class"] --> E["embed coherent units"]
```

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
