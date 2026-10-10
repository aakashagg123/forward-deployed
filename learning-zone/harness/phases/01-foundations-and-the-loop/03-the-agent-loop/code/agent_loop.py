"""The agent loop: call the model, run its tools, feed results back, repeat.

History uses the same block shapes as the Messages API, so the loop ports to the SDK.
Runs offline with a scripted model:  python3 code/agent_loop.py
"""
import json
import re

MAX_STEPS = 10
TOOLS = {"add": lambda a, b: a + b}                     # a tool is a named function


def text_of(content):
    return "".join(b["text"] for b in content if b["type"] == "text")


def tool_use(call_id, name, **args):
    return {"type": "tool_use", "id": call_id, "name": name, "input": args}


def parse_text_calls(text):
    """Fallback for a model with no native tool blocks: find add({"a": 2}) in plain text."""
    calls = []
    for i, m in enumerate(re.finditer(r"(\w+)\((\{.*?\})\)", text)):
        try:
            calls.append(tool_use(f"text_{i}", m.group(1), **json.loads(m.group(2))))
        except json.JSONDecodeError:
            pass                                        # skip junk instead of crashing
    return calls


def act(calls, tools):
    """Run EVERY tool_use block. Return one tool_result per call. Failures are data."""
    results = []
    for call in calls:
        try:
            fn = tools.get(call["name"])
            if fn is None:
                raise LookupError(f"no tool named {call['name']!r}; have {sorted(tools)}")
            out, is_error = str(fn(**call["input"])), False
        except Exception as exc:                        # bad args, tool crash, unknown tool
            out, is_error = f"{type(exc).__name__}: {exc}", True
        results.append({"type": "tool_result", "tool_use_id": call["id"],
                        "content": out, "is_error": is_error})
    return results


def check_pairing(history):
    """Each tool_use must be answered by a tool_result in the very next user message."""
    for i, msg in enumerate(history):
        if msg["role"] != "assistant" or isinstance(msg["content"], str):
            continue
        asked = sorted(b["id"] for b in msg["content"] if b["type"] == "tool_use")
        nxt = history[i + 1]["content"] if i + 1 < len(history) else []
        got = sorted(b["tool_use_id"] for b in nxt
                     if isinstance(nxt, list) and b["type"] == "tool_result")
        if asked and asked != got:
            raise ValueError(f"tool_use {asked} not answered by tool_result {got}")


def run(query, model, tools=TOOLS, max_steps=MAX_STEPS):
    """Drive a stateless model: messages -> {"stop_reason", "content"}."""
    history = [{"role": "user", "content": query}]     # history is the only memory
    for _ in range(max_steps):                         # a step ceiling always ends the loop
        check_pairing(history)
        msg = model(history)
        history.append({"role": "assistant", "content": msg["content"]})
        calls = [b for b in msg["content"] if b["type"] == "tool_use"]
        if msg["stop_reason"] != "tool_use" or not calls:
            return text_of(msg["content"]), history
        history.append({"role": "user", "content": act(calls, tools)})  # all results, one turn
    return "stopped: hit max_steps", history


def scripted_model(history):
    """A deterministic stand-in for the model. It reads history like the real one."""
    last = history[-1]["content"]
    if isinstance(last, str):                           # first turn: two independent calls
        return {"stop_reason": "tool_use", "content": [
            {"type": "text", "text": "I will add both pairs."},
            tool_use("t1", "add", a=2, b=3), tool_use("t2", "add", a=10, b=20)]}
    answer = ", ".join(r["content"] for r in last)
    return {"stop_reason": "end_turn", "content": [{"type": "text", "text": answer}]}


if __name__ == "__main__":
    answer, hist = run("add 2+3 and 10+20", scripted_model)
    assert answer == "5, 30", answer
    assert [m["role"] for m in hist] == ["user", "assistant", "user", "assistant"]
    assert len(hist[2]["content"]) == 2                 # both results came back together
    check_pairing(hist)

    # errors are data: the loop survives an unknown tool and bad arguments
    bad = [tool_use("x1", "nope"), tool_use("x2", "add", a=1)]
    res = act(bad, TOOLS)
    assert all(r["is_error"] for r in res)
    assert "no tool named 'nope'" in res[0]["content"] and "missing" in res[1]["content"]

    # a stuck model cannot loop forever
    stuck = lambda h: {"stop_reason": "tool_use", "content": [tool_use("s", "add", a=1, b=1)]}
    out, hist = run("go", stuck, max_steps=3)
    assert out == "stopped: hit max_steps" and len(hist) == 7

    # the pairing check catches a dropped result
    broken = [{"role": "user", "content": "q"},
              {"role": "assistant", "content": [tool_use("t9", "add", a=1, b=2)]},
              {"role": "user", "content": "forgot the result"}]
    try:
        check_pairing(broken)
        raise SystemExit("pairing check missed a dropped result")
    except ValueError:
        pass

    calls = parse_text_calls('I will call add({"a": 2, "b": 3}) and bad({oops}).')
    assert [(c["name"], c["input"]) for c in calls] == [("add", {"a": 2, "b": 3})]
    print("ok:", answer)
