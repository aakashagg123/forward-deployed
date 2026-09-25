# A Todo/Task data model

> **Motto** — A long task is a list of small ones with status — give the agent that list.

*Part of Phase 11 — Planning & Task Management.*

## The Problem

On a multi-step task, an agent without an explicit task list drifts: it forgets a step,
repeats one, or declares victory early. A structured **todo model** — items with a status
and order — gives the agent, and you, a shared, visible plan. The agent works through the
plan and updates it, so progress is legible and nothing is silently dropped.

## The Concept

<style>
.dgm-tm{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-tm-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-tm h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-tm-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-tm-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-tm-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-tm-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-tm-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-tm-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-tm-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-tm-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-tm-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-tm{padding:20px 16px 18px}.dgm-tm-row{flex-direction:column}}
</style>
<div class="dgm-tm">
  <span class="dgm-tm-chip">A todo list is just a loop with visible state</span>
  <h4>Pending, in_progress, completed — three states, one item worked at a time</h4>
  <p class="dgm-tm-sub">Updating status is what makes progress visible to whoever's watching the run.</p>
  <div class="dgm-tm-row">
    <div class="dgm-tm-n neutral">Goal</div>
    <span class="dgm-tm-arr">→</span>
    <div class="dgm-tm-n accent">Todo list: [pending, in_progress, completed]</div>
    <span class="dgm-tm-arr">→</span>
    <div class="dgm-tm-n blue">Work the next pending item</div>
    <span class="dgm-tm-arr">→</span>
    <div class="dgm-tm-n green">Update its status</div>
  </div>
</div>


Exactly one item `in_progress` at a time keeps focus. Statuses make "what's left" obvious.

## Build It

`code/todo.py` — a minimal task list with a single-in-progress invariant:

```python
from dataclasses import dataclass, field

@dataclass
class Task:
    id: int
    text: str
    status: str = "pending"        # pending | in_progress | completed

@dataclass
class TodoList:
    tasks: list = field(default_factory=list)

    def add(self, text):
        self.tasks.append(Task(len(self.tasks) + 1, text))

    def start(self, tid):
        for t in self.tasks:
            if t.status == "in_progress":
                raise ValueError("finish the in-progress task first")
        self._get(tid).status = "in_progress"

    def complete(self, tid):
        self._get(tid).status = "completed"

    def next_pending(self):
        return next((t for t in self.tasks if t.status == "pending"), None)

    def _get(self, tid):
        return next(t for t in self.tasks if t.id == tid)

    def render(self):
        mark = {"pending": "[ ]", "in_progress": "[~]", "completed": "[x]"}
        return "\n".join(f"{mark[t.status]} {t.text}" for t in self.tasks)
```

```python
todo = TodoList()
for s in ["read code", "write fix", "run tests"]:
    todo.add(s)
todo.start(1); todo.complete(1); todo.start(2)
print(todo.render())
```

The single-in-progress rule is what keeps a long run from fragmenting into half-done
threads.

## Use It

This is Claude Code's **todo list** (the checklist you see it maintain) and Codex's plan.
The agent writes the plan, marks one item in progress, completes it, and moves on — and
you can watch it happen. As a user, asking the agent to "make a plan first" on a big task
triggers exactly this pattern. It gives you a checkpoint to correct course before the
agent builds the wrong thing.

## Ship It

[`code/todo.py`](../../01-todo-model/code/todo.py) — a todo list with a single-in-progress
invariant.

## Check Yourself

**Q1.** Why allow only one task in progress at a time?

- A) it's simpler to code
- B) it keeps focus and prevents fragmenting into half-done threads
- C) the API requires it
- D) no reason

<details><summary>Answer</summary>B — one in-progress item keeps the run coherent.</details>

**Q2.** What does an explicit todo list give the *user*?

- A) nothing
- B) a legible plan and a checkpoint to correct course before work is done wrong
- C) faster output
- D) lower cost

<details><summary>Answer</summary>B — visibility and a steering point.</details>

**Challenge.** Add task dependencies (a task can't start until its deps are completed) and a
`next_actionable()` that respects them — echoing the wave planner from Phase 10.

## Related

- Builds on: Phase 9 — [Scratchpad](../../../09-memory-and-persistence/01-scratchpad/docs/en.md)
- Next: [Plan mode: propose before you act](../../02-plan-mode/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
