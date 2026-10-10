"""Sprint contract, waves, file isolation, real parallel workers, checkpoints.

Run:  python3 code/orchestrator.py
"""
import json
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Budget:                      # example values live in outputs/sprint-contract.json
    max_workers: int
    max_calls_per_worker: int
    max_waves: int


@dataclass
class Task:
    name: str
    files: list                    # files this task owns
    deps: list = field(default_factory=list)


@dataclass
class Contract:
    sprint_name: str
    tasks: list
    budget: Budget
    acceptance: list


def load_contract(path):
    d = json.loads(Path(path).read_text())
    return Contract(d["sprint_name"], [Task(**t) for t in d["tasks"]],
                    Budget(**d["budget"]), d["acceptance"])


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


class BudgetExceeded(Exception):
    pass


class CallMeter:
    """Counts a worker's calls. The ceiling is hard: it never extends itself."""
    def __init__(self, limit):
        self.limit, self.used = limit, 0

    def tick(self):
        self.used += 1
        if self.used > self.limit:
            raise BudgetExceeded(f"over {self.limit} calls")


def worktree_cmds(task, base="main"):
    """The git commands that give one worker its own working tree (not run here)."""
    return [f"git worktree add -b task/{task.name} ../wt-{task.name} {base}"]


def run_sprint(contract, run_worker, approve, cont, ckpt_dir):
    if not approve(contract):                                  # spec-first gate
        return "halted: contract not approved"
    waves, b = plan_waves(contract.tasks), contract.budget
    if len(waves) > b.max_waves:                               # hard ceiling
        return f"halted: {len(waves)} waves > max_waves={b.max_waves}"
    ckpt = Path(ckpt_dir)
    for i, wave in enumerate(waves, 1):
        if len(wave) > b.max_workers:
            return f"halted: wave {i} needs {len(wave)} workers > max_workers"
        todo = [t for t in wave if not (ckpt / f"{t.name}.json").exists()]  # resume

        def one(t):
            meter = CallMeter(b.max_calls_per_worker)
            try:
                out = run_worker(t, meter)
            except BudgetExceeded as e:
                return t.name, f"over budget: {e}"
            (ckpt / f"{t.name}.json").write_text(json.dumps({"task": t.name, "out": out}))
            return t.name, None

        with ThreadPoolExecutor(max_workers=b.max_workers) as pool:   # truly parallel
            failures = [(n, e) for n, e in pool.map(one, todo) if e]
        if failures:
            return f"halted in wave {i}: {failures}"
        if i < len(waves) and not cont(i):                     # HARD STOP between waves
            return f"stopped after wave {i} by human"
    return "sprint complete"


if __name__ == "__main__":
    contract = load_contract(Path(__file__).parent.parent / "outputs" / "sprint-contract.json")
    waves = plan_waves(contract.tasks)
    assert [[t.name for t in w] for w in waves] == [["api", "model"], ["ui"]]
    assert plan_waves([Task("a", ["x"]), Task("b", ["x"])]) == [[Task("a", ["x"])], [Task("b", ["x"])]]
    try:
        plan_waves([Task("a", ["x"], ["b"]), Task("b", ["y"], ["a"])])
        raise AssertionError("cycle not detected")
    except ValueError as e:
        assert "a, b" in str(e)

    barrier = threading.Barrier(2, timeout=2)   # breaks if the wave runs one after another
    def worker(task, meter):
        meter.tick()
        if task.name in ("api", "model"):
            barrier.wait()
        return f"did {task.name}"

    with tempfile.TemporaryDirectory() as d:
        assert run_sprint(contract, worker, lambda c: True, lambda i: True, d) == "sprint complete"
        assert sorted(p.stem for p in Path(d).glob("*.json")) == ["api", "model", "ui"]
        ran = []                                # resume: finished tasks are skipped
        assert run_sprint(contract, lambda t, m: ran.append(t.name), lambda c: True,
                          lambda i: True, d) == "sprint complete" and ran == []

    with tempfile.TemporaryDirectory() as d:
        assert run_sprint(contract, worker, lambda c: False, lambda i: True, d).startswith("halted")
        assert run_sprint(contract, worker, lambda c: True, lambda i: False, d) \
            .startswith("stopped after wave 1")

    def greedy(task, meter):
        for _ in range(99):
            meter.tick()
    with tempfile.TemporaryDirectory() as d:
        assert "over budget" in run_sprint(contract, greedy, lambda c: True, lambda i: True, d)

    contract.budget.max_waves = 1
    with tempfile.TemporaryDirectory() as d:
        assert "max_waves" in run_sprint(contract, worker, lambda c: True, lambda i: True, d)
    print(worktree_cmds(contract.tasks[0])[0])
    print("orchestrator: all checks passed")
