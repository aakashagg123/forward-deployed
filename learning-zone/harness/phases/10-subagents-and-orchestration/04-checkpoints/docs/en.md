# Checkpoints & resumable runs

> **Motto** — Resume from the last checkpoint, never from zero.

*Part of Phase 10 — Subagents & Orchestration. Concept:
[The Ten Principles of a Working Harness](../../../../foundations/harness-principles.md)
(principle 10).*

## The Problem

A wave is half done — three of five workers finished — when the run is interrupted: a
crash, a timeout, a closed laptop. Without checkpoints, resuming means re-running the
*entire* wave. That redoes work that already landed and can duplicate side effects.
This is the most expensive class of harness failure because it scales with how much you'd
already accomplished. The fix: each worker records progressive checkpoints, and the
orchestrator reads them to skip completed work on resume.

## The Concept

<style>
.dgm-chk{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-chk-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-chk h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-chk-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-chk-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-chk-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-chk-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-chk-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-chk-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-chk-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-chk-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-chk-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-chk{padding:20px 16px 18px}.dgm-chk-row{flex-direction:column}}
.dgm-chk-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-chk-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-chk-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-chk-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-chk-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-chk-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-chk-b.accent h6{color:#0d5c0d}
.dgm-chk-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-chk-b.blue h6{color:#0550ae}
.dgm-chk-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-chk-b.green h6{color:#1a614f}
.dgm-chk-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-chk-b.red h6{color:#82061e}
.dgm-chk-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-chk-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-chk{padding:20px 16px 18px}.dgm-chk-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-chk">
  <span class="dgm-chk-chip">A checkpoint is a resumable line in the sand</span>
  <h4>Written after every phase, read back only if the run was interrupted</h4>
  <p class="dgm-chk-sub">Resuming means skipping every phase a checkpoint already confirmed as done.</p>
  <div class="dgm-chk-row">
    <div class="dgm-chk-n neutral">Worker phase done</div>
    <span class="dgm-chk-arr">→</span>
    <div class="dgm-chk-n accent">Write checkpoint.md (phase, changes, next)</div>
  </div>
  <div class="dgm-chk-q">Interrupted?</div>
  <div class="dgm-chk-branches">
    <div class="dgm-chk-b red">
      <h6>Yes</h6>
      <p>Resume: read checkpoints, skip done phases</p>
    </div>
    <div class="dgm-chk-b green">
      <h6>No</h6>
      <p>Next phase</p>
    </div>
  </div>
</div>


A checkpoint records three things: **what phase completed**, **what changed**, and
**what's next**. On resume, the orchestrator reads each task's checkpoint and dispatches
only the unfinished work.

## Build It

`code/checkpoint.py` — write/read checkpoints and a resumable runner:

```python
import json, os

def write_checkpoint(task, phase, changes, nxt, root=".checkpoints"):
    os.makedirs(root, exist_ok=True)
    path = os.path.join(root, f"{task}.json")
    data = {"task": task, "phase": phase, "changes": changes, "next": nxt}
    with open(path, "w") as f:
        json.dump(data, f)
    return path

def read_checkpoint(task, root=".checkpoints"):
    path = os.path.join(root, f"{task}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def run_task(task, phases, root=".checkpoints"):
    """Run phases in order, skipping any already recorded as complete."""
    cp = read_checkpoint(task, root)
    done = cp["phase"] if cp else None
    started = done is None
    for phase, work in phases:
        if not started:
            if phase == done:                  # resume *after* the last completed phase
                started = True
            continue
        result = work()
        write_checkpoint(task, phase, result, nxt=None, root=root)
    return read_checkpoint(task, root)
```

```python
phases = [("scaffold", lambda: "files created"),
          ("implement", lambda: "logic added"),
          ("test", lambda: "tests pass")]
# First run completes scaffold+implement, then "crashes" before test:
# (simulate by writing a checkpoint at 'implement', then resuming)
write_checkpoint("api", "implement", "logic added", nxt="test")
print(run_task("api", phases)["phase"])     # -> "test"  (only the last phase ran)
```

On resume, `scaffold` and `implement` are skipped. Only `test` runs. An interrupted run
costs you the *current* phase, not the whole task.

## Use It

In Claude Code, this maps to per-task workspace files (e.g. `checkpoint.md`,
`file-changes.md` under `.claude-workspace/`). A worker subagent writes its checkpoint
after each meaningful phase. The orchestrator reads it before resuming an interrupted
task. The data model you built here is exactly what those files encode.

## Ship It

[`code/checkpoint.py`](../../04-checkpoints/code/checkpoint.py) — checkpoint write/read and
a resumable task runner.

## Check Yourself

**Q1.** What three things does a useful checkpoint record?

- A) timestamp, author, model
- B) the phase completed, what changed, and what's next
- C) tokens, cost, latency
- D) just a "done" flag

<details><summary>Answer</summary>B — enough to resume intelligently and to audit the
trail.</details>

**Q2.** After resuming, the runner should…

- A) re-run every phase to be safe
- B) skip phases already recorded complete and run only the rest
- C) start a brand-new task
- D) ask the model what to do

<details><summary>Answer</summary>B — that's the entire point of checkpointing.</details>

**Challenge.** Make checkpoints atomic: write to a temp file and `os.replace` it. That
way, an interruption *during* the checkpoint write can't leave a corrupt half-written
file.

## Related

- Builds on: [Sprint contracts & budgeted waves](../../01-sprint-contract-and-waves/docs/en.md)
- Next: [Supervisor / worker patterns](../../05-supervisor-worker/docs/en.md)
- Deepens in: Phase 9 — Memory & Persistence
