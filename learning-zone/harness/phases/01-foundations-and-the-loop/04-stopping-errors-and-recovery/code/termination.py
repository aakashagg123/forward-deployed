"""Stopping, errors and recovery for the agent loop. Runs offline.

Run:  python3 code/termination.py
"""
import inspect
import time

TRANSIENT = ("timeout", "429", "503", "529", "connection")

# What the harness does for each stop_reason. Unknown reasons stop the loop.
ACTIONS = {"end_turn": "return", "stop_sequence": "return", "tool_use": "run_tools",
           "max_tokens": "continue", "pause_turn": "resume",
           "refusal": "stop", "model_context_window_exceeded": "stop"}


def next_action(stop_reason, has_calls):
    if stop_reason == "max_tokens" and has_calls:
        return "stop"                      # a cut-off tool call is incomplete: raise max_tokens
    return ACTIONS.get(stop_reason, "stop")


def classify(exc):
    """transient: retry. fatal: abort the run. tool: the model sees it and decides."""
    if isinstance(exc, PermissionError) or "unauthorized" in str(exc).lower():
        return "fatal"
    if any(t in str(exc).lower() for t in TRANSIENT):
        return "transient"
    return "tool"


def result(call, text, is_error):
    return {"type": "tool_result", "tool_use_id": call["id"],
            "content": text, "is_error": is_error}


def dispatch(call, tools, sleep=time.sleep, max_retries=2):
    """Run one tool_use block. Return (tool_result, fatal)."""
    fn = tools.get(call["name"])
    if fn is None:
        return result(call, f"no tool {call['name']!r}; have {sorted(tools)}", True), False
    try:
        inspect.signature(fn).bind(**call["input"])
    except TypeError as exc:               # the model can fix its own arguments
        return result(call, f"bad arguments: {exc}", True), False
    for attempt in range(max_retries + 1):
        try:
            return result(call, str(fn(**call["input"])), False), False
        except Exception as exc:
            kind = classify(exc)
            if kind == "transient" and attempt < max_retries:
                sleep(0.5 * 2 ** attempt)  # exponential backoff, bounded by max_retries
                continue
            return result(call, f"{kind} error: {exc}", True), kind == "fatal"


def signature(calls):
    return sorted((c["name"], str(sorted(c["input"].items()))) for c in calls)


def run(query, model, tools, max_steps=6, max_continues=2, sleep=time.sleep):
    history, last_sig, continues = [{"role": "user", "content": query}], None, 0
    for _ in range(max_steps):                               # hard ceiling
        msg = model(history)
        history.append({"role": "assistant", "content": msg["content"]})
        calls = [b for b in msg["content"] if b["type"] == "tool_use"]
        text = "".join(b["text"] for b in msg["content"] if b["type"] == "text")
        action = next_action(msg["stop_reason"], bool(calls))
        if action == "return":
            return text, "done", history
        if action == "continue":                             # output was cut off
            continues += 1
            if continues > max_continues:
                return text, "max_continues", history
            history.append({"role": "user", "content": "continue"})
            continue
        if action == "resume":                               # server tool paused: send it back
            continue
        if action != "run_tools":
            return text, f"stopped:{msg['stop_reason']}", history
        if signature(calls) == last_sig:                     # same calls as last step
            nudge = "You repeated this call. Try a different approach or finish."
            history.append({"role": "user", "content": [result(c, nudge, True) for c in calls]})
            continue                                         # a nudge is still a tool_result
        last_sig, results, fatal = signature(calls), [], False
        for call in calls:
            res, is_fatal = dispatch(call, tools, sleep)
            results.append(res)
            fatal = fatal or is_fatal
        history.append({"role": "user", "content": results})
        if fatal:
            return "aborted: fatal tool error", "fatal", history
    return "stopped: hit max_steps", "max_steps", history


def call_block(i, name, **args):
    return {"type": "tool_use", "id": f"t{i}", "name": name, "input": args}


def say(text, stop="end_turn", *blocks):
    return {"stop_reason": stop, "content": [{"type": "text", "text": text}, *blocks]}


def paired(history):
    """True if every tool_use is answered by a tool_result in the next message."""
    for i, m in enumerate(history):
        if m["role"] == "assistant":
            ids = sorted(b["id"] for b in m["content"] if b["type"] == "tool_use")
            nxt = history[i + 1]["content"] if i + 1 < len(history) else []
            got = sorted(b["tool_use_id"] for b in nxt
                         if isinstance(nxt, list) and b["type"] == "tool_result")
            if ids and ids != got:
                return False
    return True


if __name__ == "__main__":
    def replies(*items):
        it = iter(items)
        return lambda history: next(it)

    assert next_action("end_turn", False) == "return"
    assert next_action("max_tokens", False) == "continue"
    assert next_action("max_tokens", True) == "stop"
    assert next_action("something_new", False) == "stop"

    # transient failures retry with backoff, then succeed
    n, naps = [0], []
    def flaky():
        n[0] += 1
        if n[0] < 3:
            raise RuntimeError("connection timeout")
        return "ok"
    out, why, hist = run("go", replies(say("try", "tool_use", call_block(1, "flaky")), say("done")),
                         {"flaky": flaky}, sleep=naps.append)
    assert (out, why, n[0], naps) == ("done", "done", 3, [0.5, 1.0])

    # model-fixable errors come back as results and the model recovers
    tools = {"add": lambda a, b: a + b}
    bad = say("hm", "tool_use", call_block(1, "nope"), call_block(2, "add", a=1))
    out, why, hist = run("go", replies(bad, say("fixed")), tools)
    errs = hist[2]["content"]
    assert why == "done" and all(e["is_error"] for e in errs) and paired(hist)
    assert "no tool" in errs[0]["content"] and "bad arguments" in errs[1]["content"]

    # a repeated call is nudged, and the ceiling still ends a stuck model
    stuck = lambda h: say("again", "tool_use", call_block(1, "add", a=1, b=1))
    out, why, hist = run("go", stuck, tools, max_steps=4)
    assert why == "max_steps" and paired(hist)
    assert any("repeated" in r["content"] for m in hist[1:] if isinstance(m["content"], list)
               for r in m["content"] if r["type"] == "tool_result")

    # cut-off text continues, but only a few times
    cut = replies(say("part one ", "max_tokens"), say("part two"))
    assert run("go", cut, tools)[:2] == ("part two", "done")
    assert run("go", lambda h: say("x", "max_tokens"), tools)[1] == "max_continues"

    # an ordinary tool failure goes to the model and the run continues
    def missing():
        raise FileNotFoundError("no such file: a.txt")
    out, why, hist = run("go", replies(say("a", "tool_use", call_block(1, "m")), say("sorry")),
                         {"m": missing})
    assert (out, why) == ("sorry", "done") and "tool error" in hist[2]["content"][0]["content"]

    # pause_turn: send the assistant content back unchanged and go on
    assert run("go", replies(say("wait", "pause_turn"), say("fin")), tools)[:2] == ("fin", "done")

    # a fatal error aborts at once
    def denied():
        raise PermissionError("auth rejected")
    out, why, hist = run("go", replies(say("a", "tool_use", call_block(1, "d"))), {"d": denied})
    assert why == "fatal" and paired(hist)
    print("ok: stop reasons, retries, nudge, ceiling and fatal abort all behave")
