"""Token -> cost accounting with attribution. Run:  python3 cost.py

Prices are illustrative USD per 1M tokens — verify current pricing before relying on it.
"""
PRICES = {
    "claude-opus-5": {"in": 5.0, "out": 25.0},
    "claude-haiku-4-5-20251001": {"in": 0.8, "out": 4.0},
}


class CostMeter:
    def __init__(self):
        self.by_tag = {}

    def record(self, model, in_tokens, out_tokens, tag="default"):
        p = PRICES[model]
        cost = (in_tokens * p["in"] + out_tokens * p["out"]) / 1_000_000
        self.by_tag[tag] = self.by_tag.get(tag, 0.0) + cost
        return cost

    def report(self):
        return {tag: round(c, 6) for tag, c in self.by_tag.items()}


if __name__ == "__main__":
    m = CostMeter()
    m.record("claude-opus-5", 10_000, 2_000, tag="feature:refactor")
    m.record("claude-haiku-4-5-20251001", 50_000, 5_000, tag="feature:search")
    print(m.report())
