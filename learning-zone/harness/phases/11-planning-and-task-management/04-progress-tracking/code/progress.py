"""Verify-driven progress tracking with re-plan escalation. Run: python3 progress.py"""


class Progress:
    def __init__(self, max_retries=2):
        self.max_retries = max_retries
        self.attempts = {}

    def run_step(self, step, do, verify):
        n = self.attempts.get(step, 0)
        while n <= self.max_retries:
            do(step)
            if verify(step):
                return {"step": step, "status": "complete", "attempts": n + 1}
            n += 1
            self.attempts[step] = n
        return {"step": step, "status": "needs_replan", "attempts": n}


if __name__ == "__main__":
    calls = {"build": 0}
    print(Progress(max_retries=3).run_step(
        "build", lambda s: calls.__setitem__(s, calls[s] + 1), lambda s: calls[s] >= 3))
    print(Progress(max_retries=1).run_step("flaky", lambda s: None, lambda s: False))
