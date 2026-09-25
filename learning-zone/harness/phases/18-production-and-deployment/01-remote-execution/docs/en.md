# Remote / sandboxed execution environments

> **Motto** — Run the agent in a fresh, isolated, ephemeral box — not on your laptop with your keys.

*Part of Phase 18 — Production & Deployment.*

## The Problem

Running an autonomous agent on your own machine gives it your full filesystem and
credentials. This is the highest-blast-radius option. Production agents run in **remote,
sandboxed, ephemeral** environments instead: a container cloned fresh from the repo, with a
scoped network policy and injected secrets. The box is reclaimed after the run. This is the
deployment form of the sandboxing (Phase 7) and security (Phase 17) lessons.

## The Concept

<style>
.dgm-re2{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-re2-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-re2 h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-re2-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-re2-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-re2-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-re2-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-re2-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-re2-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-re2-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-re2-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-re2-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-re2{padding:20px 16px 18px}.dgm-re2-row{flex-direction:column}}
</style>
<div class="dgm-re2">
  <span class="dgm-re2-chip">A fresh box for every run</span>
  <h4>Trigger, spin up, clone with scoped secrets, run, push, reclaim</h4>
  <p class="dgm-re2-sub">Reclaiming the box after every run is what keeps state from leaking between runs.</p>
  <div class="dgm-re2-row">
    <div class="dgm-re2-n neutral">Trigger (web / CI / schedule)</div>
    <span class="dgm-re2-arr">→</span>
    <div class="dgm-re2-n accent">Spin up fresh container</div>
    <span class="dgm-re2-arr">→</span>
    <div class="dgm-re2-n blue">Clone repo + inject scoped secrets + network policy</div>
    <span class="dgm-re2-arr">→</span>
    <div class="dgm-re2-n accent">Run agent</div>
    <span class="dgm-re2-arr">→</span>
    <div class="dgm-re2-n ">Commit/push results</div>
    <span class="dgm-re2-arr">→</span>
    <div class="dgm-re2-n green">Reclaim box</div>
  </div>
</div>


Key properties: ephemeral (no state survives), isolated (can't reach your laptop), scoped
(network policy + least-privilege secrets), and reproducible (fresh clone each time).

## Use It

This is exactly how **Claude Code on the web / Codex cloud** run. It's also the environment
*this very curriculum was built in*: a fresh clone, a chosen network policy, injected env,
and a box reclaimed after inactivity. Commit and push anything worth keeping, because the box
does not persist. The artifact is an environment config that captures these choices.

`outputs/environment.md` documents the deployment contract: trigger, base image, setup
script, network policy, secrets, and the "commit or lose it" rule.

## Ship It

[`outputs/environment.md`](../../01-remote-execution/outputs/environment.md) — a remote-execution
environment spec.

## Check Yourself

**Q1.** Why run a production agent in an ephemeral remote container, not locally?

- A) it's faster
- B) isolation + least privilege limit blast radius; ephemerality means no leaked state
- C) laptops are slow
- D) no reason

<details><summary>Answer</summary>B — contain the agent away from your machine and
keys.</details>

**Q2.** On an ephemeral box, results survive only if you…

- A) leave them in /tmp
- B) commit and push them before the box is reclaimed
- C) print them
- D) nothing

<details><summary>Answer</summary>B — persist to the repo; the container is
temporary.</details>

**Challenge.** Write an `environment.md` for your own project: base image, setup script,
network policy (no-net vs. allowlist), which secrets are injected, and the test command.

## Related

- Builds on: Phase 7 — [Sandboxing](../../../07-shell-and-sandbox-execution/05-sandboxing/docs/en.md), Phase 17 — Security
- Next: [GitHub integration & CI triggers](../../02-github-ci/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
