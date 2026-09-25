# Production failure-mode playbook

> **Motto** — Name the ways agents break in production, and the structural fix for each.

*Part of Phase 14 — Reliability Engineering. Completes the phase.*

## The Problem

You've built the reliability primitives: retries, repair, fallback, budgets, degraded mode.
The capstone is a **playbook** — a named list of the failure modes a coding-agent harness hits
in production, and the *structural* fix for each. When something breaks, you reach for the
mechanism, not a longer prompt. This page holds the reliability thread of the whole course.

## The Concept

<style>
.dgm-fp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-fp-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-fp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-fp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-fp-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-fp-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-fp-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-fp-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-fp-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-fp-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-fp-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-fp-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-fp{padding:20px 16px 18px}.dgm-fp-row{flex-direction:column}}
</style>
<div class="dgm-fp">
  <span class="dgm-fp-chip">Every failure mode gets a mechanism, not a prompt tweak</span>
  <h4>Diagnosis first, then a structural fix</h4>
  <p class="dgm-fp-sub">A prompt tweak papers over one instance; a mechanism fixes the class of failure.</p>
  <div class="dgm-fp-row">
    <div class="dgm-fp-n red">Failure mode</div>
    <span class="dgm-fp-arr">→</span>
    <div class="dgm-fp-n accent">Diagnosis</div>
    <span class="dgm-fp-arr">→</span>
    <div class="dgm-fp-n green">Structural fix (a mechanism, not a prompt)</div>
  </div>
</div>


## Build It (the playbook)

The artifact is `outputs/failure-playbook.md`. A sample of the entries:

| Failure mode | Structural fix |
| --- | --- |
| "The JSON sometimes doesn't parse" | validation + repair loop (L2); prefer tool-schema output (P3 L7) |
| "It worked yesterday" (silent regression) | golden-set eval + CI gate (P15) |
| "The agent ran 40 steps / spent $12" | step/tool/token/cost budgets (L4, P2, P3) |
| "Latency spikes / provider overloaded" | retries+backoff (L1), fallback chain (L3) |
| "It double-charged the customer" | idempotency keys (P3 L4) |
| "A retrieved doc hijacked the agent" | treat output as data; injection defenses (P17) |
| "It claimed success but tests failed" | verify before reporting; degraded mode (L5) |
| "Same mistake every week" | encode a lint rule / hook, delete the prompt line (P8, principles) |

Each row's fix is a mechanism you built. The playbook is the index from symptom to lesson.

## Use It

Keep this playbook handy as a pre-launch checklist and an incident guide for any agent you
ship, including how you operate Claude Code or Codex on real work. When you hit a new
failure mode, add a row: symptom, then structural fix. Per the harness principles, prefer
patching the harness over lengthening the prompt.

## Ship It

[`outputs/failure-playbook.md`](../../06-failure-playbook/outputs/failure-playbook.md) — a
production failure-mode → structural-fix playbook.

## Check Yourself

**Q1.** When the agent repeats a class of mistake, the playbook's prescribed fix is…

- A) a longer system prompt
- B) a mechanism (lint rule / hook / eval), then delete the prompt line
- C) a bigger model
- D) ignore it

<details><summary>Answer</summary>B — patch the harness, not the prompt.</details>

**Q2.** "It claimed success but tests failed" is fixed by…

- A) trusting the agent
- B) verifying before reporting + degraded mode (honest partial results)
- C) more retries
- D) a longer prompt

<details><summary>Answer</summary>B — verify, then report honestly.</details>

**Challenge.** Add three failure modes from your own experience with each one's structural
fix, and turn the table into a pre-launch checklist you run before shipping an agent.

## Related

- Builds on: the whole phase
- Concept: harness principles (patch the harness, not the prompt)
- Phase complete → next: Phase 15 — [Evals & Testing the Harness](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
