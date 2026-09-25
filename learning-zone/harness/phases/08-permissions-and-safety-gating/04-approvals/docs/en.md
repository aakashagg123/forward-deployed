# Human-in-the-loop approval flows

> **Motto** — For the actions that matter, the human is a required step — not an afterthought.

*Part of Phase 08 — Permissions & Safety Gating.*

## The Problem

When the gate says "ask" (lesson 01), the harness needs an actual **approval flow**. It
must present the pending action clearly, capture a decision, and remember it, so the agent
doesn't ask the same class of thing five times. Done badly, approvals are either skipped
(unsafe) or constant (annoying). Done well, they spend human attention only on genuine
decision points.

## The Concept

<style>
.dgm-apr{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-apr-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-apr h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-apr-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-apr-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-apr-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-apr-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-apr-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-apr-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-apr-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-apr-b.accent h6{color:#0d5c0d}
.dgm-apr-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-apr-b.blue h6{color:#0550ae}
.dgm-apr-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-apr-b.green h6{color:#1a614f}
.dgm-apr-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-apr-b.red h6{color:#82061e}
.dgm-apr-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-apr-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-apr{padding:20px 16px 18px}.dgm-apr-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-apr">
  <span class="dgm-apr-chip">Approve once, or remember the class of action</span>
  <h4>The human sees what, why, and blast radius before deciding</h4>
  <p class="dgm-apr-sub">Approve-always is a scoped memory — it auto-allows that class, not every future action.</p>
  <div class="dgm-apr-q">Action needs approval — present: what, why, blast radius</div>
  <div class="dgm-apr-branches">
    <div class="dgm-apr-b green">
      <h6>Approve once</h6>
      <p>Run</p>
    </div>
    <div class="dgm-apr-b accent">
      <h6>Approve always (this class)</h6>
      <p>Remember → auto-allow next time</p>
    </div>
    <div class="dgm-apr-b red">
      <h6>Deny</h6>
      <p>Refuse</p>
    </div>
  </div>
</div>


The "approve always for this class" option keeps you from re-approving the same safe
pattern. The harness learns the allow rule from your decision.

## Build It

`code/approvals.py` — an approval flow with remembered decisions:

```python
class Approvals:
    def __init__(self, decide):
        self.decide = decide               # (action_class, detail) -> "once"|"always"|"deny"
        self.always = set()

    def request(self, action_class, detail):
        if action_class in self.always:
            return True                    # remembered
        choice = self.decide(action_class, detail)
        if choice == "always":
            self.always.add(action_class)
            return True
        return choice == "once"
```

```python
# auto-approver for the demo: "always" for git, "deny" for rm
ap = Approvals(decide=lambda cls, d: "always" if cls == "git" else "deny")
print(ap.request("git", "git commit"))   # True (and remembered)
print(ap.request("git", "git push"))     # True (no re-ask — remembered)
print(ap.request("rm", "rm -rf build"))  # False
```

"Approve always" promotes a one-time decision into a standing allow (lesson 02). The human
teaches the policy by using it.

## Use It

This is the Claude Code / Codex approval prompt. When the agent proposes a gated action,
you choose yes / no / "yes and don't ask again for this", and the tool remembers the last
option as a session (or persisted) allow rule. The orchestration version of this is the
wave approval gate from Phase 10 — spec-first, with a hard stop between waves.

## Ship It

[`code/approvals.py`](../../04-approvals/code/approvals.py) — an approval flow with remembered
"always" decisions.

## Check Yourself

**Q1.** What does "approve always for this class" do?

- A) nothing
- B) promotes the decision into a standing allow so the same safe action isn't re-asked
- C) disables permissions
- D) denies future calls

<details><summary>Answer</summary>B — it learns an allow rule from your choice.</details>

**Q2.** Approvals should be spent on…

- A) every tool call
- B) genuine decision points (irreversible/risky actions), not routine ones
- C) reads
- D) nothing

<details><summary>Answer</summary>B — reserve human attention for real decisions.</details>

**Challenge.** Persist the `always` set to disk so remembered approvals survive across
sessions. Add a way to revoke one, too.

## Related

- Builds on: [Permission modes](../../01-permission-modes/docs/en.md), [Allow/deny](../../02-allow-deny/docs/en.md)
- Next: [Least privilege & capability scoping](../../05-least-privilege/docs/en.md)
- Related: Phase 10 — wave approval gates
- [Roadmap](../../../../ROADMAP.md)
