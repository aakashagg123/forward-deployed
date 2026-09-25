# Applying & validating patches

> **Motto** — A patch is a reviewable unit of change — apply it atomically or not at all.

*Part of Phase 06 — File & Code Operations.*

## The Problem

Single edits (lesson 02) work well for one spot, but a coherent change often spans several
hunks or files. Bundling them as a **patch** makes the change reviewable as a unit — the
review agent in Phase 10/15 sees a diff. A patch also applies **atomically**: if any hunk
fails to apply cleanly, the tool rejects the whole patch rather than leaving the tree
half-edited.

## The Concept

<style>
.dgm-pat{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pat-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-pat h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-pat-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-pat-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-pat-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-pat-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-pat-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-pat-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-pat-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-pat-b.accent h6{color:#0d5c0d}
.dgm-pat-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-pat-b.blue h6{color:#0550ae}
.dgm-pat-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-pat-b.green h6{color:#1a614f}
.dgm-pat-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-pat-b.red h6{color:#82061e}
.dgm-pat-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-pat-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-pat{padding:20px 16px 18px}.dgm-pat-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-pat">
  <span class="dgm-pat-chip">All hunks match, or none apply</span>
  <h4>A multi-file patch is one atomic operation, not a best-effort pass</h4>
  <p class="dgm-pat-sub">Partial application would leave the tree in a state nobody asked for.</p>
  <div class="dgm-pat-q">Patch: [(path, old, new), …] — all hunks match?</div>
  <div class="dgm-pat-branches">
    <div class="dgm-pat-b red">
      <h6>No</h6>
      <p>Reject all — tree untouched</p>
    </div>
    <div class="dgm-pat-b green">
      <h6>Yes</h6>
      <p>Apply all, write</p>
    </div>
  </div>
</div>


Validate every hunk first, and only write if all hunks pass. This all-or-nothing rule
avoids partial, inconsistent edits.

## Build It

`code/patch.py` — an atomic multi-hunk patch applier:

```python
def apply_patch(hunks, read, write):
    """hunks: [(path, old, new)]. read(path)->str, write(path,str). Atomic."""
    staged = {}
    for path, old, new in hunks:
        text = staged.get(path, read(path))
        if text.count(old) != 1:
            return f"reject: hunk for {path} matches {text.count(old)}x (need exactly 1)"
        staged[path] = text.replace(old, new)
    for path, text in staged.items():        # only reached if every hunk validated
        write(path, text)
    return f"applied {len(hunks)} hunk(s) across {len(staged)} file(s)"
```

```python
files = {"a.py": "x = 1\n", "b.py": "y = 2\n"}
res = apply_patch(
    [("a.py", "x = 1", "x = 10"), ("b.py", "y = 2", "y = 20")],
    read=lambda p: files[p], write=lambda p, t: files.__setitem__(p, t))
print(res, files)         # applied 2 hunks; both files updated
```

If the second hunk had failed validation, the first would *not* have been written — the
tree stays consistent.

## Use It

When Claude Code / Codex make a multi-file change, each edit is an exact-string replacement
(lesson 02). The *set* of edits is what you review as a diff before it lands, and it's also
what the review gate scores (Phase 10/15). The atomic-validate-then-apply discipline in this
lesson keeps a multi-file change from landing half-done.

## Ship It

[`code/patch.py`](../../06-patches/code/patch.py) — an atomic multi-hunk patch applier.

## Check Yourself

**Q1.** Why apply a multi-hunk patch atomically?

- A) speed
- B) so a failing hunk can't leave the tree half-edited and inconsistent
- C) the OS requires it
- D) no reason

<details><summary>Answer</summary>B — all-or-nothing keeps the tree consistent.</details>

**Q2.** Why is a patch a good review unit?

- A) it's short
- B) it's a diff — the reviewer (Phase 10/15) judges the whole change at once
- C) it's binary
- D) no reason

<details><summary>Answer</summary>B — a diff is the reviewable artifact.</details>

**Challenge.** Make the applier produce a unified-diff string for the staged changes (so a
human/reviewer can see exactly what would change before you commit).

## Related

- Builds on: [Edit tool](../../02-edit-tool/docs/en.md)
- Next: [Use It: tree-sitter for structural edits](../../07-tree-sitter/docs/en.md)
- Reviewed by: Phase 10/15
- [Roadmap](../../../../ROADMAP.md)
