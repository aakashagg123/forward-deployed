"""The failure ladder: retry transport errors, repair bad content, fall back to another model.

Run:  python3 code/ladder.py
"""
import json
import random


class Transient(Exception):
    """A failure that may pass on its own: rate limit, overload, network blip."""


def retry(call, max_attempts=4, base=0.5, cap=8.0, sleep=lambda s: None, rng=random):
    """Retry Transient errors with exponential backoff plus jitter. Anything else fails fast."""
    for attempt in range(max_attempts):
        try:
            return call()
        except Transient:
            if attempt == max_attempts - 1:
                raise
            sleep(min(cap, base * 2 ** attempt) + rng.uniform(0, base))


def repair_loop(generate, validate, max_attempts=3):
    """generate(feedback) -> output; validate(output) -> None or an error message."""
    feedback, err = None, None
    for attempt in range(max_attempts):
        out = generate(feedback)
        err = validate(out)
        if err is None:
            return {"ok": True, "output": out, "attempts": attempt + 1}
        feedback = f"Your output was invalid: {err}. Return only the corrected output."
    return {"ok": False, "error": err, "attempts": max_attempts}


def route(task, cheap, strong, is_hard):
    """Choose the first model by fit. The rest of the list is the fallback order."""
    return [strong, cheap] if is_hard(task) else [cheap, strong]


def with_fallback(chain, call):
    """Try each model in order. Return the first success, else raise the last error."""
    last = None
    for model in chain:
        try:
            return {"model": model, "result": call(model)}
        except Exception as e:
            last = e
    raise RuntimeError(f"all options failed: {last}")


def climb(chain, call_model, validate, sleep=lambda s: None):
    """Retry inside repair, repair inside fallback: each rung handles one failure class."""
    def attempt(model):
        out = repair_loop(
            lambda feedback: retry(lambda: call_model(model, feedback), sleep=sleep), validate)
        if not out["ok"]:
            raise ValueError(out["error"])
        return out
    return with_fallback(chain, attempt)


def need_age(text):
    return None if "age" in json.loads(text) else "missing key 'age'"


if __name__ == "__main__":
    # 1. Retry: two transient errors, then success. Delays grow and stay inside the jitter band.
    calls, delays = {"n": 0}, []

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise Transient("503")
        return "ok"

    assert retry(flaky, sleep=delays.append) == "ok" and calls["n"] == 3
    assert 0.5 <= delays[0] <= 1.0 and 1.0 <= delays[1] <= 1.5

    # 2. A non-transient error is not retried. An exhausted budget re-raises.
    calls["n"] = 0

    def bad_request():
        calls["n"] += 1
        raise ValueError("400")

    try:
        retry(bad_request)
        raise AssertionError("expected ValueError")
    except ValueError:
        assert calls["n"] == 1
    try:
        retry(lambda: (_ for _ in ()).throw(Transient("503")), max_attempts=2)
        raise AssertionError("expected Transient")
    except Transient:
        pass

    # 3. Repair: the validator's error text reaches the model as feedback.
    seen = []

    def gen(feedback):
        seen.append(feedback)
        return '{"name": "ada"}' if feedback is None else '{"name": "ada", "age": 36}'

    fixed = repair_loop(gen, need_age)
    assert fixed["ok"] and fixed["attempts"] == 2 and "missing key 'age'" in seen[1]
    assert not repair_loop(lambda fb: '{"name": "ada"}', need_age)["ok"]

    # 4. Routing picks the first model by fit.
    hard = lambda t: "refactor" in t
    assert route("refactor auth", "small", "big", hard) == ["big", "small"]
    assert route("fix typo", "small", "big", hard) == ["small", "big"]

    # 5. The full ladder: "big" is overloaded, "small" needs one repair round.
    tried = []

    def call_model(model, feedback):
        tried.append(model)
        if model == "big":
            raise Transient("overloaded")
        return '{"name": "ada"}' if feedback is None else '{"name": "ada", "age": 36}'

    out = climb(["big", "small"], call_model, need_age)
    assert out["model"] == "small" and out["result"]["attempts"] == 2
    assert tried == ["big"] * 4 + ["small"] * 2      # 4 retries on big, then 2 repair rounds

    # 6. When every rung fails, the caller gets one clear error, not a hang.
    try:
        climb(["big"], lambda m, fb: (_ for _ in ()).throw(Transient("down")), need_age)
        raise AssertionError("expected RuntimeError")
    except RuntimeError as e:
        assert "all options failed" in str(e)
    print("ladder ok: retry, repair, fallback all behave")
