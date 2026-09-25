# Network policies & egress control

> **Motto** — Decide what the agent may reach before it runs, not after it exfiltrates.

*Part of Phase 07 — Shell & Sandbox Execution. Completes the phase.*

## The Problem

The most dangerous thing a compromised or misled agent can do is *call home*: POST your
source or secrets to an attacker's server (a prompt-injection payoff, Phase 17). Filesystem
sandboxing doesn't stop this. You need **egress control**: an allowlist of hosts the agent's
commands may reach, which denies everything else by default.

## The Concept

<style>
.dgm-ec{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ec-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ec h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ec-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ec-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-ec-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-ec-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-ec-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-ec-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-ec-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-ec-b.accent h6{color:#0d5c0d}
.dgm-ec-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-ec-b.blue h6{color:#0550ae}
.dgm-ec-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-ec-b.green h6{color:#1a614f}
.dgm-ec-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-ec-b.red h6{color:#82061e}
.dgm-ec-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-ec-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-ec{padding:20px 16px 18px}.dgm-ec-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-ec">
  <span class="dgm-ec-chip">Default-deny, allowlist the rest</span>
  <h4>A network call only goes through if the destination host is explicitly allowed</h4>
  <p class="dgm-ec-sub">Default-deny means a new, unreviewed destination fails closed, not open.</p>
  <div class="dgm-ec-q">Command makes a network call — host on allowlist?</div>
  <div class="dgm-ec-branches">
    <div class="dgm-ec-b green">
      <h6>Yes</h6>
      <p>Permit</p>
    </div>
    <div class="dgm-ec-b red">
      <h6>No</h6>
      <p>Block (default-deny)</p>
    </div>
  </div>
</div>


Default-deny is the rule. Enumerate the few hosts you need — package registries, your
APIs — and block the rest, so an unexpected exfiltration attempt simply fails.

## Build It / Use It

True egress control is enforced at the network or OS layer (firewall, proxy, container
network policy), so this is **Use It**. The harness-side artifact is a **PreToolUse hook**
that inspects a command and blocks obvious egress to non-allowlisted hosts.
`outputs/egress-guard.sh`:

```bash
#!/usr/bin/env bash
# PreToolUse hook: block curl/wget/nc to hosts not on the allowlist. Exit 2 = deny.
ALLOW="registry.npmjs.org pypi.org github.com api.anthropic.com"
cmd="$(cat)"   # tool-call JSON on stdin
urls="$(printf '%s' "$cmd" | grep -oE 'https?://[a-zA-Z0-9.-]+' | sed -E 's#https?://##')"
for host in $urls; do
  case " $ALLOW " in
    *" $host "*) ;;                                   # allowed
    *) echo "BLOCKED egress to $host (not on allowlist)" >&2; exit 2 ;;
  esac
done
exit 0
```

This hook is a *belt* — cheap, harness-level. The *suspenders* is an actual network policy,
a default-deny firewall or proxy, that the hook can't be tricked past.

## Use It

This is precisely what the **network policy** on Claude Code on the web / Codex cloud does.
The environment's outbound access follows a chosen policy — no network, or an allowlist —
enforced at the infrastructure layer. Locally, you add a hook like this plus your OS
firewall. Either way, default-deny and allowlist only the few hosts you trust.

## Ship It

[`outputs/egress-guard.sh`](../../06-egress-control/outputs/egress-guard.sh) — a PreToolUse
egress-allowlist hook.

## Check Yourself

**Q1.** What's the right default for agent network egress?

- A) allow all
- B) default-deny with a small allowlist of trusted hosts
- C) allow internal only
- D) no policy

<details><summary>Answer</summary>B — deny by default; allowlist what you need.</details>

**Q2.** Why isn't a PreToolUse hook alone sufficient?

- A) it is
- B) a clever command can evade text inspection; real enforcement is at the network layer
- C) hooks are slow
- D) no reason

<details><summary>Answer</summary>B — the hook is a cheap belt; the firewall/proxy is the
real wall.</details>

**Challenge.** Extend the hook to also catch egress in `python -c` / `node -e` one-liners,
and note why a network-layer policy is still required.

## Related

- Builds on: [Sandboxing](../../05-sandboxing/docs/en.md)
- Deepens in: Phase 8 — Permissions (hooks), Phase 17 — Security (exfiltration)
- Phase complete → next: Phase 8 — [Permissions & Safety Gating](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
