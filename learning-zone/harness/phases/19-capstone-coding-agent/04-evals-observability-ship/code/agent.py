"""Capstone 04: production wrapper — budget (P14) + trace (P16) + cost (P16) + eval gate (P15).

Self-contained minimal versions of the earlier modules so it runs. Run: python3 agent.py
"""
import time
from contextlib import contextmanager


class Budget:                                   # P14
    def __init__(self, max_usd=1.0):
        self.spent, self.max_usd = 0.0, max_usd

    def charge(self, usd):
        self.spent += usd

    def exceeded(self):
        return self.spent >= self.max_usd


class Tracer:                                   # P16
    def __init__(self):
        self.spans = []

    @contextmanager
    def span(self, name, **attrs):
        rec = {"name": name, "attrs": attrs}
        self.spans.append(rec)
        start = time.perf_counter()
        try:
            yield rec
        finally:
            rec["ms"] = round((time.perf_counter() - start) * 1000, 1)


class CostMeter:                                # P16
    def __init__(self):
        self.total = 0.0

    def record(self, model, ti, to, tag="default"):
        self.total += (ti * 5 + to * 25) / 1_000_000
        return self.total

    def report(self):
        return {"usd": round(self.total, 6)}


def run_observed(task, agent, budget, tracer, cost):
    with tracer.span("agent.run", task=task):
        if budget.exceeded():
            return {"status": "degraded", "reason": "budget"}
        out = agent(task)
        cost.record("claude-opus-5", 1000, 200, tag="capstone")
        return {"status": "complete", "result": out,
                "spans": len(tracer.spans), "cost": cost.report()}


def eval_gate(score, baseline=0.9, tol=0.02):   # P15
    return score >= baseline - tol


if __name__ == "__main__":
    report = run_observed("fix the bug", agent=lambda t: "fixed",
                          budget=Budget(), tracer=Tracer(), cost=CostMeter())
    print(report)
    print("eval gate:", "PASS" if eval_gate(0.94) else "HOLD")
