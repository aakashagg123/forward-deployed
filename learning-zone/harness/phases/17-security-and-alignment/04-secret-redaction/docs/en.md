# Secret redaction in context & logs

> **Motto** — A secret the model never sees can't be leaked — and a secret never logged can't escape later.

*Part of Phase 17 — Security & Alignment.*

## The Problem

Secrets sneak into two dangerous places. The **context** is one — a config file the agent
reads can contain an API key, which then lands in the prompt. The **logs and traces** are
the other — you record the conversation, key and all. Either is a leak waiting to happen.
**Redaction** scrubs secret-shaped strings on the way in, before the model sees them, and on
the way out, before anything is logged or returned.

## The Concept

<style>
.dgm-sr{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-sr-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-sr h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-sr-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-sr-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-sr-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-sr-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-sr-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-sr-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-sr-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-sr-b.accent h6{color:#0d5c0d}
.dgm-sr-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-sr-b.blue h6{color:#0550ae}
.dgm-sr-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-sr-b.green h6{color:#1a614f}
.dgm-sr-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-sr-b.red h6{color:#82061e}
.dgm-sr-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-sr-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-sr{padding:20px 16px 18px}.dgm-sr-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-sr">
  <span class="dgm-sr-chip">Redact on the way in, redact on the way out</span>
  <h4>File and tool content gets redacted before the model sees it and after, before logs or the user do</h4>
  <p class="dgm-sr-sub">Two redaction points, not one — a secret can enter through content and leave through output.</p>
  <div class="dgm-sr-branches">
    <div class="dgm-sr-b accent">
      <h6>IN: file/tool content</h6>
      <p>Redact secrets → model</p>
    </div>
    <div class="dgm-sr-b blue">
      <h6>OUT: model/tool output</h6>
      <p>Redact secrets → logs / user</p>
    </div>
  </div>
</div>


Redaction combines pattern-based matching (key formats, tokens) with known-value masking
(your actual secrets). It applies at both boundaries.

## Build It

`code/redact.py` — redact common secret patterns and known values:

```python
import re

PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{16,}"),                  # API-key-ish
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),                 # GitHub token
    re.compile(r"-----BEGIN[ A-Z]+PRIVATE KEY-----[\s\S]+?-----END[ A-Z]+PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),                     # AWS access key id
]

def redact(text, known_values=()):
    for v in known_values:
        if v:
            text = text.replace(v, "[REDACTED]")
    for rx in PATTERNS:
        text = rx.sub("[REDACTED]", text)
    return text
```

```python
import os
s = "key=sk-abc123def456ghi789 and token=ghp_0123456789abcdef01234"
print(redact(s, known_values=[os.getenv("ANTHROPIC_API_KEY")]))
# key=[REDACTED] and token=[REDACTED]
```

Apply `redact` when injecting file or tool content into context, and again when writing
traces (Phase 16) or returning output. Cover both boundaries, so a secret is scrubbed coming
and going.

## Use It

Wire redaction into a PostToolUse hook (Phase 8), so tool output is scrubbed before it
enters context or logs, and into your trace exporter (Phase 16). For a Claude Code or Codex
user this complements the `.env` block (Phase 0). Even if a secret lands in some file the
agent reads, redaction keeps it out of the model and the logs. Combine this with rotating
any secret that *was* exposed.

## Ship It

[`code/redact.py`](../../04-secret-redaction/code/redact.py) — a secret-redaction filter
(patterns + known values).

## Check Yourself

**Q1.** Where must redaction be applied?

- A) only in logs
- B) both inbound (into context) and outbound (into logs/output)
- C) only the system prompt
- D) nowhere

<details><summary>Answer</summary>B — both boundaries.</details>

**Q2.** If a secret *was* exposed in context/logs, you should also…

- A) ignore it
- B) rotate it (redaction stops future leaks; the exposed one is already compromised)
- C) log it again
- D) email it

<details><summary>Answer</summary>B — rotate exposed secrets.</details>

**Challenge.** Add entropy-based detection (flag high-entropy tokens that don't match a known
pattern) and measure its false-positive rate on real code.

## Related

- Builds on: Phase 0 — [Secrets & env](../../../00-setup-and-tooling/03-secrets-and-env/docs/en.md); Phase 16 — [Tracing](../../../16-observability-and-cost/01-tracing/docs/en.md)
- Next: [Multi-tenant isolation](../../05-multitenancy/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
