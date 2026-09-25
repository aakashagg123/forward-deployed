# Task decomposition prompts

> **Motto** — A good plan is small, ordered, verifiable steps — prompt the model to produce exactly that.

*Part of Phase 11 — Planning & Task Management.*

## The Problem

"Add authentication" is not a plan — it's a wish. The quality of the agent's work depends on
how well it decomposes a fuzzy goal into concrete, ordered, independently-verifiable steps.
Left to improvise, models produce plans that are too coarse ("implement the feature") or too
fine (50 trivial steps). A decomposition *prompt* steers the model to the right grain.

## The Concept

<style>
.dgm-dec{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-dec-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-dec h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-dec-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-dec-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-dec-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-dec-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-dec-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-dec-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-dec-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-dec-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-dec-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-dec{padding:20px 16px 18px}.dgm-dec-row{flex-direction:column}}
</style>
<div class="dgm-dec">
  <span class="dgm-dec-chip">Fuzzy goal in, verifiable steps out</span>
  <h4>A decomposition prompt turns one vague ask into three to seven small ordered steps</h4>
  <p class="dgm-dec-sub">Each step has to be independently verifiable — that's what progress tracking checks against.</p>
  <div class="dgm-dec-row">
    <div class="dgm-dec-n neutral">Fuzzy goal</div>
    <span class="dgm-dec-arr">→</span>
    <div class="dgm-dec-n accent">Decomposition prompt</div>
    <span class="dgm-dec-arr">→</span>
    <div class="dgm-dec-n green">3–7 steps: each small, ordered, verifiable</div>
  </div>
</div>


The rubric for a good step: it changes one coherent thing, has a clear done-check, and is
ordered by dependency.

## Build It (the prompt)

The artifact is a reusable decomposition prompt. `outputs/decompose.md` instructs the model
to output a numbered plan where each step names the change, the files, and the verification:

- 3–7 steps (merge trivial ones, split giant ones).
- Each step: **what** changes, **where** (files), **how to verify** (test/command).
- Order by dependency.
- Flag steps that need human input.
- End with the overall acceptance check.

This maps directly onto the todo model (lesson 01) and, scaled up, the sprint contract
(Phase 10).

## Use It

In Claude Code / Codex you trigger this by asking the agent to "plan first" (often in plan
mode, lesson 02). Putting a decomposition rubric in `CLAUDE.md`/`AGENTS.md` makes *every*
plan well-formed without re-asking. A good decomposition is also what makes parallelization
(Phase 10 waves) possible — independent steps can run concurrently.

## Ship It

[`outputs/decompose.md`](../../03-decomposition/outputs/decompose.md) — a task-decomposition
prompt that yields small, ordered, verifiable steps.

## Check Yourself

**Q1.** What makes a step in a good plan?

- A) it's vague enough to be flexible
- B) it changes one coherent thing, names files, and has a done-check, ordered by dependency
- C) it's as large as possible
- D) it has no verification

<details><summary>Answer</summary>B — small, located, verifiable, ordered.</details>

**Q2.** Why does good decomposition enable parallelization (Phase 10)?

- A) it doesn't
- B) independent, well-bounded steps can run concurrently in waves
- C) it makes steps bigger
- D) no reason

<details><summary>Answer</summary>B — independence is what waves exploit.</details>

**Challenge.** Add to the prompt a requirement that each step declare the files it touches,
so you can detect conflicts (Phase 10) before dispatching steps in parallel.

## Related

- Builds on: [Todo model](../../01-todo-model/docs/en.md)
- Next: [Progress tracking & self-correction](../../04-progress-tracking/docs/en.md)
- Scales to: Phase 10 — sprint contracts
- [Roadmap](../../../../ROADMAP.md)
