"""Checkpoints & resumable runs: skip completed phases after an interruption.

A checkpoint records the completed phase, what changed, and what's next.
On resume, the runner runs only the phases after the last completed one.

Run:  python3 checkpoint.py
"""
import json
import os


def write_checkpoint(task, phase, changes, nxt, root=".checkpoints"):
    os.makedirs(root, exist_ok=True)
    path = os.path.join(root, f"{task}.json")
    with open(path, "w") as f:
        json.dump({"task": task, "phase": phase, "changes": changes, "next": nxt}, f)
    return path


def read_checkpoint(task, root=".checkpoints"):
    path = os.path.join(root, f"{task}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def run_task(task, phases, root=".checkpoints"):
    """Run phases in order, skipping any already recorded as complete."""
    cp = read_checkpoint(task, root)
    done = cp["phase"] if cp else None
    started = done is None
    for phase, work in phases:
        if not started:
            if phase == done:                  # resume *after* the last completed phase
                started = True
            continue
        result = work()
        write_checkpoint(task, phase, result, nxt=None, root=root)
    return read_checkpoint(task, root)


if __name__ == "__main__":
    import shutil
    root = ".checkpoints_demo"
    shutil.rmtree(root, ignore_errors=True)

    phases = [("scaffold", lambda: "files created"),
              ("implement", lambda: "logic added"),
              ("test", lambda: "tests pass")]

    # Simulate a run that completed through "implement", then was interrupted:
    write_checkpoint("api", "implement", "logic added", nxt="test", root=root)
    final = run_task("api", phases, root=root)        # only "test" should run now
    print("resumed to phase:", final["phase"])        # -> test
    shutil.rmtree(root, ignore_errors=True)
