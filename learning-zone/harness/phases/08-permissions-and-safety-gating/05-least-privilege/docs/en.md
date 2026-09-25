# Least privilege & capability scoping

> **Motto** — Give each agent the smallest set of tools its job needs — nothing more.

*Part of Phase 08 — Permissions & Safety Gating.*

## The Problem

A reviewer subagent doesn't need to write files or run shell commands. A doc-summarizer
doesn't need network access. Granting every agent every capability maximizes blast radius —
one confused or hijacked agent can do anything. Least privilege scopes each agent to a
capability set matched to its role. It's the security counterpart of the bounded-roles
context rule from Phase 10.

## The Concept

<style>
.dgm-lp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-lp-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-lp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-lp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-lp-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-lp-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-lp-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-lp-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-lp-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-lp-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-lp-b.accent h6{color:#0d5c0d}
.dgm-lp-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-lp-b.blue h6{color:#0550ae}
.dgm-lp-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-lp-b.green h6{color:#1a614f}
.dgm-lp-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-lp-b.red h6{color:#82061e}
.dgm-lp-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-lp-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-lp{padding:20px 16px 18px}.dgm-lp-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-lp">
  <span class="dgm-lp-chip">A role only sees its own capability set</span>
  <h4>Everything outside the role's capability set isn't just denied — it's invisible</h4>
  <p class="dgm-lp-sub">A tool the role can't reach never shows up as an option to try in the first place.</p>
  <div class="dgm-lp-q">Role → capability set</div>
  <div class="dgm-lp-branches">
    <div class="dgm-lp-b green">
      <h6>In the set</h6>
      <p>Only these tools are even visible / dispatchable</p>
    </div>
    <div class="dgm-lp-b red">
      <h6>Any other tool</h6>
      <p>Denied for this role</p>
    </div>
  </div>
</div>


Capabilities compose with the tool registry (Phase 3 L8). A role sees and can call only its
granted tools.

## Build It

`code/least_privilege.py` — role→capability scoping over a tool set:

```python
ROLE_CAPS = {
    "reader":   {"read", "grep", "glob"},
    "coder":    {"read", "grep", "glob", "edit", "write", "bash"},
    "reviewer": {"read", "grep", "glob"},            # never write/bash — judges the diff
    "summarizer": {"read"},
}

class ScopedAgent:
    def __init__(self, role, registry_dispatch):
        self.caps = ROLE_CAPS[role]
        self.dispatch = registry_dispatch

    def call(self, tool, args):
        if tool not in self.caps:
            return f"denied: role lacks capability '{tool}'"
        return self.dispatch(tool, args)
```

```python
dispatch = lambda t, a: f"ran {t}"
rev = ScopedAgent("reviewer", dispatch)
print(rev.call("read", {}))      # ran read
print(rev.call("write", {}))     # denied: role lacks capability 'write'
```

A reviewer literally cannot write or run shell — not by instruction, but by capability.
That makes it impossible for the reviewer to modify the code it's reviewing.

## Use It

In Claude Code / Codex this maps to per-subagent tool allowlists, where you specify which
tools a spawned subagent may use, and to the `permissions` scoping in `settings.json`. When
you define a custom subagent, grant it the minimum: an Explore agent gets read/search only,
and a fixer gets edit/bash. Least privilege plus bounded context (Phase 10) is the full
isolation story.

## Ship It

[`code/least_privilege.py`](../../05-least-privilege/code/least_privilege.py) — role→capability
scoping for agents.

## Check Yourself

**Q1.** Why give a reviewer agent no write/bash capability?

- A) speed
- B) so it can't modify what it's judging — impossible by capability, not by instruction
- C) cost
- D) no reason

<details><summary>Answer</summary>B — least privilege removes the ability, not just the
permission.</details>

**Q2.** Capability scoping composes with…

- A) nothing
- B) the tool registry (Phase 3) and bounded-role context (Phase 10)
- C) the model size
- D) temperature

<details><summary>Answer</summary>B — registry visibility + context bounding + capability
scoping.</details>

**Challenge.** Add a `network` capability and scope it so only a dedicated "fetcher" role
can make outbound calls. This ties to Phase 7 egress.

## Related

- Builds on: [Allow/deny](../../02-allow-deny/docs/en.md); Phase 3 — [Tool registry](../../../03-tool-engineering/08-tool-registry/docs/en.md)
- Next: [Use It: settings.json & the hooks system](../../06-settings-json/docs/en.md)
- Related: Phase 10 — bounded roles
- [Roadmap](../../../../ROADMAP.md)
