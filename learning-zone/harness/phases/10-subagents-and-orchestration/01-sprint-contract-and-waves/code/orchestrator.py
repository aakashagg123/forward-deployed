"""A from-scratch orchestrator: sprint contracts, budgeted waves, file isolation.

Implements harness principles 01 (spec-first), 03 (budget), 04 (hard stops),
06 (file isolation), 10 (checkpoints). Agents are stubs so the coordination
logic is what's visible.

Run:  python3 orchestrator.py
"""
from dataclasses import dataclass, field


@dataclass
class Budget:
    max_workers: int = 3
    max_calls_per_worker: int = 15
    max_waves: int = 2


@dataclass
class Task:
    name: str
    files: list                                   # files this task owns
    deps: list = field(default_factory=list)      # task names it depends on


@dataclass
class Contract:
    sprint_name: str
    tasks: list
    budget: Budget
    acceptance: list


def plan_waves(tasks):
    """Group tasks into waves so no wave shares a file and deps land first."""
    done, waves, remaining = set(), [], list(tasks)
    while remaining:
        wave, used_files = [], set()
        for t in list(remaining):
            if set(t.deps) <= done and not (set(t.files) & used_files):
                wave.append(t)
                used_files |= set(t.files)
        if not wave:
            raise ValueError("cycle or unsplittable file conflict")
        for t in wave:
            remaining.remove(t)
            done.add(t.name)
        waves.append(wave)
    return waves


def run_sprint(contract, run_worker, approve, cont):
    if not approve(contract):                              # invariant 1: spec-first gate
        return "halted: contract not approved"
    waves = plan_waves(contract.tasks)
    b = contract.budget
    if len(waves) > b.max_waves:                           # invariant 2: budget ceiling
        return f"halted: {len(waves)} waves exceeds maxWaves={b.max_waves}"
    for i, wave in enumerate(waves, 1):
        if len(wave) > b.max_workers:
            return f"halted: wave {i} needs {len(wave)} workers > maxWorkers={b.max_workers}"
        checkpoints = []
        for t in wave:                                    # invariant 3: disjoint files
            checkpoints.append(run_worker(t, b.max_calls_per_worker))  # inv 4: checkpoint
        print(f"wave {i} summary: {[c['task'] for c in checkpoints]} done")
        if i < len(waves) and not cont(i):                # invariant 4: HARD STOP
            return f"stopped after wave {i} by human"
    return "sprint complete"


if __name__ == "__main__":
    tasks = [
        Task("api", ["api/routes.py"]),
        Task("model", ["api/models.py"]),
        Task("ui", ["web/app.tsx"], deps=["api"]),        # waits for wave 2
    ]
    contract = Contract("health-check", tasks, Budget(), ["GET /health -> {status: ok}"])
    result = run_sprint(
        contract,
        run_worker=lambda t, n: {"task": t.name, "phase": "done", "next": None},
        approve=lambda c: True,
        cont=lambda i: True,
    )
    print(result)
