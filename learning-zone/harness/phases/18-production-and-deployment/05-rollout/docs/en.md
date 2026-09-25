# Rollout, canary & kill switches

> **Motto** — Ship to a few, watch, then ship to all — and keep a switch to turn it off instantly.

*Part of Phase 18 — Production & Deployment.*

## The Problem

A new prompt version, tool, or model can regress in ways evals missed (Phase 15), and you
find out in production. **Canary rollout** limits the blast radius: route a small % of
traffic to the new version, watch the metrics (Phase 16), and ramp up only if it's healthy. A
**kill switch** lets you revert to the known-good version instantly when something goes
wrong, with no redeploy.

## The Concept

<style>
.dgm-ro{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-ro-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-ro h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-ro-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-ro-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-ro-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-ro-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-ro-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-ro-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-ro-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-ro-b.accent h6{color:#0d5c0d}
.dgm-ro-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-ro-b.blue h6{color:#0550ae}
.dgm-ro-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-ro-b.green h6{color:#1a614f}
.dgm-ro-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-ro-b.red h6{color:#82061e}
.dgm-ro-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-ro-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-ro{padding:20px 16px 18px}.dgm-ro-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-ro">
  <span class="dgm-ro-chip">A kill switch above the canary check</span>
  <h4>The kill switch is checked first — canary percentage only matters if it's off</h4>
  <p class="dgm-ro-sub">That ordering means an incident response never has to reason about canary state at all.</p>
  <div class="dgm-ro-q">Request — kill switch on?</div>
  <div class="dgm-ro-branches">
    <div class="dgm-ro-b red">
      <h6>Yes</h6>
      <p>Stable version</p>
    </div>
    <div class="dgm-ro-b accent">
      <h6>No — in canary %?</h6>
      <p>Yes → new version (watched) · No → stable version</p>
    </div>
  </div>
</div>


## Build It

`code/rollout.py` — canary routing + kill switch (builds on the flag from lesson 04):

```python
import hashlib

class Rollout:
    def __init__(self, stable, candidate, percent=10):
        self.stable, self.candidate, self.percent = stable, candidate, percent
        self.killed = False

    def kill(self):
        self.killed = True            # instant revert to stable

    def version_for(self, unit_id):
        if self.killed:
            return self.stable
        h = int(hashlib.sha256(unit_id.encode()).hexdigest(), 16) % 100
        return self.candidate if h < self.percent else self.stable
```

```python
r = Rollout("prompt-v3", "prompt-v4", percent=20)
sample = [r.version_for(u) for u in [f"u{i}" for i in range(10)]]
print(sample.count("prompt-v4"), "of 10 on canary")
r.kill()
print(set(r.version_for(u) for u in [f"u{i}" for i in range(10)]))   # all stable
```

Canary sends ~20% to v4. If metrics dip, `kill()` routes everyone back to v3 instantly. Ramp
by raising `percent` once the canary looks healthy.

## Use It

For prompt/skill/model changes (Phase 5 versioning), roll out as a canary keyed by user/repo
and watch the eval/drift signals (Phase 15/16). Keep the kill switch wired to a config flag
(lesson 04), so revert is one toggle, not a redeploy. This is how you ship harness changes to
real users without betting everything on the first %.

## Ship It

[`code/rollout.py`](../../05-rollout/code/rollout.py) — canary routing + kill switch.

## Check Yourself

**Q1.** What does a canary rollout limit?

- A) cost only
- B) blast radius — only a small % hits the new version until it's proven healthy
- C) latency
- D) nothing

<details><summary>Answer</summary>B — contain risk, then ramp.</details>

**Q2.** A kill switch lets you…

- A) delete the repo
- B) revert to the known-good version instantly, no redeploy
- C) increase the canary
- D) nothing

<details><summary>Answer</summary>B — instant revert.</details>

**Challenge.** Auto-kill: wire the rollout to the drift detector (Phase 16 L4) so a metric
drop on the canary trips the kill switch automatically.

## Related

- Builds on: [Config & flags](../../04-config-flags/docs/en.md), Phase 5 — [Prompt versioning](../../../05-prompt-instruction-architecture/06-prompt-versioning/docs/en.md), Phase 16 — Drift
- Next: [Use It: deploy the capstone agent](../../06-deploy/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
