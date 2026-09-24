"""Category-based context budgeter. Run:  python3 budget.py"""


def estimate(text):
    return max(1, round(len(text) / 4))          # ~4 chars/token (Phase 1)


class ContextBudget:
    def __init__(self, limit, reserve_output, weights):
        self.limit, self.reserve = limit, reserve_output
        self.weights = weights                   # category -> fraction of remaining

    def allocation(self):
        usable = self.limit - self.reserve
        return {cat: int(usable * w) for cat, w in self.weights.items()}

    def check(self, sizes):
        alloc = self.allocation()
        return {cat: (sizes.get(cat, 0), alloc[cat], sizes.get(cat, 0) <= alloc[cat])
                for cat in alloc}


if __name__ == "__main__":
    b = ContextBudget(limit=200_000, reserve_output=8000,
                      weights={"system": .05, "memory": .10, "files": .45, "history": .40})
    for cat, (used, cap, ok) in b.check({"files": 100_000, "history": 90_000}).items():
        print(f"{cat:8} used={used:7} cap={cap:7} {'OK' if ok else 'OVER'}")
