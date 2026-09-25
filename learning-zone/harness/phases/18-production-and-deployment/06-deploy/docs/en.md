# Use it: deploy the capstone agent

> **Motto** — Put it all together: a triggered, sandboxed, gated, observable, reversible deployment.

*Part of Phase 18 — Production & Deployment. Completes the phase.*

## The Problem

The phase's pieces — remote execution, CI, webhooks, config/flags, rollout — combine into one
**deployment pipeline** for the coding agent you build in Phase 19. This lesson is the
checklist that takes the capstone agent from "runs on my machine" to "runs safely in
production." Each item points at the lesson that justifies it.

## The Concept

<style>
.dgm-dep{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-dep-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-dep h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-dep-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-dep-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-dep-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-dep-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-dep-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-dep-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-dep-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-dep-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-dep-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-dep{padding:20px 16px 18px}.dgm-dep-row{flex-direction:column}}
</style>
<div class="dgm-dep">
  <span class="dgm-dep-chip">Four gates between a trigger and a running agent</span>
  <h4>Sandbox, then permissions + evals, then canary + kill switch, then observe</h4>
  <p class="dgm-dep-sub">This is every earlier phase's mechanism, composed into one deploy path.</p>
  <div class="dgm-dep-row">
    <div class="dgm-dep-n neutral">Trigger: web / CI / webhook</div>
    <span class="dgm-dep-arr">→</span>
    <div class="dgm-dep-n accent">Sandboxed ephemeral box (L1)</div>
    <span class="dgm-dep-arr">→</span>
    <div class="dgm-dep-n blue">Permissions + evals gate (P8/P15)</div>
    <span class="dgm-dep-arr">→</span>
    <div class="dgm-dep-n accent">Canary rollout + kill switch (L5)</div>
    <span class="dgm-dep-arr">→</span>
    <div class="dgm-dep-n green">Observe: traces, cost, drift (P16)</div>
  </div>
</div>


## Build It / Use It

The artifact is `outputs/deploy-checklist.md` — a go-live checklist for the capstone:

- **Environment (L1):** runs in a fresh, isolated, ephemeral container; commit/push results.
- **CI gate (L2/P15):** eval harness runs on every change and blocks regressions.
- **Triggers (L3):** webhook/CI events route to handlers; payloads treated as data.
- **Config (L4):** model, budgets, prompt version, features behind layered config + flags.
- **Rollout (L5):** ship behind a canary keyed by user/repo; kill switch wired to a flag.
- **Permissions (P8) & security (P17):** least privilege, `.env` blocked, egress allowlist.
- **Observability (P16):** traces, token/cost accounting, drift detection live.
- **Reliability (P14):** retries, budgets, degraded mode on.

## Use It

Run the checklist before pointing real traffic (or a real repo's PRs) at your agent. For a
Claude Code / Codex user, the platform provides much of this: sandboxed cloud execution,
permissions, network policy. Your job is the project-level config (`settings.json`,
`CLAUDE.md`, hooks, evals in CI), and knowing which guarantees come from where. The capstone
(Phase 19) is what you deploy with it.

## Ship It

[`outputs/deploy-checklist.md`](../../06-deploy/outputs/deploy-checklist.md) — a production go-live
checklist for the agent.

## Check Yourself

**Q1.** Before pointing real traffic at the agent, you should have…

- A) just the code
- B) sandbox + eval gate + permissions/security + observability + rollout/kill switch
- C) a bigger model
- D) nothing

<details><summary>Answer</summary>B — the full production checklist.</details>

**Q2.** For a Claude Code / Codex user, which parts are platform-provided?

- A) none
- B) sandboxed cloud execution, permissions, network policy — you supply project config + evals
- C) all of it
- D) only the model

<details><summary>Answer</summary>B — platform gives the runtime; you bring config + evals.</details>

**Challenge.** Turn the checklist into a script that verifies as many items as possible
automatically (eval gate passes, `.env` blocked, budgets set) and reports the rest.

## Related

- Builds on: the whole phase + Phases 8, 14, 15, 16, 17
- Phase complete → next: Phase 19 — [Capstone](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
