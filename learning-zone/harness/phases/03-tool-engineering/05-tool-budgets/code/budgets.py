"""Tool budget guard: a total cap + a rolling-window rate limit. Pre-dispatch gate.

Run:  python3 budgets.py
"""
import time


class ToolBudget:
    def __init__(self, max_total=20, per_window=5, window_s=10):
        self.max_total = max_total
        self.per_window = per_window
        self.window_s = window_s
        self.total = 0
        self.calls = []                        # timestamps within the window

    def allow(self, now=None):
        now = now if now is not None else time.time()
        self.calls = [t for t in self.calls if now - t < self.window_s]
        if self.total >= self.max_total:
            return False, "total tool budget exhausted"
        if len(self.calls) >= self.per_window:
            return False, f"rate limit: max {self.per_window}/{self.window_s}s"
        self.calls.append(now)
        self.total += 1
        return True, None


if __name__ == "__main__":
    b = ToolBudget(max_total=20, per_window=2, window_s=10)
    print(b.allow(now=0))    # (True, None)
    print(b.allow(now=0))    # (True, None)
    print(b.allow(now=0))    # (False, 'rate limit: max 2/10s')
    print(b.allow(now=11))   # (True, None) — window slid
