# Permission modes (ask / allow / deny)

> **Motto** — Every tool call passes through a gate that says allow, ask, or deny.

*Part of Phase 08 — Permissions & Safety Gating.*

## The Problem

An agent that runs every tool call unchecked is a liability. An agent that asks before
*every* call is unusable. The fix is **modes**: a per-call decision to allow automatically,
ask the human, or deny outright. Rules drive the decision, so routine reads run free while
destructive actions stop for confirmation. This gate is the single most important safety
component in the harness.

## The Concept

<style>
.dgm-pm2{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pm2-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-pm2 h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-pm2-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-pm2-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-pm2-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-pm2-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-pm2-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-pm2-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-pm2-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-pm2-b.accent h6{color:#0d5c0d}
.dgm-pm2-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-pm2-b.blue h6{color:#0550ae}
.dgm-pm2-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-pm2-b.green h6{color:#1a614f}
.dgm-pm2-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-pm2-b.red h6{color:#82061e}
.dgm-pm2-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-pm2-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-pm2{padding:20px 16px 18px}.dgm-pm2-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-pm2">
  <span class="dgm-pm2-chip">Every call passes through one gate</span>
  <h4>Allow, ask, or deny — the gate is the single point every tool call must cross</h4>
  <p class="dgm-pm2-sub">Later lessons are all about how the gate makes that allow/ask/deny decision.</p>
  <div class="dgm-pm2-q">Tool call → permission gate</div>
  <div class="dgm-pm2-branches">
    <div class="dgm-pm2-b green">
      <h6>Allow</h6>
      <p>Run</p>
    </div>
    <div class="dgm-pm2-b accent">
      <h6>Ask</h6>
      <p>Confirm with human</p>
    </div>
    <div class="dgm-pm2-b red">
      <h6>Deny</h6>
      <p>Refuse</p>
    </div>
  </div>
</div>


The gate uses a default mode plus rules. For example: default to ask, allowlist reads to
allow, and denylist dangerous patterns to deny.

## Build It

`code/permission_modes.py` — a gate with a default and rule overrides:

```python
ALLOW, ASK, DENY = "allow", "ask", "deny"

class PermissionGate:
    def __init__(self, default=ASK, rules=None):
        self.default = default
        self.rules = rules or []          # list of (predicate, mode)

    def decide(self, tool, args):
        for predicate, mode in self.rules:
            if predicate(tool, args):
                return mode
        return self.default

    def run(self, tool, args, execute, confirm):
        mode = self.decide(tool, args)
        if mode == DENY:
            return "denied by policy"
        if mode == ASK and not confirm(tool, args):
            return "denied by user"
        return execute(tool, args)
```

```python
gate = PermissionGate(default=ASK, rules=[
    (lambda t, a: t in ("read", "grep", "glob"), ALLOW),    # reads: auto
    (lambda t, a: t == "bash" and "rm -rf" in a.get("cmd", ""), DENY),
])
print(gate.decide("read", {}))                       # allow
print(gate.decide("bash", {"cmd": "rm -rf /"}))      # deny
print(gate.decide("write", {}))                      # ask (default)
```

The gate centralizes the allow/ask/deny decision. This keeps the decision consistent and
auditable, instead of scattering `if` checks through the code.

## Use It

This is Claude Code's **permission modes** (default, acceptEdits, plan, and the
`--dangerously-skip-permissions` escape hatch) and Codex's approval settings. Reads and
edits can be auto-approved, while shell or network actions prompt. Tune the rules so the
agent flows on safe work and stops on risky work — never the reverse.

## Ship It

[`code/permission_modes.py`](../../01-permission-modes/code/permission_modes.py) — an
allow/ask/deny permission gate.

## Check Yourself

**Q1.** Why not ask before every tool call?

- A) it's unsafe
- B) it's unusable; modes let safe calls flow while risky ones stop for confirmation
- C) the API forbids it
- D) no reason

<details><summary>Answer</summary>B — modes balance safety and usability.</details>

**Q2.** A good default for an untrusted/auto context is…

- A) allow everything
- B) default-ask (or deny), with reads allowlisted to allow
- C) deny everything
- D) random

<details><summary>Answer</summary>B — conservative default, widen deliberately.</details>

**Challenge.** Add a `plan` mode that denies all *mutating* tools (write/edit/bash) but
allows reads. This is the read-only "propose first" mode from Phase 11.

## Related

- Builds on: Phase 3 — [Tool registry](../../../03-tool-engineering/08-tool-registry/docs/en.md)
- Next: [Allowlists, denylists & pattern matching](../../02-allow-deny/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
