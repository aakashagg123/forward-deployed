"""The agent loop from scratch — no SDK, no framework, just the three invariants.

Run:  python3 agent_loop.py
"""

MAX_STEPS = 10


def user(text):
    return {"role": "user", "content": text}


def assistant(text):
    return {"role": "assistant", "content": text}


def tool_result(name, out):
    return {"role": "tool", "name": name, "content": out}


# A tool is just a named Python function.
TOOLS = {
    "add": lambda a, b: str(a + b),
    "read_file": lambda path: open(path).read()[:500],
}


def run(query, model):
    """Drive a stateless `model` (messages -> message) until it stops asking for tools."""
    history = [user(query)]
    for _step in range(MAX_STEPS):
        msg = model(history)                              # messages -> message
        history.append(assistant(msg["text"]))
        if not msg["tool_calls"]:                         # invariant 3: termination
            return msg["text"]
        for call in msg["tool_calls"]:                    # invariant 2: harness runs tools
            fn = TOOLS.get(call["name"])
            try:
                out = fn(**call["args"]) if fn else f"error: no tool {call['name']}"
            except Exception as e:                        # errors go back as data
                out = f"error: {e}"
            history.append(tool_result(call["name"], out))  # invariant 1: history is memory
    return "stopped: hit MAX_STEPS"


def fake_model(history):
    """A scripted 'model' so the loop logic is provable without an LLM."""
    n = sum(1 for m in history if m["role"] == "tool")
    if n == 0:
        return {"text": "Let me add them.",
                "tool_calls": [{"name": "add", "args": {"a": 2, "b": 3}}]}
    return {"text": f"The answer is {history[-1]['content']}.", "tool_calls": []}


if __name__ == "__main__":
    print(run("what is 2 + 3?", fake_model))
