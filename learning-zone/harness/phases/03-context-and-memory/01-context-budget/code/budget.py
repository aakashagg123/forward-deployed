"""Category-based context budgeter. Run:  python3 code/budget.py"""


def estimate(text):
    return max(1, round(len(text) / 4))      # about 4 chars per token; optimistic for current models, use count_tokens when tight


class ContextBudget:
    def __init__(self, limit, reserve_output, weights):
        if sum(weights.values()) > 1.0 + 1e-9:
            raise ValueError("weights must sum to 1.0 or less")
        self.limit, self.reserve = limit, reserve_output
        self.weights = weights                   # category -> fraction of usable tokens

    def allocation(self):
        usable = self.limit - self.reserve       # the reply needs room too
        return {cat: int(usable * w) for cat, w in self.weights.items()}

    def check(self, sizes):
        alloc = self.allocation()
        return {cat: (sizes.get(cat, 0), alloc[cat], sizes.get(cat, 0) <= alloc[cat])
                for cat in alloc}

    def fit(self, sizes):
        """Tokens each over-budget category must shed. Input to trim and compact."""
        return {cat: used - cap
                for cat, (used, cap, ok) in self.check(sizes).items() if not ok}


if __name__ == "__main__":
    b = ContextBudget(limit=200_000, reserve_output=8000,
                      weights={"system": .05, "memory": .10, "files": .45, "history": .40})
    sizes = {"system": 6000, "files": 100_000, "history": 90_000}
    for cat, (used, cap, ok) in b.check(sizes).items():
        print(f"{cat:8} used={used:7} cap={cap:7} {'OK' if ok else 'OVER'}")
    shed = b.fit(sizes)
    print("must shed:", shed)

    alloc = b.allocation()
    assert sum(alloc.values()) + b.reserve <= b.limit          # the reply always fits
    assert alloc["files"] == int(192_000 * .45)                # 86,400 tokens
    assert shed == {"files": 13_600, "history": 13_200}
    assert "memory" not in shed and "system" not in shed       # under-budget categories shed nothing
    assert b.fit({"files": 1}) == {}                           # a small request needs no trimming
    try:
        ContextBudget(1000, 100, {"a": .7, "b": .7})
    except ValueError:
        pass
    else:
        raise AssertionError("weights above 1.0 must be rejected")
    assert estimate("abcd" * 100) == 100
    print("budget ok")
