"""A multi-meter (steps/tokens/cost) budget guard. Run:  python3 budget.py"""


class Budget:
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


if __name__ == "__main__":
    b = Budget(max_steps=3, max_tokens=1000, max_usd=0.10)
    for _ in range(5):
        if b.exceeded():
            break
        b.charge(steps=1, tokens=400, usd=0.03)
    print("hit:", b.exceeded(), b.report())
