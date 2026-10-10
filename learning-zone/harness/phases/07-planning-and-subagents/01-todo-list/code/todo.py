"""A todo list with a single-in-progress rule and verified completion.

Run:  python3 code/todo.py
"""
from dataclasses import dataclass, field


@dataclass
class Task:
    id: int
    text: str
    status: str = "pending"   # pending | in_progress | completed | needs_replan
    failures: int = 0


@dataclass
class TodoList:
    max_failures: int = 2
    tasks: list = field(default_factory=list)

    def add(self, text):
        self.tasks.append(Task(len(self.tasks) + 1, text))

    def start(self, tid):
        if any(t.status == "in_progress" for t in self.tasks):
            raise ValueError("finish the in-progress task first")
        self._get(tid).status = "in_progress"

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

    def next_pending(self):
        return next((t for t in self.tasks if t.status == "pending"), None)

    def _get(self, tid):
        return next(t for t in self.tasks if t.id == tid)

    def render(self):
        mark = {"pending": "[ ]", "in_progress": "[~]", "completed": "[x]", "needs_replan": "[!]"}
        return "\n".join(f"{mark[t.status]} {t.text}" for t in self.tasks)


if __name__ == "__main__":
    todo = TodoList(max_failures=2)
    for s in ["read code", "write fix", "run tests"]:
        todo.add(s)

    todo.start(1)
    assert todo.finish(1, verify=lambda: True) == "completed"

    todo.start(2)
    try:
        todo.start(3)                         # a second in-progress task must be refused
        raise AssertionError("single in-progress rule not enforced")
    except ValueError:
        pass

    assert todo.finish(2, verify=lambda: False) == "pending"        # failure 1: retry
    assert todo.next_pending().id == 2
    todo.start(2)
    assert todo.finish(2, verify=lambda: False) == "needs_replan"   # failure 2: re-plan
    assert todo.next_pending().id == 3        # the list moves on past the stuck step
    print(todo.render())
