# Memory files

> **Motto** — A memory file is a short, stable table of contents, not an encyclopedia.

*Part of Phase 04 — Prompts and instructions.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

`CLAUDE.md` and `AGENTS.md` are how you put durable, project-specific instructions into every session. The failure is easy to predict. The file grows into a 2,000-line manual. The agent follows it less. You stop updating it. It also uses budget on every turn, as [Context budget](../../../03-context-and-memory/01-context-budget/docs/en.md) shows.

The Claude Code docs give the reason: the file is context, not enforced configuration. Longer files use more context and lower adherence. A good memory file is short. It holds the few rules that apply to every task and points to detail elsewhere.

## The Concept

<style>
.dgm-mf{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-mf-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-mf h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-mf-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-mf-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-mf-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-mf-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-mf-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-mf-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-mf-b.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline)}
.dgm-mf-b.accent h6{color:var(--color-text-success)}
.dgm-mf-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-mf-b.blue h6{color:var(--color-text-info)}
.dgm-mf-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-mf-b.green h6{color:var(--color-text-success)}
.dgm-mf-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-mf-b.red h6{color:var(--color-text-danger)}
.dgm-mf-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-mf-b.neutral h6{color:var(--color-text)}
@media (max-width:640px){.dgm-mf{padding:20px 16px 18px}.dgm-mf-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-mf">
  <span class="dgm-mf-chip">A short file, read every session</span>
  <h4>CLAUDE.md stays under 100 lines by pointing, not explaining</h4>
  <p class="dgm-mf-sub">Rules load every time; the pointed-to docs load only when the task needs them.</p>
  <div class="dgm-mf-q">CLAUDE.md / AGENTS.md (~100 lines)</div>
  <div class="dgm-mf-branches">
    <div class="dgm-mf-b accent">
      <h6>The few rules that apply to every task</h6>
      <p>Agent reads once, every session</p>
    </div>
    <div class="dgm-mf-b blue">
      <h6>Pointers → docs/, pattern files</h6>
      <p>Agent loads detail on demand</p>
    </div>
  </div>
</div>


Put in the file:

- **Commands** the agent will need: test, lint, run.
- **Conventions** that are non-obvious and recurring.
- **Pointers** to deeper docs, not the docs themselves.

Leave out anything volatile, anything the system prompt already says, and anything you would not re-read. Write instructions you can check. "Use 2-space indentation" is checkable. "Format code properly" is not.

When the agent repeats a mistake, do not add a paragraph. Fix the harness: add a lint rule or a hook. Add to the file only when a fact is true in every session.

The docs advise a target under 200 lines per file. Under 100 is this course's rule of thumb.

## Build It

`outputs/CLAUDE.md` is a real lean example: 17 lines of content for a small service. `code/memory_lint.py` checks it, and it models how Claude Code loads these files.

```python
def lint(text, files=None, root=None):
    problems = []
    full = expand(text, files or {})
    lines = [line for line in full.splitlines() if line.strip()]
    if len(lines) > MAX_LINES:
        problems.append(f"{len(lines)} lines after imports; keep under {MAX_LINES}")
    for phrase in VAGUE:
        if phrase in full.lower():
            problems.append(f"vague instruction: {phrase!r}")
    if re.search(r"\b20\d\d-\d\d-\d\d\b", full):
        problems.append("date in a memory file goes stale")
    for ref in re.findall(r"`((?:docs|src)/[\w./-]+)`", full):   # a pointer to a missing file is a trap
        if root and not os.path.exists(os.path.join(root, ref)):
            problems.append(f"pointer to a missing file: {ref}")
    return problems
```

The lint measures size after expanding `@imports`. That is the point: an import organizes a file but does not make it cheaper, because imported files also load at launch. It also flags vague lines, dates, and pointers to files that do not exist.

The asserts prove the example passes with real `docs/` files and fails when they are missing. They also prove that HTML comments are stripped before the model sees the text, that a 250-line file behind an import still counts, and that the closest file is read last.

Two more functions model the load rules. `which_files` encodes the `AGENTS.md` table. `load_order` concatenates layers from broad to specific.

## Use It

Put `CLAUDE.md` at the repo root, or in `.claude/CLAUDE.md`. Claude Code reads files from your working directory and every directory above it. It orders them from the filesystem root down, so instructions closest to you come last. Files in subdirectories load on demand, when Claude reads files there. Run `/init` to generate a starter file. Run `/context` and check **Memory files** to confirm a file loaded.

By default, Claude Code reads `AGENTS.md` only when no `CLAUDE.md` is in your working directory or above it. Claude Code v2.1.277 or later (v2.1.281 on Bedrock or with telemetry off) can read `AGENTS.md` directly in that case. A `CLAUDE.local.md` also counts as a `CLAUDE.md` for this check. To share one file with other tools on any version, write `@AGENTS.md` in your `CLAUDE.md`.

Block-level HTML comments are stripped before injection, so leave maintainer notes in them. For rules that matter only for some paths, use `.claude/rules/` with a `paths` frontmatter field. Those load when Claude touches matching files. For a task procedure, use a skill.

`CLAUDE.md` is guidance. To block an action regardless of what Claude decides, use a hook: [Hooks](../../../06-permissions-and-security/02-hooks/docs/en.md).

## Challenge

Run `memory_lint.py` logic on the real `CLAUDE.md` of a repo you own. Fix every problem it reports. Then cut the file to under 100 lines without losing a command.

## Sources

Claude Code docs, "How Claude remembers your project" (code.claude.com/docs/en/memory).

Next: [Output contracts](../../03-output-contracts/docs/en.md)
