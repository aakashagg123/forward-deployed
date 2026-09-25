# Bounded roles & context allowlists

> **Motto** — Each agent reads only its allowlist — everything else is off-limits by construction.

*Part of Phase 10 — Subagents & Orchestration. Concept:
[The Ten Principles of a Working Harness](../../../../foundations/harness-principles.md)
(principle 02).*

## The Problem

When several agents share a pipeline, the lazy move is to hand each one the whole
context — the spec, the plan, the diff, everything. This feels helpful, but it quietly
breaks the pipeline. The clearest failure shows up in review. A reviewer who can see the
author's plan starts to *rationalise* the output ("the author meant well") instead of
judging it on its own terms. Context leakage turns independent review into a rubber
stamp. The fix isn't asking the agent to "be objective." Instead, build its context so
it *cannot* see what it shouldn't.

## The Concept

<style>
.dgm-br{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-br-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-br h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-br-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-br-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-br-branches{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.dgm-br-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-br-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-br-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-br-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-br-b.accent h6{color:#0d5c0d}
.dgm-br-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-br-b.blue h6{color:#0550ae}
.dgm-br-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-br-b.green h6{color:#1a614f}
.dgm-br-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-br-b.red h6{color:#82061e}
.dgm-br-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-br-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-br{padding:20px 16px 18px}.dgm-br-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-br">
  <span class="dgm-br-chip">One shared context, four narrow views</span>
  <h4>Planner sees the spec; reviewer sees only the diff</h4>
  <p class="dgm-br-sub">Each role's view is a deliberate cut, not an oversight — less context, harder to derail.</p>
  <div class="dgm-br-q">Full context: spec · plan · diff · history</div>
  <div class="dgm-br-branches">
    <div class="dgm-br-b accent">
      <h6>Planner</h6>
      <p>Spec</p>
    </div>
    <div class="dgm-br-b blue">
      <h6>Worker</h6>
      <p>Contract + its files</p>
    </div>
    <div class="dgm-br-b green">
      <h6>Reviewer</h6>
      <p>Diff ONLY</p>
    </div>
    <div class="dgm-br-b neutral">
      <h6>Memory</h6>
      <p>Review report ONLY</p>
    </div>
  </div>
</div>


Each role gets an **explicit allowlist** of context keys. The allowlist is enforced when
the prompt is *constructed* — not by trusting the agent to ignore what it was given.

## Build It

`code/roles.py` — a context store and a builder that filters by role:

```python
ROLE_ALLOWLIST = {
    "planner":  ["spec"],
    "worker":   ["contract", "files"],
    "reviewer": ["diff"],                       # never "plan" or "spec"
    "memory":   ["review_report"],
}

def build_context(role, store):
    allowed = ROLE_ALLOWLIST[role]
    leaked = [k for k in store if k not in allowed and k in ROLE_ALLOWLIST.get("_sensitive", store)]
    ctx = {k: store[k] for k in allowed if k in store}
    return ctx

def assert_no_leak(role, ctx):
    forbidden = set(ctx) - set(ROLE_ALLOWLIST[role])
    if forbidden:
        raise AssertionError(f"{role} context leaked: {forbidden}")
    return ctx
```

```python
store = {"spec": "...", "plan": "...", "diff": "- old\n+ new", "review_report": "..."}
reviewer_ctx = build_context("reviewer", store)
print(list(reviewer_ctx))                       # ['diff'] — plan/spec are absent
assert_no_leak("reviewer", reviewer_ctx)        # passes
```

The reviewer's prompt is built from `reviewer_ctx`. The plan literally isn't in scope.
`assert_no_leak` is a contract test. Run it in CI so a future refactor can't widen a
role's view by accident.

## Use It

In Claude Code, role bounding shapes how you write subagent prompts and use the `Agent`
tool. Each subagent receives only the inputs its task needs, and you never pass the
parent's full transcript. The discipline stays the same: the allowlist lives in how you
assemble the subagent's prompt, enforced by construction, not by instruction.

## Ship It

[`code/roles.py`](../../02-bounded-roles/code/roles.py) — a role→allowlist context builder
with a leak assertion for CI.

## Check Yourself

**Q1.** Why must the reviewer not see the plan?

- A) to save tokens
- B) seeing intent makes it rationalise the output instead of judging it
- C) the plan is secret from users
- D) it slows review

<details><summary>Answer</summary>B — principle 02. Independent review requires judging
the diff on its own terms.</details>

**Q2.** Where is the allowlist enforced?

- A) by asking the agent nicely to ignore extra context
- B) when the agent's prompt/context is constructed
- C) in the model weights
- D) after the agent responds

<details><summary>Answer</summary>B — enforcement is structural. Self-restraint is not a
control.</details>

**Challenge.** Add a `"taste"` reviewer role that sees the diff *and* a style guide, but
still not the plan. Prove with `assert_no_leak` that two reviewer roles cover
complementary concerns without either seeing intent.

## Related

- Concept: [Ten principles](../../../../foundations/harness-principles.md)
- Builds on: [Sprint contracts & budgeted waves](../../01-sprint-contract-and-waves/docs/en.md)
- Next: [Worktree isolation & the dependency graph](../../03-worktree-isolation/docs/en.md)
