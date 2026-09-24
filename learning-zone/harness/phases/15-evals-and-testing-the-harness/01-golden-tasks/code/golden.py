"""A golden-set eval runner. Run:  python3 golden.py"""


def run_golden(cases, harness, score):
    """cases: [{input, expect}]; harness(input)->output; score(output, expect)->0..1."""
    results = []
    for c in cases:
        out = harness(c["input"])
        results.append({"input": c["input"], "score": score(out, c["expect"])})
    avg = sum(r["score"] for r in results) / len(results)
    return {"pass_rate": avg, "results": results}


if __name__ == "__main__":
    cases = [{"input": "2+2", "expect": "4"}, {"input": "cap of France", "expect": "Paris"}]
    harness = lambda x: {"2+2": "4", "cap of France": "Lyon"}[x]    # buggy on case 2
    score = lambda out, exp: 1.0 if exp.lower() in out.lower() else 0.0
    print(run_golden(cases, harness, score)["pass_rate"])
