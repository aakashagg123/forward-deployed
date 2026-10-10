# The Repo Map

> **Motto** — Give the agent a map of the repo's symbols and cut code on structure, so it can find the right place before it reads.

*Part of Phase 08 — Extending: MCP, Skills, Retrieval.*

*Last reviewed: 2026-10 · Volatility: medium*

## The Problem

On a large repo, the agent first needs orientation. Which files exist? What does each one define? Reading every file costs too much context. Running `grep` on guessed strings wastes turns.

A **repo map** is a compact index: each file, with the functions and classes inside it and their line numbers. It is small enough to sit in context. The agent reads the map, picks a file, and then reads only that part.

Retrieval has a second need. To search code by meaning, you cut files into chunks. A fixed cut ("every 50 lines") slices functions in half. Cut on structure instead.

## The Concept

<style>
.dgm-rm{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-rm-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-rm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-rm-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-rm-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-rm-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-rm-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-rm-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-rm-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-rm-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-rm-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-rm-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
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


One parse feeds two products. The **map** lists every definition, nested ones included. A method appears as `Session.open`, so a search for `open` finds it. The **chunks** are whole definitions that you can embed in the next lesson.

Lexical search is the cheap first pass. It finds names. Semantic search is the deeper second pass. It finds meaning.

## Build It

`code/repo_map.py` uses Python's `ast` module. The `symbols` function walks definitions at every depth and builds qualified names:

```python
def symbols(source, prefix="", body=None):
    """List every def/class, nested ones too, with qualified names like Session.open."""
    out = []
    for node in ast.parse(source).body if body is None else body:
        if isinstance(node, DEFS):
            name = prefix + node.name
            kind = "class" if isinstance(node, ast.ClassDef) else "def"
            out.append({"name": name, "kind": kind, "line": _start(node), "end": node.end_lineno})
            out += symbols(source, name + ".", node.body)
    return out
```

A decorated function starts at its first decorator, not at `def`. The helper `_start` takes the earliest line, so a chunk never loses its decorators.

The `chunks` function makes one chunk per top-level definition. A class larger than `max_lines` splits into its methods, each labelled with the class name. This keeps every chunk small enough to embed and still named after its parent:

```python
        if isinstance(node, ast.ClassDef) and node.end_lineno - _start(node) + 1 > max_lines:
            out += [make(f"{node.name}.{m.name}", m) for m in node.body if isinstance(m, DEFS)]
        else:
            out.append(make(node.name, node))
```

`build_map` walks a directory, skips `.git` and virtual environments, and returns the files it could not parse. It reports them instead of hiding them. `search` ranks an exact name above a prefix, and a prefix above a substring.

The asserts cover the hard cases: an `async def`, two decorators, a function inside a function, a class split into methods, a file with a syntax error, and the ranking order.

Module-level code between definitions is not chunked. A script with logic at the top level needs a "module" chunk too.

## Use It

`ast` works for Python only. For other languages you need another parser, such as tree-sitter. The design stays the same: parse, list definitions, record lines.

You can write a map by hand. A `CLAUDE.md` that says where things live (see [Memory Files](../../../04-prompts-and-instructions/02-memory-files/docs/en.md)) is a repo map in prose. It saves the agent the discovery work on every session. Exact-string search is still the right tool when you know the string; see [Search](../../../05-files-and-shell/03-search/docs/en.md).

Keep the generated map short. A map of thousands of files can cost more than it saves. Measure yours. Show only the directories the task touches, or rank by the query.

## Challenge

Add a `module` chunk for top-level statements outside any definition (imports and script code). Assert that every line of a sample file belongs to exactly one chunk.

Next: [A search_code tool](../../05-search-code-tool/docs/en.md)
