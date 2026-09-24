"""Supervisor/worker: decompose a goal, dispatch isolated workers, aggregate results.

The supervisor holds the plan; each worker holds only its task and returns a
Result (not its transcript). Concurrency is bounded by max_workers.

Run:  python3 supervisor.py
"""
from dataclasses import dataclass


@dataclass
class Result:
    task: str
    ok: bool
    output: str


class Supervisor:
    def __init__(self, run_worker, max_workers=3):
        self.run_worker = run_worker           # (task) -> Result, runs in isolation
        self.max_workers = max_workers

    def decompose(self, goal):
        """Toy decomposition: a real supervisor asks the model for sub-tasks."""
        return [t.strip() for t in goal.split(";") if t.strip()]

    def dispatch(self, tasks):
        results = []
        for start in range(0, len(tasks), self.max_workers):
            batch = tasks[start:start + self.max_workers]
            results.extend(self.run_worker(t) for t in batch)    # isolated workers
        return results

    def aggregate(self, results):
        ok = [r for r in results if r.ok]
        return {
            "completed": [r.task for r in ok],
            "failed": [r.task for r in results if not r.ok],
            "summary": f"{len(ok)}/{len(results)} tasks succeeded",
        }

    def run(self, goal):
        return self.aggregate(self.dispatch(self.decompose(goal)))


if __name__ == "__main__":
    def worker(task):
        return Result(task=task, ok=("fail" not in task), output=f"did {task}")

    sup = Supervisor(run_worker=worker, max_workers=2)
    print(sup.run("add route; add model; fail step"))
