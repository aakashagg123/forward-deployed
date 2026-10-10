# Search: Glob by Name, Grep by Content

> **Motto** — Find the right 20 lines in a million by searching, not by reading everything.

*Part of Phase 05 — Files and Shell.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

"Where is `parse_config` defined, and who calls it?" The agent cannot read the whole repo to find out. That is slow and it breaks the context budget.

The agent needs two search tools. One finds files by **name** ("every `*.py` under `src`"). One finds lines by **content** ("every line that matches this regex"). Both must return short, citable results, and both must be capped.

## The Concept

<style>
.dgm-grp{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-grp-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-grp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-grp-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-grp-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-grp-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-grp-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-grp-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-grp-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-grp-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-grp-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-grp-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
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


Glob returns paths. Grep returns `path:line: text`. The agent then reads the promising hit and edits it. The core file loop is search, read, edit.

Two details decide the quality of a search tool. Results need an order and a cap. Glob sorts newest first, because recently changed files are usually the relevant ones. Both tools skip vendored and VCS folders such as `.git` and `node_modules`, or the output fills with noise. A truncation line tells the model to narrow the query.

## Build It

`code/search_tools.py` has `find_files` (glob) and `grep` in one file. Grep has three output modes: full lines, file names only, or counts. Context lines use `-` after the file name and match lines use `:`, the same marks as `grep -n -C`.

```python
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}


def _files(root, pattern):
    root = Path(root)
    for p in root.glob(pattern):
        if p.is_file() and not (set(p.relative_to(root).parts) & SKIP_DIRS):
            yield p


def find_files(pattern, root=".", limit=100):
    """Glob by name. Newest first, capped, so recent files surface."""
    paths = sorted(_files(root, pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    out = [str(p.relative_to(root)) for p in paths[:limit]]
    if len(paths) > limit:
        out.append(f"[truncated: {len(paths)} files match, showing {limit}; narrow the pattern]")
    return out


def grep(pattern, root=".", glob="**/*", context=0, mode="content", limit=50):
    """Regex search by content. mode: content | files_with_matches | count."""
    rx = re.compile(pattern)
    hits, files, counts = [], [], {}
    for p in sorted(_files(root, glob)):
        try:
            lines = p.read_text().splitlines()
        except (UnicodeDecodeError, PermissionError):
            continue                                   # binary or unreadable
        name = str(p.relative_to(root))
        for i, line in enumerate(lines):
            if not rx.search(line):
                continue
            counts[name] = counts.get(name, 0) + 1
            for j in range(max(0, i - context), min(len(lines), i + context + 1)):
                mark = ":" if j == i else "-"
                hits.append(f"{name}{mark}{j + 1}: {lines[j]}")
        if name in counts:
            files.append(name)
    if mode == "files_with_matches":
        return files
    if mode == "count":
        return [f"{n}:{counts[n]}" for n in files]
    if len(hits) > limit:
        return hits[:limit] + [f"[truncated: {len(hits)} lines, showing {limit}]"]
    return hits
```

There is no index to build or keep in sync. The price is a scan on every call. That is fine for a repo-sized tree. A huge tree needs a real indexer such as ripgrep, or the repo map in [Repo Map](../../../08-extending-mcp-skills-retrieval/04-repo-map/docs/en.md).

The asserts build a small tree with fixed modification times. They check the newest-first order, the skipped folders, the context marks, all three modes, and both truncation notes. Run `python3 code/search_tools.py`.

## Use It

Claude Code has **Glob** and **Grep** tools. Glob matches patterns such as `**/*.js`. It sorts by modification time and caps results at 100 files. It does not respect `.gitignore` by default.

Grep is built on ripgrep, so it uses ripgrep regex syntax. Braces need escaping: find `interface{}` with `interface\{\}`. It has three modes: `files_with_matches` (the default), `content`, and `count`. It respects `.gitignore`. It can filter by `glob` or by file `type`, and it can match across lines with `multiline: true`.

The docs say Glob and Grep are absent by default on macOS, Linux and WSL, with documented ways to bring them back. Check your install before you write a rule for them.

`Read(path)` deny rules are applied to Grep and Glob on a best-effort basis. A `Glob(...)` rule on its own is never consulted. The [Settings.json](../../../06-permissions-and-security/03-settings-json/docs/en.md) lesson explains why.

## Challenge

Add a `.gitignore` reader to `find_files`, so it skips ignored paths the way Grep does. Assert that a file listed in `.gitignore` disappears from the results. Then explain why Claude Code's Glob and Grep differ on this point.

## Sources

Claude Code docs, "Tools reference", sections "Glob tool behavior" and "Grep tool behavior" (code.claude.com/docs/en/tools-reference).

Next: [Bash and Timeouts](../../04-bash-and-timeouts/docs/en.md)
