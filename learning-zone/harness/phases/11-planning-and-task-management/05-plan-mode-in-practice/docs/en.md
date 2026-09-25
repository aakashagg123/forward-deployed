# Use it: plan mode in a real harness

> **Motto** — Wire decomposition, plan mode, the todo list, and progress tracking into one workflow.

*Part of Phase 11 — Planning & Task Management. Completes the phase.*

## The Problem

You've built the pieces — task model (01), plan-mode gate (02), decomposition prompt (03),
progress tracker (04). The payoff is a single workflow a Claude Code / Codex user runs on any
non-trivial task: **decompose → review in plan mode → execute with verification → re-plan on
stall**. This lesson packages that as a skill.

## The Concept

<style>
.dgm-pmp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-pmp-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-pmp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-pmp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-pmp-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-pmp-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-pmp-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-pmp-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-pmp-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-pmp-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-pmp-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-pmp-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-pmp{padding:20px 16px 18px}.dgm-pmp-row{flex-direction:column}}
.dgm-pmp-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-pmp-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-pmp-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-pmp-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-pmp-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-pmp-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-pmp-b.accent h6{color:#0d5c0d}
.dgm-pmp-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-pmp-b.blue h6{color:#0550ae}
.dgm-pmp-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-pmp-b.green h6{color:#1a614f}
.dgm-pmp-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-pmp-b.red h6{color:#82061e}
.dgm-pmp-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-pmp-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-pmp{padding:20px 16px 18px}.dgm-pmp-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-pmp">
  <span class="dgm-pmp-chip">Decompose, approve, execute, verify — and re-plan if it stalls</span>
  <h4>The full loop from Phase 11 in one diagram</h4>
  <p class="dgm-pmp-sub">A stalled run goes back to decomposition, not straight to giving up.</p>
  <div class="dgm-pmp-row">
    <div class="dgm-pmp-n neutral">Goal</div>
    <span class="dgm-pmp-arr">→</span>
    <div class="dgm-pmp-n accent">Decompose → plan</div>
  </div>
  <div class="dgm-pmp-q">Approve (plan mode)?</div>
  <div class="dgm-pmp-branches">
    <div class="dgm-pmp-b red">
      <h6>No</h6>
      <p>Back to decompose</p>
    </div>
    <div class="dgm-pmp-b green">
      <h6>Yes</h6>
      <p>Execute step, verify (progress)</p>
    </div>
  </div>
  <div class="dgm-pmp-q">All complete?</div>
  <div class="dgm-pmp-branches">
    <div class="dgm-pmp-b accent">
      <h6>No, stalled</h6>
      <p>Back to decompose</p>
    </div>
    <div class="dgm-pmp-b green">
      <h6>Yes</h6>
      <p>Done</p>
    </div>
  </div>
</div>


## Build It / Use It

The artifact is `outputs/SKILL.md` — a `/plan-and-build` skill that runs the loop using this
phase's discipline. It produces a decomposed plan, then stops in plan mode for approval.
After approval, it executes each step and checks it off only when verification passes.
If a step stalls, it re-plans.

## Use It

Install the skill and run `/plan-and-build "<goal>"` in Claude Code / Codex. It enforces the
habits this phase teaches: plan before acting, keep a visible todo list, verify each step,
and re-plan instead of grinding. For most users, this is the single highest-leverage workflow. It turns "the agent went off
and did something" into "the agent and I agreed on a plan, and I watched it land."

## Ship It

[`outputs/SKILL.md`](../../05-plan-mode-in-practice/outputs/SKILL.md) — a `/plan-and-build`
skill composing the phase.

## Check Yourself

**Q1.** The plan-and-build loop's order is…

- A) act, then plan
- B) decompose → approve (plan mode) → execute with verification → re-plan on stall
- C) execute → verify → decompose
- D) random

<details><summary>Answer</summary>B — plan first, verify throughout, re-plan when
stuck.</details>

**Q2.** Why is this the highest-leverage workflow for a coding-agent user?

- A) it's fastest
- B) it gives a checkpoint before work and verified progress during it
- C) it uses fewer tokens
- D) no reason

<details><summary>Answer</summary>B — alignment up front + real progress.</details>

**Challenge.** Extend the skill so that, for a large goal, it offers to dispatch independent
steps in parallel (Phase 10 waves) instead of sequentially.

## Related

- Builds on: the whole phase
- Scales to: Phase 10 — Orchestration
- Phase complete → next: Phase 12 — [MCP & Extensibility](../../../../ROADMAP.md)
- [Roadmap](../../../../ROADMAP.md)
