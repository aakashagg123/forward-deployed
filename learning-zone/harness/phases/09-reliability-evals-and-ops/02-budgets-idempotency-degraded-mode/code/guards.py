"""Three guards for a runaway agent: a budget, a tool rate limit, and idempotent side effects.

Run:  python3 code/guards.py
"""
import hashlib
import json


class Budget:
    """Several meters at once. Hitting any one of them stops the run."""

    def __init__(self, max_steps=20, max_tokens=100_000, max_usd=1.0):
        self.limits = {"steps": max_steps, "tokens": max_tokens, "usd": max_usd}
        self.spent = {"steps": 0, "tokens": 0, "usd": 0.0}

    def charge(self, steps=0, tokens=0, usd=0.0):
        self.spent["steps"] += steps
        self.spent["tokens"] += tokens
        self.spent["usd"] += usd

    def exceeded(self):
        return [k for k in self.limits if self.spent[k] >= self.limits[k]]

    def report(self):
        return {k: f"{self.spent[k]}/{self.limits[k]}" for k in self.limits}


class ToolBudget:
    """A total cap on tool calls plus a rolling-window rate limit. Call allow() before dispatch."""

    def __init__(self, max_total=20, per_window=5, window_s=10):
        self.max_total, self.per_window, self.window_s = max_total, per_window, window_s
        self.total, self.calls = 0, []

    def allow(self, now):
        self.calls = [t for t in self.calls if now - t < self.window_s]
        if self.total >= self.max_total:
            return False, "total tool budget exhausted"
        if len(self.calls) >= self.per_window:
            return False, f"rate limit: max {self.per_window} per {self.window_s}s"
        self.calls.append(now)
        self.total += 1
        return True, None


class Idempotent:
    """Run a side effect once per key. A repeat gets the stored result and does nothing."""

    def __init__(self):
        self._done = {}

    def run(self, key, action):
        if key in self._done:
            return self._done[key], "replayed"
        self._done[key] = action()
        return self._done[key], "executed"


def key_for(tool, args):
    """Derive the key from intent: same tool and args give the same key."""
    blob = json.dumps([tool, args], sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


if __name__ == "__main__":
    # Budget: the token meter trips first, after the second step.
    b = Budget(max_steps=5, max_tokens=1000, max_usd=1.0)
    for _ in range(5):
        if b.exceeded():
            break
        b.charge(steps=1, tokens=600, usd=0.03)
    assert b.exceeded() == ["tokens"] and b.spent["steps"] == 2
    assert b.report()["tokens"] == "1200/1000"

    # ToolBudget: the rate limit blocks the third call, then the window slides.
    tb = ToolBudget(max_total=3, per_window=2, window_s=10)
    assert tb.allow(0) == (True, None) and tb.allow(0) == (True, None)
    ok, why = tb.allow(0)
    assert not ok and "rate limit" in why
    assert tb.allow(11) == (True, None)            # window slid, third and last call
    ok, why = tb.allow(30)
    assert not ok and "total" in why               # total cap holds even with a free window

    # Idempotent: two identical calls, one real send. A different call still runs.
    idem, sent = Idempotent(), []

    def send(to):
        return lambda: (sent.append(to), f"sent to {to}")[1]

    k = key_for("send_email", {"to": "a@b.com"})
    assert idem.run(k, send("a@b.com")) == ("sent to a@b.com", "executed")
    assert idem.run(k, send("a@b.com")) == ("sent to a@b.com", "replayed")
    assert sent == ["a@b.com"]
    k2 = key_for("send_email", {"to": "c@d.com"})
    assert k2 != k and idem.run(k2, send("c@d.com"))[1] == "executed"
    assert key_for("t", {"a": 1, "b": 2}) == key_for("t", {"b": 2, "a": 1})   # arg order is irrelevant
    print("guards ok")
