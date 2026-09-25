# Memory files (CLAUDE.md / AGENTS.md)

> **Motto** — A memory file is a short, stable table of contents — not an encyclopedia.

*Part of Phase 05 — Prompt & Instruction Architecture.*

## The Problem

`CLAUDE.md` (Claude Code) and `AGENTS.md` (Codex) are how *you* inject durable,
project-specific instructions into every turn. The failure mode is predictable: the file
grows into a 2,000-line manual, and the agent stops absorbing it. You stop maintaining it,
and it crowds the cached prefix. A good memory file is short, and it points to detail
rather than inlining it (the legibility principle from harness foundations).

## The Concept

<style>
.dgm-mf{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-mf-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-mf h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-mf-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-mf-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-mf-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-mf-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-mf-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-mf-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-mf-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-mf-b.accent h6{color:#0d5c0d}
.dgm-mf-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-mf-b.blue h6{color:#0550ae}
.dgm-mf-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-mf-b.green h6{color:#1a614f}
.dgm-mf-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-mf-b.red h6{color:#82061e}
.dgm-mf-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-mf-b.neutral h6{color:#1f2328}
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


Keep the root file ~100 lines: the handful of always-true rules plus links to deeper docs.
Detail lives one hop away, loaded only when needed.

## Build It

The artifact is a memory-file skill/template. `outputs/CLAUDE.md.template` gives a lean
structure: project one-liner, build/test commands, hard conventions, and a pointer list to
`docs/`. The same content works as `AGENTS.md` for Codex.

What belongs in it:
- **Commands** the agent will need (how to run tests, lint, build).
- **Conventions** that are non-obvious and recurring (import discipline, naming).
- **Pointers** to deeper docs, not the docs themselves.

What doesn't: anything volatile, anything restated from the system prompt, anything you
wouldn't re-read.

## Use It

Drop the file at the repo root as `CLAUDE.md` (Claude Code) or `AGENTS.md` (Codex), and
both tools load it automatically each session. When the agent repeats a mistake, resist
adding a paragraph. Instead, encode the fix as a lint rule or hook (Phase 8) and keep the
memory file lean — patch the harness, not the prompt.

## Ship It

[`outputs/CLAUDE.md.template`](../../02-memory-files/outputs/CLAUDE.md.template) — a lean
project-memory file that doubles as `AGENTS.md`.

## Check Yourself

**Q1.** How long should a root memory file be?

- A) as long as possible
- B) short (~100 lines) — a table of contents pointing to detail
- C) one line
- D) it doesn't matter

<details><summary>Answer</summary>B — lean and pointer-based; detail lives one hop
away.</details>

**Q2.** The agent keeps making the same mistake. Best fix?

- A) add a paragraph to CLAUDE.md
- B) encode the fix as a lint rule / hook and keep the memory file lean
- C) a bigger model
- D) repeat the rule three times

<details><summary>Answer</summary>B — patch the harness, not the prompt.</details>

**Challenge.** Write a `CLAUDE.md` for a real repo of yours in under 100 lines, with at
least three pointers to `docs/` instead of inlined detail.

## Related

- Builds on: [System prompt anatomy](../../01-system-prompt-anatomy/docs/en.md)
- Next: [Steering: tone, refusals & guardrail text](../../03-steering/docs/en.md)
- Deepens in: Phase 9 — Memory & Persistence
- [Roadmap](../../../../ROADMAP.md)
