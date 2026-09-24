"""A todo list with a single-in-progress invariant. Run:  python3 todo.py"""
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
        if any(t.status == "in_progress" for t in self.tasks):
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


if __name__ == "__main__":
    todo = TodoList()
    for s in ["read code", "write fix", "run tests"]:
        todo.add(s)
    todo.start(1)
    todo.complete(1)
    todo.start(2)
    print(todo.render())
