"""Supervisor and workers with bounded roles.

The supervisor holds the plan. Each worker gets only its allowlisted context
and returns a short Result, never its transcript.

Run:  python3 code/supervisor.py
"""
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

# What each role may see. Enforced when the prompt is built, not by asking nicely.
ROLE_ALLOWLIST = {
    "worker":   ["task", "files"],
    "reviewer": ["diff"],                 # never the plan or the spec
}


def build_context(role, store):
    """Copy only the allowed keys out of the shared store."""
    return {k: store[k] for k in ROLE_ALLOWLIST[role] if k in store}


@dataclass
class Result:
    task: str
    ok: bool
    output: str


class Supervisor:
    def __init__(self, run_worker, max_workers=3):
        self.run_worker = run_worker      # (context dict) -> output string
        self.max_workers = max_workers

    def decompose(self, goal):
        """Toy decomposition. A real supervisor asks the model for sub-tasks."""
        return [t.strip() for t in goal.split(";") if t.strip()]

    def _one(self, task, store):
        ctx = build_context("worker", {**store, "task": task})
        try:
            return Result(task, True, self.run_worker(ctx))
        except Exception as e:            # a crash stays inside one Result
            return Result(task, False, f"{type(e).__name__}: {e}")

    def dispatch(self, tasks, store):
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            return list(pool.map(lambda t: self._one(t, store), tasks))

    def aggregate(self, results):
        ok = [r for r in results if r.ok]
        return {"completed": [r.task for r in ok],
                "failed": [r.task for r in results if not r.ok],
                "summary": f"{len(ok)}/{len(results)} tasks succeeded"}

    def run(self, goal, store=None):
        store = store or {}
        return self.aggregate(self.dispatch(self.decompose(goal), store))


if __name__ == "__main__":
    store = {"spec": "SECRET SPEC", "plan": "SECRET PLAN", "diff": "- old\n+ new",
             "files": ["api.py"]}

    # 1. Role allowlists: the reviewer cannot see intent.
    assert build_context("reviewer", store) == {"diff": "- old\n+ new"}
    assert set(build_context("worker", {**store, "task": "t"})) == {"task", "files"}

    # 2. Workers see only their task, so the plan never leaks into a worker.
    seen, lock = [], threading.Lock()
    active = peak = 0

    def worker(ctx):
        global active, peak
        with lock:
            active += 1
            peak = max(peak, active)
            seen.append(ctx)
        threading.Event().wait(0.05)      # let the threads overlap
        with lock:
            active -= 1
        if "fail" in ctx["task"]:
            raise RuntimeError("boom")
        return f"did {ctx['task']}"

    sup = Supervisor(worker, max_workers=2)
    out = sup.run("add route; add model; fail step", store)
    print(out)

    # 3. A failing worker is isolated; the others still finish.
    assert out["completed"] == ["add route", "add model"]
    assert out["failed"] == ["fail step"]
    assert all("plan" not in c and "spec" not in c for c in seen)
    # 4. Concurrency never passes the cap, and it really is concurrent.
    assert peak == 2
    print("supervisor: all checks passed")
