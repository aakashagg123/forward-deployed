# API keys, secrets & env hygiene

> **Motto** — A secret in code is a secret already leaked.

*Part of Phase 00 — Setup & Tooling.*

## The Problem

The harness runs an agent that reads and writes files. Two failure modes follow
immediately. A key hardcoded in source gets committed to git forever. An agent might
"helpfully" edit `.env` and print it into a transcript or log. Both are how credentials
escape. Hygiene here is structural, not a reminder you hope everyone remembers.

## The Concept

Three rules:

1. **Secrets live in the environment** (`ANTHROPIC_API_KEY`), loaded from a `.env` that
   is **git-ignored** — never committed.
2. **The agent may not touch `.env`** — enforce with a pre-edit hook that blocks it.
3. **Redact on the way out** — never log raw key values (Phase 17 generalizes this).

<style>
.dgm-sae{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-sae-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-sae h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-sae-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-sae-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-sae-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-sae-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-sae-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-sae-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-sae-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-sae-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-sae-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-sae{padding:20px 16px 18px}.dgm-sae-row{flex-direction:column}}
.dgm-sae-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-sae-branches{display:grid;grid-template-columns:repeat(1,1fr);gap:10px}
.dgm-sae-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-sae-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-sae-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-sae-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-sae-b.accent h6{color:#0d5c0d}
.dgm-sae-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-sae-b.blue h6{color:#0550ae}
.dgm-sae-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-sae-b.green h6{color:#1a614f}
.dgm-sae-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-sae-b.red h6{color:#82061e}
.dgm-sae-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-sae-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-sae{padding:20px 16px 18px}.dgm-sae-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-sae">
  <span class="dgm-sae-chip">Secrets never reach the model</span>
  <h4>The key flows from .env to the process, never through the agent</h4>
  <p class="dgm-sae-sub">An agent attempt to edit .env is caught by a hook, not by convention.</p>
  <div class="dgm-sae-row">
    <div class="dgm-sae-n neutral">.env (gitignored)</div>
    <span class="dgm-sae-arr">→</span>
    <div class="dgm-sae-n accent">Process env</div>
    <span class="dgm-sae-arr">→</span>
    <div class="dgm-sae-n blue">Harness reads ANTHROPIC_API_KEY</div>
  </div>
  <div class="dgm-sae-branches">
    <div class="dgm-sae-b red">
      <h6>Agent edit attempt on .env</h6>
      <p>PreToolUse hook → BLOCK</p>
    </div>
  </div>
</div>


## Build It

A `PreToolUse` hook that blocks any edit/write targeting `.env`. `outputs/block-env-edit.sh`
reads the tool-call JSON on stdin and exits non-zero to deny:

```bash
#!/usr/bin/env bash
# PreToolUse hook: deny any Edit/Write whose path touches a .env file.
input="$(cat)"
path="$(printf '%s' "$input" | grep -oE '"(file_path|path)"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed -E 's/.*"([^"]*)"$/\1/')"
case "$path" in
  *.env|*.env.*|*/.env) echo "BLOCKED: edits to .env are not allowed" >&2; exit 2 ;;
  *) exit 0 ;;
esac
```

Exit code 2 tells the harness to deny the call and surface the message. The agent sees
"BLOCKED" and moves on. The secret file is never writable by the model.

## Use It

In Claude Code this is wired in `.claude/settings.json` under `hooks.PreToolUse` (Phase 8
covers the hook system in depth). The same idea — a deterministic gate around a dangerous
action — recurs throughout the permissions phase.

## Ship It

[`outputs/block-env-edit.sh`](../../03-secrets-and-env/outputs/block-env-edit.sh) — a
drop-in PreToolUse hook that protects `.env` files.

## Check Yourself

**Q1.** Why block `.env` edits with a hook instead of a prompt instruction?

- A) hooks are faster
- B) a deterministic gate can't be talked around; an instruction can be ignored
- C) prompts cost tokens
- D) no reason

<details><summary>Answer</summary>B — structural enforcement beats hoping the model
complies.</details>

**Q2.** What makes a hardcoded key unrecoverable once pushed?

- A) nothing, just delete it
- B) git history retains it even after deletion, so it must be rotated
- C) GitHub auto-redacts it
- D) it expires

<details><summary>Answer</summary>B — committed secrets live in history; rotate the key,
don't just delete the line.</details>

**Challenge.** Extend the hook to also block reads of `.env` (not just edits), and to
allow a `.env.example` template through.

## Related

- Builds on: [Dev environment](../../01-dev-environment/docs/en.md)
- Next: [A REPL you can talk to](../../04-repl/docs/en.md)
- Deepens in: Phase 8 — Permissions, Phase 17 — Security
