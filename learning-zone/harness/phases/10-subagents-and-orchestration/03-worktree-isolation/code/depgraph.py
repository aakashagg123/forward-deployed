"""Dependency-graph wave planning with file-conflict detection and worktree commands.

Run:  python3 depgraph.py
"""
from dataclasses import dataclass, field


@dataclass
class Task:
    name: str
    files: list
    deps: list = field(default_factory=list)


def detect_conflicts(tasks):
    """Return (a, b, shared_files) for independent tasks that share a file."""
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
                wave.append(t)
                used |= set(t.files)
        if not wave:
            raise ValueError("cycle or unsplittable file conflict")
        for t in wave:
            remaining.remove(t)
            done.add(t.name)
        waves.append(wave)
    return waves


def worktree_cmds(task, base="feature-head"):
    branch = f"task/{task.name}"
    return [f"git worktree add -b {branch} ../wt-{task.name} {base}"]


if __name__ == "__main__":
    tasks = [
        Task("api", ["api/routes.py"]),
        Task("model", ["api/models.py"]),
        Task("ui", ["web/app.tsx"], deps=["api"]),
        Task("routes2", ["api/routes.py"]),          # shares a file with `api`
    ]
    print("conflicts:", detect_conflicts(tasks))     # api vs routes2 on api/routes.py
    waves = plan_waves(tasks)
    for i, w in enumerate(waves, 1):
        print(f"wave {i}:", [t.name for t in w])     # conflicting tasks land in diff waves
    print("worktree:", worktree_cmds(tasks[0])[0])
