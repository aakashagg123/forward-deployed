# Use it: a security-review skill

> **Motto** — Make the agent review its own diff for the exact threats this phase taught.

*Part of Phase 17 — Security & Alignment. Completes the phase.*

## The Problem

You've built injection evals, output-as-data, egress guards, redaction, and tenant isolation.
The payoff is a **security-review skill**: the agent runs it on a diff, its own or a PR's, to
catch the vulnerabilities this phase covers before they ship. It turns the phase's knowledge
into a repeatable check, the way `/security-review` works in Claude Code.

## The Concept

<style>
.dgm-secr{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-secr-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-secr h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-secr-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-secr-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-secr-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-secr-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-secr-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-secr-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-secr-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-secr-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-secr-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-secr{padding:20px 16px 18px}.dgm-secr-row{flex-direction:column}}
</style>
<div class="dgm-secr">
  <span class="dgm-secr-chip">One skill, five checks, every diff</span>
  <h4>Injection, output-as-control, egress, secrets, tenant isolation — checked as a set</h4>
  <p class="dgm-secr-sub">Running this as a skill against every diff makes the check repeatable, not ad hoc.</p>
  <div class="dgm-secr-row">
    <div class="dgm-secr-n neutral">Diff / changes</div>
    <span class="dgm-secr-arr">→</span>
    <div class="dgm-secr-n accent">security-review skill</div>
    <span class="dgm-secr-arr">→</span>
    <div class="dgm-secr-n blue">Check: injection · output-as-control · egress · secrets · tenant isolation</div>
    <span class="dgm-secr-arr">→</span>
    <div class="dgm-secr-n green">Findings + severity</div>
  </div>
</div>


## Build It / Use It

The artifact is `outputs/SKILL.md` — a `/security-review` skill whose checklist *is* this
phase. It scans a diff for executing model output as code, unbounded egress, hardcoded
secrets, missing tenant scoping, and unsafe handling of untrusted content. It reports each
finding with a severity and a fix.

## Use It

Run `/security-review` before merging anything that touches tool dispatch, network calls,
auth, caching, or untrusted-input handling. In Claude Code this mirrors the built-in
`/security-review`, but installing this skill focuses it on *harness* threats specifically.
Pair it with the injection eval (lesson 01) in CI. The skill is the human-in-the-loop review,
and the eval is the automated gate.

## Ship It

[`outputs/SKILL.md`](../../06-security-review/outputs/SKILL.md) — a `/security-review` skill
covering the phase's threats.

## Check Yourself

**Q1.** What does the security-review skill check a diff for?

- A) formatting
- B) injection, output-as-control-flow, egress, secrets, tenant isolation
- C) test coverage only
- D) nothing

<details><summary>Answer</summary>B — the phase's threat checklist.</details>

**Q2.** Skill vs. eval for security?

- A) same thing
- B) the skill is the human-facing review; the injection eval is the automated CI gate
- C) neither matters
- D) only the skill

<details><summary>Answer</summary>B — review + gate, complementary.</details>

**Challenge.** Add a severity rubric (critical/high/low) and have the skill block (advise
"do not merge") on any critical finding, mirroring the review agent from Phase 10.

## Related

- Builds on: the whole phase
- Related: Phase 10 — review agent, Phase 15 — adversarial evals
- Phase complete → next: Phase 18 — [Production & Deployment](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
