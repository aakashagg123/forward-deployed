# Use it: settings.json & the hooks system

> **Motto** — Everything you built this phase is configuration — declare it in settings.json.

*Part of Phase 08 — Permissions & Safety Gating. Completes the phase.*

## The Problem

You've built permission modes, allow/deny lists, hooks, approvals, and capability scoping
from scratch. In Claude Code / Codex you don't re-implement these — you **declare** them.
The artifact that ties the phase together is a real `settings.json` (Claude Code) that
wires up permission rules and hooks. The safety layer becomes version-controlled config,
not code you maintain.

## The Concept

<style>
.dgm-sj{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-sj-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-sj h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-sj-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-sj-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-sj-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-sj-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-sj-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-sj-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-sj-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-sj-b.accent h6{color:#0d5c0d}
.dgm-sj-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-sj-b.blue h6{color:#0550ae}
.dgm-sj-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-sj-b.green h6{color:#1a614f}
.dgm-sj-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-sj-b.red h6{color:#82061e}
.dgm-sj-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-sj-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-sj{padding:20px 16px 18px}.dgm-sj-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-sj">
  <span class="dgm-sj-chip">One file, two mechanisms</span>
  <h4>permissions.* feeds the gate, hooks.* feeds the hook points</h4>
  <p class="dgm-sj-sub">settings.json is the single source both the gate and the hooks read from.</p>
  <div class="dgm-sj-q">settings.json</div>
  <div class="dgm-sj-branches">
    <div class="dgm-sj-b accent">
      <h6>permissions.allow / permissions.deny</h6>
      <p>→ the gate (lessons 01–02)</p>
    </div>
    <div class="dgm-sj-b blue">
      <h6>hooks.PreToolUse / PostToolUse</h6>
      <p>→ the hooks (lesson 03)</p>
    </div>
  </div>
</div>


`permissions` encodes the allow/deny lists. `hooks` wires the deterministic pre/post
scripts — the `.env` guard, the linter, the egress guard.

## Build It / Use It

The artifact is `outputs/settings.json` — a ready-to-use Claude Code config that wires this
phase's safety layer:

```json
{
  "permissions": {
    "allow": ["Read(*)", "Grep(*)", "Glob(*)", "Bash(git status:*)", "Bash(npm test:*)"],
    "deny":  ["Bash(rm -rf:*)", "Bash(git push:*)", "Edit(.env)", "Read(.env)"]
  },
  "hooks": {
    "PreToolUse": [
      {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": ".claude/hooks/block-env-edit.sh"}]},
      {"matcher": "Bash", "hooks": [{"type": "command", "command": ".claude/hooks/egress-guard.sh"}]}
    ],
    "PostToolUse": [
      {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": ".claude/hooks/lint.sh"}]}
    ]
  }
}
```

Drop it at `.claude/settings.json`, and put the hook scripts (from Phase 0/7) under
`.claude/hooks/`. The gate and hooks you built by hand are now enforced by the tool.
Codex uses its own config file for the equivalent approval and command rules.

## Use It

This is the practical payoff of the phase for a Claude Code / Codex user: a checked-in
config that makes your agent safe by default on this repo. Reads flow, dangerous commands
are denied, `.env` is protected, and the linter runs after every edit. Because it's a file,
it's reviewable and shareable with your team.

## Ship It

[`outputs/settings.json`](../../06-settings-json/outputs/settings.json) — a Claude Code
permissions + hooks configuration wiring the phase.

## Check Yourself

**Q1.** Where do the allow/deny lists and hooks live for Claude Code?

- A) in the prompt
- B) in `settings.json` (`permissions` and `hooks`)
- C) in the model
- D) nowhere

<details><summary>Answer</summary>B — declarative config, version-controlled.</details>

**Q2.** Why is config-as-a-file better than enforcing rules in a prompt?

- A) it's shorter
- B) it's deterministic, reviewable, shareable, and can't be talked around
- C) it's faster
- D) no reason

<details><summary>Answer</summary>B — config is enforcement; prompts are
persuasion.</details>

**Challenge.** Add a `permissions.deny` entry for writing anywhere outside the repo. Also
add a PostToolUse hook that runs the test suite after edits to `src/`.

## Related

- Builds on: the whole phase
- Phase complete → next: Phase 9 — [Memory & Persistence](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
