# The Todo List

> **Motto** — A long task is a list of small ones with status, and a step is done only when its check passes.

*Part of Phase 07 — Planning and Subagents.*

*Last reviewed: 2026-10 · Volatility: fast*

## The Problem

On a task with many steps, an agent drifts. It forgets a step. It repeats one. It declares victory early. Two failures are common.

First, the agent marks a step done when it never passed its check. That is false progress. Second, a step fails and the agent retries it forever. That is grinding.

A **todo list** fixes both. It is a list of steps with a status. The harness owns the list, so you and the agent see the same plan. The harness also decides when a step counts as done.

## The Concept

<style>
.dgm-tm{background:var(--color-surface);border:1px solid var(--color-border);border-top:3px solid var(--color-border-success-outline);
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgb(var(--shadow-color) / 0.04),0 8px 24px rgb(var(--shadow-color) / 0.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-tm-chip{position:absolute;top:-11px;left:24px;background:var(--color-background-success-solid);color:var(--white);
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px color-mix(in oklab, var(--color-background-success-solid) 28%, transparent)}
.dgm-tm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:var(--color-text-secondary)}
.dgm-tm-sub{font-size:12px;color:var(--color-text-secondary);margin:0 0 16px}
.dgm-tm-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-tm-n{background:var(--color-surface-tertiary);border:1px solid var(--color-border);border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:var(--color-text);line-height:1.3}
.dgm-tm-n.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline);color:var(--color-text-success)}
.dgm-tm-n.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface);color:var(--color-text-info)}
.dgm-tm-n.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface);color:var(--color-text-success)}
.dgm-tm-n.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface);color:var(--color-text-danger)}
.dgm-tm-arr{color:var(--color-text-tertiary);font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-tm-arr .lbl{font-size:8.5px;font-weight:700;color:var(--color-text-tertiary);text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-tm{padding:20px 16px 18px}.dgm-tm-row{flex-direction:column}}
.dgm-tm-q{background:var(--color-surface-tertiary);border:1px dashed var(--color-border);border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:var(--color-text);margin-bottom:10px}
.dgm-tm-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:10px}
.dgm-tm-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-tm-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-tm-b p{margin:0;font-size:10px;color:var(--color-text-secondary);line-height:1.35}
.dgm-tm-b.accent{background:var(--color-background-success-surface);border-color:var(--color-border-success-outline)}
.dgm-tm-b.accent h6{color:var(--color-text-success)}
.dgm-tm-b.blue{background:var(--color-background-info-surface);border-color:var(--color-border-info-surface)}
.dgm-tm-b.blue h6{color:var(--color-text-info)}
.dgm-tm-b.green{background:var(--color-background-success-surface);border-color:var(--color-border-success-surface)}
.dgm-tm-b.green h6{color:var(--color-text-success)}
.dgm-tm-b.red{background:var(--color-background-danger-surface);border-color:var(--color-border-danger-surface)}
.dgm-tm-b.red h6{color:var(--color-text-danger)}
.dgm-tm-b.neutral{background:var(--color-surface-tertiary);border-color:var(--color-border)}
.dgm-tm-b.neutral h6{color:var(--color-text)}
@media (max-width:640px){.dgm-tm-branches{grid-template-columns:1fr}}
.dgm-tm-branches.three{grid-template-columns:repeat(3,1fr)}
@media (max-width:640px){.dgm-tm-branches.three{grid-template-columns:1fr}}
</style>
<div class="dgm-tm">
  <span class="dgm-tm-chip">A todo list is a loop with a check</span>
  <h4>Four statuses, one step in_progress, a gate before done</h4>
  <p class="dgm-tm-sub">The agent cannot mark a step completed by saying so. A check must pass.</p>
  <div class="dgm-tm-row">
    <div class="dgm-tm-n neutral">Goal</div>
    <span class="dgm-tm-arr">→</span>
    <div class="dgm-tm-n accent">Todo list: pending, in_progress, completed, needs_replan</div>
    <span class="dgm-tm-arr">→</span>
    <div class="dgm-tm-n blue">Start next pending step (one in progress)</div>
  </div>
  <div class="dgm-tm-q" style="margin-top:12px">Done-check passes?</div>
  <div class="dgm-tm-branches three">
    <div class="dgm-tm-b green">
      <h6>Yes</h6>
      <p>completed, then back to the list</p>
    </div>
    <div class="dgm-tm-b neutral">
      <h6>No, retries left</h6>
      <p>back to the list</p>
    </div>
    <div class="dgm-tm-b red">
      <h6>No, retries spent</h6>
      <p>needs_replan: change the approach</p>
    </div>
  </div>
</div>


Four statuses cover everything: `pending`, `in_progress`, `completed`, `needs_replan`.

Two rules keep the list honest. Only one step is `in_progress` at a time, so work does not split into half-done threads. And the agent cannot mark a step `completed` by saying so. A check must pass. After a set number of failures, the step goes to `needs_replan` and the agent or the human changes the approach.

## Build It

`code/todo.py` holds the whole model. The `start` method enforces the single in-progress rule:

```python
    def start(self, tid):
        if any(t.status == "in_progress" for t in self.tasks):
            raise ValueError("finish the in-progress task first")
        self._get(tid).status = "in_progress"
```

The `finish` method takes a `verify` function. The harness calls it, not the model:

```python
    def finish(self, tid, verify):
        """Mark done only if the done-check passes. Else count a failure."""
        task = self._get(tid)
        if verify():
            task.status = "completed"
        else:
            task.failures += 1
            # Out of retries: stop grinding and hand the step back for re-planning.
            task.status = "needs_replan" if task.failures >= self.max_failures else "pending"
        return task.status
```

A passing check completes the step. A failing check sends it back to `pending` for one more try. A second failure (the default `max_failures=2`) sets `needs_replan`, and `next_pending` skips it. The file ends with asserts that prove each rule: a second `start` raises, a failed check never completes a step, and the list moves past a stuck step.

In a real harness, `verify` runs a test command or a file check. Do not let `verify` be a model opinion. A model that grades its own work passes it too often.

## Use It

Claude Code has task tools for this: `TaskCreate`, `TaskGet`, `TaskList` and `TaskUpdate`. The model creates tasks, updates their status as it works, and lists them again to see what is left. They are on by default only for some older models (background and cloud sessions get them on every model). On newer models, turn them on with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`. Check the tools reference for your version.

The tools store the list. They do not run your done-checks. You add that part yourself. Put it in your instructions ("run the tests before you mark a step complete"), or enforce it with a hook (see [Hooks](../../../06-permissions-and-security/02-hooks/docs/en.md)).

When you start a big task, ask for a plan first. The list gives you a checkpoint. You can correct the course before the agent builds the wrong thing.

## Challenge

Add dependencies to `Task` (a list of task ids). Write `next_actionable()` so a step cannot start until all its dependencies are `completed`. Assert that a step blocked by a `needs_replan` dependency is never returned. [Lesson 03](../../03-contract-waves-and-isolation/docs/en.md) uses the same idea to order work.

## Sources

Claude Code docs, "Tools reference" (code.claude.com/docs).

Next: [Plan mode](../../02-plan-mode/docs/en.md)
