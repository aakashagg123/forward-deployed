# Edit, Write and Patch: Change Files Safely

> **Motto** — Change a file by replacing one exact string, and never overwrite what the agent has not seen.

*Part of Phase 05 — Files and Shell.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

The lazy way to edit is to ask the model for the whole new file. That is slow and costs many tokens. It is also risky. The model can drop a function or reformat code it should not touch.

Three rules fix this. Edit by replacing one exact string. Overwrite a file only after the agent has read it. Apply a multi-file change as one unit, so a failure leaves nothing half done.

## The Concept

<style>
.dgm-edt{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-edt-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-edt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-edt-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-edt-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-edt-lane{font-size:9.5px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary);text-align:center;margin:0 0 6px}
.dgm-edt-lane.gap{margin-top:16px}
.dgm-edt-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-edt-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-edt-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-edt-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-edt-b.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline)}
.dgm-edt-b.accent h6{color:var(--color-text-success)}
.dgm-edt-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-edt-b.blue h6{color:var(--color-text-info)}
.dgm-edt-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-edt-b.green h6{color:var(--color-text-success)}
.dgm-edt-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-edt-b.red h6{color:var(--color-text-danger)}
.dgm-edt-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-edt-b.neutral h6{color:var(--color-text)}
.dgm-edt-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-edt-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-edt-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-edt-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-edt-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-edt-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-edt-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-edt-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
.dgm-edt-split{display:flex;flex-direction:column;gap:6px}
.dgm-edt-note{font-size:10px;color:var(--color-text-secondary);text-align:center;margin:8px 0 0}
@media (max-width:640px){.dgm-edt{padding:20px 16px 18px}.dgm-edt-branches{grid-template-columns:1fr}.dgm-edt-row{flex-direction:column}}
</style>
<div class="dgm-edt">
  <span class="dgm-edt-chip">Read first, match once, patch whole</span>
  <h4>Three gates before a file changes</h4>
  <p class="dgm-edt-sub">A failed check writes nothing. A crash never leaves half a file.</p>
  <p class="dgm-edt-lane">Read gate: write</p>
  <div class="dgm-edt-q">write(path, content) — file read this session?</div>
  <div class="dgm-edt-branches">
    <div class="dgm-edt-b red">
      <h6>Not read</h6>
      <p>Error: read the file first</p>
    </div>
    <div class="dgm-edt-b red">
      <h6>Changed since read</h6>
      <p>Error: read it again</p>
    </div>
    <div class="dgm-edt-b green">
      <h6>Read, unchanged, or new file</h6>
      <p>Write (temp file, rename)</p>
    </div>
  </div>
  <p class="dgm-edt-lane gap">Exact-once edit</p>
  <div class="dgm-edt-q">edit(path, old, new) — old occurs exactly once?</div>
  <div class="dgm-edt-branches">
    <div class="dgm-edt-b red">
      <h6>No (0)</h6>
      <p>Error: not found</p>
    </div>
    <div class="dgm-edt-b red">
      <h6>No (&gt;1)</h6>
      <p>Error: ambiguous, add context</p>
    </div>
    <div class="dgm-edt-b green">
      <h6>Yes</h6>
      <p>Replace, write</p>
    </div>
  </div>
  <p class="dgm-edt-lane gap">Atomic patch</p>
  <div class="dgm-edt-row">
    <div class="dgm-edt-n accent">Patch: list of (path, old, new) hunks</div>
    <span class="dgm-edt-arr">→</span>
    <div class="dgm-edt-n blue">Check every hunk on staged text</div>
    <span class="dgm-edt-arr">→</span>
    <div class="dgm-edt-split">
      <div class="dgm-edt-n green">All pass: write all</div>
      <div class="dgm-edt-n red">Any fails: write nothing</div>
    </div>
  </div>
</div>


Uniqueness is the safety property. If `old` matches twice, the tool refuses and asks for more context. It never guesses a spot.

Reading is the second gate. The harness records a digest of each file at read time. An edit needs a prior read. A write to an existing file needs a read and an unchanged digest. New files need neither.

A patch is a list of `(path, old, new)` hunks. The tool checks every hunk against staged text first. It writes only if all hunks pass.

## Build It

`code/edit_tool.py` holds one `Workspace` class. Each write goes to a temp file and then `os.replace`, so a crash never leaves a half-written file.

```python
def _write_atomic(path, text):
    """Write to a temp file in the same folder, then rename over the target."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)))
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.replace(tmp, path)


class Workspace:
    def __init__(self):
        self.seen = {}                       # abs path -> digest at last read

    def read(self, path):
        with open(path) as f:
            text = f.read()
        self.seen[os.path.abspath(path)] = _digest(text)
        return text

    def edit(self, path, old, new, replace_all=False):
        ap = os.path.abspath(path)
        if ap not in self.seen:
            return "error: read the file before you edit it"
        with open(ap) as f:
            text = f.read()
        n = text.count(old)
        if n == 0:
            return "error: old_string not found"
        if n > 1 and not replace_all:
            return f"error: old_string matches {n} times; add surrounding context"
        _write_atomic(ap, text.replace(old, new))
        self.seen[ap] = _digest(text.replace(old, new))
        return f"ok: {n if replace_all else 1} replacement(s)"

    def write(self, path, content):
        ap = os.path.abspath(path)
        if os.path.exists(ap):
            if ap not in self.seen:
                return "error: file exists and was not read this session"
            with open(ap) as f:
                if _digest(f.read()) != self.seen[ap]:
                    return "error: file changed since you read it; read it again"
        _write_atomic(ap, content)
        self.seen[ap] = _digest(content)
        return "ok: wrote " + path

    def apply_patch(self, hunks):
        """hunks: [(path, old, new)]. Validate every hunk, then write all or none."""
        staged = {}
        for path, old, new in hunks:
            ap = os.path.abspath(path)
            if ap not in self.seen:
                return f"reject: {path} was not read"
            if ap not in staged:
                with open(ap) as f:
                    staged[ap] = f.read()
            n = staged[ap].count(old)
            if n != 1:
                return f"reject: hunk for {path} matches {n} times (need 1); nothing written"
            staged[ap] = staged[ap].replace(old, new)
        for ap, text in staged.items():      # reached only if every hunk passed
            _write_atomic(ap, text)
            self.seen[ap] = _digest(text)
        return f"applied {len(hunks)} hunk(s) in {len(staged)} file(s)"
```

Look at `apply_patch`. It stages text in memory, so a second hunk on the same file sees the first hunk's result. The disk is touched only in the last loop. If hunk three fails, hunks one and two never wrote.

The file ends with asserts. They prove that an unread edit fails, that an ambiguous match fails, that a clobbering write leaves the file unchanged, and that a bad hunk leaves both files untouched. Run `python3 code/edit_tool.py`.

## Use It

Claude Code has an **Edit** tool and a **Write** tool. Edit does exact string replacement. It uses no regex and no fuzzy match. A single changed space makes it miss.

The documented checks are close to this lesson. The file must have been read in the conversation, and a read cut short by a `PARTIAL view` notice does not count. `old_string` must appear exactly once, or Claude sets `replace_all: true`. Newer models may edit an unread file when reading it would need no permission prompt. Older models always need the read.

Write creates a file or replaces it whole. Older models must read an existing file before they overwrite it. Newer models may overwrite an unread file when reading it would need no permission prompt. Claude Code also lets Edit proceed on a file that changed on disk after the read, if `old_string` still matches. The digest gate in this lesson is a stricter design. For a partial change, Claude uses Edit.

The docs do not describe an atomic multi-file patch tool. Treat `apply_patch` as your own design for review and rollback. Path rules use `Edit(path)`, so one rule covers every built-in tool that edits files. See [Settings.json](../../../06-permissions-and-security/03-settings-json/docs/en.md).

## Challenge

Make `apply_patch` return a unified diff of the staged changes without writing anything (Python's `difflib.unified_diff` helps). Add a `dry_run=True` flag. Assert that a dry run leaves every file unchanged.

## Sources

Claude Code docs, "Tools reference", sections "Edit tool behavior" and "Write tool behavior" (code.claude.com/docs/en/tools-reference).

Next: [Search](../../03-search/docs/en.md)
