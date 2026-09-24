"""A one-command eval suite + gate composing the phase. Run:  python3 eval_harness.py"""


def run_evals(suites):
    """suites: {name: callable()->score 0..1}. Returns aggregate + per-suite."""
    scores = {name: fn() for name, fn in suites.items()}
    agg = sum(scores.values()) / len(scores)
    return {"aggregate": round(agg, 3), "suites": scores}


def gate(current, baseline, tol=0.02):
    return current >= baseline - tol


if __name__ == "__main__":
    suites = {
        "golden": lambda: 0.92,
        "trajectory": lambda: 1.0,
        "adversarial": lambda: 1.0,
    }
    report = run_evals(suites)
    passed = gate(report["aggregate"], 0.93)
    print(report, "PASS" if passed else "FAIL")
    raise SystemExit(0 if passed else 1)
