# Glob & file discovery

> **Motto** — Before it can read the right file, the agent has to find it.

*Part of Phase 06 — File & Code Operations.*

## The Problem

The agent rarely knows exact paths up front. It needs to *discover* files by pattern —
"all `*.py` under `src`", "every test file" — to build a mental map of the repo and pick
what to read. A glob tool turns a pattern into a list of paths. Ideally the list runs
newest-first, so recently-changed files surface.

## The Concept

```mermaid
flowchart LR
  P["pattern, e.g. **/*.py"] --> G["match files"] --> S["sort by mtime (recent first)"] --> L["paths"]
```

## Build It

`code/glob_tool.py` — pattern discovery with recency sort, stdlib `pathlib`:

```python
from pathlib import Path

def glob(pattern, root="."):
    paths = [p for p in Path(root).glob(pattern) if p.is_file()]
    paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)   # recent first
    return [str(p) for p in paths]
```

```python
import tempfile, os
d = tempfile.mkdtemp()
for n in ["a.py", "b.py", "c.txt"]:
    open(os.path.join(d, n), "w").write("x")
print(glob("*.py", root=d))      # ['.../b.py', '.../a.py'] (recent first)
```

Recency-first ordering matters. When many files match, the ones the agent (or developer)
just touched are usually the relevant ones.

## Use It

This is the **Glob** tool in Claude Code / Codex. It does fast pattern matching and returns
paths sorted by modification time, so the agent can answer "where is X?" and choose what to
Read without scanning the whole tree. It pairs with Grep (next lesson): glob narrows by
name, and grep narrows by content.

## Ship It

[`code/glob_tool.py`](../../04-glob/code/glob_tool.py) — a recency-sorted glob tool.

## Check Yourself

**Q1.** Why sort glob results by modification time?

- A) alphabetical is wrong
- B) recently-changed files are usually the relevant ones
- C) the OS requires it
- D) no reason

<details><summary>Answer</summary>B — recency surfaces likely-relevant files.</details>

**Q2.** Glob narrows by ____; Grep narrows by ____.

- A) content; name
- B) name/path pattern; content
- C) size; date
- D) both by content

<details><summary>Answer</summary>B — glob = name, grep = content.</details>

**Challenge.** Add an `ignore` list (e.g. `node_modules`, `.git`) so discovery skips
vendored and VCS directories.

## Related

- Builds on: [Read tool](../../01-read-tool/docs/en.md)
- Next: [Grep / content search](../../05-grep/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
