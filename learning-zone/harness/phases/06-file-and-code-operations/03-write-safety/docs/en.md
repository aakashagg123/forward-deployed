# Write & overwrite safety

> **Motto** — Writing a file is destructive — gate it so the agent never clobbers what it hasn't seen.

*Part of Phase 06 — File & Code Operations.*

## The Problem

`write(path, content)` replaces a file wholesale. If the agent writes a file it never read,
it may destroy content it didn't know was there. Coding agents use one safety rule: you may
only overwrite a file you've **read this session**, so the model saw what it's replacing.
New files are always fine. This rule prevents the "agent nuked my config" class of incident.

## The Concept

<style>
.dgm-ws{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ws-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ws h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ws-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ws-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-ws-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-ws-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-ws-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-ws-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-ws-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-ws-b.accent h6{color:#0d5c0d}
.dgm-ws-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-ws-b.blue h6{color:#0550ae}
.dgm-ws-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-ws-b.green h6{color:#1a614f}
.dgm-ws-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-ws-b.red h6{color:#82061e}
.dgm-ws-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-ws-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-ws{padding:20px 16px 18px}.dgm-ws-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-ws">
  <span class="dgm-ws-chip">You can't overwrite what you haven't read</span>
  <h4>Creating a new file is always safe; overwriting an existing one requires a read first</h4>
  <p class="dgm-ws-sub">This session-scoped read check is what stops a write from silently clobbering someone else's edit.</p>
  <div class="dgm-ws-q">write(path, content) — file exists?</div>
  <div class="dgm-ws-branches">
    <div class="dgm-ws-b green">
      <h6>No</h6>
      <p>Create — safe</p>
    </div>
    <div class="dgm-ws-b accent">
      <h6>Yes — read this session?</h6>
      <p>Yes → overwrite allowed · No → deny: read it first</p>
    </div>
  </div>
</div>


## Build It

`code/write_tool.py` — a write tool that tracks reads and gates overwrites:

```python
import os

class FileWriter:
    def __init__(self):
        self.read_files = set()

    def read(self, path):
        self.read_files.add(os.path.abspath(path))
        with open(path) as f:
            return f.read()

    def write(self, path, content):
        ap = os.path.abspath(path)
        if os.path.exists(ap) and ap not in self.read_files:
            return "error: refusing to overwrite a file you haven't read this session"
        with open(ap, "w") as f:
            f.write(content)
        self.read_files.add(ap)
        return "ok: wrote " + path
```

```python
import tempfile, os
fw = FileWriter(); p = tempfile.mktemp()
print(fw.write(p, "v1"))            # new file: ok
open(p, "w").write("changed out-of-band")
print(fw.write(p, "v2"))            # exists but not read this session → denied
fw.read(p); print(fw.write(p, "v2"))  # now allowed
os.remove(p)
```

The gate is structural: the agent must demonstrate it has seen the file before it can
replace it.

## Use It

This is the **Write** tool rule in Claude Code / Codex. Overwriting an existing file you
haven't read in the session is blocked. Creating a new file is always fine. This is why the
agent reads before it writes. For partial changes, it prefers Edit (lesson 02) over Write.

## Ship It

[`code/write_tool.py`](../../03-write-safety/code/write_tool.py) — a read-gated write tool.

## Check Yourself

**Q1.** When may the agent overwrite an existing file?

- A) anytime
- B) only after reading it this session (so it saw what it's replacing)
- C) never
- D) only new files

<details><summary>Answer</summary>B — read-before-overwrite is the safety gate.</details>

**Q2.** For a small change to a large file, prefer…

- A) Write (rewrite the whole file)
- B) Edit (exact-string replacement)
- C) delete and recreate
- D) append

<details><summary>Answer</summary>B — Edit is surgical; Write risks clobbering.</details>

**Challenge.** Add a `.bak` backup written before each overwrite, and a `restore()` that
reverts the last write.

## Related

- Builds on: [Edit tool](../../02-edit-tool/docs/en.md)
- Next: [Glob & file discovery](../../04-glob/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
