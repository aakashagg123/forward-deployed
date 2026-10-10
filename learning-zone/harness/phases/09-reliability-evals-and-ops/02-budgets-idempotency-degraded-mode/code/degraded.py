"""Degraded mode: always return an honest, structured outcome.

Run:  python3 code/degraded.py
"""
from guards import Budget


def run_with_degrade(steps, do_step, budget):
    """Run steps in order. Return complete, degraded, or failed, and always keep verified work."""
    done = []
    for step in steps:
        hit = budget.exceeded()
        if hit:
            return {"status": "degraded", "done": done, "remaining": steps[len(done):],
                    "reason": f"budget exhausted: {', '.join(hit)}", "spent": budget.report(),
                    "next": "narrow the scope or raise the budget, then resume"}
        try:
            done.append(do_step(step, budget))
        except Exception as e:
            return {"status": "failed", "done": done, "failed_step": step, "error": str(e),
                    "next": "fix the error and resume from the failed step, or ask a human"}
    return {"status": "complete", "done": done, "spent": budget.report()}


if __name__ == "__main__":
    def do_step(step, budget):
        if step == "boom":
            raise RuntimeError("type-check failed in boom.py")
        budget.charge(steps=1, tokens=400)
        return f"{step}: ok"

    five = ["a", "b", "c", "d", "e"]

    full = run_with_degrade(five, do_step, Budget(max_steps=10, max_tokens=10_000))
    assert full["status"] == "complete" and len(full["done"]) == 5

    # The token meter trips after 3 steps (3 x 400 >= 1000): keep 3, name the 2 left, say why.
    cut = run_with_degrade(five, do_step, Budget(max_steps=10, max_tokens=1000))
    assert cut["status"] == "degraded"
    assert cut["done"] == ["a: ok", "b: ok", "c: ok"] and cut["remaining"] == ["d", "e"]
    assert "tokens" in cut["reason"] and cut["spent"]["tokens"] == "1200/1000"

    # A failure keeps the work done so far and names the step that broke.
    bad = run_with_degrade(["a", "boom", "c"], do_step, Budget())
    assert bad["status"] == "failed" and bad["done"] == ["a: ok"] and bad["failed_step"] == "boom"
    print("degraded ok:", cut["status"], cut["reason"])
