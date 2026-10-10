# Plan Mode

> **Motto** — For risky or unclear work, the agent proposes a plan and waits, and it stays read-only until you say go.

*Part of Phase 07 — Planning and Subagents.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

An agent that starts editing at once on a big or vague task builds the wrong thing fast. You find out after the diff is large. Then you pay twice: once to build it and once to undo it.

Asking nicely ("plan first, do not edit yet") is weak. The model can forget or decide the plan is obvious. You want the harness to enforce the pause.

## The Concept

<style>
.dgm-plm{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-plm-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-plm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-plm-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-plm-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-plm-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-plm-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-plm-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-plm-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-plm-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-plm-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-plm-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-plm{padding:20px 16px 18px}.dgm-plm-row{flex-direction:column}}
.dgm-plm-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-plm-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-plm-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-plm-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-plm-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-plm-b.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline)}
.dgm-plm-b.accent h6{color:var(--color-text-success)}
.dgm-plm-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-plm-b.blue h6{color:var(--color-text-info)}
.dgm-plm-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-plm-b.green h6{color:var(--color-text-success)}
.dgm-plm-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-plm-b.red h6{color:var(--color-text-danger)}
.dgm-plm-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-plm-b.neutral h6{color:var(--color-text)}
@media (max-width:640px){.dgm-plm{padding:20px 16px 18px}.dgm-plm-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-plm">
  <span class="dgm-plm-chip">Read-only, until a human says go</span>
  <h4>Plan mode can analyze and propose — it cannot act until the plan is approved</h4>
  <p class="dgm-plm-sub">That read-only boundary is what makes it safe to let the agent plan autonomously.</p>
  <div class="dgm-plm-row">
    <div class="dgm-plm-n neutral">Task</div>
    <span class="dgm-plm-arr">→</span>
    <div class="dgm-plm-n accent">PLAN MODE: read-only — analyze + propose</div>
  </div>
  <div class="dgm-plm-q">Human approves plan?</div>
  <div class="dgm-plm-branches">
    <div class="dgm-plm-b red">
      <h6>No</h6>
      <p>Revise / redirect</p>
    </div>
    <div class="dgm-plm-b green">
      <h6>Yes</h6>
      <p>Exit plan mode → act</p>
    </div>
  </div>
</div>


**Plan mode** is a permission state. Reads are allowed. In this model, edits and risky commands are denied. In Claude Code, edits are blocked, and commands outside the read-only set prompt you or go to the auto-mode classifier. The exception is an interactive terminal session where bypass permissions is available: there, plan blocks are not enforced. The agent can explore the codebase and write a plan. It cannot change anything.

A human then makes a decision. Reject, and the agent stays read-only and revises. Approve, and the state changes to acting. The permission gate from [Phase 06](../../../06-permissions-and-security/01-permission-gate/docs/en.md) does the enforcing, so plan mode is a setting and not a promise.

## Build It

`code/plan_mode.py` is a small model of the idea. It is not Claude Code's code. It has three states: `planning`, `awaiting_approval` and `acting`. The gate decides one tool call:

```python
    def gate(self, tool, command=None):
        """Return 'allow' or 'deny: <reason>' for one tool call."""
        if self.state == "acting":
            return "allow"
        if tool in READ_ONLY_TOOLS:
            return "allow"
        if tool == "bash" and command in READ_ONLY_COMMANDS:
            return "allow"                # exploring with a read-only command is fine
        return f"deny: '{tool}' is blocked until a plan is approved"
```

Note the third rule. A plan needs exploration, and exploration needs `git status` or `ls`. So read-only shell commands pass and everything else is denied.

The `decide` method moves the state. Approval sets `acting`. Rejection returns to `planning` so the agent revises. The asserts check that proposing a plan does not unlock edits, that a rejected plan leaves the agent read-only, and that only approval allows an edit.

## Use It

Plan mode is one of the Claude Code permission modes (`default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`). You can enter it three ways:

- Press `Shift+Tab` to cycle modes.
- Prefix one prompt with `/plan`.
- Start a session with `claude --permission-mode plan`.

In plan mode Claude reads files, runs shell commands to explore, and writes a plan. It does not edit your source. When the plan is ready, you pick one of the approve options or choose to keep planning with feedback. Approving exits plan mode and switches the session to the mode that option names, so editing starts.

Two details matter. Plan mode keeps its blocks in non-interactive runs (`-p`) and in Agent SDK sessions. But in an interactive terminal session where bypass permissions is available, Claude Code does not enforce those blocks. Claude is still told to plan without editing, but an edit it attempts runs anyway. Do not rely on plan mode as a guard in that setup.

To make plan mode the default for a project, set `defaultMode` to `plan` in `.claude/settings.json`. A subagent definition can also set `permissionMode: plan`.

## Challenge

Connect `PlanMode` to a permission gate. Write a gate with three decisions (allow, ask, deny) and a `plan` mode in which every mutating tool returns `deny`. Show with an assert that switching the mode to `acting` changes only the mutating decisions, and that a deny rule still wins in both modes.

## Sources

Claude Code docs, "Choose a permission mode" (code.claude.com/docs).

Next: [Contract, waves and isolation](../../03-contract-waves-and-isolation/docs/en.md)
