# Allowlists, denylists & pattern matching

> **Motto** — Deny wins over allow, and the most specific rule wins — make precedence explicit.

*Part of Phase 08 — Permissions & Safety Gating.*

## The Problem

"Allow `git` but deny `git push`." "Allow reads anywhere but deny writing to `/etc`." Rules
overlap and conflict. If precedence is fuzzy, you get surprises — an allow rule silently
permits something a deny rule meant to block. You need pattern-based allow/deny lists with
a clear, documented precedence: **deny always wins**, and specificity breaks ties.

## The Concept

<style>
.dgm-ad{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ad-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ad h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ad-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ad-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-ad-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-ad-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-ad-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-ad-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-ad-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-ad-b.accent h6{color:#0d5c0d}
.dgm-ad-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-ad-b.blue h6{color:#0550ae}
.dgm-ad-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-ad-b.green h6{color:#1a614f}
.dgm-ad-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-ad-b.red h6{color:#82061e}
.dgm-ad-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-ad-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-ad{padding:20px 16px 18px}.dgm-ad-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-ad">
  <span class="dgm-ad-chip">Deny always wins</span>
  <h4>Deny is checked first; only then does allow get a say; otherwise it falls to the default</h4>
  <p class="dgm-ad-sub">This ordering is what makes a deny rule un-overridable by a broader allow rule.</p>
  <div class="dgm-ad-q">Tool + args — matches any DENY pattern?</div>
  <div class="dgm-ad-branches">
    <div class="dgm-ad-b red">
      <h6>Yes</h6>
      <p>Deny (deny wins)</p>
    </div>
    <div class="dgm-ad-b accent">
      <h6>No — matches any ALLOW pattern?</h6>
      <p>Yes → allow · No → fall through to default (ask)</p>
    </div>
  </div>
</div>


## Build It

`code/policy.py` — glob-style pattern rules with deny-wins precedence:

```python
import fnmatch

class PolicyList:
    def __init__(self, allow=(), deny=()):
        self.allow, self.deny = list(allow), list(deny)

    def _match(self, patterns, signature):
        return any(fnmatch.fnmatch(signature, p) for p in patterns)

    def decide(self, signature):           # signature e.g. "bash:git push origin main"
        if self._match(self.deny, signature):
            return "deny"                  # deny always wins
        if self._match(self.allow, signature):
            return "allow"
        return "ask"                       # fall through
```

```python
pol = PolicyList(allow=["bash:git *", "read:*"], deny=["bash:git push*", "write:/etc/*"])
print(pol.decide("bash:git status"))       # allow
print(pol.decide("bash:git push origin"))  # deny (deny wins over the git * allow)
print(pol.decide("write:/etc/hosts"))      # deny
print(pol.decide("write:/tmp/x"))          # ask (no match)
```

Deny-wins is the safe default. An allow rule can never accidentally re-permit something a
deny rule blocked.

## Use It

This is how Claude Code's `permissions.allow` / `permissions.deny` in `settings.json` work
(e.g. `Bash(git push:*)` in deny), and how Codex's command rules work. Write broad allows
for safe families and narrow denies for the dangerous specifics. Deny wins, so the narrow
denies stay safe.

## Ship It

[`code/policy.py`](../../02-allow-deny/code/policy.py) — pattern allow/deny lists with
deny-wins precedence.

## Check Yourself

**Q1.** An allow rule and a deny rule both match. Which wins?

- A) allow
- B) deny — deny always wins, so a block can't be accidentally re-permitted
- C) the first listed
- D) the longer pattern

<details><summary>Answer</summary>B — deny-wins is the safe precedence.</details>

**Q2.** No rule matches. The decision should…

- A) allow
- B) fall through to the default mode (ask/deny)
- C) deny everything
- D) error

<details><summary>Answer</summary>B — fall through to the configured default.</details>

**Challenge.** Add specificity tie-breaking among *allow* rules, so the longer, more
specific pattern wins. Show a case where it matters.

## Related

- Builds on: [Permission modes](../../01-permission-modes/docs/en.md)
- Next: [Pre/post tool-use hooks](../../03-hooks/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
