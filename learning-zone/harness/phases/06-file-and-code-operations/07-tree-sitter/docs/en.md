# Use it: tree-sitter for structural edits

> **Motto** — Some edits are about *structure*, not strings — parse the code to target them.

*Part of Phase 06 — File & Code Operations. Completes the phase.*

## The Problem

Exact-string edits (lesson 02) cover most changes, but some are inherently structural:
"rename this function everywhere it's *called*", "add a parameter to every method in this
class", "find all functions missing a docstring". String matching can't reliably tell a
call from a definition from a comment. For these tasks you parse the code into a syntax
tree and operate on nodes. That's what **tree-sitter** gives you.

## The Concept

<style>
.dgm-tst{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-tst-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-tst h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-tst-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-tst-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-tst-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-tst-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-tst-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-tst-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-tst-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-tst-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-tst-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-tst{padding:20px 16px 18px}.dgm-tst-row{flex-direction:column}}
</style>
<div class="dgm-tst">
  <span class="dgm-tst-chip">Edit by node span, not by line number</span>
  <h4>Parse to an AST, query the nodes you care about, then edit by their span</h4>
  <p class="dgm-tst-sub">Node spans stay correct even after earlier edits shift line numbers around them.</p>
  <div class="dgm-tst-row">
    <div class="dgm-tst-n neutral">Source</div>
    <span class="dgm-tst-arr">→</span>
    <div class="dgm-tst-n accent">tree-sitter parse → AST</div>
    <span class="dgm-tst-arr">→</span>
    <div class="dgm-tst-n blue">Query nodes (functions, calls…)</div>
    <span class="dgm-tst-arr">→</span>
    <div class="dgm-tst-n green">Edit by node span</div>
  </div>
</div>


A parser turns text into a typed tree. You query node types and edit by their byte or line
spans, which stays precise where strings are ambiguous.

## Build It / Use It

Tree-sitter is a library, so this is **Use It**. `code/structural.py` shows the shape with
`tree_sitter` (install required). It also includes a stdlib `ast`-based fallback that runs
here. This fallback lists every function definition and its line — the kind of structural
query strings can't do reliably:

```python
import ast

def list_functions(source):
    tree = ast.parse(source)
    return [(n.name, n.lineno) for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef)]

def functions_missing_docstring(source):
    tree = ast.parse(source)
    return [n.name for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and ast.get_docstring(n) is None]
```

```python
src = "def a():\n    'doc'\n    pass\ndef b():\n    pass\n"
print(list_functions(src))                 # [('a', 1), ('b', 4)]
print(functions_missing_docstring(src))    # ['b']
```

`ast` is Python-only. **tree-sitter** generalizes this to dozens of languages with one API.
That's why coding agents use it for cross-language structural understanding.

## Use It

Claude Code / Codex lean on string Edit for most changes. But structural awareness — via
tree-sitter under the hood, or language servers — powers accurate symbol navigation and
large-scale refactors. When your task is "every call site" or "every method," reach for a
parser instead of a regex.

## Ship It

[`code/structural.py`](../../07-tree-sitter/code/structural.py) — structural queries (ast
fallback now; tree-sitter for multi-language).

## Check Yourself

**Q1.** When is a parser better than exact-string editing?

- A) always
- B) for structural edits (call sites vs. definitions, every method) where strings are ambiguous
- C) never
- D) only for JSON

<details><summary>Answer</summary>B — structure-aware tasks need an AST.</details>

**Q2.** Why tree-sitter over Python's `ast` in a real agent?

- A) it's older
- B) it parses dozens of languages with one API
- C) it's pure Python
- D) no reason

<details><summary>Answer</summary>B — multi-language structural parsing.</details>

**Challenge.** Use the `ast` helper to find every function with more than N parameters — a
structural lint a string search couldn't do reliably.

## Related

- Builds on: [Edit tool](../../02-edit-tool/docs/en.md), [Patches](../../06-patches/docs/en.md)
- Phase complete → next: Phase 7 — [Shell & Sandbox Execution](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
