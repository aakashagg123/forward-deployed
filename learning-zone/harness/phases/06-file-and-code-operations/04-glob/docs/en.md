# Glob & file discovery

> **Motto** — Before it can read the right file, the agent has to find it.

*Part of Phase 06 — File & Code Operations.*

## The Problem

The agent rarely knows exact paths up front. It needs to *discover* files by pattern —
"all `*.py` under `src`", "every test file" — to build a mental map of the repo and pick
what to read. A glob tool turns a pattern into a list of paths. Ideally the list runs
newest-first, so recently-changed files surface.

## The Concept

<style>
.dgm-glb{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-glb-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-glb h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-glb-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-glb-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-glb-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-glb-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-glb-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-glb-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-glb-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-glb-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-glb-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-glb{padding:20px 16px 18px}.dgm-glb-row{flex-direction:column}}
</style>
<div class="dgm-glb">
  <span class="dgm-glb-chip">Pattern in, recent files first</span>
  <h4>Glob matches, then sorts by mtime — recency is a free relevance signal</h4>
  <p class="dgm-glb-sub">The files you touched most recently are usually the ones you're about to touch again.</p>
  <div class="dgm-glb-row">
    <div class="dgm-glb-n neutral">Pattern, e.g. **/*.py</div>
    <span class="dgm-glb-arr">→</span>
    <div class="dgm-glb-n accent">Match files</div>
    <span class="dgm-glb-arr">→</span>
    <div class="dgm-glb-n blue">Sort by mtime (recent first)</div>
    <span class="dgm-glb-arr">→</span>
    <div class="dgm-glb-n green">Paths</div>
  </div>
</div>


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
