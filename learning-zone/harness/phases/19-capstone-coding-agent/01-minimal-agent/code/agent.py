"""Minimal coding agent: loop (P2) + tools (P3) + files (P6) + shell (P7).

A scripted model stands in for the SDK so it runs offline and shows the full
read -> edit -> run cycle on a temp file. Run:  python3 agent.py
"""
import subprocess


def _edit(path, old, new):
    text = open(path).read()
    if text.count(old) != 1:
        return f"error: {text.count(old)} matches for old_string"
    open(path, "w").write(text.replace(old, new))
    return "ok: edited"


TOOLS = {
    "read": lambda path: open(path).read(),
    "edit": lambda path, old, new: _edit(path, old, new),
    "bash": lambda cmd: subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip(),
}


def dispatch(name, args):
    fn = TOOLS.get(name)
    if not fn:
        return f"error: no tool {name}"
    try:
        return str(fn(**args))
    except Exception as e:
        return f"error: {e}"


def run(task, model, max_steps=10):
    history = [{"role": "user", "content": task}]
    for _ in range(max_steps):
        msg = model(history)
        history.append({"role": "assistant", "content": msg["text"]})
        if not msg["tool_calls"]:
            return msg["text"]
        for call in msg["tool_calls"]:
            out = dispatch(call["name"], call["args"])
            history.append({"role": "tool", "content": out})
    return "stopped: max_steps"


def scripted_model(path):
    """A model that fixes a bug in `path` then runs it to verify."""
    steps = [
        {"text": "Read the file.", "tool_calls": [{"name": "read", "args": {"path": path}}]},
        {"text": "Fix the bug.",
         "tool_calls": [{"name": "edit", "args": {"path": path, "old": "a - b", "new": "a + b"}}]},
        {"text": "Run it.", "tool_calls": [{"name": "bash", "args": {"cmd": f"python3 {path}"}}]},
        {"text": "Done — output is 5.", "tool_calls": []},
    ]
    i = {"n": 0}

    def model(history):
        s = steps[min(i["n"], len(steps) - 1)]
        i["n"] += 1
        return s
    return model


if __name__ == "__main__":
    import tempfile
    import os
    path = tempfile.mktemp(suffix=".py")
    open(path, "w").write("def add(a, b):\n    return a - b\nprint(add(2, 3))\n")  # bug
    print(run(f"Fix the add() bug in {path} and verify", scripted_model(path)))
    print("file now:", open(path).read().splitlines()[1].strip())
    os.remove(path)
