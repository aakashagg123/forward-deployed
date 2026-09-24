"""Degrade-gracefully run wrapper: always return a structured, honest outcome.

Run:  python3 degraded.py
"""


def run_with_degrade(do, budget):
    """do(budget)->partial result. Returns complete | degraded | failed."""
    try:
        result = do(budget)
        hit = budget.exceeded()
        if hit:
            return {"status": "degraded", "partial": result,
                    "reason": f"budget exhausted: {hit}",
                    "next": "narrow the scope or raise the budget and resume"}
        return {"status": "complete", "result": result}
    except Exception as e:
        return {"status": "failed", "error": str(e),
                "next": "retry later or escalate to a human"}


if __name__ == "__main__":
    class B:
        def exceeded(self):
            return ["tokens"]

    print(run_with_degrade(lambda b: {"done": ["step1", "step2"]}, B()))
    print(run_with_degrade(lambda b: (_ for _ in ()).throw(RuntimeError("boom")), B()))
