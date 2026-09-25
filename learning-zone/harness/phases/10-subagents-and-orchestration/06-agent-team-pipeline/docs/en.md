# Use it: the agent-team pipeline

> **Motto** — Wire the contract, roles, dependency graph, checkpoints, and review into one skill.

*Part of Phase 10 — Subagents & Orchestration. Builds on lessons 01–05 and completes the phase.*

## The Problem

You've built every piece separately: the budgeted-wave orchestrator (01), bounded roles
(02), worktree isolation and the dependency graph (03), checkpoints (04), and the
supervisor pattern (05). On their own they're modules. Assembled, they're a **pipeline**:
a repeatable, auditable process that takes a goal and produces reviewed, merged code with
a memory of what was learned. This lesson wires them into a single Claude Code skill. A
human runs `/agent-team "build X"` and gets the whole disciplined flow.

## The Concept

<style>
.dgm-atp{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-atp-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-atp h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-atp-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-atp-chain{display:flex;flex-direction:column;gap:2px}
.dgm-atp-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-atp-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-atp-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-atp{padding:20px 16px 18px}}
.dgm-atp-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-atp-branches{display:grid;grid-template-columns:repeat(1,1fr);gap:10px}
.dgm-atp-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-atp-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-atp-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-atp-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-atp-b.accent h6{color:#0d5c0d}
.dgm-atp-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-atp-b.blue h6{color:#0550ae}
.dgm-atp-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-atp-b.green h6{color:#1a614f}
.dgm-atp-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-atp-b.red h6{color:#82061e}
.dgm-atp-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-atp-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-atp{padding:20px 16px 18px}.dgm-atp-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-atp">
  <span class="dgm-atp-chip">Six roles, one human gate, one hard stop</span>
  <h4>Plan → approve → discover → build in worktrees → review → stop for the human → remember</h4>
  <p class="dgm-atp-sub">The review agent only ever sees the diff, and ships only at or above a 70 bar.</p>
  <div class="dgm-atp-chain">
    <div class="dgm-atp-node accent">/agent-team 'goal'</div>
    <div class="dgm-atp-arr">↓</div>
    <div class="dgm-atp-node alt">Planning agent → sprint contract + arch options</div>
  </div>
  <div class="dgm-atp-q">Human approves contract?</div>
  <div class="dgm-atp-branches">
    <div class="dgm-atp-b red">
      <h6>No</h6>
      <p>Halt</p>
    </div>
  </div>
  <div class="dgm-atp-chain">
    <div class="dgm-atp-node accent">Discovery agent → codebase map + dep graph</div>
    <div class="dgm-atp-arr">↓</div>
    <div class="dgm-atp-node alt">Worker agents in worktrees (disjoint files per wave)</div>
    <div class="dgm-atp-arr">↓</div>
    <div class="dgm-atp-node accent">Review agent (diff only) → ship / hold (≥70)</div>
    <div class="dgm-atp-arr">↓</div>
    <div class="dgm-atp-node alt">Wave summary + HARD STOP → human: continue?</div>
    <div class="dgm-atp-arr">↓</div>
    <div class="dgm-atp-node accent">Memory agent → append to knowledge.md</div>
  </div>
</div>


Five agents, each with a bounded role. Budgets and hard stops come from lesson 01, file
isolation from lesson 03, and checkpoints from lesson 04. The skill is the glue.

## Build It (the skill definition)

The pipeline is encoded as `outputs/SKILL.md` — a Claude Code skill that orchestrates
five subagents. It declares each agent's inputs/outputs (legibility: the pipeline is
discoverable from the repo), the budget defaults, and the wave discipline. The Python
modules from lessons 01–05 are the reference implementation of its control logic. The
skill expresses the same logic for a real agent runtime.

Key wiring decisions, each tracing to an earlier lesson:

| Pipeline step | Backed by |
| --- | --- |
| Sprint contract + approval gate | Lesson 01 (`Contract`, `approve`) |
| Each agent sees only its inputs | Lesson 02 (`ROLE_ALLOWLIST`) |
| Workers get disjoint files in worktrees | Lesson 03 (`plan_waves`, `worktree_cmds`) |
| Resumable interrupted waves | Lesson 04 (`checkpoint`) |
| Decompose → dispatch → aggregate | Lesson 05 (`Supervisor`) |
| Diff-only review, score ≥ 70 | Phase 15 (Evals) |
| Append-only learnings | Phase 9 (Memory), `knowledge.md` |

## Use It

Install the skill and run it:

```bash
cp outputs/SKILL.md .claude/skills/agent-team/SKILL.md
# in Claude Code:
/agent-team "add a health-check route returning {status: ok}"
```

The planning agent emits a contract, and you approve it. Workers run in isolated
worktrees. The reviewer returns ship or hold. The wave halts for your "continue". The
memory agent records what was learned. Every principle from the
[ten principles](../../../../foundations/harness-principles.md) is now mechanical.

## Ship It

[`outputs/SKILL.md`](../../06-agent-team-pipeline/outputs/SKILL.md) — the installable
agent-team pipeline skill.

## Check Yourself

**Q1.** Why encode the pipeline as a skill in the repo rather than a Slack/Notion doc?

- A) it looks nicer
- B) legibility — the pipeline is discoverable and auditable from the repo itself
- C) to save tokens
- D) skills run faster

<details><summary>Answer</summary>B — the repo explains itself. An agent (or human) finds
the process without external context.</details>

**Q2.** The review agent in the pipeline receives…

- A) the contract, plan, and diff
- B) the diff only
- C) the full worker transcripts
- D) the memory file

<details><summary>Answer</summary>B — bounded roles (lesson 02). Independent review needs
the diff alone.</details>

**Challenge.** Extend the skill with a `dry-run` that prints the wave plan, per-wave
worker count, and file ownership *before* dispatch, so a human can sanity-check the
contract against the budget.

## Related

- Concept: [The ten principles of a working harness](../../../../foundations/harness-principles.md)
- Builds on: lessons [01](../../01-sprint-contract-and-waves/docs/en.md)–[05](../../05-supervisor-worker/docs/en.md)
- Next phases: Phase 15 — Evals (the review agent), Phase 9 — Memory (`knowledge.md`)
