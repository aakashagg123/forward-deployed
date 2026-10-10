"""Run the several tool calls of one turn, then answer them in one user message.

Independent read-only calls run in threads. Anything else runs one at a time.
Runs offline:  python3 code/parallel_tools.py
"""
import threading
import time
from concurrent.futures import ThreadPoolExecutor


def outcome(call, impls):
    """Run one call. A crash becomes an error result, never an exception."""
    try:
        text, is_error = str(impls[call["name"]](**call["input"])), False
    except Exception as exc:
        text, is_error = f"{type(exc).__name__}: {exc}", True
    return {"type": "tool_result", "tool_use_id": call["id"], "content": text, "is_error": is_error}


def run_batch(calls, impls, read_only):
    """Return one tool_result per call, in call order."""
    if all(c["name"] in read_only for c in calls):
        with ThreadPoolExecutor(max_workers=len(calls)) as pool:   # independent reads
            return list(pool.map(lambda c: outcome(c, impls), calls))
    results = []
    for n, call in enumerate(calls):                               # side effects: in order
        res = outcome(call, impls)
        results.append(res)
        if res["is_error"]:                                        # skip the rest, but still answer
            for rest in calls[n + 1:]:
                results.append({"type": "tool_result", "tool_use_id": rest["id"], "is_error": True,
                                "content": f"Not executed: the earlier {call['name']} call failed."})
            break
    return results


def user_turn(results, note=None):
    """All results go in ONE user message. tool_result blocks come first, any text after."""
    content = list(results) + ([{"type": "text", "text": note}] if note else [])
    return {"role": "user", "content": content}


if __name__ == "__main__":
    # Three reads wait for each other at a barrier. Only real parallelism gets through.
    gate = threading.Barrier(3, timeout=2)
    def slow_read(path):
        gate.wait()
        return f"contents of {path}"
    calls = [{"id": f"t{i}", "name": "read", "input": {"path": f"f{i}.txt"}} for i in range(3)]
    t0 = time.time()
    results = run_batch(calls, {"read": slow_read}, read_only={"read"})
    assert [r["content"] for r in results] == [f"contents of f{i}.txt" for i in range(3)]
    assert [r["tool_use_id"] for r in results] == ["t0", "t1", "t2"]   # order is kept
    assert not any(r["is_error"] for r in results) and time.time() - t0 < 1.5

    # one message, results first, text last
    turn = user_turn(results, note="Anything else?")
    assert turn["role"] == "user" and len(turn["content"]) == 4
    assert [b["type"] for b in turn["content"]] == ["tool_result"] * 3 + ["text"]

    # a write in the batch forces sequential runs; a failure skips the rest but is still answered
    log = []
    impls = {"write": lambda p: log.append(p) or "ok",
             "fail": lambda: 1 / 0}
    mixed = [{"id": "a", "name": "write", "input": {"p": 1}},
             {"id": "b", "name": "fail", "input": {}},
             {"id": "c", "name": "write", "input": {"p": 2}}]
    res = run_batch(mixed, impls, read_only={"read"})
    assert log == [1] and [r["tool_use_id"] for r in res] == ["a", "b", "c"]
    assert res[1]["content"].startswith("ZeroDivisionError")
    assert res[2]["is_error"] and res[2]["content"].startswith("Not executed")
    print("ok: parallel reads, ordered results, one user turn")
