# Worktree isolation & the dependency graph

> **Motto** — Disjoint files per wave, derived from the dependency graph — no shared writes.

*Part of Phase 10 — Subagents & Orchestration. Concept:
[The Ten Principles of a Working Harness](../../../../foundations/harness-principles.md)
(principle 06).*

## The Problem

Two workers running in parallel both edit `api/routes.py`. One finishes, the other
finishes a moment later and overwrites the first — silently. No error, no conflict
marker, just lost work. This is the worst class of harness failure because nothing
*tells* you it happened. The prevention is structural. Derive which files each task owns
from a dependency graph, and never put two tasks that touch the same file in the same
wave. Give each worker its own git worktree so even the filesystem is isolated.

## The Concept

<style>
.dgm-wi{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-wi-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-wi h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-wi-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-wi-chain{display:flex;flex-direction:column;gap:2px}
.dgm-wi-node{background:#e6f5e6;border:1.5px solid #a8d8a8;border-radius:10px;padding:9px 14px;
  font-weight:700;font-size:11px;color:#0d5c0d}
.dgm-wi-node.alt{background:#f6f8fa;border-color:#d1d9e0;color:#1f2328}
.dgm-wi-arr{display:flex;justify-content:center;color:#8c959f;padding:1px 0;font-size:9.5px;text-align:center}
@media (max-width:640px){.dgm-wi{padding:20px 16px 18px}}
</style>
<div class="dgm-wi">
  <span class="dgm-wi-chip">Waves are just dependency depth</span>
  <h4>A wave is every task whose dependencies are already satisfied and whose files don't overlap</h4>
  <p class="dgm-wi-sub">Disjoint files inside a wave is what makes parallel workers safe without locking.</p>
  <div class="dgm-wi-chain">
    <div class="dgm-wi-node alt">Tasks + file ownership + deps</div>
    <div class="dgm-wi-arr">↓</div>
    <div class="dgm-wi-node accent">Dependency graph</div>
    <div class="dgm-wi-arr">↓</div>
    <div class="dgm-wi-node alt">Wave 1: disjoint files, no unmet deps</div>
    <div class="dgm-wi-arr">↓</div>
    <div class="dgm-wi-node accent">Wave 2: deps satisfied</div>
    <div class="dgm-wi-arr">↓</div>
    <div class="dgm-wi-node alt">…</div>
  </div>
</div>


Two rules turn a task list into safe waves:

1. **No shared files in a wave** — group so file ownership sets are disjoint.
2. **Dependencies land first** — a task waits until everything it depends on is done.

Each worker checks out its own `git worktree` off the feature head, so parallel edits
never touch the same working tree.

## Build It

`code/depgraph.py` — topological wave planning with file-conflict detection (the same
`plan_waves` from lesson 01, plus an explicit conflict check and worktree command
generation):

```python
def detect_conflicts(tasks):
    """Return pairs of independent tasks that share a file (would collide in parallel)."""
    bad = []
    for i, a in enumerate(tasks):
        for b in tasks[i + 1:]:
            if b.name not in a.deps and a.name not in b.deps:
                shared = set(a.files) & set(b.files)
                if shared:
                    bad.append((a.name, b.name, sorted(shared)))
    return bad

def plan_waves(tasks):
    done, waves, remaining = set(), [], list(tasks)
    while remaining:
        wave, used = [], set()
        for t in list(remaining):
            if set(t.deps) <= done and not (set(t.files) & used):
                wave.append(t); used |= set(t.files)
        if not wave:
            raise ValueError("cycle or unsplittable file conflict")
        for t in wave:
            remaining.remove(t); done.add(t.name)
        waves.append(wave)
    return waves

def worktree_cmds(task, base="feature-head"):
    branch = f"task/{task.name}"
    return [f"git worktree add -b {branch} ../wt-{task.name} {base}"]
```

`detect_conflicts` is the safety net: even if two same-file tasks lack a declared
dependency, the planner separates them across waves rather than risk a silent overwrite.

## Use It

In a real harness, `worktree_cmds` runs for real. Each worker gets `../wt-<task>` as its
working directory, edits only its owned files, and commits to its branch. Between waves,
the orchestrator merges the branches — that's where the review gate (Phase 15) decides
ship or hold. Git worktrees give you filesystem-level isolation for free, with no
containers required for the same-repo case.

## Ship It

[`code/depgraph.py`](../../03-worktree-isolation/code/depgraph.py) — conflict detection,
wave planning, and worktree command generation.

## Check Yourself

**Q1.** Two tasks with no declared dependency both own `db/schema.sql`. The planner should…

- A) run them in parallel; git will merge
- B) place them in different waves so they never edit it simultaneously
- C) drop one
- D) error and stop the whole sprint

<details><summary>Answer</summary>B — disjoint files per wave (principle 06). The
conflict detector forces the split.</details>

**Q2.** Why give each worker its own git worktree?

- A) to use less disk
- B) filesystem-level isolation so parallel edits can't touch the same working tree
- C) to avoid writing tests
- D) it's required by the SDK

<details><summary>Answer</summary>B — isolation is the point. Branches merge after the
wave.</details>

**Challenge.** Add cycle detection that names the tasks in the cycle (e.g. `a → b → a`)
instead of the generic error, so a bad contract is debuggable.

## Related

- Builds on: [Sprint contracts & budgeted waves](../../01-sprint-contract-and-waves/docs/en.md)
- Next: [Checkpoints & resumable runs](../../04-checkpoints/docs/en.md)
