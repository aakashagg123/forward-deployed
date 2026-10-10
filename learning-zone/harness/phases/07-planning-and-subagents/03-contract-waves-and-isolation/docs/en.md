# Contract, Waves and Isolation

> **Motto** — Lock the contract, declare the budget, give each worker its own files, and stop between waves for a human.

*Part of Phase 07 — Planning and Subagents.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

One subagent is easy. Several agents on one repo is where harnesses fail.

Two workers edit `api/routes.py`. The later one overwrites the earlier one. No error appears. A run loops far past its purpose and spends real money. An interrupted run restarts from zero. Nobody approved what got built.

A smarter prompt does not fix this. Structure does. A **contract** fixes the target and the budget before any worker starts. **Waves** group the work so that no two workers share a file. A hard stop between waves lets a human decide.

## The Concept

<style>
.dgm-scw{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-scw-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-scw h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-scw-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-scw-chain{display:flex;flex-direction:column;gap:2px}
.dgm-scw-node{background:var(--color-background-success-surface);border:1.5px solid var(--color-border-success-outline);border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:var(--color-text-success)}
.dgm-scw-node.alt{background:var(--color-surface-tertiary);border-color:var(--color-border);color:var(--color-text)}
.dgm-scw-arr{display:flex;justify-content:center;color:var(--color-text-tertiary);padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-scw{padding:20px 16px 18px}}
.dgm-scw-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-scw-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-scw-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-scw-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-scw-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-scw-b.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline)}
.dgm-scw-b.accent h6{color:var(--color-text-success)}
.dgm-scw-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-scw-b.blue h6{color:var(--color-text-info)}
.dgm-scw-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-scw-b.green h6{color:var(--color-text-success)}
.dgm-scw-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-scw-b.red h6{color:var(--color-text-danger)}
.dgm-scw-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-scw-b.neutral h6{color:var(--color-text)}
@media (max-width:640px){.dgm-scw{padding:20px 16px 18px}.dgm-scw-branches{grid-template-columns:1fr}}
.dgm-scw-par{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}
.dgm-scw-w{background:var(--color-surface);border:1px solid var(--color-border-success-surface);border-radius:7px;padding:3px 8px;font-size:9.5px;font-weight:700;color:var(--color-text-success)}
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
      <p>Dependency graph → file ownership → dispatch wave: workers in parallel, disjoint files</p>
      <div class="dgm-scw-par"><span class="dgm-scw-w">Worker 1</span><span class="dgm-scw-w">Worker 2</span><span class="dgm-scw-w">Worker 3</span></div>
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


Four rules hold the design together.

1. **No worker runs until a human approves the contract.**
2. **The budget is a hard ceiling.** Workers, calls per worker and waves are all capped. Hitting a cap stops the run. It never extends itself.
3. **No two workers in a wave share a file.** A task also waits for its dependencies.
4. **Each worker writes a checkpoint.** A rerun skips finished work.

## Build It

The contract is data. `outputs/sprint-contract.json` holds one. Its numbers (3 workers, 15 calls per worker, 2 waves) are example values. Set your own from your task size and cost limit.

`plan_waves` is the core. It builds each wave from tasks whose dependencies are done and whose files do not overlap with the wave so far. If it cannot place any task, it names the stuck tasks:

```python
def plan_waves(tasks):
    """Group tasks so no wave shares a file and every dependency lands first."""
    done, waves, remaining = set(), [], list(tasks)
    while remaining:
        wave, used = [], set()
        for t in remaining:
            if set(t.deps) <= done and not (set(t.files) & used):
                wave.append(t)
                used |= set(t.files)
        if not wave:
            raise ValueError("cycle in deps: " + ", ".join(t.name for t in remaining))
        for t in wave:
            remaining.remove(t)
            done.add(t.name)
        waves.append(wave)
    return waves
```

Two tasks that own the same file land in different waves, even with no declared dependency. That is the guard against silent overwrite.

`run_sprint` runs each wave in a `ThreadPoolExecutor`, so the workers in a wave run at the same time. The test proves it. Two workers wait on a `threading.Barrier`. If the wave ran them one after another, the barrier would time out and the test would fail.

The worker is a stub that returns a string. The coordination is real: approval, budget, parallel dispatch, checkpoint files, resume, and the hard stop. A `CallMeter` raises `BudgetExceeded` when a worker passes its call limit, and the sprint halts.

For file isolation on disk, each worker needs its own working tree. `worktree_cmds` prints the `git worktree add` command for each task. The demo does not run it.

## Use It

Claude Code subagents map to this design. A subagent is a Markdown file in `.claude/agents/` with YAML frontmatter. Each one runs in its own context window and returns only its final report to the parent.

Set `isolation: worktree` in the frontmatter and the subagent works in its own git worktree, so parallel edits cannot touch the same tree. The `maxTurns` field caps its turns, which plays the role of the call budget.

Claude Code has no built-in "wave" command. Treat the wave plan as your own process. Approve the contract, start one wave, read the summaries, then start the next. The hard stop is you.

## Challenge

Add a `dry_run=True` option to `run_sprint`. It should print each wave and its worker count and return without calling any worker. Assert that no checkpoint file exists afterward.

## Sources

Claude Code docs, "Subagents" (code.claude.com/docs).

Next: [Supervisor and workers](../../04-supervisor-and-workers/docs/en.md)
