# Config, settings & feature flags

> **Motto** — Change behavior with config, not a redeploy — and roll features without shipping code.

*Part of Phase 18 — Production & Deployment.*

## The Problem

A production harness has knobs: which model, which tools are enabled, budgets, prompt
version, new features. Hardcoding them means a redeploy for every change, and no way to turn
something off fast. **Layered config + feature flags** let you change behavior at runtime
instead — defaults in code, overrides per environment, and flags that enable a feature for
some or all traffic.

## The Concept

<style>
.dgm-cf{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-cf-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-cf h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-cf-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-cf-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-cf-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-cf-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-cf-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-cf-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-cf-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-cf-b.accent h6{color:#0d5c0d}
.dgm-cf-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-cf-b.blue h6{color:#0550ae}
.dgm-cf-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-cf-b.green h6{color:#1a614f}
.dgm-cf-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-cf-b.red h6{color:#82061e}
.dgm-cf-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-cf-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-cf{padding:20px 16px 18px}.dgm-cf-branches{grid-template-columns:1fr}}
.dgm-cf-chain{display:flex;flex-direction:column;gap:2px}
.dgm-cf-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-cf-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-cf-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-cf{padding:20px 16px 18px}}
</style>
<div class="dgm-cf">
  <span class="dgm-cf-chip">Three sources merge into one effective config</span>
  <h4>Defaults, env/file overrides, and runtime feature flags all merge in that priority order</h4>
  <p class="dgm-cf-sub">Feature flags are the only one of the three that can change without a redeploy.</p>
  <div class="dgm-cf-branches">
    <div class="dgm-cf-b neutral">
      <h6>Defaults (code)</h6>
    </div>
    <div class="dgm-cf-b blue">
      <h6>Env / file overrides</h6>
    </div>
    <div class="dgm-cf-b accent">
      <h6>Feature flags (runtime)</h6>
    </div>
  </div>
  <div class="dgm-cf-chain">
    <div class="dgm-cf-node alt">Merge</div>
    <div class="dgm-cf-arr">↓</div>
    <div class="dgm-cf-node accent">Effective config</div>
  </div>
</div>


Later layers override earlier ones. Flags gate features independently of a deploy.

## Build It

`code/config.py` — layered config + a percentage feature flag:

```python
import hashlib

def load_config(defaults, *overrides):
    cfg = dict(defaults)
    for o in overrides:
        cfg.update({k: v for k, v in o.items() if v is not None})
    return cfg

def flag_enabled(name, unit_id, percent):
    """Stable per-unit rollout: same unit_id always gets the same answer."""
    h = int(hashlib.sha256(f"{name}:{unit_id}".encode()).hexdigest(), 16) % 100
    return h < percent
```

```python
cfg = load_config({"model": "haiku", "max_steps": 10},
                  {"model": "claude-opus-5"})        # env override
print(cfg["model"], cfg["max_steps"])                  # opus, 10

# enable a feature for ~30% of users, stably
print([flag_enabled("new_planner", u, 30) for u in ["u1", "u2", "u3", "u4"]])
```

Config merges deterministically: the last layer wins. The flag hashes the unit id, so a given
user consistently sees the feature on or off. This is the basis for canary rollout (next
lesson).

## Use It

For Claude Code / Codex, this maps to `settings.json` layering (user / project / local) plus
env vars — the same defaults→overrides model. In a custom harness, flags let you ship a new
prompt version or tool to 10% of traffic and watch the metrics (Phase 16) before going to
100%. Config-as-data keeps behavior changes reviewable and reversible.

## Ship It

[`code/config.py`](../../04-config-flags/code/config.py) — layered config + percentage feature
flags.

## Check Yourself

**Q1.** Why feature-flag a change instead of hardcoding it?

- A) it's prettier
- B) you can enable/disable at runtime (and per-percentage) without a redeploy
- C) it's required
- D) no reason

<details><summary>Answer</summary>B — runtime control + gradual rollout.</details>

**Q2.** Why hash the unit id for a percentage flag?

- A) security
- B) so the same user stably gets the same on/off answer (no flicker)
- C) speed
- D) no reason

<details><summary>Answer</summary>B — stable per-unit assignment.</details>

**Challenge.** Add config layering precedence matching Claude Code (enterprise → user →
project → local) and show which wins on a conflicting key.

## Related

- Builds on: Phase 8 — [settings.json](../../../08-permissions-and-safety-gating/06-settings-json/docs/en.md), Phase 5 — [Prompt versioning](../../../05-prompt-instruction-architecture/06-prompt-versioning/docs/en.md)
- Next: [Rollout, canary & kill switches](../../05-rollout/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
