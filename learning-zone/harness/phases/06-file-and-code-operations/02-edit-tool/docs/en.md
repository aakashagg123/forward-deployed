# Exact-string edit & why diffs beat rewrites

> **Motto** — Edit by replacing a unique exact string, not by regenerating the whole file.

*Part of Phase 06 — File & Code Operations.*

## The Problem

The tempting way to "edit" with an LLM is to have it output the entire new file. That
approach is slow and token-hungry. It is also dangerous: the model can silently drop a
function or reformat code it shouldn't touch. The robust primitive is an **exact-string
replacement**: find one unique occurrence of `old` and replace it with `new`. The change
stays surgical and verifiable, and everything else stays untouched by construction.

## The Concept

<style>
.dgm-edt{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-edt-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-edt h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-edt-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-edt-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-edt-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-edt-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-edt-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-edt-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-edt-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-edt-b.accent h6{color:#0d5c0d}
.dgm-edt-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-edt-b.blue h6{color:#0550ae}
.dgm-edt-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-edt-b.green h6{color:#1a614f}
.dgm-edt-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-edt-b.red h6{color:#82061e}
.dgm-edt-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-edt-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-edt{padding:20px 16px 18px}.dgm-edt-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-edt">
  <span class="dgm-edt-chip">Exactly-once match, or refuse</span>
  <h4>Zero matches and multiple matches both fail loudly, on purpose</h4>
  <p class="dgm-edt-sub">An ambiguous edit is worse than a rejected one — the fix is more surrounding context.</p>
  <div class="dgm-edt-q">edit(path, old, new) — old occurs exactly once?</div>
  <div class="dgm-edt-branches">
    <div class="dgm-edt-b red">
      <h6>No (0)</h6>
      <p>Error: not found</p>
    </div>
    <div class="dgm-edt-b red">
      <h6>No (&gt;1)</h6>
      <p>Error: ambiguous — add context</p>
    </div>
    <div class="dgm-edt-b green">
      <h6>Yes</h6>
      <p>Replace, write</p>
    </div>
  </div>
</div>


Uniqueness is the safety property. If `old` matches twice, the tool refuses and asks for
more surrounding context, so it never edits the wrong spot.

## Build It

`code/edit_tool.py` — exact replace with a uniqueness guard:

```python
def edit(path, old, new):
    with open(path) as f:
        text = f.read()
    count = text.count(old)
    if count == 0:
        return "error: old_string not found"
    if count > 1:
        return f"error: old_string is ambiguous ({count} matches) — add surrounding context"
    with open(path, "w") as f:
        f.write(text.replace(old, new))
    return "ok: 1 replacement"
```

```python
import tempfile, os
p = tempfile.mktemp(); open(p, "w").write("def add(a, b):\n    return a + b\n")
print(edit(p, "return a + b", "return a + b  # sum"))   # ok
print(edit(p, "nope", "x"))                              # not found
os.remove(p)
```

A single, unambiguous replacement is auditable (it's a diff) and can't clobber unrelated
code.

## Use It

This is the **Edit** tool in Claude Code / Codex. It requires `old_string` to match exactly
and uniquely, and it errors when the match is ambiguous. That's why the agent reads first
(lesson 01): reading grabs enough surrounding context for a unique match. `replace_all` is
the opt-in for intentional multi-site edits.

## Ship It

[`code/edit_tool.py`](../../02-edit-tool/code/edit_tool.py) — an exact-string edit tool with
a uniqueness guard.

## Check Yourself

**Q1.** Why replace an exact string instead of rewriting the whole file?

- A) it's prettier
- B) surgical edits can't silently drop or reformat unrelated code, and they're auditable
- C) the API requires it
- D) no reason

<details><summary>Answer</summary>B — precise, verifiable, safe.</details>

**Q2.** `old_string` matches twice. The tool should…

- A) edit both silently
- B) refuse and ask for more surrounding context (unless replace_all is set)
- C) edit the first
- D) crash

<details><summary>Answer</summary>B — ambiguity → refuse, to avoid wrong-spot edits.</details>

**Challenge.** Add `replace_all=True` support and return the replacement count, mirroring
the real Edit tool.

## Related

- Builds on: [Read tool](../../01-read-tool/docs/en.md)
- Next: [Write & overwrite safety](../../03-write-safety/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
