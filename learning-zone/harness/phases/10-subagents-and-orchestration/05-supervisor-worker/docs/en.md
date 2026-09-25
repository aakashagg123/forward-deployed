# Supervisor / worker patterns

> **Motto** — A supervisor decomposes and delegates — workers execute in isolation and report back.

*Part of Phase 10 — Subagents & Orchestration. Builds on lessons 01–04.*

## The Problem

A single agent doing everything in one context hits two walls. The context fills with
detail irrelevant to the current sub-task, and there's no parallelism. The
supervisor/worker pattern splits the roles: a supervisor that *plans and coordinates*
but writes no code, and workers that each own one isolated sub-task. The supervisor never
sees a worker's full transcript, only its result. This keeps each context small and lets
independent work run in parallel (within the budget from lesson 01).

## The Concept

<style>
.dgm-sw{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-sw-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-sw h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-sw-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-sw-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-sw-branches{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.dgm-sw-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-sw-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-sw-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-sw-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-sw-b.accent h6{color:#0d5c0d}
.dgm-sw-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-sw-b.blue h6{color:#0550ae}
.dgm-sw-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-sw-b.green h6{color:#1a614f}
.dgm-sw-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-sw-b.red h6{color:#82061e}
.dgm-sw-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-sw-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-sw{padding:20px 16px 18px}.dgm-sw-branches{grid-template-columns:1fr}}
.dgm-sw-chain{display:flex;flex-direction:column;gap:2px}
.dgm-sw-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-sw-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-sw-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-sw{padding:20px 16px 18px}}
</style>
<div class="dgm-sw">
  <span class="dgm-sw-chip">Fan out, then fan back in</span>
  <h4>The supervisor decomposes, dispatches isolated workers, and aggregates what comes back</h4>
  <p class="dgm-sw-sub">Workers never see each other — only the supervisor sees every result.</p>
  <div class="dgm-sw-chain">
    <div class="dgm-sw-node accent">Supervisor: decompose → tasks</div>
    <div class="dgm-sw-arr">↓</div>
    <div class="dgm-sw-node alt">Dispatch workers (isolated)</div>
  </div>
  <div class="dgm-sw-branches">
    <div class="dgm-sw-b blue">
      <h6>Worker 1</h6>
      <p>→ result</p>
    </div>
    <div class="dgm-sw-b green">
      <h6>Worker 2</h6>
      <p>→ result</p>
    </div>
    <div class="dgm-sw-b neutral">
      <h6>Worker 3</h6>
      <p>→ result</p>
    </div>
  </div>
  <div class="dgm-sw-chain">
    <div class="dgm-sw-node accent">Supervisor: aggregate results</div>
    <div class="dgm-sw-arr">↓</div>
    <div class="dgm-sw-node alt">Combined output</div>
  </div>
</div>


The supervisor holds the *plan*. Each worker holds only its *task*. Results flow back up
— not transcripts. This is bounded roles (lesson 02) applied to delegation.

## Build It

`code/supervisor.py` — a supervisor that decomposes, dispatches isolated workers, and
aggregates, reusing the wave planner for safety:

```python
from dataclasses import dataclass

@dataclass
class Result:
    task: str
    ok: bool
    output: str

class Supervisor:
    def __init__(self, run_worker, max_workers=3):
        self.run_worker = run_worker          # (task) -> Result, runs in isolation
        self.max_workers = max_workers

    def decompose(self, goal):
        """Toy decomposition: a real supervisor asks the model for sub-tasks."""
        return [t.strip() for t in goal.split(";") if t.strip()]

    def dispatch(self, tasks):
        results = []
        for batch_start in range(0, len(tasks), self.max_workers):
            batch = tasks[batch_start:batch_start + self.max_workers]
            results.extend(self.run_worker(t) for t in batch)   # isolated workers
        return results

    def aggregate(self, results):
        ok = [r for r in results if r.ok]
        return {"completed": [r.task for r in ok],
                "failed": [r.task for r in results if not r.ok],
                "summary": f"{len(ok)}/{len(results)} tasks succeeded"}

    def run(self, goal):
        return self.aggregate(self.dispatch(self.decompose(goal)))
```

```python
def worker(task):
    return Result(task=task, ok=("fail" not in task), output=f"did {task}")

sup = Supervisor(run_worker=worker, max_workers=2)
print(sup.run("add route; add model; fail step"))
# {'completed': ['add route', 'add model'], 'failed': ['fail step'],
#  'summary': '2/3 tasks succeeded'}
```

The supervisor only ever sees each worker's `Result`, never its internal steps.
Context stays small, and a failure stays isolated instead of spreading.

## Use It

In Claude Code this is the `Agent` tool: the parent (supervisor) spawns subagents with
scoped prompts and receives only their final message. Subagent *types* (e.g. an explore
agent, a plan agent) are specialized workers. The supervisor pattern you built is the
control structure underneath the agent-team pipeline (next lesson).

## Ship It

[`code/supervisor.py`](../../05-supervisor-worker/code/supervisor.py) — a `Supervisor` that
decomposes, dispatches isolated workers in batches, and aggregates results.

## Check Yourself

**Q1.** What does the supervisor receive back from a worker?

- A) the worker's full transcript
- B) only the worker's result
- C) nothing
- D) the worker's system prompt

<details><summary>Answer</summary>B — results flow up, not transcripts. This keeps the
supervisor's context small and bounded (lesson 02).</details>

**Q2.** Why batch worker dispatch by `max_workers`?

- A) to respect the budget ceiling and avoid unbounded parallelism
- B) to make it slower
- C) the model requires it
- D) to share files

<details><summary>Answer</summary>A — the budget from lesson 01 bounds concurrency.</details>

**Challenge.** Make `decompose` return tasks *with file ownership and deps*, then feed
them through `plan_waves` (lesson 03) so the supervisor dispatches conflict-free waves
instead of fixed-size batches.

## Related

- Builds on: [Bounded roles](../../02-bounded-roles/docs/en.md), [Worktree isolation](../../03-worktree-isolation/docs/en.md)
- Next: [Use It: the agent-team pipeline](../../06-agent-team-pipeline/docs/en.md)
