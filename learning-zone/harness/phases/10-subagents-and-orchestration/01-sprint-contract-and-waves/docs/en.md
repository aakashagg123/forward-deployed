# Sprint contracts & budgeted waves

> **Motto** — Lock the contract, declare the budget, dispatch a wave, then stop and let a human decide.

*Part of Phase 10 — Subagents & Orchestration. Concept reading:
[The Ten Principles of a Working Harness](../../../../foundations/harness-principles.md)
(principles 01, 03, 04, 06, 10).*

## The Problem

Spawning one subagent is easy (previous lessons). Coordinating *several* against the
same repo is where harnesses go wrong. Two workers edit the same file and silently
overwrite each other. A run loops 40 times and spends $12. An interrupted wave has to
restart from zero. Nobody approved what got built. The fix isn't a smarter prompt — it's
structure: a **contract** that fixes the target and budget before dispatch, and **waves**
that hard-stop for a human between them.

## The Concept

<style>
.dgm-scw{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-scw-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-scw h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-scw-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-scw-chain{display:flex;flex-direction:column;gap:2px}
.dgm-scw-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-scw-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-scw-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-scw{padding:20px 16px 18px}}
.dgm-scw-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-scw-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-scw-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-scw-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-scw-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-scw-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-scw-b.accent h6{color:#0d5c0d}
.dgm-scw-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-scw-b.blue h6{color:#0550ae}
.dgm-scw-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-scw-b.green h6{color:#1a614f}
.dgm-scw-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-scw-b.red h6{color:#82061e}
.dgm-scw-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-scw-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-scw{padding:20px 16px 18px}.dgm-scw-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-scw">
  <span class="dgm-scw-chip">A human gate before every wave, a budget check inside it</span>
  <h4>Plan, approve, dispatch a wave, checkpoint, then stop for the human again</h4>
  <p class="dgm-scw-sub">The loop only continues if a human says so after every wave summary.</p>
  <div class="dgm-scw-chain">
    <div class="dgm-scw-node accent">Spec → plan → sprint contract</div>
  </div>
  <div class="dgm-scw-q">Human approves?</div>
  <div class="dgm-scw-branches">
    <div class="dgm-scw-b red">
      <h6>No</h6>
      <p>Halt</p>
    </div>
    <div class="dgm-scw-b green">
      <h6>Yes</h6>
      <p>Dependency graph → file ownership → dispatch wave (zero shared files)</p>
    </div>
  </div>
  <div class="dgm-scw-q">Budget hit?</div>
  <div class="dgm-scw-branches">
    <div class="dgm-scw-b red">
      <h6>Yes</h6>
      <p>Report &amp; halt</p>
    </div>
    <div class="dgm-scw-b accent">
      <h6>No</h6>
      <p>Checkpoint each worker → wave summary + HARD STOP</p>
    </div>
  </div>
  <div class="dgm-scw-q">Human: continue?</div>
  <div class="dgm-scw-branches">
    <div class="dgm-scw-b green">
      <h6>Yes</h6>
      <p>Next wave</p>
    </div>
    <div class="dgm-scw-b neutral">
      <h6>No</h6>
      <p>End</p>
    </div>
  </div>
</div>


Four invariants, straight from the principles:

1. **Spec first (01):** no worker runs until a contract is approved.
2. **Budget upfront (03):** `maxWorkers / maxCallsPerWorker / maxWaves` are declared.
   Hitting any ceiling stops the run — it never auto-extends.
3. **File isolation (06):** the dependency graph assigns each worker disjoint files.
   Anything with an unresolved dependency waits for the next wave.
4. **Hard stops + checkpoints (04, 10):** each wave ends with a summary and waits for
   an explicit "continue." Every worker writes a checkpoint, so an interrupted run
   resumes instead of restarting.

## Build It

A real orchestrator, standard library only. The agents are stubs, so the *coordination*
is what you can see. `code/orchestrator.py`:

```python
from dataclasses import dataclass, field

@dataclass
class Budget:
    max_workers: int = 3
    max_calls_per_worker: int = 15
    max_waves: int = 2

@dataclass
class Task:
    name: str
    files: list          # files this task owns
    deps: list = field(default_factory=list)   # task names it depends on

@dataclass
class Contract:
    sprint_name: str
    tasks: list
    budget: Budget
    acceptance: list

def plan_waves(tasks):
    """Group tasks into waves so no wave shares a file and deps land first."""
    done, waves = set(), []
    remaining = list(tasks)
    while remaining:
        wave, used_files = [], set()
        for t in list(remaining):
            if set(t.deps) <= done and not (set(t.files) & used_files):
                wave.append(t); used_files |= set(t.files)
        if not wave:
            raise ValueError("cycle or unsplittable file conflict")
        for t in wave:
            remaining.remove(t); done.add(t.name)
        waves.append(wave)
    return waves

def run_sprint(contract, run_worker, approve, cont):
    if not approve(contract):                       # invariant 1: spec-first gate
        return "halted: contract not approved"
    waves = plan_waves(contract.tasks)
    b = contract.budget
    if len(waves) > b.max_waves:                    # invariant 2: budget ceiling
        return f"halted: {len(waves)} waves exceeds maxWaves={b.max_waves}"
    for i, wave in enumerate(waves, 1):
        if len(wave) > b.max_workers:
            return f"halted: wave {i} needs {len(wave)} workers > maxWorkers"
        checkpoints = []
        for t in wave:                              # invariant 3: disjoint files
            cp = run_worker(t, b.max_calls_per_worker)   # invariant 4: checkpoint
            checkpoints.append(cp)
        print(f"wave {i} summary: {[c['task'] for c in checkpoints]} done")
        if i < len(waves) and not cont(i):          # invariant 4: HARD STOP
            return f"stopped after wave {i} by human"
    return "sprint complete"
```

Driving it with stubs proves the structure (`__main__` in the file):

```python
tasks = [
    Task("api",   ["api/routes.py"]),
    Task("model", ["api/models.py"]),
    Task("ui",    ["web/app.tsx"], deps=["api"]),   # waits for wave 2
]
contract = Contract("health-check", tasks, Budget(), ["GET /health -> {status: ok}"])
run_sprint(contract,
           run_worker=lambda t, n: {"task": t.name, "phase": "done", "next": None},
           approve=lambda c: True,
           cont=lambda i: True)
# wave 1 summary: ['api', 'model'] done   (disjoint files, no deps)
# wave 2 summary: ['ui'] done             (ui waited for api)
# sprint complete
```

`plan_waves` is the heart. It refuses to put two tasks that touch the same file in the
same wave, and it holds back tasks whose dependencies haven't landed.

## Use It

In a real harness the stubs become Claude Code subagents and git worktrees. The
contract becomes `_agent-team/sprint-contract.json`. `approve`/`cont` become the human
gates. `run_worker` spawns an agent in its own worktree and reads back its
`checkpoint.md`. The deck's `/agent-team` skill is exactly this orchestrator, wired to
the planning, discovery, worker, review, and memory agents. See `outputs/` for the
contract template and the one-shot setup prompt that generates the whole pipeline.

## Ship It

This lesson ships two artifacts:

- [`outputs/sprint-contract-template.json`](../outputs/sprint-contract-template.json) —
  the contract every sprint fills in before dispatch.
- [`outputs/agent-team-setup-prompt.md`](../outputs/agent-team-setup-prompt.md) — the
  one-shot prompt that generates `CLAUDE.md`, the pipeline skill, hooks, reviewer
  prompt, and workspace.

## Check Yourself

**Q1.** Why must the reviewer agent see only the diff, not the plan?

- A) To save tokens
- B) Context leakage turns review into rationalising the author's intent
- C) The plan is secret
- D) It's faster

<details><summary>Answer</summary>B — principle 02. With the plan in hand, the reviewer
defends intent instead of judging the output on its own terms.</details>

**Q2.** Two tasks both edit `api/routes.py`. The orchestrator should…

- A) run them in parallel and merge later
- B) put them in different waves so they never share a file in one wave
- C) pick one and drop the other
- D) ask the model to resolve conflicts

<details><summary>Answer</summary>B — principle 06. Shared files across parallel workers
cause silent overwrites; `plan_waves` enforces disjoint file sets per wave.</details>

**Q3.** A run hits `maxWaves`. The correct behavior is…

- A) auto-extend by one wave
- B) stop and report — never auto-extend
- C) lower the budget and retry
- D) merge whatever's done

<details><summary>Answer</summary>B — principle 03. Ceilings are hard; the human
decides whether to spend more.</details>

**Challenge.** Add a `dry_run` mode that prints the wave plan and the per-wave worker
count *without* dispatching. This lets a human sanity-check file ownership against the
budget before approving the contract.

## Related

- Concept: [The Ten Principles of a Working Harness](../../../../foundations/harness-principles.md)
- Builds on: [The Agent Loop from Scratch](../../../02-the-agent-loop/01-agent-loop/docs/en.md)
- Next: adversarial review → [Phase 15 — Evals](../../../../ROADMAP.md); persistent memory → [Phase 9](../../../../ROADMAP.md)
