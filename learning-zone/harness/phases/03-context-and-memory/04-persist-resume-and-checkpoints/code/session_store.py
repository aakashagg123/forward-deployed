"""Save and resume a session: history + scratchpad, plus phase checkpoints.

Run:  python3 code/session_store.py
"""
import json
import os
import tempfile


def atomic_write(path, data):
    """Write to a temp file, then rename. A process crash never leaves a half-written file. For power-loss safety, also call `os.fsync` before the rename."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)))
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)                        # one atomic step
    except BaseException:
        os.unlink(tmp)
        raise


def read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


class Scratchpad:
    """Structured working notes, kept outside the message history."""
    def __init__(self, notes=None):
        self.notes = dict(notes or {})

    def set(self, key, value):
        self.notes[key] = value
        return f"noted {key}"

    def get(self, key, default=None):
        return self.notes.get(key, default)

    def summary(self):
        return "\n".join(f"- {k}: {v}" for k, v in self.notes.items()) or "(empty)"


class SessionStore:
    def __init__(self, path):
        self.path = path

    def save(self, history, scratch):
        atomic_write(self.path, {"history": history, "scratch": scratch.notes})
        return f"saved {len(history)} messages"

    def load(self):
        data = read_json(self.path, {})
        return data.get("history", []), Scratchpad(data.get("scratch"))


def run_task(path, phases):
    """Run phases in order. Skip any phase the checkpoint file records as done."""
    state = read_json(path, {"done": []})
    for name, work in phases:
        if name in [d["phase"] for d in state["done"]]:
            continue
        result = work()                              # may raise: the crash case
        state["done"].append({"phase": name, "changes": result})
        atomic_write(path, state)                    # checkpoint after every phase
    return state


if __name__ == "__main__":
    tmp = tempfile.mkdtemp()
    store = SessionStore(os.path.join(tmp, "session.json"))
    history = [{"role": "user", "content": "fix the bug"},
               {"role": "assistant", "content": [
                   {"type": "tool_use", "id": "tu_1", "name": "read", "input": {"path": "a.py"}}]},
               {"role": "user", "content": [
                   {"type": "tool_result", "tool_use_id": "tu_1", "content": "def f(): ..."}]}]
    pad = Scratchpad()
    pad.set("editing", "a.py")
    print(store.save(history, pad))

    # 1. Resume restores history (with its tool pair) and the scratchpad exactly.
    h2, pad2 = store.load()
    assert h2 == history and pad2.get("editing") == "a.py"
    assert h2[1]["content"][0]["id"] == h2[2]["content"][0]["tool_use_id"]

    # 2. A crash in the middle of a save leaves the last good file readable.
    real_dump = json.dump

    def dying_dump(obj, f, **kw):
        f.write('{"history": [{"role": "us')         # half a file, then the process dies
        raise OSError("disk pulled")

    json.dump = dying_dump
    try:
        store.save([{"role": "user", "content": "new"}], Scratchpad())
    except OSError:
        pass
    finally:
        json.dump = real_dump
    h3, pad3 = store.load()
    assert h3 == history and pad3.get("editing") == "a.py"
    assert os.listdir(tmp) == ["session.json"]       # no temp file left behind

    # 3. A missing file is an empty session, not an error.
    assert SessionStore(os.path.join(tmp, "none.json")).load()[0] == []

    # 4. A run that crashes in phase 3 resumes there and does not redo phases 1 and 2.
    calls, ckpt = [], os.path.join(tmp, "task.json")

    def step(name, fail=False):
        def work():
            calls.append(name)
            if fail:
                raise RuntimeError("crash")
            return f"{name} ok"
        return work

    try:
        run_task(ckpt, [("scaffold", step("scaffold")), ("implement", step("implement")),
                        ("test", step("test", fail=True))])
    except RuntimeError:
        pass
    state = run_task(ckpt, [("scaffold", step("scaffold")), ("implement", step("implement")),
                            ("test", step("test"))])
    assert calls == ["scaffold", "implement", "test", "test"]      # phases 1-2 ran once
    assert [d["phase"] for d in state["done"]] == ["scaffold", "implement", "test"]
    print("resume ok:", calls)
