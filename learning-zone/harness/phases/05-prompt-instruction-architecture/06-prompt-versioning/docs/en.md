# Prompt versioning & A/B in the harness

> **Motto** — Prompts are code: version them, and prove a change is better before you ship it.

*Part of Phase 05 — Prompt & Instruction Architecture. Completes the phase.*

## The Problem

You tweak the system prompt and "it feels better." Then next week a different tweak quietly
regresses 5% of cases. Prompts deserve the same discipline as code: named versions, the
ability to roll back, and an A/B comparison scored by an eval (Phase 15) rather than vibes.
Without versioning you can't even tell which prompt produced a given result.

## The Concept

<style>
.dgm-pv{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pv-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-pv h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-pv-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-pv-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-pv-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-pv-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-pv-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-pv-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-pv-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-pv-b.accent h6{color:#0d5c0d}
.dgm-pv-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-pv-b.blue h6{color:#0550ae}
.dgm-pv-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-pv-b.green h6{color:#1a614f}
.dgm-pv-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-pv-b.red h6{color:#82061e}
.dgm-pv-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-pv-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-pv{padding:20px 16px 18px}.dgm-pv-branches{grid-template-columns:1fr}}
.dgm-pv-chain{display:flex;flex-direction:column;gap:2px}
.dgm-pv-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-pv-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-pv-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-pv{padding:20px 16px 18px}}
</style>
<div class="dgm-pv">
  <span class="dgm-pv-chip">A/B the prompt like you'd A/B anything else</span>
  <h4>Two versions, one eval set, one winner</h4>
  <p class="dgm-pv-sub">The registry keeps the losing version around — rollback is just re-promoting it.</p>
  <div class="dgm-pv-q">Prompt registry: name → versions</div>
  <div class="dgm-pv-branches">
    <div class="dgm-pv-b neutral">
      <h6>A: v3 (current)</h6>
    </div>
    <div class="dgm-pv-b accent">
      <h6>B: v4 (candidate)</h6>
    </div>
  </div>
  <div class="dgm-pv-chain">
    <div class="dgm-pv-node alt">Run eval set on both</div>
    <div class="dgm-pv-arr">↓</div>
    <div class="dgm-pv-node accent">Pick winner; promote or roll back</div>
  </div>
</div>


A registry stores versioned prompts. An A/B run scores both on a fixed eval set. You
promote the winner, and can revert instantly.

## Build It

`code/prompt_registry.py` — versioned prompts with selection and a tiny A/B harness:

```python
from dataclasses import dataclass, field

@dataclass
class PromptRegistry:
    versions: dict = field(default_factory=dict)     # name -> {version: text}
    active: dict = field(default_factory=dict)       # name -> version

    def register(self, name, version, text, activate=False):
        self.versions.setdefault(name, {})[version] = text
        if activate or name not in self.active:
            self.active[name] = version

    def get(self, name, version=None):
        return self.versions[name][version or self.active[name]]

    def rollback(self, name, version):
        self.active[name] = version

def ab_test(registry, name, va, vb, eval_set, run, score):
    """run(prompt, case)->output; score(output, case)->0..1. Returns mean scores."""
    def mean(v):
        outs = [score(run(registry.get(name, v), c), c) for c in eval_set]
        return sum(outs) / len(outs)
    return {va: mean(va), vb: mean(vb)}
```

```python
r = PromptRegistry()
r.register("sys", "v1", "Be terse.", activate=True)
r.register("sys", "v2", "Be terse. Always cite files.")
res = ab_test(r, "sys", "v1", "v2",
              eval_set=[{"want": "cite"}],
              run=lambda p, c: p, score=lambda o, c: 1.0 if c["want"] in o.lower() else 0.0)
print(res)     # {'v1': 0.0, 'v2': 1.0} → promote v2
```

Now "is the new prompt better?" has a number, and rollback is one call.

## Use It

For **Claude Code / Codex** users, the practical form is simple. Keep your
`CLAUDE.md`/`AGENTS.md` and any custom skill prompts in git, since they're versioned
automatically. When you change one, run your eval set (Phase 15) on a few representative
tasks before and after. The registry here is what you'd build inside a larger harness or
skill that ships multiple prompt variants.

## Ship It

[`code/prompt_registry.py`](../../06-prompt-versioning/code/prompt_registry.py) — a versioned
prompt registry with rollback and an A/B harness.

## Check Yourself

**Q1.** Why version prompts?

- A) neatness
- B) to roll back regressions and know which prompt produced a result
- C) the API requires it
- D) no reason

<details><summary>Answer</summary>B — prompts are code; version and revert them.</details>

**Q2.** How do you decide a new prompt is better?

- A) it feels better
- B) A/B it on a fixed eval set and compare scores
- C) it's longer
- D) ask the model

<details><summary>Answer</summary>B — measure on an eval set (Phase 15).</details>

**Challenge.** Add a `canary` mode that routes 10% of calls to the candidate version and
logs scores, so you A/B in production gradually (ties to Phase 18 rollout).

## Related

- Builds on: the whole phase
- Deepens in: Phase 15 — Evals, Phase 18 — Rollout
- Phase complete → next: Phase 6 — [File & Code Operations](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
