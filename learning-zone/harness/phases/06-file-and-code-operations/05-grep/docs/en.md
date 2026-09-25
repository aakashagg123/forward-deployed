# Grep / ripgrep-style content search

> **Motto** — Find the right 20 lines in a million by searching content, not by reading everything.

*Part of Phase 06 — File & Code Operations.*

## The Problem

"Where is `parse_config` defined and used?" The agent can't read the whole repo to find
out — that's slow and blows the budget. It needs content search: a regex over files
returning `path:line: matched text`, optionally with surrounding context. This is how an
agent locates code before reading and editing it.

## The Concept

<style>
.dgm-grp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-grp-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-grp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-grp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-grp-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-grp-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-grp-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-grp-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-grp-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-grp-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-grp-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-grp-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-grp{padding:20px 16px 18px}.dgm-grp-row{flex-direction:column}}
</style>
<div class="dgm-grp">
  <span class="dgm-grp-chip">A regex over a file filter, not a full index</span>
  <h4>Scan matching files, return path:line:match with context</h4>
  <p class="dgm-grp-sub">No index to build or keep in sync — the tradeoff is scan cost on every call.</p>
  <div class="dgm-grp-row">
    <div class="dgm-grp-n accent">Regex + file filter</div>
    <span class="dgm-grp-arr">→</span>
    <div class="dgm-grp-n blue">Scan matching files</div>
    <span class="dgm-grp-arr">→</span>
    <div class="dgm-grp-n green">path:line: match (+ context)</div>
  </div>
</div>


Grep returns *locations*. The agent then Reads the promising ones (lesson 01) and Edits
them (lesson 02). Search → read → edit is the core file-ops loop.

## Build It

`code/grep_tool.py` — regex search with line numbers and optional context, stdlib:

```python
import re
from pathlib import Path

def grep(pattern, root=".", glob="**/*", context=0):
    rx = re.compile(pattern)
    hits = []
    for p in Path(root).glob(glob):
        if not p.is_file():
            continue
        try:
            lines = p.read_text().splitlines()
        except (UnicodeDecodeError, PermissionError):
            continue
        for i, line in enumerate(lines):
            if rx.search(line):
                lo, hi = max(0, i - context), min(len(lines), i + context + 1)
                for j in range(lo, hi):
                    mark = ":" if j == i else "-"
                    hits.append(f"{p}{mark}{j+1}: {lines[j]}")
    return hits
```

```python
import tempfile, os
d = tempfile.mkdtemp()
open(os.path.join(d, "x.py"), "w").write("def parse_config():\n    return {}\n")
print(grep(r"parse_config", root=d))   # ['.../x.py:1: def parse_config():']
```

The `path:line` format is what the agent cites and feeds straight into the read tool.

## Use It

This is the **Grep** tool in Claude Code / Codex, built on ripgrep. It does regex content
search with file-type and glob filters and context flags, and it returns matches the agent
uses to navigate. Glob (lesson 04) finds files by name, and Grep finds them by content. Read
loads the hit, and Edit changes it.

## Ship It

[`code/grep_tool.py`](../../05-grep/code/grep_tool.py) — a regex content-search tool with
line numbers and context.

## Check Yourself

**Q1.** What does grep return that the agent acts on next?

- A) the whole file
- B) `path:line` locations to Read and Edit
- C) a summary
- D) nothing

<details><summary>Answer</summary>B — locations drive the read→edit step.</details>

**Q2.** Search → ___ → edit is the core file-ops loop.

- A) compile
- B) read
- C) delete
- D) commit

<details><summary>Answer</summary>B — grep to locate, read to load, edit to change.</details>

**Challenge.** Add an `output_mode="files_with_matches"` that returns just the unique file
paths, like ripgrep's `-l`.

## Related

- Builds on: [Glob](../../04-glob/docs/en.md), [Read tool](../../01-read-tool/docs/en.md)
- Next: [Applying & validating patches](../../06-patches/docs/en.md)
- Deepens in: Phase 13 — Retrieval
- [Roadmap](../../../../ROADMAP.md)
