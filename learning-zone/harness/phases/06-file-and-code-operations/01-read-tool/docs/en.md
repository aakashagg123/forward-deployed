# A read tool with line numbers & ranges

> **Motto** — The agent edits what it can cite — so reads return numbered lines and bounded ranges.

*Part of Phase 06 — File & Code Operations.*

## The Problem

An agent that edits code must read it first. Reading a 5,000-line file whole blows the
context budget (Phase 4), and it gives the model no way to refer to a location. The read
tool must return **line numbers**, so the model can cite `path:line` and target edits. It
must also support **ranges**, so it loads only what it needs.

## The Concept

<style>
.dgm-rdt{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-rdt-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-rdt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-rdt-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-rdt-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-rdt-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-rdt-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-rdt-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-rdt-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-rdt-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-rdt-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-rdt-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-rdt{padding:20px 16px 18px}.dgm-rdt-row{flex-direction:column}}
</style>
<div class="dgm-rdt">
  <span class="dgm-rdt-chip">Every line gets a number before it goes anywhere</span>
  <h4>Numbered, then bounded — a read never dumps a whole huge file</h4>
  <p class="dgm-rdt-sub">Line numbers are what let a later edit target an exact location.</p>
  <div class="dgm-rdt-row">
    <div class="dgm-rdt-n accent">read(path, offset, limit)</div>
    <span class="dgm-rdt-arr">→</span>
    <div class="dgm-rdt-n blue">Prefix each line with its number</div>
    <span class="dgm-rdt-arr">→</span>
    <div class="dgm-rdt-n green">Return bounded slice</div>
  </div>
</div>


Line numbers turn the file into an addressable surface. Offset and limit keep reads within
budget.

## Build It

`code/read_tool.py` — numbered, range-bounded reads:

```python
def read(path, offset=1, limit=2000):
    """Return lines [offset, offset+limit) prefixed with 1-based line numbers."""
    with open(path) as f:
        lines = f.readlines()
    start = max(0, offset - 1)
    chunk = lines[start:start + limit]
    width = len(str(start + len(chunk)))
    return "".join(f"{start+i+1:>{width}}  {ln}" for i, ln in enumerate(chunk))
```

```python
import tempfile, os
p = tempfile.mktemp()
open(p, "w").write("\n".join(f"content {i}" for i in range(1, 21)) + "\n")
print(read(p, offset=5, limit=3))     # lines 5–7, numbered
os.remove(p)
```

The numbering is what lets the model say "change line 6". The edit tool (next lesson) and
`path:line` citations depend on this same numbering.

## Use It

This is the **Read** tool in Claude Code / Codex. It returns `cat -n`-style numbered lines
and accepts offset/limit, so the agent pages through large files instead of swallowing them
whole. Because reads are numbered and bounded, the agent's context stays lean (Phase 4) and
its edits stay precise.

## Ship It

[`code/read_tool.py`](../../01-read-tool/code/read_tool.py) — a numbered, range-bounded read
tool.

## Check Yourself

**Q1.** Why return line numbers from a read tool?

- A) decoration
- B) so the model can cite `path:line` and target precise edits
- C) speed
- D) no reason

<details><summary>Answer</summary>B — numbering makes the file addressable.</details>

**Q2.** Why support offset/limit?

- A) to load only what's needed and respect the context budget
- B) the OS requires it
- C) to sort lines
- D) no reason

<details><summary>Answer</summary>A — bounded reads keep context lean.</details>

**Challenge.** Add a `max_line_chars` that truncates very long lines (e.g. minified JS)
with a marker, so one giant line can't blow the budget.

## Related

- Builds on: Phase 4 — [Injecting context](../../../04-context-engineering/05-injecting-context/docs/en.md)
- Next: [Exact-string edit](../../02-edit-tool/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
