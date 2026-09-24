"""Score an agent trajectory against expectations. Run:  python3 trajectory.py"""


def score_trajectory(steps, must_include=(), must_not=(), max_steps=None):
    tools = [s["tool"] for s in steps]
    problems = []
    for t in must_include:
        if t not in tools:
            problems.append(f"missing expected tool: {t}")
    for t in must_not:
        if t in tools:
            problems.append(f"used forbidden tool: {t}")
    if max_steps and len(steps) > max_steps:
        problems.append(f"too many steps: {len(steps)} > {max_steps}")
    score = 1.0 if not problems else max(0.0, 1 - 0.34 * len(problems))
    return {"score": round(score, 2), "problems": problems}


if __name__ == "__main__":
    traj = [{"tool": "read"}, {"tool": "edit"}, {"tool": "bash"}]
    print(score_trajectory(traj, must_include=["read", "bash"], must_not=["rm"], max_steps=10))
    bad = [{"tool": "edit"}, {"tool": "rm"}]
    print(score_trajectory(bad, must_include=["read"], must_not=["rm"]))
