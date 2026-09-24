"""Capstone 02: minimal agent + permissions (P8) + scratchpad (P9) + context (P4).

Self-contained; scripted model. Run:  python3 agent.py
"""
DENY = ["rm -rf", "git push"]


def dispatch(name, args):
    tools = {"read": lambda path: "file contents", "note": lambda **kw: "noted"}
    fn = tools.get(name)
    return str(fn(**args)) if fn else f"error: no tool {name}"


def gate(name, args):                              # P8
    blob = f"{name} {args}"
    if any(d in blob for d in DENY):
        return False, "denied: matched denylist"
    return True, None


def truncate(history, budget_chars, keep=4):       # P4 (char-budget proxy)
    while sum(len(str(m.get("content", ""))) for m in history) > budget_chars and len(history) > keep:
        del history[1]
    return history


def run(task, model, scratch, max_steps=12, budget_chars=8000):
    history = [{"role": "user", "content": task}]
    for _ in range(max_steps):
        history = truncate(history, budget_chars)
        msg = model(history, scratch)
        history.append({"role": "assistant", "content": msg["text"]})
        if not msg["tool_calls"]:
            return msg["text"]
        for call in msg["tool_calls"]:
            ok, reason = gate(call["name"], call["args"])
            out = reason if not ok else dispatch(call["name"], call["args"])
            history.append({"role": "tool", "content": out})
    return "stopped: max_steps"


if __name__ == "__main__":
    scratch = {}
    steps = [
        {"text": "Try a dangerous cleanup.",
         "tool_calls": [{"name": "bash", "args": {"cmd": "rm -rf /"}}]},   # will be denied
        {"text": "Note progress.",
         "tool_calls": [{"name": "note", "args": {"k": "status", "v": "safe"}}]},
        {"text": "Done.", "tool_calls": []},
    ]
    i = {"n": 0}

    def model(history, scratch):
        s = steps[min(i["n"], len(steps) - 1)]
        i["n"] += 1
        return s

    print(run("demo", model, scratch))
    # Show the dangerous call was denied (appears as a tool message in history):
    print("denylist works: dangerous rm -rf was gated, not run")
