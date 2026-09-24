"""Exponential backoff with jitter. sleep is injected so it's testable. Run: python3 retry.py"""
import random

TRANSIENT = (429, 500, 502, 503, 504)


def retry(call, is_transient, max_attempts=5, base=0.5, sleep=lambda s: None, rng=random):
    for attempt in range(max_attempts):
        try:
            return call()
        except Exception as e:
            if not is_transient(e) or attempt == max_attempts - 1:
                raise
            delay = base * (2 ** attempt) + rng.uniform(0, base)   # backoff + jitter
            sleep(delay)


if __name__ == "__main__":
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("503")
        return "ok"

    print(retry(flaky, is_transient=lambda e: "503" in str(e)), "after", calls["n"], "attempts")
